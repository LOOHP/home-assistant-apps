#!/usr/bin/env bash
set -euo pipefail

OPTIONS="/data/options.json"

interval_minutes="$(jq -r '.interval_minutes' "$OPTIONS")"
output_path="$(jq -r '.output_path' "$OPTIONS")"
email="$(jq -r '.timetree_email' "$OPTIONS")"
password="$(jq -r '.timetree_password' "$OPTIONS")"
calendar_code="$(jq -r '.calendar_code' "$OPTIONS")"

output_dir="$(dirname "$output_path")"
tmp_path="${output_path}.tmp"

if [[ -z "$email" || -z "$password" || -z "$calendar_code" ]]; then
  echo "[ERROR] timetree_email, timetree_password, and calendar_code must be set."
  exit 1
fi

mkdir -p "$output_dir"

export TIMETREE_EMAIL="$email"
export TIMETREE_PASSWORD="$password"

echo "[INFO] Starting local-only HTTP server on 127.0.0.1:8088"
python3 -m http.server 8088 \
  --bind 127.0.0.1 \
  --directory "$output_dir" \
  >/dev/null 2>&1 &

run_export() {
  echo "[INFO] Exporting TimeTree at $(date -Iseconds)"

  timetree-exporter \
    -e "$email" \
    -c "$calendar_code" \
    -o "$tmp_path"

  python3 - "$tmp_path" <<'PY'
import re
from datetime import datetime, timedelta
import sys

path = sys.argv[1]

with open(path) as f:
    text = f.read()

def fix(match):
    block = match.group(0)

    # detect all-day event (DATE without time)
    if not re.search(r'^DTSTART:\d{8}$', block, re.M):
        return block

    m = re.search(r'^DTEND:(\d{8})$', block, re.M)
    if not m:
        return block

    end = datetime.strptime(m.group(1), "%Y%m%d")
    end += timedelta(days=1)

    return re.sub(
        r'^DTEND:\d{8}$',
        "DTEND:" + end.strftime("%Y%m%d"),
        block,
        flags=re.M
    )

text = re.sub(
    r'BEGIN:VEVENT.*?END:VEVENT',
    fix,
    text,
    flags=re.S
)

with open(path, "w") as f:
    f.write(text)
PY

  if [[ ! -s "$tmp_path" ]] || ! grep -q "BEGIN:VCALENDAR" "$tmp_path"; then
    echo "[ERROR] Export failed or produced invalid ICS. Keeping previous file."
    rm -f "$tmp_path"
    return 1
  fi

  mv -f "$tmp_path" "$output_path"
  echo "[INFO] Updated $output_path ($(wc -c < "$output_path") bytes)"
}

run_export || true

while true; do
  sleep "$((interval_minutes * 60))"
  run_export || true
done