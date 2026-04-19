import asyncio
import json
import os
import socket
import sys
import time
from collections import deque
from contextlib import asynccontextmanager, suppress
from typing import Deque, Optional

import httpx
from fastapi import FastAPI, HTTPException, Request, WebSocket, WebSocketDisconnect
from fastapi.responses import HTMLResponse, JSONResponse, StreamingResponse
from pydantic import BaseModel, Field

# =========================
# Configuration
# =========================
HA_BASE_URL = os.getenv("HA_BASE_URL", "http://homeassistant:8123").rstrip("/")
APP_HOST = os.getenv("APP_HOST", "0.0.0.0")
APP_PORT = 8099
APP_BASE_URL = os.getenv('APP_BASE_URL', f"http://{os.getenv('HOME_ASSISTANT_IP', '127.0.0.1')}:{APP_PORT}").rstrip('/')
HA_TOKEN = os.getenv("HA_TOKEN", "")
LOG_LEVEL = os.getenv("LOG_LEVEL", "info")


def _load_targets() -> list[dict]:
    raw = os.getenv("TARGETS_JSON", "[]")
    try:
        parsed = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise RuntimeError(f"TARGETS_JSON is not valid JSON: {exc}") from exc

    if not isinstance(parsed, list) or not parsed:
        raise RuntimeError("TARGETS_JSON must be a non-empty JSON array")

    cleaned = []
    seen_ids = set()
    for idx, item in enumerate(parsed):
        if not isinstance(item, dict):
            raise RuntimeError(f"Target at index {idx} must be an object")
        target_id = str(item.get("id", "")).strip()
        name = str(item.get("name", "")).strip()
        entity_id = str(item.get("entity_id", "")).strip()
        kind = str(item.get("kind", "speaker")).strip() or "speaker"
        if not target_id or not name or not entity_id:
            raise RuntimeError(f"Target at index {idx} requires id, name, entity_id")
        if target_id in seen_ids:
            raise RuntimeError(f"Duplicate target id: {target_id}")
        seen_ids.add(target_id)
        cleaned.append({
            "id": target_id,
            "name": name,
            "entity_id": entity_id,
            "kind": kind,
        })
    return cleaned


TARGETS = _load_targets()
TARGETS_BY_ID = {item["id"]: item for item in TARGETS}


def build_headers() -> dict:
    return {
        "Authorization": f"Bearer {HA_TOKEN}",
        "Content-Type": "application/json",
    }


# =========================
# App state
# =========================
@asynccontextmanager
async def lifespan(app: FastAPI):
    app.state.ha_client = httpx.AsyncClient(
        timeout=httpx.Timeout(20.0, connect=5.0),
        limits=httpx.Limits(max_keepalive_connections=20, max_connections=50),
    )
    try:
        yield
    finally:
        await engine.stop()
        with suppress(Exception):
            await app.state.ha_client.aclose()


app = FastAPI(title="PA System", lifespan=lifespan)


class AudioEngine:
    def __init__(self) -> None:
        self.proc: Optional[asyncio.subprocess.Process] = None
        self.stdin_lock = asyncio.Lock()
        self.state_lock = asyncio.Lock()
        self.broadcast_task: Optional[asyncio.Task] = None
        self.stderr_task: Optional[asyncio.Task] = None
        self.listeners: set[asyncio.Queue[bytes]] = set()
        self.listeners_lock = asyncio.Lock()
        self.recent_buffer: Deque[bytes] = deque(maxlen=256)
        self.active_ws_count = 0
        self.received_audio = False

    async def start(self) -> None:
        async with self.state_lock:
            if self.proc and self.proc.returncode is None:
                return

            self.recent_buffer.clear()
            self.received_audio = False

            self.proc = await asyncio.create_subprocess_exec(
                "ffmpeg",
                "-hide_banner",
                "-loglevel",
                "warning",
                "-avioflags",
                "direct",
                "-fflags",
                "+nobuffer",
                "-flush_packets",
                "1",
                "-f",
                "s16le",
                "-ar",
                "48000",
                "-ac",
                "1",
                "-i",
                "pipe:0",
                "-vn",
                "-ac",
                "1",
                "-ar",
                "24000",
                "-b:a",
                "48k",
                "-f",
                "mp3",
                "pipe:1",
                stdin=asyncio.subprocess.PIPE,
                stdout=asyncio.subprocess.PIPE,
                stderr=asyncio.subprocess.PIPE,
            )

            self.broadcast_task = asyncio.create_task(self._stdout_pump())
            self.stderr_task = asyncio.create_task(self._stderr_pump())
            print("Audio engine started")

    async def stop(self) -> None:
        async with self.state_lock:
            proc = self.proc
            self.proc = None
            broadcast_task = self.broadcast_task
            stderr_task = self.stderr_task
            self.broadcast_task = None
            self.stderr_task = None

        if proc is not None:
            with suppress(Exception):
                if proc.stdin:
                    proc.stdin.close()
            with suppress(ProcessLookupError):
                proc.terminate()
            with suppress(asyncio.TimeoutError):
                await asyncio.wait_for(proc.wait(), timeout=3)
            if proc.returncode is None:
                with suppress(ProcessLookupError):
                    proc.kill()
                with suppress(Exception):
                    await proc.wait()

        for task in (broadcast_task, stderr_task):
            if task:
                task.cancel()
                with suppress(asyncio.CancelledError):
                    await task

        self.recent_buffer.clear()
        print("Audio engine stopped")

    async def write(self, data: bytes) -> None:
        proc = self.proc
        if not proc or proc.returncode is not None or not proc.stdin:
            raise RuntimeError("ffmpeg is not running")

        if data:
            self.received_audio = True

        async with self.stdin_lock:
            proc.stdin.write(data)
            await proc.stdin.drain()

    async def add_listener(self) -> asyncio.Queue[bytes]:
        queue: asyncio.Queue[bytes] = asyncio.Queue(maxsize=128)
        async with self.listeners_lock:
            self.listeners.add(queue)
            for chunk in self.recent_buffer:
                with suppress(asyncio.QueueFull):
                    queue.put_nowait(chunk)
        return queue

    async def remove_listener(self, queue: asyncio.Queue[bytes]) -> None:
        async with self.listeners_lock:
            self.listeners.discard(queue)

    async def _broadcast_chunk(self, chunk: bytes) -> None:
        dead: list[asyncio.Queue[bytes]] = []
        async with self.listeners_lock:
            for queue in self.listeners:
                try:
                    queue.put_nowait(chunk)
                except asyncio.QueueFull:
                    dead.append(queue)
            for queue in dead:
                self.listeners.discard(queue)

    async def _stdout_pump(self) -> None:
        proc = self.proc
        if not proc or not proc.stdout:
            return

        try:
            while True:
                chunk = await proc.stdout.read(1024)
                if not chunk:
                    break
                self.recent_buffer.append(chunk)
                await self._broadcast_chunk(chunk)
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print("FFMPEG stdout pump failed:", exc)
        finally:
            print("FFMPEG stdout pump exited")

    async def _stderr_pump(self) -> None:
        proc = self.proc
        if not proc or not proc.stderr:
            return

        try:
            while True:
                line = await proc.stderr.readline()
                if not line:
                    break
                print("FFMPEG:", line.decode(errors="ignore").rstrip())
        except asyncio.CancelledError:
            raise
        except Exception as exc:
            print("FFMPEG stderr pump failed:", exc)
        finally:
            print("FFMPEG stderr pump exited")

    def is_running(self) -> bool:
        return bool(self.proc and self.proc.returncode is None)


engine = AudioEngine()

session_lock = asyncio.Lock()
active_session = {
    "running": False,
    "leader": None,
    "selected_ids": [],
    "selected_entity_ids": [],
    "status": "Idle",
    "ready": False,
    "started_at": None,
    "recorder_client_id": None,
    "recorder_claimed_at": None,
    "volumes": {},
}
recorder_disconnect_task: Optional[asyncio.Task] = None


# =========================
# Models
# =========================
class StartRequest(BaseModel):
    target_ids: list[str] = Field(default_factory=list)
    client_id: str = Field(min_length=1)
    volumes: dict[str, int] = Field(default_factory=dict)


class VolumeUpdateRequest(BaseModel):
    client_id: str = Field(min_length=1)
    volumes: dict[str, int] = Field(default_factory=dict)
    target_ids: list[str] = Field(default_factory=list)


# =========================
# Helpers
# =========================
def ensure_ha_token() -> None:
    if not HA_TOKEN:
        raise RuntimeError("Set HA_TOKEN in the environment to a Home Assistant long-lived access token")


async def set_session_status(status: str, ready: bool | None = None) -> None:
    active_session["status"] = status
    if ready is not None:
        active_session["ready"] = ready


def clamp_volume(value: int) -> int:
    return max(0, min(100, int(value)))


def validate_client_owns_session(client_id: str) -> None:
    owner = active_session.get("recorder_client_id")
    if not owner:
        raise HTTPException(status_code=409, detail="No active recorder session")
    if owner != client_id:
        raise HTTPException(status_code=409, detail="Another device is currently recording")


def get_ha_client() -> httpx.AsyncClient:
    client = getattr(app.state, "ha_client", None)
    if client is None:
        raise RuntimeError("Home Assistant HTTP client is not initialized")
    return client


async def set_target_volume(entity_id: str, volume_percent: int) -> None:
    await ha_post(
        "media_player/volume_set",
        {
            "entity_id": entity_id,
            "volume_level": clamp_volume(volume_percent) / 100.0,
        },
    )


async def apply_volumes(targets: list[dict], requested_volumes: dict[str, int]) -> dict[str, int]:
    applied: dict[str, int] = {}
    for target in targets:
        volume = clamp_volume(requested_volumes.get(target["id"], 50))
        await set_target_volume(target["entity_id"], volume)
        applied[target["id"]] = volume
    active_session["volumes"] = applied
    return applied


async def ha_get(path: str):
    ensure_ha_token()
    url = f"{HA_BASE_URL}{path}"
    client = get_ha_client()
    resp = await client.get(url, headers=build_headers())
    print("HA GET", url, "->", resp.status_code)
    resp.raise_for_status()
    return resp.json()


async def ha_post(service: str, data: dict):
    ensure_ha_token()
    url = f"{HA_BASE_URL}/api/services/{service}"
    client = get_ha_client()
    resp = await client.post(url, headers=build_headers(), json=data)
    print("HA POST", url, data, "->", resp.status_code, resp.text[:300])
    resp.raise_for_status()
    return resp.json()


async def get_state(entity_id: str) -> dict:
    return await ha_get(f"/api/states/{entity_id}")


def get_lan_ip() -> str:
    if APP_BASE_URL.startswith(("http://", "https://")):
        try:
            host = APP_BASE_URL.split("://", 1)[1].split("/", 1)[0].split(":", 1)[0]
            if host not in {"0.0.0.0", "localhost", "127.0.0.1"}:
                return host
        except Exception:
            pass

    sock = socket.socket(socket.AF_INET, socket.SOCK_DGRAM)
    try:
        sock.connect(("8.8.8.8", 80))
        return sock.getsockname()[0]
    finally:
        sock.close()


def stream_url() -> str:
    return f"{APP_BASE_URL}/live.mp3"


async def fetch_target_state(target: dict) -> dict:
    item = dict(target)
    try:
        state_obj = await get_state(target["entity_id"])
        item["ha_state"] = state_obj.get("state", "unknown")
        attrs = state_obj.get("attributes", {})
        item["friendly_name"] = attrs.get("friendly_name", target["name"])
        item["available"] = state_obj.get("state") != "unavailable"
        item["volume"] = int(round(float(attrs.get("volume_level", 0.5)) * 100))
    except Exception as exc:
        print("Target lookup failed for", target["entity_id"], exc)
        item["ha_state"] = "unknown"
        item["friendly_name"] = target["name"]
        item["available"] = False
        item["volume"] = 50
    return item


async def resolve_targets() -> list[dict]:
    return await asyncio.gather(*(fetch_target_state(target) for target in TARGETS))


def validate_target_ids(target_ids: list[str]) -> list[dict]:
    seen = set()
    resolved = []
    for target_id in target_ids:
        if target_id in seen:
            continue
        seen.add(target_id)
        target = TARGETS_BY_ID.get(target_id)
        if not target:
            raise HTTPException(status_code=400, detail=f"Unknown target id: {target_id}")
        resolved.append(target)

    if not resolved:
        raise HTTPException(status_code=400, detail="Select at least one target")

    kinds = {target.get("kind", "speaker") for target in resolved}
    if "camera" in kinds and len(resolved) > 1:
        raise HTTPException(status_code=400, detail="Cameras must be selected on their own")
    if len(kinds) > 1:
        raise HTTPException(status_code=400, detail="Do not mix cameras with speakers")

    return resolved


async def join_targets_if_needed(leader: str, members: list[str]) -> None:
    if not members:
        return
    await ha_post(
        "media_player/join",
        {
            "entity_id": leader,
            "group_members": members,
        },
    )


async def play_stream_on_targets(targets: list[dict]) -> None:
    if not targets:
        return

    kind = targets[0].get("kind", "speaker")
    if kind == "camera":
        for target in targets:
            await ha_post(
                "media_player/play_media",
                {
                    "entity_id": target["entity_id"],
                    "media_content_id": stream_url(),
                    "media_content_type": "music",
                    "extra": {
                        "title": "PA",
                        "stream_type": "LIVE",
                    },
                },
            )
        return

    leader = targets[0]["entity_id"]
    await play_stream_on_leader(leader)


async def play_stream_on_leader(leader: str) -> None:
    await ha_post(
        "media_player/play_media",
        {
            "entity_id": leader,
            "media_content_id": stream_url(),
            "media_content_type": "music",
            "extra": {
                "title": "PA",
                "stream_type": "LIVE",
            },
        },
    )


async def stop_targets(entity_ids: list[str]) -> None:
    if not entity_ids:
        return

    leader = entity_ids[0]
    members = entity_ids[1:]

    with suppress(Exception):
        await ha_post("media_player/media_stop", {"entity_id": leader})

    for entity_id in members:
        with suppress(Exception):
            await ha_post("media_player/unjoin", {"entity_id": entity_id})

    with suppress(Exception):
        await ha_post("media_player/unjoin", {"entity_id": leader})


async def wait_until_targets_ready(targets: list[dict], timeout_seconds: float = 15.0) -> tuple[bool, dict[str, str]]:
    if not targets:
        return False, {}

    pending = {target["entity_id"] for target in targets}
    states = {target["entity_id"]: "unknown" for target in targets}
    deadline = time.monotonic() + timeout_seconds

    while time.monotonic() < deadline:
        for entity_id in list(pending):
            try:
                state_obj = await get_state(entity_id)
                state = state_obj.get("state", "unknown")
                states[entity_id] = state
                print("Target state:", entity_id, state)
                if state in {"buffering", "playing"}:
                    pending.discard(entity_id)
            except Exception as exc:
                print("State poll failed:", entity_id, exc)
        if not pending:
            return True, states
        await asyncio.sleep(0.5)

    return False, states


async def stop_if_recorder_does_not_return(client_id: str, delay: float = 5.0) -> None:
    await asyncio.sleep(delay)
    async with session_lock:
        if (
            active_session["running"]
            and active_session.get("recorder_client_id") == client_id
            and engine.active_ws_count == 0
        ):
            print("Recorder did not reconnect in time; stopping active session")
            entity_ids = list(active_session["selected_entity_ids"])
            with suppress(Exception):
                await stop_targets(entity_ids)
            await reset_session(stop_audio_engine=True)


async def reset_session(stop_audio_engine: bool) -> None:
    global recorder_disconnect_task
    if recorder_disconnect_task:
        recorder_disconnect_task.cancel()
        with suppress(asyncio.CancelledError):
            await recorder_disconnect_task
        recorder_disconnect_task = None

    active_session.update(
        {
            "running": False,
            "leader": None,
            "selected_ids": [],
            "selected_entity_ids": [],
            "started_at": None,
            "status": "Idle",
            "ready": False,
            "recorder_client_id": None,
            "recorder_claimed_at": None,
            "volumes": {},
        }
    )
    if stop_audio_engine:
        await engine.stop()


# =========================
# Routes
# =========================
@app.get("/", response_class=HTMLResponse)
async def index():
    return HTML_PAGE


@app.get("/api/targets")
async def api_targets():
    return {"targets": await resolve_targets()}


@app.get("/api/status")
async def api_status():
    return {
        **active_session,
        "active_ws_count": engine.active_ws_count,
        "ffmpeg_running": engine.is_running(),
        "stream_url": stream_url(),
    }


@app.post("/api/volumes")
async def api_set_volumes(payload: VolumeUpdateRequest):
    requested_ids = payload.target_ids or active_session["selected_ids"]
    if not requested_ids:
        raise HTTPException(status_code=400, detail="No target ids provided")

    targets = []
    for target_id in requested_ids:
        target = TARGETS_BY_ID.get(target_id)
        if target:
            targets.append(target)

    if not targets:
        raise HTTPException(status_code=400, detail="No valid targets provided")

    if active_session["running"]:
        owner = active_session.get("recorder_client_id")
        if owner and owner != payload.client_id:
            raise HTTPException(status_code=409, detail="Another device is currently recording")

    applied = await apply_volumes(targets, payload.volumes)
    return {"ok": True, "volumes": applied}


@app.post("/api/start")
async def api_start(payload: StartRequest):
    targets = validate_target_ids(payload.target_ids)
    entity_ids = [t["entity_id"] for t in targets]
    leader = entity_ids[0]
    members = entity_ids[1:]
    target_kind = targets[0].get("kind", "speaker")

    async with session_lock:
        if active_session["running"]:
            stale_entity_ids = list(active_session["selected_entity_ids"])
            stale = (engine.active_ws_count == 0) or (not engine.is_running())
            if stale:
                print("Recovering stale session before starting a new one")
                await stop_targets(stale_entity_ids)
                await reset_session(stop_audio_engine=True)
            else:
                raise HTTPException(status_code=409, detail="Another device is currently recording")

        await engine.start()
        active_session["running"] = True
        active_session["leader"] = leader
        active_session["selected_ids"] = [t["id"] for t in targets]
        active_session["selected_entity_ids"] = entity_ids
        active_session["started_at"] = time.time()
        active_session["recorder_client_id"] = payload.client_id
        active_session["recorder_claimed_at"] = time.time()
        await set_session_status("Grouping speakers…", ready=False)

        try:
            if target_kind == "speaker":
                await join_targets_if_needed(leader, members)

            await apply_volumes(targets, payload.volumes)
            await set_session_status("Starting playback…", ready=False)
            await play_stream_on_targets(targets)
            ok, states = await wait_until_targets_ready(targets)

            if ok:
                await set_session_status("You can speak now", ready=True)
                return {
                    "ok": True,
                    "leader": leader,
                    "state": states.get(leader, "unknown"),
                    "states": states,
                    "message": "You can speak now",
                    "stream_url": stream_url(),
                    "volumes": active_session["volumes"],
                }

            await stop_targets(entity_ids)
            await reset_session(stop_audio_engine=True)
            return JSONResponse(
                status_code=504,
                content={
                    "ok": False,
                    "leader": leader,
                    "state": states.get(leader, "unknown"),
                    "states": states,
                    "message": "Playback did not become ready in time",
                    "stream_url": stream_url(),
                },
            )
        except httpx.HTTPStatusError as exc:
            detail = exc.response.text[:500]
            await set_session_status(f"Home Assistant error: {detail}", ready=False)
            await stop_targets(entity_ids)
            await reset_session(stop_audio_engine=True)
            raise HTTPException(status_code=502, detail=f"Home Assistant error: {detail}")
        except Exception as exc:
            await set_session_status(f"Start failed: {exc}", ready=False)
            await stop_targets(entity_ids)
            await reset_session(stop_audio_engine=True)
            raise HTTPException(status_code=500, detail=str(exc))


@app.post("/api/stop")
async def api_stop(payload: VolumeUpdateRequest | None = None):
    client_id = payload.client_id if payload is not None else None
    async with session_lock:
        if active_session["running"] and client_id is not None:
            validate_client_owns_session(client_id)
        entity_ids = list(active_session["selected_entity_ids"])
        await set_session_status("Stopping…", ready=False)
        await stop_targets(entity_ids)
        await reset_session(stop_audio_engine=True)
    return {"ok": True}


@app.websocket("/ws/audio")
async def ws_audio(ws: WebSocket):
    global recorder_disconnect_task

    await ws.accept()
    client_id = ws.query_params.get("client_id", "")
    if not client_id:
        await ws.close(code=1008, reason="Missing client_id")
        return

    if active_session.get("recorder_client_id") == client_id and recorder_disconnect_task:
        recorder_disconnect_task.cancel()
        with suppress(asyncio.CancelledError):
            await recorder_disconnect_task
        recorder_disconnect_task = None

    engine.active_ws_count += 1
    await engine.start()

    try:
        while True:
            data = await ws.receive_bytes()
            if not active_session["running"] or active_session.get("recorder_client_id") != client_id:
                continue
            await engine.write(data)
    except WebSocketDisconnect:
        pass
    except RuntimeError as exc:
        print("Audio engine write failed:", exc)
        with suppress(Exception):
            await ws.close(code=1011)
    except Exception as exc:
        print("WebSocket audio error:", exc)
        with suppress(Exception):
            await ws.close(code=1011)
    finally:
        engine.active_ws_count = max(0, engine.active_ws_count - 1)

        if active_session.get("recorder_client_id") == client_id and active_session["running"]:
            print("Recorder websocket disconnected; session left running until manual stop")


@app.get("/live.mp3")
async def live_mp3(request: Request):
    await engine.start()
    queue = await engine.add_listener()

    async def streamer():
        try:
            while True:
                if await request.is_disconnected():
                    break
                chunk = await queue.get()
                yield chunk
        finally:
            await engine.remove_listener(queue)

    return StreamingResponse(
        streamer(),
        media_type="audio/mpeg",
        headers={
            "Cache-Control": "no-cache, no-store, must-revalidate",
            "Pragma": "no-cache",
            "Expires": "0",
            "Connection": "keep-alive",
        },
    )


@app.get("/health")
async def health():
    return {
        "ok": True,
        "ha_base_url": HA_BASE_URL,
        "app_base_url": APP_BASE_URL,
        "stream_url": stream_url(),
        "lan_ip": get_lan_ip(),
        "ffmpeg_running": engine.is_running(),
        "active_ws_count": engine.active_ws_count,
        "session": active_session,
        "targets_count": len(TARGETS),
        "log_level": LOG_LEVEL,
    }


HTML_PAGE = r"""
<!doctype html>
<html lang="en">
<head>
  <meta charset="utf-8" />
  <meta name="viewport" content="width=device-width, initial-scale=1" />
  <title>PA System</title>
  <style>
    :root {
      color-scheme: light dark;
      --bg: #0f172a;
      --panel: #111827;
      --text: #e5e7eb;
      --muted: #9ca3af;
      --accent: #38bdf8;
      --ok: #22c55e;
      --danger: #ef4444;
      --border: rgba(255,255,255,0.12);
      --panel-padding: clamp(14px, 3vw, 24px);
    }
    * { box-sizing: border-box; }
    body {
      margin: 0;
      font-family: Inter, system-ui, sans-serif;
      background: linear-gradient(180deg, var(--bg), #020617);
      color: var(--text);
      display: flex;
      justify-content: center;
      align-items: center;
      min-height: 100vh;
    }
    .wrap {
      width: 100%;
      max-width: 720px;
      padding: 16px;
    }
    .panel {
      background: rgba(17,24,39,0.95);
      border: 1px solid var(--border);
      border-radius: 18px;
      padding: var(--panel-padding);
      box-shadow: 0 12px 40px rgba(0,0,0,0.3);
    }
    h1 {
      margin: 0 0 8px;
      font-size: clamp(1.4rem, 4vw, 2rem);
      line-height: 1.1;
    }
    p { color: var(--muted); }
    .targets {
      display: grid;
      gap: 12px;
      margin: 20px 0;
    }
    .target {
      border: 1px solid var(--border);
      border-radius: 16px;
      padding: 14px;
      background: rgba(255,255,255,0.03);
      display: grid;
      gap: 12px;
    }
    .targetTop {
      display: flex;
      align-items: center;
      justify-content: space-between;
      gap: 12px;
    }
    .target label {
      display: flex;
      align-items: flex-start;
      gap: 12px;
      cursor: pointer;
      flex: 1;
      min-width: 0;
    }
    .meta {
      display: flex;
      flex-direction: column;
      gap: 4px;
      min-width: 0;
    }
    .name {
      font-weight: 700;
      overflow-wrap: anywhere;
    }
    .entity {
      color: var(--muted);
      font-size: 0.88rem;
      overflow-wrap: anywhere;
    }
    .badge {
      border-radius: 999px;
      padding: 6px 10px;
      font-size: 0.82rem;
      border: 1px solid var(--border);
      white-space: nowrap;
      align-self: flex-start;
    }
    .ok { color: var(--ok); }
    .bad { color: var(--danger); }
    .sliderRow {
      display: grid;
      grid-template-columns: 1fr auto;
      gap: 10px;
      align-items: center;
    }
    .sliderWrap {
      display: grid;
      gap: 6px;
    }
    .sliderLabel {
      color: var(--muted);
      font-size: 0.88rem;
    }
    input[type="range"] {
      width: 100%;
      min-height: 40px;
    }
    .volumeValue {
      min-width: 52px;
      text-align: right;
      font-weight: 700;
    }
    .row {
      display: grid;
      grid-template-columns: repeat(3, minmax(0, 1fr));
      gap: 12px;
      margin-top: 18px;
    }
    button {
      border: 0;
      border-radius: 14px;
      padding: 14px 16px;
      font-size: 1rem;
      font-weight: 700;
      cursor: pointer;
      min-height: 48px;
    }
    button.primary { background: var(--accent); color: #082f49; }
    button.secondary { background: #334155; color: var(--text); }
    button.danger { background: var(--danger); color: white; }
    button:disabled { opacity: 0.45; cursor: not-allowed; }
    .status {
      margin-top: 18px;
      border-radius: 14px;
      padding: 14px 16px;
      border: 1px solid var(--border);
      background: rgba(255,255,255,0.03);
    }
    .status strong {
      display: block;
      margin-bottom: 6px;
      font-size: 1rem;
    }
    .footnote {
      margin-top: 18px;
      color: var(--muted);
      font-size: 0.92rem;
      line-height: 1.45;
    }
    .sessionInfo {
      margin-top: 10px;
      color: var(--muted);
      font-size: 0.9rem;
      line-height: 1.4;
    }
    @media (max-width: 700px) {
      body {
        align-items: flex-start;
      }
      .wrap { padding: 10px; }
      .row { grid-template-columns: 1fr; }
      .targetTop {
        flex-direction: column;
        align-items: stretch;
      }
      .badge { align-self: flex-start; }
      .sliderRow { grid-template-columns: 1fr; }
      .volumeValue { text-align: left; }
    }
  </style>
</head>
<body>
  <div class="wrap">
    <div class="panel">
      <h1>PA System</h1>
      <p>Select one or more Speaker targets, set their volumes, press Record, wait for the ready message, then speak.</p>

      <div id="targets" class="targets"></div>

      <div class="row">
        <button id="refreshBtn" class="secondary">Refresh targets</button>
        <button id="recordBtn" class="primary" disabled>Record</button>
        <button id="stopBtn" class="danger" disabled>Stop</button>
      </div>

      <div class="status">
        <strong id="statusTitle">Idle</strong>
        <div id="statusBody">Nothing is playing.</div>
        <div id="sessionInfo" class="sessionInfo"></div>
      </div>

      <div class="footnote">
        Only one device can record at a time. Other devices can still open this page and adjust selections, but they cannot start or stop another device's live session. Camera speakers must be selected on their own and cannot be mixed with WiiM speakers.
      </div>
    </div>
  </div>

  <script>
    const clientId = (() => {
      const existing = localStorage.getItem('wiim_live_mic_client_id');
      if (existing) return existing;
      const created = (crypto && crypto.randomUUID)
        ? crypto.randomUUID()
        : `client-${Date.now()}-${Math.random().toString(16).slice(2)}`;
      localStorage.setItem('wiim_live_mic_client_id', created);
      return created;
    })();

    const volumeState = (() => {
      try {
        return JSON.parse(localStorage.getItem('wiim_live_mic_volumes') || '{}');
      } catch {
        return {};
      }
    })();

    const volumeDirtyUntil = {};
    const LOCAL_VOLUME_HOLD_MS = 2500;

    function apiUrl(path) {
      return new URL(`./${path.replace(/^\/+/, '')}`, window.location.href).toString();
    }

    function wsUrl(path) {
      const url = new URL(`./${path.replace(/^\/+/, '')}`, window.location.href);
      url.protocol = url.protocol === 'https:' ? 'wss:' : 'ws:';
      return url.toString();
    }

    function saveVolumeState() {
      localStorage.setItem('wiim_live_mic_volumes', JSON.stringify(volumeState));
    }

    function setLocalVolume(targetId, value, holdMs = LOCAL_VOLUME_HOLD_MS) {
      volumeState[targetId] = Number(value);
      volumeDirtyUntil[targetId] = Date.now() + holdMs;
      saveVolumeState();
    }

    function isLocalVolumeFresh(targetId) {
      return (volumeDirtyUntil[targetId] || 0) > Date.now();
    }

    let mediaStream = null;
    let mediaRecorder = null;
    let audioSocket = null;
    let appRunning = false;
    let currentOwner = null;
    let selectedTargetIdsState = [];
    let targetMetaState = {};
    let loadTargetsRequestId = 0;

    const targetsEl = document.getElementById('targets');
    const recordBtn = document.getElementById('recordBtn');
    const stopBtn = document.getElementById('stopBtn');
    const refreshBtn = document.getElementById('refreshBtn');
    const statusTitle = document.getElementById('statusTitle');
    const statusBody = document.getElementById('statusBody');
    const sessionInfo = document.getElementById('sessionInfo');

    function setStatus(title, body, extra = '') {
      statusTitle.textContent = title;
      statusBody.textContent = body;
      sessionInfo.textContent = extra;
    }

    function setTargetMeta(targets) {
      targetMetaState = Object.fromEntries((targets || []).map(t => [t.id, {
        available: Boolean(t.available),
        kind: t.kind || 'speaker'
      }]));
    }

    function getSelectedTargetIds() {
      return [...selectedTargetIdsState];
    }

    function setSelectedTargetIds(selectedIds) {
      selectedTargetIdsState = normalizeSelectedIds(selectedIds);
      return getSelectedTargetIds();
    }

    function allTargetInputs() {
      return [...document.querySelectorAll('input[name="target"]')];
    }

    function targetTypeForId(targetId) {
      return targetMetaState[targetId]?.kind || 'speaker';
    }

    function selectedTargetKind(selectedIds = getSelectedTargetIds()) {
      if (!selectedIds.length) return null;
      return targetTypeForId(selectedIds[0]);
    }

    function normalizeSelectedIds(selectedIds) {
      const unique = [...new Set(selectedIds)].filter(id => {
        const meta = targetMetaState[id];
        return meta ? meta.available : false;
      });
      if (!unique.length) return [];

      const firstKind = targetTypeForId(unique[0]);
      if (firstKind === 'camera') {
        return [unique[0]];
      }

      return unique.filter(id => targetTypeForId(id) !== 'camera');
    }

    function currentVolumes() {
      const volumes = {};
      document.querySelectorAll('input[name="volume"]').forEach(el => {
        volumes[el.dataset.targetId] = Number(el.value);
      });
      return volumes;
    }

    function desiredVolumes() {
      return { ...volumeState, ...currentVolumes() };
    }

    function renderVolumeValue(targetId, value) {
      const out = document.getElementById(`volume-value-${targetId}`);
      if (out) out.textContent = `${value}%`;
    }

    function updateButtons() {
      const normalizedSelectedIds = setSelectedTargetIds(getSelectedTargetIds());

      allTargetInputs().forEach(input => {
        input.checked = normalizedSelectedIds.includes(input.value);
      });

      const hasSelection = normalizedSelectedIds.length > 0;
      const anotherDeviceRunning = currentOwner && currentOwner !== clientId;
      const kind = selectedTargetKind(normalizedSelectedIds);
      const cameraMode = kind === 'camera';

      allTargetInputs().forEach(input => {
        const inputKind = input.dataset.kind || 'speaker';
        const baseDisabled = input.dataset.available !== 'true';
        let disabled = baseDisabled;

        if (!disabled && kind) {
          if (cameraMode) {
            disabled = inputKind !== 'camera' || (!input.checked && normalizedSelectedIds.length >= 1);
          } else {
            disabled = inputKind === 'camera';
          }
        }

        input.disabled = disabled;
      });

      recordBtn.disabled = appRunning || !hasSelection || anotherDeviceRunning;
      stopBtn.disabled = !appRunning;
    }

    async function pushVolumes(targetIds = []) {
      try {
        const res = await fetch(apiUrl('api/volumes'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            client_id: clientId,
            target_ids: targetIds,
            volumes: desiredVolumes()
          })
        });

        if (!res.ok) {
          const data = await res.json().catch(() => ({}));
          throw new Error(data.detail || 'Volume update failed');
        }

        const data = await res.json();
        if (data.volumes) {
          for (const [targetId, value] of Object.entries(data.volumes)) {
            setLocalVolume(targetId, value, 800);
            const slider = document.querySelector(`input[name="volume"][data-target-id="${targetId}"]`);
            if (slider && !slider.matches(':active')) {
              slider.value = String(value);
            }
            renderVolumeValue(targetId, value);
          }
        }
      } catch (err) {
        console.error('Volume update failed', err);
        setStatus('Volume update failed', String(err.message || err));
      }
    }

    function renderTargets(targets, { selectedIds = [] } = {}) {
      const normalizedSelectedIds = normalizeSelectedIds(selectedIds);
      selectedTargetIdsState = [...normalizedSelectedIds];
      targetsEl.innerHTML = '';

      for (const t of targets) {
        const item = document.createElement('div');
        item.className = 'target';
        const stateText = t.available ? (t.ha_state || 'unknown') : 'unavailable';
        const stateClass = t.available ? 'ok' : 'bad';
        const targetKind = t.kind || 'speaker';
        const kindLabel = targetKind === 'camera' ? 'Camera speaker' : 'Speaker';
        const safeVolume = (isLocalVolumeFresh(t.id) && Object.prototype.hasOwnProperty.call(volumeState, t.id))
          ? Number(volumeState[t.id])
          : (typeof t.volume === 'number' ? t.volume : 50);
        const isChecked = normalizedSelectedIds.includes(t.id) && t.available;

        item.innerHTML = `
          <div class="targetTop">
            <label>
              <input type="checkbox" name="target" value="${t.id}" data-kind="${targetKind}" data-available="${t.available ? 'true' : 'false'}" ${isChecked ? 'checked' : ''} ${t.available ? '' : 'disabled'} />
              <div class="meta">
                <div class="name">${t.friendly_name || t.name}</div>
                <div class="entity">${t.entity_id}</div>
                <div class="entity">${kindLabel}</div>
              </div>
            </label>
            <div class="badge ${stateClass}">${stateText}</div>
          </div>
          <div class="sliderRow">
            <div class="sliderWrap">
              <div class="sliderLabel">Volume</div>
              <input type="range" name="volume" min="0" max="100" step="1" value="${safeVolume}" data-target-id="${t.id}" ${t.available ? '' : 'disabled'} />
            </div>
            <div class="volumeValue" id="volume-value-${t.id}">${safeVolume}%</div>
          </div>
        `;
        targetsEl.appendChild(item);
      }

      document.querySelectorAll('input[name="target"]').forEach(el => {
        el.addEventListener('change', () => {
          const current = new Set(getSelectedTargetIds());
          if (el.checked) {
            current.add(el.value);
          } else {
            current.delete(el.value);
          }
          setSelectedTargetIds([...current]);
          updateButtons();
        });
      });

      document.querySelectorAll('input[name="volume"]').forEach(el => {
        el.addEventListener('input', () => {
          setLocalVolume(el.dataset.targetId, el.value);
          renderVolumeValue(el.dataset.targetId, el.value);
        });
        el.addEventListener('change', () => pushVolumes([el.dataset.targetId]));
      });

      updateButtons();
    }

    async function loadTargets({ silent = false } = {}) {
      const requestId = ++loadTargetsRequestId;

      if (!silent) {
        setStatus('Loading targets…', 'Checking Home Assistant media players.');
      }

      const previousTitle = statusTitle.textContent;
      const previousBody = statusBody.textContent;
      const previousExtra = sessionInfo.textContent;

      const [targetsRes, statusRes] = await Promise.all([
        fetch(apiUrl('api/targets')),
        fetch(apiUrl('api/status'))
      ]);

      if (requestId !== loadTargetsRequestId) {
        return;
      }

      const targetsData = await targetsRes.json();
      const statusData = await statusRes.json();
      const targets = targetsData.targets || [];

      setTargetMeta(targets);

      currentOwner = statusData.recorder_client_id || null;
      appRunning = Boolean(statusData.running && currentOwner === clientId);

      for (const t of targets) {
        if (!isLocalVolumeFresh(t.id)) {
          volumeState[t.id] = typeof t.volume === 'number' ? t.volume : 50;
        }
      }
      saveVolumeState();

      renderTargets(targets, { selectedIds: getSelectedTargetIds() });

      if (statusData.running) {
        if (currentOwner === clientId) {
          setStatus(
            statusData.status || 'Running',
            'Your device is currently recording.',
            `Stream: ${statusData.stream_url || ''}`
          );
        } else {
          setStatus(
            statusData.status || 'Busy',
            'Another device is currently recording.',
            'You can watch the status here, but only the active recorder can stop or change the live session.'
          );
        }
      } else if (!silent) {
        setStatus('Idle', 'Select one or more speakers.');
      } else {
        setStatus(
          previousTitle || 'Idle',
          previousBody || 'Select one or more speakers.',
          previousExtra || ''
        );
      }

      updateButtons();
    }

    async function openMicAndSocket() {
      mediaStream = await navigator.mediaDevices.getUserMedia({
        audio: {
          channelCount: 1,
          echoCancellation: false,
          noiseSuppression: false,
          autoGainControl: false
        },
        video: false
      });

      const socketUrl = new URL(wsUrl('ws/audio'));
      socketUrl.searchParams.set('client_id', clientId);
      audioSocket = new WebSocket(socketUrl.toString());
      audioSocket.binaryType = 'arraybuffer';

      await new Promise((resolve, reject) => {
        let settled = false;
        audioSocket.onopen = () => {
          settled = true;
          resolve();
        };
        audioSocket.onerror = () => {
          if (!settled) reject(new Error('WebSocket connection failed'));
        };
        audioSocket.onclose = () => {
          console.warn('Audio websocket closed');
        };
      });

      const AudioContextCtor = window.AudioContext || window.webkitAudioContext;
      if (!AudioContextCtor) {
        throw new Error('This browser does not support AudioContext');
      }

      const audioContext = new AudioContextCtor({ sampleRate: 48000 });
      const source = audioContext.createMediaStreamSource(mediaStream);
      const processor = audioContext.createScriptProcessor(2048, 1, 1);
      const sink = audioContext.createGain();
      sink.gain.value = 0;

      processor.onaudioprocess = (event) => {
        if (!audioSocket || audioSocket.readyState !== WebSocket.OPEN) return;
        const input = event.inputBuffer.getChannelData(0);
        const pcm = new Int16Array(input.length);
        for (let i = 0; i < input.length; i += 1) {
          const s = Math.max(-1, Math.min(1, input[i]));
          pcm[i] = s < 0 ? s * 0x8000 : s * 0x7fff;
        }
        audioSocket.send(pcm.buffer);
      };

      source.connect(processor);
      processor.connect(sink);
      sink.connect(audioContext.destination);

      mediaRecorder = {
        state: 'recording',
        stop() {
          try { processor.disconnect(); } catch {}
          try { source.disconnect(); } catch {}
          try { sink.disconnect(); } catch {}
          try { audioContext.close(); } catch {}
          this.state = 'inactive';
        }
      };
    }

    async function stopLocalAudio() {
      if (mediaRecorder && mediaRecorder.state !== 'inactive') {
        mediaRecorder.stop();
      }
      mediaRecorder = null;

      if (mediaStream) {
        mediaStream.getTracks().forEach(track => track.stop());
      }
      mediaStream = null;

      if (audioSocket && audioSocket.readyState === WebSocket.OPEN) {
        audioSocket.close();
      }
      audioSocket = null;
    }

    async function startSession() {
      const targetIds = getSelectedTargetIds();
      if (!targetIds.length) return;

      try {
        appRunning = true;
        currentOwner = clientId;
        updateButtons();

        setStatus('Starting speakers…', 'Grouping the selected targets and waiting for playback to become ready.');
        const res = await fetch(apiUrl('api/start'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({
            target_ids: targetIds,
            client_id: clientId,
            volumes: currentVolumes()
          })
        });

        const data = await res.json();
        if (!res.ok) {
          throw new Error(data.detail || data.message || 'Start failed');
        }

        setStatus('Preparing microphone…', 'Speakers are ready. Opening your microphone now.', `Stream: ${data.stream_url}`);
        await openMicAndSocket();
        setStatus('You can speak now', 'The selected speakers are ready.', `Stream: ${data.stream_url}`);
      } catch (err) {
        console.error(err);
        setStatus('Start failed', String(err.message || err));
        await stopLocalAudio();
        appRunning = false;
        currentOwner = null;
        updateButtons();
      }
    }

    async function stopSession() {
      try {
        setStatus('Stopping…', 'Stopping playback and ungrouping speakers.');
        await fetch(apiUrl('api/stop'), {
          method: 'POST',
          headers: { 'Content-Type': 'application/json' },
          body: JSON.stringify({ client_id: clientId, volumes: {} })
        });
      } catch (err) {
        console.error(err);
      } finally {
        await stopLocalAudio();
        appRunning = false;
        currentOwner = null;
        updateButtons();
        setStatus('Idle', 'Nothing is playing.');
      }
    }

    refreshBtn.addEventListener('click', () => {
      loadTargets().catch(err => {
        console.error(err);
        setStatus('Error', 'Could not load Home Assistant targets.');
      });
    });

    recordBtn.addEventListener('click', startSession);
    stopBtn.addEventListener('click', stopSession);

    setSelectedTargetIds([]);
    loadTargets().catch(err => {
      console.error(err);
      setStatus('Error', 'Could not load Home Assistant targets.');
    });

    setInterval(() => {
      loadTargets({ silent: true }).catch(err => console.error(err));
    }, 5000);
  </script>
</body>
</html>
"""

if __name__ == "__main__":
    import uvicorn

    if sys.platform == "win32":
        asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())

    uvicorn.run(
        "pa_system_app:app",
        host=APP_HOST,
        port=APP_PORT,
        reload=False,
        log_level=LOG_LEVEL,
    )
