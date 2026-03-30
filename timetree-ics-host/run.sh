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
import sys
from datetime import datetime, timedelta

path = sys.argv[1]

with open(path, "r", encoding="utf-8") as f:
    text = f.read()

def parse_date(s):
    return datetime.strptime(s, "%Y%m%d").date()

def fmt_date(d):
    return d.strftime("%Y%m%d")

def fix_until_for_timed(block: str) -> str:
    # Timed DTSTART => UNTIL must be DATE-TIME
    def repl(m):
        val = m.group(1)
        if re.fullmatch(r"\d{8}", val):
            return f"UNTIL={val}T235959Z"
        return m.group(0)
    return re.sub(r'UNTIL=(\d{8}(?:T\d{6}Z)?)', repl, block)

def fix_until_for_allday(block: str) -> str:
    # All-day DTSTART => UNTIL must be DATE only
    def repl(m):
        val = m.group(1)
        if re.fullmatch(r"\d{8}T\d{6}Z", val):
            return f"UNTIL={val[:8]}"
        return m.group(0)
    return re.sub(r'UNTIL=(\d{8}(?:T\d{6}Z)?)', repl, block)

def fix_vevent(match):
    block = match.group(0)

    # All-day event in exporter 0.7.0 format: DTSTART:YYYYMMDD
    is_all_day = bool(re.search(r'^DTSTART:\d{8}$', block, re.M))

    if is_all_day:
        m = re.search(r'^DTEND:(\d{8})$', block, re.M)
        if m:
            end = parse_date(m.group(1)) + timedelta(days=1)
            block = re.sub(
                r'^DTEND:\d{8}$',
                f'DTEND:{fmt_date(end)}',
                block,
                flags=re.M
            )
        block = fix_until_for_allday(block)
    else:
        block = fix_until_for_timed(block)

    return block

text = re.sub(
    r'BEGIN:VEVENT.*?END:VEVENT',
    fix_vevent,
    text,
    flags=re.S
)

with open(path, "w", encoding="utf-8", newline="") as f:
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