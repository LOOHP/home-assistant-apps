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

newline = "\r\n" if "\r\n" in text else "\n"

def parse_date(s):
    return datetime.strptime(s, "%Y%m%d").date()

def fmt_date(d):
    return d.strftime("%Y%m%d")

def fix_until(block: str, is_all_day: bool) -> str:
    def repl(m):
        value = m.group(1)
        if is_all_day:
            if len(value) == 8:
                return f"UNTIL={value}"
            if len(value) == 16 and value.endswith("Z"):
                return f"UNTIL={value[:8]}"
            return m.group(0)
        else:
            if len(value) == 8:
                return f"UNTIL={value}T235959Z"
            return f"UNTIL={value}"
    return re.sub(r'UNTIL=([0-9]{8}(?:T[0-9]{6}Z)?)', repl, block)

def fix_vevent(block: str) -> str:
    is_all_day = bool(re.search(r'^DTSTART;VALUE=DATE:\d{8}$', block, re.M))

    if is_all_day:
        m_start = re.search(r'^DTSTART;VALUE=DATE:(\d{8})$', block, re.M)
        start = parse_date(m_start.group(1))

        m_end = re.search(r'^DTEND;VALUE=DATE:(\d{8})$', block, re.M)
        if m_end:
            end = parse_date(m_end.group(1))
            fixed_end = end + timedelta(days=1)
            block = re.sub(
                r'^DTEND;VALUE=DATE:\d{8}$',
                f'DTEND;VALUE=DATE:{fmt_date(fixed_end)}',
                block,
                flags=re.M,
            )
        else:
            fixed_end = start + timedelta(days=1)
            block = re.sub(
                r'^(DTSTART;VALUE=DATE:\d{8})$',
                r'\1' + newline + f'DTEND;VALUE=DATE:{fmt_date(fixed_end)}',
                block,
                count=1,
                flags=re.M,
            )

        return fix_until(block, is_all_day=True)

    return fix_until(block, is_all_day=False)

text = re.sub(
    r'BEGIN:VEVENT\r?\n.*?END:VEVENT',
    lambda m: fix_vevent(m.group(0)),
    text,
    flags=re.S,
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