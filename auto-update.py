from __future__ import annotations

import base64
import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from packaging.version import InvalidVersion, Version
from ruamel.yaml import YAML

SEMVER_RE = re.compile(r"^v?\d+\.\d+\.\d+([\-+].+)?$")
GITHUB_REPO_RE = re.compile(r"^https?://github\.com/([^/]+)/([^/]+?)(?:\.git)?/?$")


def parse_image(image: str) -> Tuple[str, str]:
    image = image.strip()
    if "@" in image:
        image = image.split("@", 1)[0]
    if ":" in image and image.count(":") == 1 and "/" in image.split(":")[0]:
        image = image.rsplit(":", 1)[0]
    parts = image.split("/")
    if "." in parts[0]:
        return parts[0], "/".join(parts[1:])
    return "ghcr.io", image


def parse_www_authenticate(header: str) -> Tuple[Optional[str], Optional[str], Optional[str]]:
    realm = service = scope = None
    for key, value in re.findall(r'(\w+)="([^"]+)"', header or ""):
        if key == "realm":
            realm = value
        elif key == "service":
            service = value
        elif key == "scope":
            scope = value
    return realm, service, scope


def get_bearer_token(www_auth: str) -> Optional[str]:
    realm, service, scope = parse_www_authenticate(www_auth)
    if not realm:
        return None

    params = {}
    if service:
        params["service"] = service
    if scope:
        params["scope"] = scope

    username = os.getenv("GHCR_USERNAME") or os.getenv("GITHUB_USERNAME")
    token = os.getenv("GHCR_TOKEN") or os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    auth = (username, token) if username and token else None

    r = requests.get(realm, params=params, auth=auth, timeout=20)
    if r.status_code != 200:
        return None

    data = r.json()
    return data.get("token") or data.get("access_token")


def list_ghcr_tags(repository: str) -> List[str]:
    base_url = f"https://ghcr.io/v2/{repository}/tags/list"

    def do_get(url: str, *, headers=None, params=None):
        return requests.get(url, headers=headers, params=params, timeout=20)

    r = do_get(base_url, params={"n": 1000})
    headers = {}

    if r.status_code == 401:
        bearer = get_bearer_token(r.headers.get("WWW-Authenticate", ""))
        if not bearer:
            raise RuntimeError(
                f"Authentication required for {repository}. "
                f"Set GHCR_USERNAME and GHCR_TOKEN for private repos."
            )
        headers = {"Authorization": f"Bearer {bearer}"}
        r = do_get(base_url, headers=headers, params={"n": 1000})

    if r.status_code != 200:
        raise RuntimeError(f"Failed to list tags for {repository}: {r.text[:200]}")

    tags: List[str] = []
    while True:
        payload = r.json() or {}
        tags.extend(payload.get("tags") or [])

        link = r.headers.get("Link", "")
        m = re.search(r'<([^>]+)>;\s*rel="next"', link)
        if not m:
            break

        next_url = m.group(1)
        r = do_get(next_url, headers=headers)
        if r.status_code != 200:
            raise RuntimeError(f"Pagination failed for {repository}: {r.text[:200]}")

    seen = set()
    out = []
    for t in tags:
        if t not in seen:
            seen.add(t)
            out.append(t)
    return out


def latest_semver(tags: List[str]) -> Optional[str]:
    versions: List[Tuple[Version, str]] = []
    for tag in tags:
        if tag == "latest" or not SEMVER_RE.match(tag):
            continue
        try:
            versions.append((Version(tag.lstrip("v")), tag))
        except InvalidVersion:
            pass
    if not versions:
        return None
    versions.sort(key=lambda x: x[0])
    return versions[-1][1]


def github_repo_full_from_url(url: str) -> Optional[str]:
    url = (url or "").strip()
    m = GITHUB_REPO_RE.match(url)
    if not m:
        return None
    return f"{m.group(1)}/{m.group(2)}"


def github_headers() -> dict:
    token = os.getenv("GITHUB_TOKEN") or os.getenv("GH_TOKEN")
    headers = {"Accept": "application/vnd.github+json"}
    if token:
        headers["Authorization"] = f"Bearer {token}"
    return headers


def github_default_branch(repo_full: str) -> Optional[str]:
    url = f"https://api.github.com/repos/{repo_full}"
    r = requests.get(url, headers=github_headers(), timeout=20)
    if r.status_code != 200:
        return None
    return (r.json() or {}).get("default_branch")


def github_fetch_file(repo_full: str, path_in_repo: str, ref: str) -> Optional[str]:
    url = f"https://api.github.com/repos/{repo_full}/contents/{path_in_repo}"
    r = requests.get(url, headers=github_headers(), params={"ref": ref}, timeout=20)
    if r.status_code != 200:
        return None

    data = r.json() or {}
    dl = data.get("download_url")
    if dl:
        rr = requests.get(dl, headers=github_headers(), timeout=20)
        if rr.status_code == 200:
            return rr.text
        return None

    content = data.get("content")
    encoding = data.get("encoding")
    if content and encoding == "base64":
        return base64.b64decode(content).decode("utf-8", errors="replace")

    return None


def github_fetch_first_existing(repo_full: str, paths: List[str], ref: str) -> Optional[Tuple[str, str]]:
    for p in paths:
        txt = github_fetch_file(repo_full, p, ref)
        if txt is not None:
            return p, txt
    return None


def github_get_release_body(repo_full: str, version: str) -> Optional[Tuple[str, str]]:
    headers = github_headers()
    for tag in (f"v{version}", version):
        url = f"https://api.github.com/repos/{repo_full}/releases/tags/{tag}"
        r = requests.get(url, headers=headers, timeout=20)
        if r.status_code == 200:
            data = r.json() or {}
            body = (data.get("body") or "").strip()
            tag_name = (data.get("tag_name") or tag).strip()
            if body:
                return tag_name, body
    return None


def write_if_changed(dst: Path, content: str) -> bool:
    current = dst.read_text() if dst.exists() else None
    if current == content:
        return False
    dst.write_text(content)
    return True


def prepend_release_notes(dst: Path, version: str, body_md: str) -> bool:
    existing = dst.read_text() if dst.exists() else ""
    if re.search(rf"^##\s*\[?v?{re.escape(version)}\]?\b", existing, flags=re.M):
        return False
    new_section = f"## {version}\n\n{body_md.strip()}\n\n"
    dst.write_text(new_section + existing)
    return True


def sync_upstream_docs(addon_dir: Path, repo_full: str, version_for_release_fallback: str) -> bool:
    branch = github_default_branch(repo_full)
    if not branch:
        print(f"DOCS   skip ({repo_full} default branch not found)")
        return False

    changed = False

    readme = github_fetch_first_existing(
        repo_full,
        ["README.md", "Readme.md", "readme.md", "docs/README.md", "docs/readme.md"],
        branch,
    )
    if readme is not None:
        _, text = readme
        if write_if_changed(addon_dir / "README.md", text):
            print(f"README    {addon_dir/'README.md'} updated from {repo_full}@{branch}")
            changed = True
        else:
            print(f"README    {addon_dir/'README.md'} OK")
    else:
        print(f"README    skip ({repo_full}@{branch} README not found)")

    changelog = github_fetch_first_existing(
        repo_full,
        [
            "CHANGELOG.md",
            "Changelog.md",
            "changelog.md",
            "docs/CHANGELOG.md",
            "docs/Changelog.md",
            "docs/changelog.md",
            "CHANGELOG",
            "Changelog",
            "changelog",
        ],
        branch,
    )

    if changelog is not None:
        _, text = changelog
        if write_if_changed(addon_dir / "CHANGELOG.md", text):
            print(f"CHANGELOG {addon_dir/'CHANGELOG.md'} updated from {repo_full}@{branch}")
            changed = True
        else:
            print(f"CHANGELOG {addon_dir/'CHANGELOG.md'} OK")
    else:
        rel = github_get_release_body(repo_full, version_for_release_fallback)
        if rel:
            _, body = rel
            if prepend_release_notes(addon_dir / "CHANGELOG.md", version_for_release_fallback, body):
                print(f"CHANGELOG {addon_dir/'CHANGELOG.md'} updated from {repo_full} release notes")
                changed = True
            else:
                print(f"CHANGELOG {addon_dir/'CHANGELOG.md'} already has {version_for_release_fallback}")
        else:
            print(
                f"CHANGELOG skip ({repo_full}: no changelog file and no release notes for {version_for_release_fallback})"
            )

    return changed


def update_config(path: Path) -> Tuple[bool, bool]:
    yaml = YAML()
    yaml.preserve_quotes = True

    data = yaml.load(path.read_text())
    if not isinstance(data, dict):
        return False, False

    image = data.get("image")
    if not image:
        return False, False

    registry, repo = parse_image(str(image))
    if registry != "ghcr.io":
        print(f"SKIP   {path} (registry {registry})")
        return False, False

    tags = list_ghcr_tags(repo)
    latest = latest_semver(tags)
    if not latest:
        print(f"SKIP   {path} (no semver tags)")
        return False, False

    new_version = latest.lstrip("v")
    current = str(data.get("version", "")).strip().strip('"')

    version_changed = False
    if current != new_version:
        data["version"] = new_version
        with path.open("w") as f:
            yaml.dump(data, f)
        print(f"UPDATE {path}: {current} → {new_version}")
        version_changed = True
    else:
        print(f"OK     {path} ({current})")

    addon_dir = path.parent
    repo_url = data.get("repo")
    repo_full = github_repo_full_from_url(str(repo_url)) if repo_url else None

    docs_changed = False
    if repo_full:
        try:
            docs_changed = sync_upstream_docs(addon_dir, repo_full, new_version)
        except Exception as e:
            print(f"DOCS   ERROR {path}: {e}")
    else:
        if repo_url:
            print(f"DOCS   skip (invalid repo URL: {repo_url})")
        else:
            print("DOCS   skip (no repo: field in config.yaml)")

    return version_changed, docs_changed


def main() -> None:
    configs = sorted(Path(".").glob("*/config.yaml"))
    if not configs:
        print("No ./*/config.yaml files found")
        return

    updated_versions = 0
    updated_docs = 0

    for cfg in configs:
        try:
            v_changed, d_changed = update_config(cfg)
            if v_changed:
                updated_versions += 1
            if d_changed:
                updated_docs += 1
        except Exception as e:
            print(f"ERROR  {cfg}: {e}")

    print(f"\nDone. Updated versions: {updated_versions}. Updated docs: {updated_docs}.")


if __name__ == "__main__":
    main()