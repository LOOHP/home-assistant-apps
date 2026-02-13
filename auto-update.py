from __future__ import annotations

import os
import re
from pathlib import Path
from typing import List, Optional, Tuple

import requests
from packaging.version import Version, InvalidVersion
from ruamel.yaml import YAML

SEMVER_RE = re.compile(r"^v?\d+\.\d+\.\d+([\-+].+)?$")


def parse_image(image: str) -> Tuple[str, str]:
    image = image.strip()

    # Remove digest
    if "@" in image:
        image = image.split("@", 1)[0]

    # Remove tag
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
    versions = []
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


def update_config(path: Path) -> bool:
    yaml = YAML()
    yaml.preserve_quotes = True

    data = yaml.load(path.read_text())
    if not isinstance(data, dict):
        return False

    image = data.get("image")
    if not image:
        return False

    registry, repo = parse_image(str(image))
    if registry != "ghcr.io":
        print(f"SKIP   {path} (registry {registry})")
        return False

    tags = list_ghcr_tags(repo)
    latest = latest_semver(tags)
    if not latest:
        print(f"SKIP   {path} (no semver tags)")
        return False

    new_version = latest.lstrip("v")
    current = str(data.get("version", "")).strip('"')

    if current == new_version:
        print(f"OK     {path} ({current})")
        return False

    data["version"] = new_version
    yaml.dump(data, path.open("w"))

    print(f"UPDATE {path}: {current} → {new_version}")
    return True


def main() -> None:
    configs = sorted(Path(".").glob("*/config.yaml"))
    if not configs:
        print("No ./*/config.yaml files found")
        return

    updated = 0
    for cfg in configs:
        try:
            if update_config(cfg):
                updated += 1
        except Exception as e:
            print(f"ERROR  {cfg}: {e}")

    print(f"\nDone. Updated {updated} addon(s).")


if __name__ == "__main__":
    main()
