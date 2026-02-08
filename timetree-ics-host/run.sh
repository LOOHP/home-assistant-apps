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

  # Export to temp file
  timetree-exporter \
    -e "$email" \
    -c "$calendar_code" \
    -o "$tmp_path"

  # Fix invalid RRULE UNTIL values (DATE -> DATE-TIME)
  sed -E -i \
    's/UNTIL=([0-9]{8})([^T])/UNTIL=\1T235959Z\2/g' \
    "$tmp_path"

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