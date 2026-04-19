# PA System

This add-on hosts the PA System web UI inside Home Assistant through ingress and streams live browser microphone audio to Home Assistant media players.

## Configuration

The add-on UI now only needs these main settings:

- `home_assistant_ip`: the LAN IP your speakers can reach, for example `192.168.1.3`
- `app_port`: the listener port for the MP3 stream, default `8099`
- `ha_token`: a Home Assistant long-lived access token
- `targets_json`: your media player target list

The add-on generates the other URLs automatically:

- Home Assistant API URL: `http://homeassistant:8123`
- Speaker stream base URL: `http://<home_assistant_ip>:<app_port>`
- UI URL: Home Assistant ingress via the **Open Web UI** button

## Installation

1. Copy this folder into your Home Assistant add-on repository.
2. Add the repository to Home Assistant, or place it under your local add-ons folder.
3. Install the add-on.
4. Open the **Configuration** tab.
5. Set `home_assistant_ip` to the LAN IP your speakers can reach.
6. Leave `app_port` at `8099` unless you want a different listener port.
7. Set `ha_token` to a Home Assistant long-lived access token.
8. Edit `targets_json` to match your `media_player` entity IDs.
9. Start the add-on and open it from the sidebar.

## Notes

- TLS is no longer configured in the add-on. Home Assistant ingress handles HTTPS for the UI.
- The `/live.mp3` stream is served directly over HTTP at `http://<home_assistant_ip>:<app_port>/live.mp3` so your speakers can fetch it on the LAN.
- The sidebar UI uses Home Assistant ingress paths, so the frontend uses relative API and WebSocket URLs and does not need a separate UI base URL.
- The add-on uses `ffmpeg` to transcode browser WebM audio into MP3 for live playback.