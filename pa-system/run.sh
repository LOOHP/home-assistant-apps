#!/usr/bin/env bash
set -euo pipefail

OPTIONS="/data/options.json"

home_assistant_ip="$(jq -r '.home_assistant_ip' "$OPTIONS")"
ha_token="$(jq -r '.ha_token' "$OPTIONS")"
log_level="$(jq -r '.log_level' "$OPTIONS")"
targets_json="$(jq -r '.targets_json' "$OPTIONS")"

if [[ -z "$home_assistant_ip" || "$home_assistant_ip" == "null" ]]; then
  echo "[ERROR] home_assistant_ip must be configured in the add-on options."
  exit 1
fi

if [[ -z "$ha_token" || "$ha_token" == "null" ]]; then
  echo "[ERROR] ha_token must be configured in the add-on options."
  exit 1
fi

export HA_BASE_URL="http://homeassistant:8123"
export APP_HOST="0.0.0.0"
export APP_BASE_URL="http://${home_assistant_ip}:8099"
export HA_TOKEN="$ha_token"
export LOG_LEVEL="$log_level"
export TARGETS_JSON="$targets_json"
export HOME_ASSISTANT_IP="$home_assistant_ip"

python3 - <<'PY2'
import json
import os

home_assistant_ip = os.environ.get("HOME_ASSISTANT_IP", "").strip()
if not home_assistant_ip:
    raise SystemExit("[ERROR] home_assistant_ip must not be empty")

targets = os.environ.get("TARGETS_JSON", "[]")
try:
    parsed = json.loads(targets)
except Exception as exc:
    raise SystemExit(f"[ERROR] targets_json is not valid JSON: {exc}")

if not isinstance(parsed, list) or not parsed:
    raise SystemExit("[ERROR] targets_json must be a non-empty JSON array")

for idx, item in enumerate(parsed):
    if not isinstance(item, dict):
        raise SystemExit(f"[ERROR] target at index {idx} must be an object")
    for key in ("id", "name", "entity_id"):
        if not item.get(key):
            raise SystemExit(f"[ERROR] target at index {idx} is missing '{key}'")
    item.setdefault("kind", "speaker")

print(f"[INFO] Home Assistant LAN IP: {home_assistant_ip}")
print(f"[INFO] Public stream URL base: http://{home_assistant_ip}:8099")
print(f"[INFO] Loaded {len(parsed)} targets")
PY2

echo "[INFO] Home Assistant internal URL: ${HA_BASE_URL}"
echo "[INFO] Starting PA System with HTTP on 0.0.0.0:8099"

exec uvicorn pa_system_app:app \
  --host 0.0.0.0 \
  --port 8099 \
  --proxy-headers \
  --forwarded-allow-ips='*' \
  --log-level "$log_level"
