## 2.3.0

Two headliners this release: new ONT monitoring providers (a Zyxel GPON-SFP stick and a vendor-neutral HTTP JSON provider you can attach to an SFP module), and continued Multi-Site work for multi-location and MSP deployments, most notably agent tunnels no longer silently breaking behind a reverse proxy. Plus sharper ISP Health Transit scoring and better device names on the maps.

See the [v2.2.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.2.0) for what came before this.

## ONT Device Monitoring

- **Zyxel GPON-SFP PMG3000 (HTTP) provider** - Read-only optics, line status, and temperature for the Zyxel PMG3000-D20B GPON-SFP stick on ONT Stats. (#1033, thanks @Optic00)
- **Network Optimizer Custom (HTTP JSON) provider** - Point it at any endpoint serving vendor-neutral PON stats and it feeds ONT Stats and alerts like a built-in provider. In Attach to SFP Module mode the PON data (link status, FEC/BIP errors) merges onto that module in SFP Stats, so a PON-over-SFP setup shows as one device instead of two.
- **Nokia ONT works on more firmware** - Sends browser headers and falls back to a page-walk auth flow, so ONT stats now populate on T-Fiber/Metronet CLEI variants that previously 401'd. (#929, thanks to the testers who helped figure this out)
- **Smoother setup** - Selecting a provider prefills the ONT Host with the address that device ships on, and the ONT form and Add-a-Site wizard no longer linger on stale state.

## Monitoring - ISP Health

- **Your direct peering now shows up in Transit Health** - Internet targets reached directly over your ISP's peering/IX are graded as a synthetic IX Peering entry instead of dragging Transit against a neutral fill, each peer scored on its own so one flapping peer doesn't crater it. (#1031)
- **More accurate Transit scoring** - Transit Health is now a plain involvement-weighted average (no more neutral-100 blend inflating it), jitter is scored at P90 instead of P95 to stop double-counting bursts, and a transit ASN is no longer penalized for jitter when a destination proven to route through it looks clean. Off-path networks scoring low now carry a tooltip explaining they may just be deprioritizing ICMP. (#1028, #1034)

## Monitoring - Live View

- **Better names and throughput on the LAN Flow Map** - UniFi Device Bridge clients (e.g. a Protect camera bridged onto the LAN) now show their friendly name and real throughput on the 2D/3D maps and in Client Performance, and name-less clients use UniFi's display name instead of a raw MAC. Works in historic playback too. (#1027)

## Multi-Site

- **Reverse proxies no longer silently break the agent tunnel** - The canonical-host redirect no longer catches the agent's gRPC stream, which could redirect the tunnel to death behind a reverse proxy while REST heartbeats kept the agent falsely green. A down tunnel now correctly reads as offline. (#1032)
- **Agent setup polish** - A LAN speed test toggle in the default-site token flow, a dismiss X on the expanded site config row, and an installer that self-remediates AppArmor-confined nginx and adds a `--uninstall` flag. (#1035)

## Fixes

- **Duplicate Health Issues entries** - A load-vs-refresh race could double every Health Issues entry (the "(2)" badges); refreshes are now serialized. (#1026)
- **Spurious console-connection error** - A reconnect mid-login no longer surfaces a "Cannot access a disposed object" error; it degrades to the normal retry. (#1026)
- **Technitium DNS detection** - Now prefers Technitium's /api/status endpoint. (#1023, thanks @jimstrang)

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 2.2.0

The headline: the On-Site Agent can now run directly on the site's UniFi gateway, so a monitoring-only site doesn't need a separate box for it. Plus a synced Live View timeline, sharper ISP/Transit loss, two Security Audit false-positive fixes, and SNMP credential self-healing.

## What's New

Catching up the v2.1 line, in case you're coming from v2.0.x (see the [v2.1.0](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.1.0) / [v2.1.1](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.1.1) notes for detail):

- **Multi-Site, rounded out** - self-healing UniFi Console connections, first-class alerts when a console or On-Site Agent drops, and a real site lifecycle (add, disable, remove) - enough to run every network you touch from one instance.
- **Native Starlink monitoring** - a live dashboard card with an obstruction sky map, a dedicated Starlink Stats tab with history, and ISP Health scoring built on what only the dish knows. Works at external sites over the agent tunnel.
- **Monitor duplicate management IPs** - two devices answering at the same address on different WANs (classically an ONT and a Starlink dish both at 192.168.100.1) can now both be monitored, via a per-interface alias IP on the gateway.
- **Nokia XS-010X-Q ONT support** - reads optical power and device info over the ONT's web interface, with a temperature alert and configurable thresholds.
- **Channel optimizer on a real scale** - the optimizer never moves an AP onto a measurably-worse channel, and channel scores are now readable.

## Multi-Site

**The On-Site Agent can now run directly on the site's UniFi gateway** - any current UniFi OS gateway (UCG, UXG, UDM, UDR, EFG lines). Monitoring-only by design: hosting a speed-test server on the router would compete with the data plane. The Set up agent wizard generates a third one-liner alongside Docker and bare metal. It installs to `/data` (persists on UniFi OS) with a memory-fenced systemd unit that holds a ~50 MB footprint, so it can never pressure routing or IPS. Free memory is the only check; there's no model gate. Re-running the command upgrades in place or reinstates the service after a firmware update, and `--uninstall` gives clean teardown.

- **Speed-test surfaces adapt** - a gateway-resident agent hosts no speed-test listener, so the LAN, WAN, and client speed-test pages explain how to add a separate agent box for testing instead of pointing at the router.

## Monitoring

### ISP Health

- **Outages that began before the view window** - an outage already in progress when a view opened was clipped to its recovery tail and mislabeled as a path-wide ISP outage with its duration collapsed to seconds. Detection now reaches back before the window start, so an outage is classified and timed consistently across views.

### Live View

- **Synced timeline playback** - scrubbing the timeline moves the 3D/2D map, the WAN chart cursor, the Port Statistics table, and the stat cards to the same instant, with uniform keyboard steps and no jump when resuming playback.
- **Click the WAN chart to seek** - clicking the WAN live chart scrubs the whole timeline to that instant, with a Historic badge and a play/pause control while off the live edge. Tap-for-tooltip is preserved on touch devices.
- **ISP/Transit loss accuracy** - the WAN chart Loss series and the map's WAN globes share one combined ISP+Transit loss figure, and loss is no longer dropped between sampling windows or when a probe cycle times out under load, so sustained loss shows for its full duration.

### 3D LAN Flow Map

- **Property-relative sizing** - devices, pipes, particle streams, and WAN globes scale with the property, so fixed-size objects no longer tower over shrunken buildings on large or multi-building sites.
- **Link speed tooltips and precise device height** - adds link-speed tooltips and accurate device height, and fixes a placement round-trip bug. The capacity changes also improve the 2D LAN Topology Flow Map.
- **Full-duplex link load colour** - link colour reserves red for both directions loaded; a single saturated direction reads as amber. Applies to the 3D and 2D maps.

### ONT Stats

- **Nokia ONT resilience** - the Nokia XS-010X-Q provider retries transient failures on a fresh connection, so intermittent stat gaps self-recover, and logs the ONT's raw responses so the ones that still fail leave a diagnosable trace.

### Setup

- **SNMP Community String length warning** - UniFi Network accepts a Community String longer than devices reliably support (20 characters), so switches silently drop from polling while the gateway keeps reporting - which reads as "no data from my switches". Setup and Live View now warn with the measured length, the banner auto-appears when the string changes mid-session and auto-dismisses once it's fixed, and a too-long value is never adopted as the polling credential.
- **SNMP credential self-heal** - a rotated Community String (or changed v3 credentials, or SNMP toggled off and back on) previously needed Monitoring disabled and re-enabled to pick up. The server now detects the fabric-wide poll failure, re-pulls the SNMP config from the UniFi Console, and adopts the change automatically - recovery in about 30-45 seconds on direct sites and within 2 minutes on agent sites.

## Security Audit

- **Missing Isolation false positive when a narrow block precedes a broad block** - a port-specific block (e.g. a DoT block) ahead of an all-traffic block made the isolation check fail and report the pair as unisolated. Partial-block rules are now transparent to the evaluation, so a broad block behind a narrow one still satisfies isolation, while an allow ahead of a broad block is still flagged as a bypass. (fixes #1010, thanks @jimstrang for the repro)
- **Raw-MAC policy sources recognized** - UniFi's newer raw source MAC restriction now parses alongside the older client-based shape, so a one-device allow ahead of a zone-wide deny is classified as an intentional exception instead of a rule-order warning. Also fixes a cross-zone eclipse false positive. (fixes #1011, thanks @jimstrang for the sample policy JSON)

## Performance Tweaks

- **UniFi OS 5.1.26 supported** - the firmware gate that disables deploying new tweaks on untested versions now allows UniFi OS 5.1.26, verified statically compatible and confirmed in the field. (thanks @mark0263 for confirming)

## Fixes

- **Duplicate default agent names** - new agents were named count+1, which collided after deletions (a site with a sole "Agent 2" minted a second "Agent 2"). Default names now take the first free number.
- **Site switcher kept a stale client pinned on Client Performance** - switching sites carried the pinned client along, pinning the new site's page to a client from the old site. The switcher now drops it (tab and range selections still carry).
- **Client identity for off-site viewers** - the agent's client-identity probe gained Private Network Access support for Chromium browsers enforcing public-to-private fetch rules at sites, so own-device identity resolves where the browser previously blocked it.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 2.1.1

A focused round of ONT monitoring, Starlink handling, and Wi-Fi channel improvements. See the [v2.1.0 notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.1.0) for the bigger picture.

## Monitoring

### ONT Stats
- **Nokia XS-010X-Q** support - reads optical power and device info over its web interface (thanks @jakerobb for the traces).
- **ONT temperature alert** - fires when a monitored ONT reports a temperature over the limit.
- **ONT Alert Thresholds** - a new card to set the ONT temperature and RX-power limits.

### SFP Stats
- Empty RX / TX / Temp columns now explain themselves: the module isn't reporting DDM. If it's an ONT, monitor it directly instead.

### Monitoring Interfaces
- Selecting a **Starlink WAN** now steers you to native Starlink Stats instead of a monitoring interface, detected by ISP rather than WAN name (thanks @Optic00).

## Alerts & Schedule - Rules
- **Threshold shortcuts** - the SFP, ONT, and Device temperature rules link straight to the card that configures their limits.
- The SFP power alerts are renamed **SFP: RX Power Low** and **SFP: TX Power High** (they cover Active Ethernet and other optical modules, not just PON).

## Wi-Fi Optimizer - Channels
- The optimizer never moves an AP onto a measurably-worse channel, and channel scores are now on a real, readable scale.

## Fixes
- **LAN flow map** - corrected the throughput direction shown for hypervisor/server nodes.
- **Multi-site** - new default alert rules now enable on secondary sites that already run the matching monitoring.
- **UI tables** - action buttons stay readable on row hover and inside nested cards.

## Coming soon
- **Multi-WAN ISP Health and Monitoring** - a lot of the groundwork landed here; full support is likely the next minor release.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 2.1.0

**On-Site Agent update (optional):** this release includes a small agent update that fixes one minor bug - client speed tests run from an external site could log the IPv4-mapped (`::ffff:`) form of a client's address instead of its real IP. It's not critical, so update the agent on your external sites whenever it's convenient (re-run the install script, or use the in-app update prompt). Nothing else needs it.

Network Optimizer has been in production for over seven months and runs on roughly 15,000 networks today, mostly power users looking after their own homes and their family's. It has always had MSP-grade capabilities - deep monitoring, ISP Health, security auditing, alerting - that those power users found cool. Multi-Site is the newest piece, and 2.1 is where it comes together: self-healing console connections, first-class alerts when a UniFi Console or On-Site Agent drops, and a real site lifecycle (add, pause, remove) make it a genuinely viable way to manage every network you touch from one instance. Around that, 2.1 adds native Starlink dish monitoring, support for two devices that share one management IP across different WANs, and a round of Wi-Fi Optimizer and client-identification fixes. For what came before, see [v2.0.0](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0) and the [v2.0.1](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.1) / [v2.0.2](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.2) patches.

## What's New

- **Multi-Site, rounded out** - Built on a single-site core with 7+ months in production, Multi-Site now has the operational pieces to run on day to day - connections that recover on their own, alerts when a console or agent goes offline, and a full site lifecycle - making Network Optimizer a viable way to manage many networks, not just your own. Still off by default and free for personal use on up to 3 sites.
- **Native Starlink monitoring** - First-class health for Starlink dishes: a live dashboard card with an obstruction sky map, a dedicated Monitoring tab with history, and ISP Health scoring built on what only the dish knows. Works at external sites over the agent tunnel too.
- **Monitor duplicate management IPs** - Two devices that answer at the same IP on different WANs (a common one is an ONT or cable modem sharing 192.168.100.1 with a Starlink dish on another WAN) can now both be monitored, using a per-interface alias IP on the gateway.
- **Self-healing console connections** - A UniFi Network restart, upgrade, or brief outage no longer takes your console connection down. Previously it stayed down until you re-saved the connection in Settings or restarted Network Optimizer; now it re-validates and recovers on its own, usually within a minute.

## Multi-Site

- **Disable / Remove Site** - A new section in each site's Configuration panel (Settings - Multi-Site). Disable stops that site's monitoring and console connection immediately and hides it from the site switcher, keeping all data so you can re-enable it in place later. Remove is permanent and behind a double confirmation: it deletes the site, its database, and its agent enrollments, and frees the license seat. InfluxDB buckets are deliberately left in place (removing them needs the admin token, which is never stored), and the confirmation tells you so. Both actions are blocked for the default site and the site you're currently viewing.
- **Clearer feedback during site creation** - The provisioning spinner now actually shows while a new site is being built, so you can see it working instead of wondering whether your click registered, and a re-entrancy guard swallows the double-click that could previously create a duplicate "-2" copy.
- **Add Site lands on the form** - The + card on the Sites page now scrolls the add form into view with the name field focused, instead of just opening the settings tab.
- **Live site switcher** - The switcher rebuilds in every open browser tab when sites are created, renamed, enabled, disabled, or removed, instead of waiting for a page reload. It also gained keyboard support: Escape closes it, Up/Down move through sites, Enter or Space selects.

## Monitoring

### Starlink Dish / Terminal Monitoring

- **Starlink Stats dashboard card** - A live panel centered on the obstruction sky map, rendered from the dish's own 123x123 SNR grid so blockages appear exactly where they sit in the sky. Alongside it: sky-obstruction percentage, dish-side packet loss, power draw, negotiated Ethernet speed, uptime, GPS fix, last outage, and any active dish alerts. Present by default with a configure prompt when no dish is set up, matching the Cable Modem and ONT cards.
- **Starlink Stats monitoring tab** - A new tab to the right of Cellular Stats with history charts for power draw, dish ping-drop rate, sky obstruction, outage seconds, GPS satellite count, and alignment offset. Supports multiple dishes.
- **ISP Health scoring for satellite WANs** - For any WAN set to the Satellite access technology, Starlink becomes the Physical Link source, scored on sky obstruction, dish-to-ground packet loss, and outage burden, with caps for thermal shutdown, tilt, water intrusion, and persistently low SNR. A slow-negotiated Ethernet link is surfaced as advice rather than counted against the ISP.
- **Set it up under Settings - Starlink Monitoring** - Add and manage dishes (host defaults to 192.168.100.1, port 9200) with a connection test. No credentials needed, since the dish's local API is unauthenticated. We deliberately leave latency and throughput out of this feature: the monitoring pipeline already measures RTT and WAN speed with better fidelity, so Starlink Stats tracks only what the dish uniquely reports.

### General

- **Show or hide hardware stat tabs per site** - The CM Stats, ONT Stats, Cellular Stats, and Starlink Stats tabs each get a "Show this tab in Monitoring" toggle in their Settings section. All stay visible by default; hiding one just drops it from the Monitoring nav for that site, so a site that only has a cable modem isn't carrying tabs it can't use. Switching to a site that hides your current tab lands you on the default tab instead of a stranded one.
- **Stat cards link only when there's something to view** - The Cable Modem Stats, ONT Stats, Cellular Stats, and Starlink Stats dashboard cards are whole-card links only when a device is actually configured. With nothing to show, the card keeps its own Configure button instead of bouncing you to an empty tab.
- **Cleaner jumps between Settings and Monitoring** - A link icon next to each hardware monitoring card title (Cable Modem, ONT, Cellular, Starlink) opens the matching tab, and ONT Device Monitoring now explains when an SFP ONT should be read off the gateway port via Set ONT on the SFP Stats tab instead.

### Monitoring Interfaces

- **Alias IP for duplicate management IPs** - Monitoring Interfaces can now poll a device through an alias IP, so two devices sharing the same management address on different WANs (for example an ONT and a Starlink dish both answering at 192.168.100.1) can both be monitored at once. Set an alias on one interface and the gateway translates for it (policy routing plus DNAT out that interface's own path), while the other device keeps the plain address and UniFi's own native dashboards stay untouched. Deploys are gated by subnet-overlap and mark/table ownership checks so it never collides with UniFi's own routing, and each interface holds a stable MAC across gateway reboots. Verified on real dual-WAN hardware.

## UniFi Console Connection

- **API key connections self-heal after a Network restart or upgrade** - While the UniFi Network application restarts, upgrades, or wedges, its proxy answers with 401/403 even though your API key is still valid. The client used to read that as a revoked key and permanently stop calling the console, so Wi-Fi Optimizer, Config Optimizer, Security Audit, Threat Intelligence, and SNMP detection all went dark until you re-saved the connection in Settings or restarted Network Optimizer. It now re-validates the key instead (throttled to one probe a minute, so a genuinely revoked key stays cheap) and recovers on its own within a minute of the console coming back.
- **Reverse-proxied consoles recover from gateway errors** - Connections through a reverse proxy now self-heal on 502, 503, and 504 the same way they already did on 401 and 403.
- **The default site auto-reconnects after a transient outage** - A brief blip no longer leaves the main site's console connection down until you touch it.

## Alerts & Schedule - Rules

- **UniFi Console connection alerts** - New `console.connection_failed` (Warning) and `console.connection_restored` (Info) event types, per site, armed only after a first successful connection so setup-time failures never alert. A 30-minute failure cooldown keeps a flapping console upgrade to a single alert.
- **On-Site Agent alerts** - New `agent.offline` (Warning) fires when an enrolled agent has been continuously offline for 3 minutes, paired with `agent.reconnected` (Info). Judged by the same live definition the UI uses, so routine agent redeploys and brief tunnel bounces stay silent, and single-site installs without an agent never see rules they can't use. Both sets deliver through your existing Notification Channels.

## Wi-Fi Optimizer

- **Wi-Fi-less gateways no longer show up as empty access points** - A UXG-Fiber (or any gateway without integrated Wi-Fi) could appear in the Wi-Fi Optimizer as an access point with zero clients and then trip a false "Significant Load Imbalance," because some firmware reports phantom radio entries for radio-less gateways. Gateway Wi-Fi capability is now decided by model against a curated list of the gateways that genuinely have Wi-Fi, so gateway-only hardware is treated correctly and real Wi-Fi gateways (including an Express uplinked as an AP) behave exactly as before.
- **No more channel moves onto a measurably-worse channel** - The recommender no longer moves an AP onto a channel its own radio measured as worse (a louder noise floor or more airtime) when the move buys no co-channel relief for your own APs. It only ever holds an AP in place, so it can't create new churn, and a move that genuinely unsticks a collision among your own APs still goes through.
- **Re-scan prompt when a stale scan is steering the advice** - When an AP's spectrum scan is 3+ days old and that aging reading is actually holding or deciding a channel while nearby networks no longer corroborate it, the channel recommendations now offer a Re-scan option. It stays quiet when a fresh scan wouldn't change the answer. Scan age now comes from the console's real scan timestamp, so staleness is accurate.

## Client Performance

- **Devices resolve when clients arrive as IPv4-mapped IPv6** - On a dual-stack setup, an IPv4 client can be accepted as the IPv4-mapped form `::ffff:10.x.x.x`, which never matched the console's plain-IPv4 client list. Where that happened, the page showed "Device Not Found" with a `::ffff:`-prefixed address, and stored speed-test results under the mapped address with the wrong LAN/WAN label and no device correlation. Client addresses are now normalized to plain IPv4 everywhere they're captured, including the on-site agent's whoami path, so those devices resolve, speed tests store the real IP with the correct label and attach to the right client's speed history, and a data migration cleans up existing `::ffff:` results for display. Genuine IPv6 clients are never altered.

## Fixes

- **Clearer agent alert names** - An agent that's simply named "agent" no longer shows a redundant quoted name in its alerts, and pasted console URLs in Settings - Monitoring are trimmed to the bare host.
- **Settings polish** - Form help text is a touch larger and more legible across the settings forms.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 2.0.2

More fixes and a couple of nice additions, mostly around Monitoring's Upstream path discovery. See [v2.0.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0) for what's new in v2.0.

## Client Performance

- **Simplified view for VPN clients** - Tailscale, UniFi Teleport, and UniFi One-Click / S2S VPN clients now get their own dashboard: name, IP, both speed-test buttons, live results, speed map, and path traces.
- **Clearer "device not found" copy** - distinguishes "console unreachable" from "console fine, device just isn't listed yet," and shows the detected address.

## Monitoring

- **Right access ISP on silent first miles** - some fiber/PPPoE first miles don't announce themselves, which let Upstream path discovery crown the wrong provider (in one case a DNS resolver's edge). It now anchors on your gateway's WAN address, and those first-mile hops become monitorable targets.
- **"Did you switch internet providers?"** - when your access ISP actually changed, Upstream path discovery asks; confirm and it pauses the old targets and adopts the new path in one save.
- **Off-path transit networks get cleaned up** - when your ISP re-routes, targets for a transit network you no longer use are surfaced for pausing instead of dragging down ISP Health. Nothing is deleted.
- **First-mile device picks the real WAN gateway** - on a shared WAN segment it no longer reads the device from an unrelated same-subnet neighbor.
- **Flaky monitoring targets advisory clears on recovery** - a flagged target drops off once its monitoring is clean again (about half an hour for a target that was fully down) instead of nagging for up to two days.
- **Flaky monitoring targets advisory on ISP Health** - the advisory now also appears on the ISP Health tab where the score lives, not just Live View.

## LAN Speed Test

- **Speed map auto-fit** - a new result or a time-range change brings the visible results back into view, unless you've manually panned or zoomed. Applies to the Client Performance speed map too.

## Multi-Site

- **Current site opens its dashboard** - clicking the site you're already on now opens it instead of doing nothing. Ctrl/cmd/shift/middle-click still opens a new tab.
- **Cold managed-site connection** - shows the device picker right away and auto-loads once the on-site agent's tunnel comes up, instead of stranding you until a manual refresh.
- **Cleaner logs on agent sites** - ONT, cable modem, and cellular modem poll logs name the configured device host instead of the internal tunnel loopback; agent version labels drop the `+build` suffix.

## Fixes

- **Break out of a wedged reconnect spinner** - if "Reconnecting..." gets stuck and never clears, the app now probes the server and reloads once it answers.
- **Settings polish** - darker row hover so rows read differently from buttons, dark chrome on native form controls, and the site-name field focuses when you click edit.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 2.0.1

More multi-site fixes and hardening. See the [v2.0.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0) for the multi-site launch and the rest of the feature set.

**Multi-Site Agent update:** this release updates the On-Site Agent - update it on each external site (re-run the agent install script, or use the in-app update prompt). One-time for this release, not every release.

## Multi-Site

- **Per-tab site context** - each browser tab pins its own site via a `?site=` URL, so you can keep different sites open in different tabs at once.
- **Alert "View" links open the site the alert came from** (including the main site), pinning only that tab instead of the browser-wide default.
- **Site name shown next to the Dashboard header** when multi-site is enabled.

### On-Site Agent

**Monitoring**

- **External sites keep collecting through tunnel and WAN outages.** The agent buffers probe and SNMP data while the tunnel is down and replays it on reconnect, with end-to-end acks so nothing is silently lost. Charts backfill the gap automatically.
- **Alerts aren't silently suppressed by agent clock skew** - if an external site's agent host clock is off, its samples could look too old and quietly skip alerting; that's now surfaced instead of silent.

**Console & SSH Proxy**

- **Switching to an offline external site is instant, not a hang** - a dead tunnel is detected fast and the site shows a "waiting for the site's agent" banner instead of freezing.
- **The Ignore-SSL-errors setting is shown as forced-on** for agent-connected consoles (it can't apply through the tunnel), instead of a toggle that does nothing.
- **Agent-owned dial policy** - the proxy only dials site-local addresses by default, with an optional `proxyAllowedCidrs` pin and an agent-side dial audit log.

## Monitoring

### ISP Health

- **Path-shift detection accepts noisy transition windows** - a step whose transition median dips just outside the band is no longer discarded.

### Network Performance

- **Flaky LAN target advisory** - a dismissible hint on LAN latency charts when a non-gateway/non-AP device shows loss that's usually a measurement artifact (roaming, ping deprioritization), linking to its target row. Gateways and APs excluded.

## Fixes

- **Mobile scroll no longer locks up after backgrounding,** and the top bar's hide/reveal is smoother.
- **Returning to the app on mobile keeps your place** - a backgrounded app used to go back to the homepage/dashboard when resuming, now it correctly returns to where you left off
- **Dismissed "install as an app" and channel-analysis banners stay dismissed** across site switches.
- **Live WAN chart no longer clips hover tooltips** at its edges.
- **2D Flow Map** fits devices tighter on the canvas instead of behind the scrubber bar.
- **ONT external refresh button** disables with a spinner while polling, preventing double-taps.
- **Per-device SSH:** setting a key path clears any stored password; a blank password on edit means "keep," not "clear."

## Installation

On a beta build? See "Switching from a beta build" in the [v2.0.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0) to get back on the stable track.

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 2.0.0-beta.8

**Preview (beta) build of Network Optimizer 2.0 (with new Multi-Site support) for testers.** Pin a beta tag below - `:latest` stays on stable 1.x. Feedback welcome.

Beta.7 plus the below. Already on beta.5 or later? No agent update needed, nothing has changed on the agent since beta.5. Coming from an earlier beta, update your site agents as beta.5 described.

## Site Licensing

2.0 introduces license keys. The short version: personal, non-commercial use on up to 3 sites stays exactly as it is - free, no key, no account, and the app never phones home. That is most of you, and that is by design.

- **License keys** - Commercial use takes a license key (at any site count), and so does going past 3 sites. Keys go in under Settings > Application > Licensing; they stack, cover a set number of sites, and come in perpetual and term flavors, with per-site coverage assignment and status on the Sites page. No accounts, ever - just keys.
- **Grace, not cliffs** - An expired key gives its sites a 10-day grace period with a countdown banner before anything is restricted. Restriction only stops new operations and stats collection; all historic data stays viewable, and entering a new key restores everything within seconds.
- **Built for self-hosters** - Entitlements are signature-verified and cached locally, so a license server outage can never disable your sites. Perpetual keys confirm once about a month after activation and then never phone home again.
- **Firewall note** - Activating or renewing a key makes an outbound HTTPS request to `licensing.ozarkconnect.net`; strict egress rules need 443 allowed to that hostname. Free-tier installs never make this connection.

## WAN Speed Test

- **ISP Health score in the header** - Your ISP Health score now shows right where you run tests, auto-refreshing as results land.
- **Smarter sparse-data scoring** - ISP Health tops up to 4 WAN speed samples from before its window, so a quiet couple of days does not blank the throughput factor.
- **No empty score flash on managed sites** - ISP Health and the header tile wait for the site's UniFi Console connection before computing.

## Monitoring

- **Live View and LAN flow map self-heal** - Both now recover on their own when a site's console connects after the page loads, instead of staying empty until a refresh.

## Fixes

- **Small fixes** - Speed results with no direction show a dash instead of a blank, and the mobile nav logout is icon-only so it fits the bar.

New to the 2.0 beta? See the [beta.5 notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0-beta.5) for the Multi-Site overview.

## Installation

**Windows**: Download the MSI installer below

**Docker**: new for beta.8 - a rolling `:beta` tag. Set it once and every future beta is just a pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:beta
image: ghcr.io/ozark-connect/speedtest:beta
```
```bash
docker compose pull && docker compose up -d
```
Prefer to hold a specific build? Pin `2.0.0-beta.8` instead.

**Proxmox** - new install? Run the standard installer first, then pin the beta below:
```bash
bash -c "$(wget -qLO - https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```
Upgrade (new and existing installs). Beta upgrades migrate your database and can't roll back to stable 1.x, so snapshot the LXC first. This pins the rolling `:beta` tag, so future betas are just a pull:
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && cp -n data/network_optimizer.db data/network_optimizer.db.pre-beta8 2>/dev/null; sed -i -E 's#(network-optimizer|speedtest):(latest|beta|2\.0\.0-beta\.[0-9]+)#\1:beta#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.8 && ./scripts/install-macos-native.sh
```

## 2.0.0-beta.7

**Preview (beta) build of Network Optimizer 2.0 (with new Multi-Site support) for testers.** Pin the tag below - `:latest` stays on stable 1.x. Feedback welcome.

Beta.6 plus the below. Already on beta.6? No agent update needed, nothing changed on the agent. Coming from an earlier beta, update your site agents as beta.5 described.

## Wi-Fi Channel Optimizer

- **Soaking APs hold their channel** - A soaking AP keeps its channel for the full soak window, so toggling DFS no longer bumps it mid-measurement.
- **Others avoid a soaking channel** - The optimizer keeps other APs off a channel a soaking AP is holding, and tags mesh children of a soaking leader.
- **Band-aware escape from a bad channel** - A soaking AP can leave a genuinely congested channel early, at per-band airtime thresholds (2.4 GHz 60%, 5 GHz 50%, 6 GHz 45%) instead of a flat 70%.

## Multi-Site

- **External sites need a live agent to probe** - Upstream Discovery and adding Latency Targets require a connected on-site agent; default internet targets seed disabled and auto-enable on first agent deploy.
- **Clearer WAN gateway test status** - When Gateway (Direct) can't run, the reason shows below the option (not just a badge) and links to the right Settings page.
- **LAN Speed Test respects managed sites** - No agent locks out the tests with a setup pointer, and the server iperf3 version badge is hidden (the test runs on the agent).
- **Per-site schedule reminder** - On managed sites the schedule banner notes that schedules are per site.

## Fixes since beta.6

- **Clearer agent-offline wording** - Speed Test, Monitoring Tools, and WAN Steering say tests "can resume when the agent reconnects" rather than implying they auto-run.
- **LAN Speed Test polish on managed sites** - The device list now populates on its own when the agent reconnects (no manual Refresh), no SSH-warning flash on load, connection and setup warnings stay readable while the section is locked, and it degrades gracefully if the gateway status can't be read.

New to the 2.0 beta? See the [beta.5 notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0-beta.5) for the Multi-Site overview.

## Installation

**Windows**: Download the MSI installer below

**Docker**: pin the beta tags in `docker-compose.yml` (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.7
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.7
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** - new install? Run the standard installer first, then pin the beta below:
```bash
bash -c "$(wget -qLO - https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```
Upgrade (new and existing). Beta upgrades migrate your database and can't roll back to stable 1.x, so snapshot the LXC first:
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && cp -n data/network_optimizer.db data/network_optimizer.db.pre-beta7 2>/dev/null; sed -i -E 's#(network-optimizer|speedtest):(latest|2\.0\.0-beta\.[0-9]+)#\1:2.0.0-beta.7#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.7 && ./scripts/install-macos-native.sh
```

## 2.0.0-beta.6

**Preview (beta) build of Network Optimizer 2.0 (with new Multi-Site support) for testers.** Pin the tag below - `:latest` stays on stable 1.x. Feedback welcome.

Beta.5 plus the below. Already on beta.5? No agent update needed, nothing changed on the agent. Coming from an earlier beta, update your site agents as beta.5 described.

## New in this beta

- **Transit route changes don't count against your access line** - When a transit or backbone network on your path goes fully unreachable for more than a few minutes, that's a routing (BGP) change, not your access line dropping packets. ISP Health now carves that window out of your access-layer Packet Loss and shows it as a path change on the timeline and RTT chart. The network's own health still reflects it; brief flaps and lossy-but-reachable transit still count as loss.
- **"That was me" on outages** - Mark your own maintenance (pulled the coax to add a splitter, unplugged a fiber to clean the connector, swapped gear) so it doesn't count against your ISP Health score. On each outage and its finding, with undo. Remembered per site.

## Also improved

- **Pull to refresh on ISP Health** - Pull down on the tab to recompute the scorecard instead of reloading the page.

## Fixes since beta.5

- **Mobile top bar** - Scrolling up reliably reveals it and keeps it visible.
- **Mobile site switcher** - No longer goes tap-dead after the top bar auto-hides.
- **ISP Health findings on mobile** - Cleaned up cramped, mislaid cards on narrow screens.

New to the 2.0 beta? See the [beta.5 notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v2.0.0-beta.5) for the Multi-Site overview.

## Installation

**Windows**: Download the MSI installer below

**Docker**: pin the beta tags in `docker-compose.yml` (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.6
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.6
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** - new install? Run the standard installer first, then pin the beta below:
```bash
bash -c "$(wget -qLO - https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```
Upgrade (new and existing). Beta upgrades migrate your database and can't roll back to stable 1.x, so snapshot the LXC first:
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && cp -n data/network_optimizer.db data/network_optimizer.db.pre-beta6 2>/dev/null; sed -i -E 's#(network-optimizer|speedtest):(latest|2\.0\.0-beta\.[0-9]+)#\1:2.0.0-beta.6#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.6 && ./scripts/install-macos-native.sh
```

## 2.0.0-beta.5

**This is a preview (beta) build of Network Optimizer 2.0 for testers.** Pin the tag below - do not use `:latest`, which stays on stable 1.x. The headline is Multi-Site, and there's plenty here for single-site users too. Feedback very welcome.

This build is beta.4 plus the changes below.

## Update your on-site agents with this release

This beta updates the agent's speed test web server with a new identity endpoint that Client Performance uses to recognize devices at remote sites, so update each site's agent alongside the server: the agent list flags outdated agents and shows the upgrade one-liner right next to the flag (or `docker compose pull && docker compose up -d` for Docker agents). This churn is a beta thing - after 2.0 ships, agent updates will be rare, and a built-in update system is planned.

## New in this beta

- **Client Performance works for devices at managed sites** - Opening Client Performance on a remote site used to dead-end at "Device Not Found", since the central server only ever sees the site's public IP. The page now asks the on-site agent who you are and lands straight on your device with full features (live signal, walk-test mapping, speed tests). If the agent can't answer (offline, or your browser hasn't trusted its certificate), you get a device picker instead, remembered per browser.
- **Telekom Glasfaser-Modem 2 ONT support** - Optical stats (TX/RX power, errors, uptime) for Telekom Germany's Glasfaser-Modem 2 in ONT Device Monitoring, verified on real hardware. Contributed by @Optic00 (#962) - thank you!
- **HTTPS retrofit for existing Proxmox installs** - New installs have offered automatic HTTPS (Traefik + Let's Encrypt) for a while; existing containers had no way to add it later. Run this on the Proxmox host and follow the prompts (needs a Cloudflare DNS API token):
```bash
bash -c "$(wget -qLO - https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/v2.0.0-beta.5/scripts/proxmox/add-https.sh)"
```

## Fixes since beta.4

- **Agent-run WAN speed test traces** - The path trace for a WAN test run at a remote site's agent either failed ("could not determine server position") or traced to a random device. It now traces from the agent through the site's own gateway and WAN, like the server test does at the main site.
- **ISP Health: outage break attribution rebuilt** - "Break upstream of X" could name a target that isn't on the traced path at all, an internet endpoint (everything is upstream of a destination), or a clean sibling transit branch while the loss sat elsewhere. Attribution now only anchors on trace-mapped path hops with everything nearer verified clean, names the lossy network's ASN when no clean boundary exists, and says "Path-wide" when the loss picture has no single culprit.
- **ISP Health: brief total outages no longer read "Partial loss"** - A short sharp outage that straddled detection bucket edges landed in the partial-loss pass and undersold itself. When the loss hit the blackout threshold on essentially every monitored hop, the event now reads "Total loss / Path-wide total loss".
- **ISP Health: coalesced outages read whole-WAN correctly** - An outage window padded by gap-bridging could dilute every hop's dark time below the attribution threshold, so an everything-went-dark event claimed a break "upstream of" the deepest hop. Darkness is now measured against the outage's own dark span, immune to padding.
- **Agent WAN test progress text** - The status line under the progress bar during an agent-run WAN test just repeated the progress bar's own label, so it's gone. The result summary still appears when the test completes.

## What's New in 2.0

- **Multi-Site** - Manage multiple networks from one Network Optimizer. Each site is fully isolated: its own database, monitoring, speed tests, alerts, threat intelligence, and UniFi Console connection. Turn it on under **Settings > Multi-Site**.
- **Agent-backed remote sites** - Add a site on another network by running a lightweight on-site agent that tunnels back to your main instance. Gateway/device SSH, modem and ONT status, WAN and LAN speed tests, SNMP and custom OID polling, path analysis, and Network Tools probes all work - no VPN, no port forwarding. A guided wizard handles enrollment.
- **Per-site everything** - Monitoring, ISP Health, alerts and digests, threat intelligence, path analysis, and InfluxDB buckets are all scoped per site.

## Also improved for everyone (single-site too)

- **Settings reorganized into tabs** - Connection, Monitoring, Speed Tests, Security & Alerts, Application, Multi-Site.
- **Network Tools** - TCP ping does a real TCP connect from gateway and device vantages; friendlier vantage labels.
- **WAN Speed Test** - The gateway (direct) test raises completion and degradation alerts.

## Trying this preview

Pin the beta tag - do not use `:latest`, which stays on stable 1.x. When 2.0 ships for real, switch back to `:latest` to rejoin the stable track. Multi-site is off by default, so your single-site experience is unchanged until you enable it.

## Installation

**Windows**: Download the MSI installer below

**Docker**: edit your `docker-compose.yml` to pin the beta tags (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.5
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.5
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** - new install? Run the standard installer first (creates the LXC on stable, with optional automatic HTTPS), then pin the beta with the one-liner below:
```bash
bash -c "$(wget -qLO - https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```
Upgrade to the beta (new and existing installs - best-effort backs up the database, rewrites the compose tags, then pulls). Beta upgrades migrate your database and can't be rolled back to stable 1.x, so existing installs should snapshot the LXC first:
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && cp -n data/network_optimizer.db data/network_optimizer.db.pre-beta5 2>/dev/null; sed -i -E 's#(network-optimizer|speedtest):(latest|2\.0\.0-beta\.[0-9]+)#\1:2.0.0-beta.5#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.5 && ./scripts/install-macos-native.sh
```

When 2.0 ships for real, switch back to the stable track: Docker/Proxmox rewrite the image tags back to `:latest`; macOS `git checkout main && git pull && ./scripts/install-macos-native.sh`.

## 2.0.0-beta.4

**This is a preview (beta) build of Network Optimizer 2.0 for testers.** Pin the tag below - do not use `:latest`, which stays on stable 1.x. The headline is Multi-Site, and there's plenty here for single-site users too. Feedback very welcome.

This build is beta.3 plus the fixes below.

## Update your on-site agents with this release

This beta fixes agent-side bugs, so update each site's agent alongside the server: the agent list flags outdated agents and now shows the upgrade one-liner right next to the flag (or `docker compose pull && docker compose up -d` for Docker agents). This churn is a beta thing - after 2.0 ships, agent updates will be rare, and a built-in update system is planned.

## Fixes since beta.3

- **Agents now survive extended server downtime** - If the central server's host was powered off long enough (think hardware maintenance), agents stopped retrying entirely and sat "running" but disconnected until manually restarted: a timed-out heartbeat was mistaken for a shutdown signal. Agents now keep retrying every ~30 seconds for as long as the outage lasts and reconnect promptly when the server comes back.
- **False packet loss when an agent restarts** - Stopping or updating an on-site agent killed its in-flight pings, and the agent reported them as real packet loss before shutting down - planting a loss spike on the site at every agent update. The agent now shuts down cleanly and discards in-flight probes; stops are also instant instead of hanging for 90 seconds.
- **Upgrade one-liner in the UI** - The "Update agent" flag in Settings > Multi-Site now shows the copyable upgrade command (enrollment is preserved; only the binaries update).
- **Smarter transit hop selection in Upstream Discovery** - When a transit network appears twice in your path (ingress near you, egress on the far side), discovery now auto-selects the lowest-latency reachable hop in each run instead of just the first hop it saw - so ISP Health can tell which end of a transit network is misbehaving.
- **ISP Health speed test load failures are now logged** - If ISP Health can't read your WAN speed test history (for example database contention right after a restart), the Speed vs Plan card could claim "no recent tests" until the next recompute even though tests exist. The failure now logs a warning so it's diagnosable; a fuller fix distinguishing "couldn't read" from "none exist" is planned.

## What's New in 2.0

- **Multi-Site** - Manage multiple networks from one Network Optimizer. Each site is fully isolated: its own database, monitoring, speed tests, alerts, threat intelligence, and UniFi Console connection. Turn it on under **Settings > Multi-Site**.
- **Agent-backed remote sites** - Add a site on another network by running a lightweight on-site agent that tunnels back to your main instance. Gateway/device SSH, modem and ONT status, WAN and LAN speed tests, SNMP and custom OID polling, path analysis, and Network Tools probes all work - no VPN, no port forwarding. A guided wizard handles enrollment.
- **Per-site everything** - Monitoring, ISP Health, alerts and digests, threat intelligence, path analysis, and InfluxDB buckets are all scoped per site.

## Also improved for everyone (single-site too)

- **Settings reorganized into tabs** - Connection, Monitoring, Speed Tests, Security & Alerts, Application, Multi-Site.
- **Network Tools** - TCP ping does a real TCP connect from gateway and device vantages; friendlier vantage labels.
- **WAN Speed Test** - The gateway (direct) test raises completion and degradation alerts.

## Trying this preview

Pin the beta tag - do not use `:latest`, which stays on stable 1.x. When 2.0 ships for real, switch back to `:latest` to rejoin the stable track. Multi-site is off by default, so your single-site experience is unchanged until you enable it.

## Installation

**Windows**: Download the MSI installer below

**Docker**: edit your `docker-compose.yml` to pin the beta tags (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.4
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.4
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** (upgrade an existing LXC install - best-effort backs up the database, rewrites the compose tags, then pulls). Beta upgrades migrate your database and can't be rolled back to stable 1.x, so snapshot the LXC first:
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && cp -n data/network_optimizer.db data/network_optimizer.db.pre-beta4 2>/dev/null; sed -i -E 's#(network-optimizer|speedtest):(latest|2\.0\.0-beta\.[0-9]+)#\1:2.0.0-beta.4#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.4 && ./scripts/install-macos-native.sh
```

When 2.0 ships for real, switch back to the stable track: Docker/Proxmox rewrite the image tags back to `:latest`; macOS `git checkout main && git pull && ./scripts/install-macos-native.sh`.

## 2.0.0-beta.3

**This is a preview (beta) build of Network Optimizer 2.0 for testers.** Pin the tag below - do not use `:latest`, which stays on stable 1.x. The headline is Multi-Site, and there's plenty here for single-site users too. Feedback very welcome.

This build is beta.2 plus the fixes below.

## Update your on-site agents with this release

This beta changes the agent tunnel contract, so update each site's agent alongside the server: re-run the install one-liner from **Settings > Multi-Site > (site) > Agents**, or `docker compose pull && docker compose up -d` for Docker agents. The agent list now flags agents running an older release. This churn is a beta thing - after 2.0 ships, agent updates will be rare, and a built-in update system is planned.

## Fixes since beta.2

- **Port Statistics "Client" column on managed sites** - The agent never relayed the SNMP interface index needed to correlate switch ports, leaving the column empty. Fixed.
- **Phantom gateway ports** - Virtual interfaces could claim real port numbers and names, showing duplicate port rows on gateways. Fixed, and old bad rows heal themselves after upgrading.
- **Client column in playback** - Scrubbing Port Statistics back in time now shows which client was on which port. History from before this release has no port data, so it fills from upgrade time.
- **UI freeze switching to a site whose agent is down** - Console calls now fail fast into the "waiting for the agent" state instead of hanging pages for a minute-plus, and reconnect the moment the agent returns.
- **Monitoring charts after a console outage** - Charts on the Monitoring page stayed blank once the console (re)connected until you switched tabs. They now load on their own.
- **Optical (SFP / ONT) tables blank after a restart** - The live readings grid now warms itself from recorded data at startup instead of waiting minutes for the next polling cycle.
- **Site status indicators disagreed** - The site picker, All Sites page, and Multi-Site settings each had their own stale idea of agent status. All now share one live, tunnel-driven definition.
- **WAN speed tests on agentless managed sites** - The test buttons and links now explain the site's agent is required instead of silently measuring or recording against the wrong network.
- **2D LAN map fullscreen** - Fixed fullscreen not expanding the 2D topology map.
- **Monitoring chart polish** - Tooltips on the RTT, Network Performance, and Device Health charts sort by value to match the line order and no longer clip; compacter filter badges and spacing tweaks throughout.
- **Monitoring deep links before setup** - Now land on Setup instead of an empty page.

## What's New in 2.0

- **Multi-Site** - Manage multiple networks from one Network Optimizer. Each site is fully isolated: its own database, monitoring, speed tests, alerts, threat intelligence, and UniFi Console connection. Turn it on under **Settings > Multi-Site**.
- **Agent-backed remote sites** - Add a site on another network by running a lightweight on-site agent that tunnels back to your main instance. Gateway/device SSH, modem and ONT status, WAN and LAN speed tests, SNMP and custom OID polling, path analysis, and Network Tools probes all work - no VPN, no port forwarding. A guided wizard handles enrollment.
- **Per-site everything** - Monitoring, ISP Health, alerts and digests, threat intelligence, path analysis, and InfluxDB buckets are all scoped per site.

## Also improved for everyone (single-site too)

- **Settings reorganized into tabs** - Connection, Monitoring, Speed Tests, Security & Alerts, Application, Multi-Site.
- **Network Tools** - TCP ping does a real TCP connect from gateway and device vantages; friendlier vantage labels.
- **WAN Speed Test** - The gateway (direct) test raises completion and degradation alerts.

## WAN speed tests on managed sites

- **Start from the site's agent** - The WAN Speed Test page on an agent-backed site links through the on-site agent (`https://<agent>:3000/wan/`), which forwards to your external test server. Results land in the right site, attributed to the client device's LAN IP - no site parameter in any URL. Picking a non-default server routes through `/wan/<server-id>/` automatically.

## Agent improvements

- **Update callout** - Settings > Multi-Site > Configuration > Agents flags agents running an older release.
- **Plain-HTTP opt-out** - Set `AGENT_SPEEDTEST_TLS=0` to serve the agent's LAN speed test over HTTP instead of self-signed TLS (for sites behind their own reverse proxy). LAN tests only - the WAN post-back needs HTTPS. Details in the agent README.
- **Clearer speed test override** - The per-site override field shows the auto-detected agent address as its placeholder, with a gear-icon shortcut from the speed test banner. SFP module codes show their vendor on hover.

## Windows (MSI)

- **Agent tunnel out of the box** - The bundled Traefik config now routes the multi-site agent tunnel, so remote agents can enroll against a Windows-hosted server without manual reverse-proxy work.

## Trying this preview

Pin the beta tag - do not use `:latest`, which stays on stable 1.x. When 2.0 ships for real, switch back to `:latest` to rejoin the stable track. Multi-site is off by default, so your single-site experience is unchanged until you enable it.

## Installation

**Windows**: Download the MSI installer below

**Docker**: edit your `docker-compose.yml` to pin the beta tags (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.3
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.3
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** (upgrade an existing LXC install - best-effort backs up the database, rewrites the compose tags, then pulls). Beta upgrades migrate your database and can't be rolled back to stable 1.x, so snapshot the LXC first:
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && cp -n data/network_optimizer.db data/network_optimizer.db.pre-beta3 2>/dev/null; sed -i -E 's#(network-optimizer|speedtest):(latest|2\.0\.0-beta\.[0-9]+)#\1:2.0.0-beta.3#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.3 && ./scripts/install-macos-native.sh
```

When 2.0 ships for real, switch back to the stable track: Docker/Proxmox rewrite the image tags back to `:latest`; macOS `git checkout main && git pull && ./scripts/install-macos-native.sh`.

## 2.0.0-beta.2

**This is a preview (beta) build of Network Optimizer 2.0 for testers.** Pin the tag below - do not use `:latest`, which stays on stable 1.x. The headline is Multi-Site, and there's plenty here for single-site users too. Feedback very welcome.

This build is beta.1 plus the fixes below.

## Fixes since beta.1

- **Alerts now name their site** - Notifications from a managed (agent-backed) site were indistinguishable from your main site: no site name, and the "View" link ignored the site. Delivered alerts now carry the site name and a link that takes you straight to that site.
- **Roaming failures rated by success rate** - The roaming-failures health issue flagged any AP pair with a single failed roam and escalated on the raw count, so busy links looked broken. It now fires only when the roam success rate drops below 95% (critical below 90%).
- **Site switcher lands on the dashboard** - Switching sites via the nav bar site picker while on the All Sites overview now takes you to the new site's dashboard instead of reloading the All Sites list, and nav-ing to a site from an alert link no longer gets you stuck on the linked site.
- **Fixed a reconnect crash loop** - A console reconnect could throw a dispatcher error that crash-looped the app on several pages (Wi-Fi, Dashboard, Adaptive SQM, Monitoring). Reconnects now refresh cleanly.

## What's New

- **Multi-Site** - Manage multiple networks from one Network Optimizer. Each site is fully isolated: its own database, monitoring, speed tests, alerts, threat intelligence, and UniFi Console connection. Turn it on under **Settings > Multi-Site**.
- **Agent-backed remote sites** - Add a site on a different network by running a lightweight on-site agent that tunnels back to your main instance. Once connected, that remote site's gateway and device SSH, cable modem / ONT status, WAN and LAN speed tests, SNMP and custom OID polling, path analysis, and Network Tools probes all work - no VPN, no port forwarding. A guided wizard walks you through enrollment.
- **Per-site everything** - Monitoring, ISP Health, alerts and digests, threat intelligence, path analysis, and InfluxDB buckets are all scoped per site, so one site's data never bleeds into another.

## Also improved for everyone (single-site too)

- **Settings reorganized into tabs** - Connection, Monitoring, Speed Tests, Security & Alerts, Application, and Multi-Site.
- **Network Tools** - TCP ping now does a real TCP connect to the port (instead of silently falling back to ICMP) from gateway and device vantages; friendlier vantage labels; ping limited to the modes that make sense.
- **WAN Speed Test** - The gateway (direct) test now raises completion and degradation alerts, with a smoother progress animation.
- **Polish** - MaxMind GeoIP gets its own Settings card; the pre-setup ISP Health tile links to Upstream Discovery.

## Trying this preview

Pin the beta tag - do not use `:latest`, which stays on stable 1.x. When 2.0 ships for real, switch your image back to `:latest` to rejoin the stable track. Multi-site is off by default, so your single-site experience is unchanged until you enable it.

## Installation

**Windows**: Download the MSI installer below

**Docker**: edit your `docker-compose.yml` to pin the beta tags (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.2
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.2
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** (upgrade an existing LXC install to the beta - rewrites the compose tags, then pulls):
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && sed -i -E 's#(network-optimizer|speedtest):latest#\1:2.0.0-beta.2#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.2 && ./scripts/install-macos-native.sh
```

When 2.0 ships for real, switch back to the stable track: Docker/Proxmox rewrite the image tags back to `:latest`; macOS `git checkout main && git pull && ./scripts/install-macos-native.sh`.

## 2.0.0-beta.1

**This is a preview (beta) build of Network Optimizer 2.0 for testers.** Pin the tag below - do not use `:latest`, which stays on stable 1.x. The headline is Multi-Site, and there's plenty here for single-site users too. Feedback very welcome.

## What's New

- **Multi-Site** - Manage multiple networks from one Network Optimizer. Each site is fully isolated: its own database, monitoring, speed tests, alerts, threat intelligence, and UniFi Console connection. Turn it on under **Settings > Multi-Site**.
- **Agent-backed remote sites** - Add a site on a different network by running a lightweight on-site agent that tunnels back to your main instance. Once connected, that remote site's gateway and device SSH, cable modem / ONT status, WAN and LAN speed tests, SNMP and custom OID polling, path analysis, and Network Tools probes all work - no VPN, no port forwarding. A guided wizard walks you through enrollment.
- **Per-site everything** - Monitoring, ISP Health, alerts and digests, threat intelligence, path analysis, and InfluxDB buckets are all scoped per site, so one site's data never bleeds into another.

## Also improved for everyone (single-site too)

- **Settings reorganized into tabs** - Connection, Monitoring, Speed Tests, Security & Alerts, Application, and Multi-Site.
- **Network Tools** - TCP ping now does a real TCP connect to the port (instead of silently falling back to ICMP) from gateway and device vantages; friendlier vantage labels; ping limited to the modes that make sense.
- **WAN Speed Test** - The gateway (direct) test now raises completion and degradation alerts, with a smoother progress animation.
- **Polish** - MaxMind GeoIP gets its own Settings card; the pre-setup ISP Health tile links to Upstream Discovery.

## Trying this preview

Pin the beta tag - do not use `:latest`, which stays on stable 1.x. When 2.0 ships for real, switch your image back to `:latest` to rejoin the stable track. Multi-site is off by default, so your single-site experience is unchanged until you enable it.

## Installation

**Windows**: Download the MSI installer below

**Docker**: edit your `docker-compose.yml` to pin the beta tags (since `:latest` stays on stable), then pull:
```yaml
image: ghcr.io/ozark-connect/network-optimizer:2.0.0-beta.1
image: ghcr.io/ozark-connect/speedtest:2.0.0-beta.1
```
```bash
docker compose pull && docker compose up -d
```

**Proxmox** (upgrade an existing LXC install to the beta - rewrites the compose tags, then pulls):
```bash
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && sed -i -E 's#(network-optimizer|speedtest):latest#\1:2.0.0-beta.1#' docker-compose.yml && docker compose pull && docker compose up -d"
```

**macOS** (native):
```bash
cd NetworkOptimizer && git fetch --tags && git checkout v2.0.0-beta.1 && ./scripts/install-macos-native.sh
```

When 2.0 ships for real, switch back to the stable track: Docker/Proxmox rewrite the image tags back to `:latest`; macOS `git checkout main && git pull && ./scripts/install-macos-native.sh`.

## 1.24.2

More refinements to ISP Health and the Wi-Fi Channel Optimizer. See [v1.24.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.24.0) for what's new in v1.24.0+.

## Monitoring: ISP Health

- **Optical readings survive a transient glitch** - The Physical Link score reads a fiber ONT's optical power (GPON and XGS-PON), where a single bad reading could briefly ding a healthy link. It now grades receive and transmit power over the whole window instead of one sample, and compensates receive power for temperature (an optic reads a little lower when it runs cool, higher when warm). A brief thermal swing no longer looks like a signal drop, but a genuine dip still gets flagged.
- **Brief WAN load is recognized as load** - A congestion event that lined up with a short download or a quick speed test was being reported as external congestion instead of "under heavy WAN load." Short bursts of local saturation are now recognized, so they get labeled correctly. Sustained events are unchanged.
- **Congestion rows show the real latency rise** - A congestion row could show a near-zero latency/jitter change that didn't match what actually happened. Rows now use the affected hop's own numbers, so you see its real rise. Display only; scoring is unchanged.
- **Outages split by a monitoring gap are stitched together** - An outage with a gap in the middle of monitoring could show up as two separate events. They now merge into the single outage they really were.

## Wi-Fi Channel Optimizer

- **The optimizer now has a memory** - Channel Recommendations learn from the channels you've actually run and the neighbors it has actually seen, instead of judging every candidate on a single live snapshot. Each channel's real-world performance (utilization, interference, TX retries) is recorded per radio and kept for months, well past the UniFi Console's short retention, with older evidence aging out. Remembered neighbors are weighted by how consistently they show up, so a one-off guest hotspot can't pile up into load a channel never carried. Works on all bands but bites hardest on noisy 2.4 GHz, where a single scan could otherwise talk the optimizer into a confident but pointless swap.
- **No ping-ponging after a channel change** - Once a radio moves, the channel it just left is held out of recommendations for a 16-hour soak, long enough for a real evening peak to prove out the new channel. If the new channel turns out genuinely catastrophic (70%+ of airtime from other networks), the soak lifts so a bad move can be corrected. A "Soaking" badge shows which APs are in their soak window and until when.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.24.1

Expanding the timeline history to 90 days, locking down noisy 2.4 GHz channel churn, and rolling out massive performance and timeout fixes for ISP Health on lower-power hardware. See [v1.24.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.24.0) for what's new in v1.24.0+.

## What's New

* **Extended Live View timeline history** - Unlocked the scrubber from its 24-hour limit. You can now select presets up to 30 days and Max (the 90-day retention cap), using a server-side cache so younger installs cleanly clamp to their actual data duration.
* **Smarter 2.4 GHz optimization** - Raised the bar for channel moves on the crowded 2.4 GHz band. The optimizer now requires an 8% whole-site score improvement (up from 3%) before recommending a change, stopping zero-sum channel churn.
* **Adaptive ISP Health fallback** - Low-power boxes and spinning disks no longer hang on heavy computations. The engine now automatically scales back the evaluation window ($48\text{h} \to 24\text{h} \to 16\text{h}$) if a step exceeds the time budget.

## Wi-Fi Optimizer

* **Surfaced scan permission errors** - Read-only accounts no longer fail silently or loop through re-authentication. The UI now catches the 403 error immediately and prompts you to grant the account the Network: Site Admin role.
* **Streamlined scan button and UI** - Condensed the wordy scan banner into a single line, moving details to a tooltip. The scan button now stretches full-width on mobile and shows live per-band progress (e.g., "Scanning… 2/3 bands").
* **Updated connection guidance** - Changed the setup instructions in Settings to recommend Network: Site Admin, adding a note that View Only covers everything except on-demand RF scans.

## Monitoring

### ISP Health

* **5x faster computations** - Optimized in-memory hot paths to prevent timeouts on 30-day windows. The engine now precomputes indexes, sorts series exactly once instead of 4 to 5 times, and skips per-bucket object allocations. Output remains bit-identical.
* **Adaptive fallback badges** - Added a small badge next to the date selector when the compute window has been auto-reduced. Hovering explains why, and clicking it re-probes the full target window.
* **Fixed InfluxDB query timeouts** - Raised the default query timeout past the compute budget, fixing a bug where heavy database reads were canceled mid-flight (#941).
* **Hero loading states** - Changing time windows, refreshing, or switching access technology now shows a styled loading spinner in the score area instead of sticking on stale numbers.

### Network Performance

* **Pooled loss percentage investigation** - Modified the Latency & Packet Loss "Investigate" highlight band to show the pooled mean loss across the exact target definitions used to grade the score, eliminating data drift.

## Fixes

* **2D Map Mobile Scrubber** - Fixed a layout bug to ensure the mobile timeline scrubber renders correctly beneath the 2D canvas area.
* **Congestion timeline phrasing** - Gated the phrase "and the hops beyond" strictly on a placed bottleneck hop, preventing unlocalized events without saved traces from using intermediate hop phrasing.

## Installation

**Windows**: Download the MSI installer below

**Docker**:

```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):

```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:

```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.24.0

Bringing measured RF spectrum into the Channel Optimizer, deeper ISP Health investigation tools, and a round of accuracy fixes across Wi-Fi and Monitoring. See [v1.23.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.23.0) for the bigger picture.

## What's New

- **Channel Optimizer now measures real RF** - Channel recommendations factor in UniFi's per-channel spectrum scan (actual airtime and RF noise floor), not just neighbor network and historic AP airtime metric data, with on-demand scans when a radio has no recent measurement. See below for the full writeup.
- **ISP Health Physical Link factor** - ISP Health grades the actual health of your WAN's connection medium (fiber ONT optical power, DOCSIS SNR/FEC/power, or cellular signal) and folds it into the Access Layer score. (v1.23.4)
- **Smarter outage scoring** - Outages score by severity, recurrence, and time of day, not just total duration, with the heavy-vs-idle profile derived automatically from recorded throughput. (v1.23.4)
- **Re-pair Uplink for mesh APs** - A per-AP button that nudges a stuck wireless mesh child to re-roam to its strongest available parent, now working across the U6 and U7 lines. (v1.23.3, v1.23.4)
- **Upstream Discovery fallback** - When no first-mile hop inside your ISP answers ICMP, discovery falls back to a curated reachable ISP speed-test endpoint so the access-ISP cloud still resolves. (v1.23.2)
- **Performance Tweaks on UniFi OS 5.1.21** - Validated up to UniFi OS 5.1.21 on the UCG-Fiber, plus a module-update banner when a deployed gateway module has a newer version. (v1.23.1, v1.23.2)
- **Fixed Netgear CM700 support** - Netgear modems that emit malformed HTTP (the CM700 is the usual culprit) now report their DOCSIS status via a lenient reader. (v1.23.1)

## Wi-Fi Optimizer

- **Measured RF spectrum in scoring** - Recommendations now use actual airtime utilization and RF noise floor from UniFi's spectrum scan. A channel that looks quiet by neighbor network and historic AP airtime metric data but is noisy in RF (radar, microwaves, other non-Wi-Fi interference, or hidden congestion) is now correctly penalized. Wide channels are aggregated across their whole span the way UniFi's own wide-channel scan does, and an AP's current channel is read from a neighbor's vantage so it isn't penalized for traffic that follows it wherever it moves. (#940)
- **Span-aware neighbor influence** - A wide neighbor's full spectral footprint now counts against every channel it overlaps, instead of only its control channel, so a nearby 160 MHz network is scored against its whole span. (#940)
- **On-demand RF scans** - When a radio has no recent spectrum measurement, the recommendation page prompts you to run a quick scan on exactly those radios, then re-runs on the fresh data. Scans run at each radio's current bandwidth, one band at a time per AP and in parallel across APs. Mesh APs are excluded (they can't scan without dropping their uplink), and the wording adapts to each AP's scan hardware. (#940)
- **Safer, more honest recommendations** - The engine never recommends a plan that would worsen the overall network score, per-AP fallback moves are judged on the real network objective, and DFS handling gets a span-aware penalty, a badge on the current channel, and friction when leaving DFS for unscanned channels. (#940)
- **DFS toggle defaults from your console** - The 5 GHz DFS toggle now defaults to match your UniFi Console's Auto-Optimize (RF Scanning) setting instead of always starting on Include DFS. Once you pick an option yourself, your choice is preserved. (#937)

## Monitoring

### ISP Health

- **Investigate links on loss findings** - The "Packet loss under load" and "Packet loss above acceptable" findings now link straight to the matching event on the Network Performance charts, so you can confirm which series drove the finding. (#938)
- **Anycast DNS on the Per-Network RTT chart** - Cloudflare (1.1.1.1) and Google (8.8.8.8) now plot as their own lines, giving a known-good baseline to read a noisy ISP or transit hop against. (#938)
- **Smarter loss advice** - Persistent-loss recommendations now name oversubscription alongside physical-plant faults on shared media, stay physical-layer-only on dedicated media, and defer to Adaptive SQM's own tuning knobs when it's already shaping the WAN. (#938)
- **DOCSIS 3.1/4.0 label** - The Physical Link RF-health description reads "DOCSIS 3.1/4.0" when OFDMA is detected, since OFDMA alone doesn't distinguish 3.1 from 4.0. (#939)
- **WoodyNet / PCH excluded from Transit** - IXP route-server and anycast DNS infrastructure no longer lands in the Transit dimension, since it doesn't haul traffic upstream. (#939)
- **Branded loading spinner** - The initial load now shows a centered loading state that matches the ISP Health hero card instead of a tiny left-aligned spinner. (#939)
- **Re-score by access technology** - You can select the connection's access technology to re-score, and the Physical Link subheader links to its monitoring tab.

### Network Performance

- **Event-based loss investigation** - Stepping through Packet Loss / Loaded Loss events now coalesces contiguous loss minutes into distinct events and steps event-to-event (landing on each event's peak-loss minute), with the investigated event highlighted by a labeled band. The Investigate card moved above the chart and is now collapsible with a saved state. (#938)

## Client WAN Speed Test

- **Steadier charts** - Charts refresh after a new result and only re-render when results actually change.

## Fixes

- **Visited links keep their color** - Dropped a global `a:visited` override so visited links no longer fade into body text.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.23.4

This release deepens ISP Health with a new Physical Link factor and a smarter outage score, plus a cross-platform fix for the Wi-Fi mesh Re-pair Uplink action. See [v1.23.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.23.0) for what's new in v1.23.0+.

## Monitoring

### ISP Health

- **New Physical Link factor** - ISP Health now grades the actual health of your WAN's connection medium and folds it into the Access Layer score. It automatically matches your connection's access technology and grades the real signal: fiber ONT optical power (PON or active Ethernet, via SFP DDM or an external ONT), DOCSIS cable (downstream SNR/MER, FEC, and power levels), or cellular signal quality. If there's no monitored source for that WAN, the factor is simply left out: no penalty, no free points. When more than one source could match, you choose which one.
- **Smarter outage scoring** - Outages now score by severity, recurrence, and time of day, not just total duration. A widespread near-total drop reads hotter than a narrow shallow one, ten separate micro-drops cost far more than one slightly-longer dip, and a drop during your heavy-usage hours counts in full while one at a typically-idle hour dings less. The heavy-vs-idle profile is derived automatically from throughput already being recorded, so there's nothing to set up.

### ONT Monitoring

- **8311 ONT error counters** - SFP ONT sticks running 8311 firmware now have their FEC and BIP error counts read from the pontop page, feeding the fiber Physical Link score.

## Wi-Fi Optimizer

- **Re-pair Uplink works across more access points** - The mesh Re-pair Uplink action was tuned for the U7 line and failed on others (notably the U6 line) with "Couldn't read the mesh backhaul status." It now adapts to each AP's wpa_supplicant socket layout, so it works across platforms.

## Device Status

- **Provisioning devices no longer show as Offline** - A device that's reprovisioning, updating, adopting, or pending now shows an accurate status (a yellow "Provisioning" or "Updating") instead of grey "Offline." This applies to the Dashboard Device Status list, the Wi-Fi Optimizer AP cards, and the Client Speed Test device list. A device mid-reprovision is also no longer briefly dropped from monitoring and speed-test target lists.

## Alerts & Schedule

- **Device event reference completed** - The Device Health group now lists every device event (offline, high temperature, gateway CPU, gateway memory), and `device.offline` is grouped with them instead of being stranded under Schedule.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.23.3

One-click function to roam a stuck mesh AP to its strongest parent, plus accurate mesh channel width, and a UDM gateway temperature monitoring fix. See [v1.23.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.23.0) for what's new in v1.23.0+

## Wi-Fi Optimizer

- **Re-pair Uplink for mesh APs** - A new per-AP button that re-scans a wireless mesh child's backhaul so it reconnects to its strongest available parent. Mesh children often get stuck on a weaker parent after you reconfigure the parent or after a firmware upgrade, and don't re-roam on their own; this nudges them to. It only prompts the scan (UniFi Network still decides which parents are eligible), is safe to re-run, and reports whether the AP actually moved.
- **Accurate mesh channel width** - The radio panel now shows the width a mesh backhaul is actually running at, not just the configured width. An AP set to 160 MHz but negotiated down to its parent's 80 MHz now correctly reads 80 MHz.

## Signal Map

- **Map frames to your real layout** - The Signal Map and floor plan editor now fit the view to your actual placed content (APs, drawn walls, floors with an uploaded image) instead of being dragged off to a default location by a brand-new building or floor that hasn't been positioned yet. New buildings and floors are also seeded wherever you've got the map pointed rather than at a fixed default.

## Monitoring

- **Gateway temperature when SNMP is quiet** - Some gateways (like the UDM family) report CPU and memory over SNMP but not temperature. Gateway temperature now falls back to UniFi Network data when SNMP leaves it out, while gateways that do report it over SNMP are left untouched.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.23.2

This release sharpens the Wi-Fi Optimizer's channel recommendations and broadens Upstream Discovery so it can still map your ISP even when its first-mile routers stay silent to pings. See [v1.23.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.23.0) for what's new in v1.23.0+.

## Wi-Fi Optimizer

- **Signal Map framing** - The map no longer zooms out to the whole globe when a floor or AP was created but never placed; un-positioned items are excluded from the map fit.
- **Better co-channel detection** - Two APs on different control channels that share the same bonding block (e.g. 100/160 and 112/160) are now correctly scored as fully co-channel.
- **Mesh-aware recommendations** - Mesh children stay pinned to their leader's channel through the whole recommendation flow, so suggested plans are always physically valid for the backhaul.
- **More accurate channel scoring** - Airtime contention and raw utilization are now scored separately instead of as one lumped penalty.

## Monitoring

- **Upstream Discovery: ISP test-server fallback** - When no first-mile hop inside your ISP's own network answers ICMP, discovery now falls back to a curated, reachable ISP speed-test endpoint so the access-ISP cloud still resolves on the map. Currently covers Deutsche Telekom, T-Mobile / T-Mobile Fiber, and Spectrum (Charter). Discovery also counts as complete when the path is proven through transit alone. If your ISP also exposes no pingable access-network hops, open an Issue and we'll try to add fallback targets for it.
- **WAN globes** - A down WAN now reports zero throughput instead of inheriting the gateway's aggregate rate, unused WANs are hidden, and labels and discovery messaging are clearer.
- **Flex 2.5G latency probing** - Flex 2.5G switches are re-asserted as disabled latency targets on every reconcile, so a target missed during an offline or reconnect window self-heals once the model resolves.
- **Custom OID discovery** - The Setup tab's device card is now "SNMP Devices and Custom OIDs" and auto-expands the first device once, so custom OID polling is easier to find.

## Performance Tweaks

- **Lighter MongoDB eMMC backups** - The MongoDB SSD-offload backup now keeps a single compressed archive on eMMC instead of an uncompressed copy, with a one-time migration. Your console's stock boot failsafe is untouched.
- **Module update banner** - A banner now surfaces when a deployed gateway module (WAN Steering, Adaptive SQM, Performance Tweaks) has a newer version available.

## Alerts & Schedule

- **Bulk incident actions** - New "Acknowledge All" and "Resolve All" actions handle the whole incident list at once.
- **Easier speed test scheduling** - "Add Test" buttons and helper text make it clear you can schedule a separate test for each WAN line or device.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.23.1

Performance Tweaks unlocked on UniFi OS 5.1.21, plus steadier upstream change detection, fixed Netgear CM700 support, and a smarter WAN Steering redeploy prompt. See [v1.23.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.23.0) for what's new in v1.23.0.

## ISP Health

- **Steadier upstream change detection** - Scheduled re-discovery now compares your upstream on stable per-ASN identity instead of exact hop IPs, so normal ECMP hop shuffling no longer looks like a change. A hop has to go missing for three runs in a row before it's flagged as removed, and once something's pending the recheck happens daily so a real change confirms in days instead of weeks.
- **Results-ready banner** - When a scheduled re-discovery finds your path changed, a dismissable banner now appears on the Live View and Network Performance tabs so you can review and update your targets. It re-arms on its own if the next run finds something new.
- **Manual targets stay put** - Transit and Access ISP targets you add by hand are now treated as curated, so re-discovery won't flag them as removed or keep suggesting them back.
- **Scheduled runs match manual ones** - The background scheduler now carries your saved access technology forward, so an automatic re-discovery infers roles and reachability exactly the way a run you kick off yourself does.

## Cable Modems

- **Netgear modems that emit malformed HTTP** - Some Netgear modems (the CM700 is the usual culprit) intermittently send slightly corrupted HTTP that .NET refuses to parse, even though browsers read it fine. We now fall back to a lenient reader on exactly that failure so these modems report their DOCSIS status. Modems that behave normally are untouched.

## WAN Steering

- **Only nag when the daemon actually changed** - The "binary outdated, redeploy" prompt now tracks the daemon's behavior version rather than the app version, so it only shows up when redeploying would actually change something, not after every release. One heads-up: on Mac, Windows, and Linux bare-metal installs you'll see the prompt once after updating. Do a single WAN Steering deploy to push the version-aware binary and it stays clear from then on.

## Performance Tweaks

- **UniFi OS 5.1.21 support** - Performance tweaks are now validated up to UniFi OS 5.1.21 on the UCG-Fiber.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.23.0

Smarter Wi-Fi channel planning, configurable temperature and SFP alert thresholds, and a round of ISP Health improvements. See [v1.22.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.22.0) for the bigger picture.

## What's New

- **Address search on maps** - Search an address to jump there on the Speed Test and Signal maps, with zoom improvements. (#887, #888)
- **Satellite imagery toggle** - Switch the maps between street and satellite views. (#888)
- **More cable modem support** - Added the Netgear CM2050V, plus a CM700 auth fix for gateways that need an anti-CSRF cookie primed. (#883, #881)
- **More accurate ISP Health** - Loaded latency and loss now align with WAN rate windows, and brief loaded-event edges are captured via window dilation. (#875, #882)
- **Threat Intelligence accuracy** - Disabled port-forwarding rules are no longer counted as exposure. (#886)
- **Adaptive SQM** - Stopped flagging the firmware regression on gateways that are already patched. (#884)

## Wi-Fi Optimizer

- **Smarter channel recommendations** - Fixes and improvements to the physical interference model behind channel planning, with better per-AP channel moves. (#890)
- **Stable suggestions between scans** - Marginal channel suggestions no longer flicker on and off as conditions shift slightly between scans. (#893)
- **Overview auto-refresh** - The Overview tab refreshes itself when its data goes stale instead of showing old numbers until a manual reload. (#895)

## Monitoring

- **Configurable temperature and SFP alert thresholds** - Switch and gateway high-temperature alerts are now configurable per device type (Monitoring -> Device Stats), and the per-transceiver-type SFP thresholds (PON / Active Ethernet / generic SFP+) are editable (Monitoring -> SFP Stats) instead of hard-coded. Each falls back to the built-in default when unset. (#894)
- **ISP Health improvements** - Detects brief and partial-loss disruptions, more accurate congestion scoring, a clearer timeline, and faster data loading (initial load and when switching tabs). (#891)

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.22.3

By request, satellite imagery and a smarter address search for the Wi-Fi Optimizer maps. See [v1.22.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.22.0) for what's new in v1.22.0+

## Wi-Fi Optimizer: Signal & Speed Maps

### Satellite imagery

- **Satellite toggle** - Flip the base layer to satellite imagery on the Signal and Speed Test maps. Works out of the box with Esri World Imagery, which needs no account or API key. A one-time confirm notes the built-in imagery is free for personal, non-commercial use.
- **Optional Mapbox token for commercial use** - A new Settings > Satellite Imagery section accepts a Mapbox public token. When set, the satellite layer uses commercially licensed Mapbox imagery instead of Esri, with a badge showing the active provider.

### Address search

- **Smarter zoom by place type** - Searching a country zooms to a wide view, a city to a regional view, and a specific house all the way in, instead of one fixed zoom for everything.
- **Grid-style address matching** - Addresses like "1234 S 5678 W" now resolve by retrying without the cardinal direction when the first pass comes up empty.
- **Clear button** - An X appears in the search field when you have text, to clear and start over without retyping.
- **Staged Esc** - Esc steps back one level at a time: close the suggestions, then clear the text, then collapse the search box, so dismissing suggestions no longer wipes what you typed.
- **Result pin cleanup** - The pin dropped on a search result goes away when you clear the search.

### Map controls

- **Esc exits fullscreen** - On the Signal Map, after backing out of any open dialog, mode, or building selection, a final Esc leaves fullscreen.
- **Zoom button styling** - The zoom buttons on the Signal and Speed Test maps now match the 2D / 3D LAN flow maps, including a muted look when you are at the zoom limit.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.22.2

A couple of fixes plus a handy map addition. See [v1.22.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.22.0) for what's new in v1.22.0+

## Wi-Fi Optimizer

- **Address search on the maps** - Both the Speed Test Map and the Signal Map (Floor Plan Editor) now have a collapsible search control in the top-right corner. Click the magnifying glass, type a street address or place name, and the map jumps there with a dropped pin instead of you panning around by hand. This should help with getting your initial bearings when placing your APs and buildings.

## Threat Intelligence

- **Disabled forwarding rules no longer counted as exposed** - A disabled port forwarding rule isn't passing any traffic, so it no longer shows up in the exposure report as an exposed service under attack. UPnP rules are still treated as live since they inherently are.

## Config Optimizer

- **SQM firmware regression advisory knows about the fix** - The "SQM Performance Regression on Current Firmware" advisory now knows the download-throughput regression is fixed in UniFi OS 5.1.17 on the UXG line and 5.1.19 on the UCG line. It only fires for firmware in the affected window, and it now points you forward ("upgrade to the fixed version or later") instead of recommending a rollback to 5.0.10.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.22.1

More improvements on ISP Health and added cable modem support. See [v1.22.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.22.0) for what's new in v1.22.


## ISP Health

- **More accurate Loaded Latency and Loaded Loss** - In short: loaded latency and loss are now measured more accurately during normal usage (like user-initiated speed tests), without mis-attributing downstream loss to the upstream direction or vice versa. Under the hood, the measurements are matched against a dilated loaded window that captures the ramp-in and drain edges of a load event, which previously fell in transition windows and got dropped. The dilation never crosses into an opposite-direction loaded run, so a speed test's download phase can't be misattributed to its upload phase; it's direction-symmetric, so it's equally correct for download- and upload-bottlenecked connections. The idle baseline stays a strict, clean uncongested floor.

## Cable Modem Monitoring

- **Netgear CM2050V support** - The Netgear / Nighthawk CM provider now also handles the CM2050V and the newer .htm web UI it serves: it auto-detects the form login (instead of HTTP Basic) and parses the DOCSIS 3.1 OFDM and OFDMA channels, all from the same provider entry with nothing new to pick. Other newer Netgear cable modems may work too; if yours doesn't, please open an issue with a scrubbed HAR capture so we can add support.
- **Netgear CM700** - Primes the anti-CSRF cookie before Basic auth, which should fix CM700 support.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.22.0

The headline this release is deep per-port visibility: a live, timeline-synced statistics table for every switch and gateway port, plus the ability to poll any SNMP OID your gear exposes.

## The 1.21 line, recapped

If you're jumping up from 1.21.0 or earlier, here's what landed across that cycle:

- **ISP Health grew up** - Line-aware scoring (per-technology jitter, fair grading for sprawling regional ISPs), internet-outage detection with a per-hop recovery waterfall, congestion pinned to the exact bottleneck hop, flaky-target detection, and a date/time filter for the whole tab.
- **Your network, in motion** - Monitoring Interfaces can now reach a modem or ONT that sits behind your WAN, and the 2D/3D LAN maps play back what the network was actually doing (device up/down, Wi-Fi roaming, signal and throughput) live and across the timeline.
- **More devices, more visibility** - Quantum Fiber Q1000K ONT, Motorola and Realtek modem/ONT fixes, EF-Core and UNVR-G2 support, and sortable mean/min/max stats tables on every monitoring tab.

## Monitoring

### Live View

- **Per-port statistics** - A new per-port table below the maps shows link rate (in/out), cumulative bytes transferred (in/out), unicast/multicast/broadcast packet counters, and errors/discards for every SNMP-polled switch and gateway, synced to the map timeline with live updates and historical playback (current support for -24 h but your NO instance is already collecting data for looking even further back). Color-coded RJ45/SFP connector glyphs show negotiated link speed, and each access port links to its connected client's performance dashboard. Includes VPN / tunnel interfaces, raw UniFi 5G / LTE modem interfaces, raw AP Wi-Fi interfaces, and VLAN sub-interfaces.
- **Note** - _On many gateways and APs the raw SNMP stats from the device can be misleading. For example, on UCG-Fiber/UXG-Fiber and other IPQ gateways, the WAN VLAN sub-interface byte counters / rates are double-counted. This is taken into account in our Live views, ISP Health, displayed WAN rates and graphs, but in the raw port table the double-counted data can be seen on these interfaces._

### SNMP & Device Stats

- **Custom OID polling** - Add any SNMP OID per device, test it against the live device, map it to a named field, and it auto-charts on the Device Stats tab with mean/min/max columns. Standard per-port packet counters now poll on the 5s fast tier too.

### ISP Health

- **Loaded latency, separated from congestion** - When every monitored path slows together under load, that's your access link (bufferbloat or a busy shared-access network), not a single ISP hop. It now reads as Loaded Latency and no longer counts against your ISP Health score.

### Cable Modem

- **Netgear CM700** - Added alongside the CM600 and CM1000, pulling full downstream/upstream power, SNR, and error-correction stats whether your modem requires a login or serves its status page openly.

## Security Audit

- **Sharper DNS leak detection** - More precise detection of DNS that bypasses your configured resolver, reported as clear rule-level findings.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.21.5

A big upgrade to ISP Health: congestion localizes to the exact hop, the whole tab gets a date/time filter, and LAN/gateway outages are told apart from real WAN outages. See the [v1.21.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.21.0) for what's new in v1.21.0+.

## Monitoring

### ISP Health

#### Congestion
- **Bottleneck localization** - Congestion is pinned to the specific hop that's actually congested instead of being merged into a time-based blur of networks. The feed names the hop.
- **A disposition for every event** - Each event says whether it's a confirmed bottleneck, control-plane (ICMP) noise, self-inflicted bufferbloat, or unverifiable, with a plain-language reason so you know how much to trust it.
- **Sibling confirmation** - A dead-end hop with nothing monitored beyond it is confirmed when a sibling hop on the same network is congested in the same window.
- **Latency and jitter** - The feed reports both, and tells you when other monitored paths stayed clean under the same load, so you can separate a single-hop problem from your access link.

#### Date and time filter
- **Filter any window** - The standard Monitoring date/time filter is now on the ISP Health tab (24h, 48h, 7d, 14d, 30d, or a custom range from 4 hours up to a month), defaulting to 48h. The chart and report follow the window.

#### Outages
- **LAN/gateway vs WAN** - If your own gateway goes unreachable, it's surfaced as a "LAN / Gateway outage" and does not lower your ISP score, since it isn't the ISP's fault. Real WAN outages score as before.
- **Score impact on hover** - Each outage shows what it cost the score, or "not scored", on the badge and the type text.

## Dashboard
- **LAN Speed Test client IP** - For a client that doesn't match a known device (such as a VPN client), the LAN Speed Test panel on the dashboard shows its IP in a code block instead of "Unknown".

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.21.4

More accuracy fixes for ISP Health upstream discovery, plus a couple of dependency-install fixes. See [v1.21.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.21.0) for what's new in v1.21.0+

## Monitoring

- **More accurate upstream transit detection** - Reworked how we decide which upstream hops actually belong to your ISP versus the wider internet backbone. The near-transit window is now computed per individual traceroute and unioned across them, so multi-homed connections keep all their genuine direct upstreams instead of dropping one when several surface at the same hop. Tier-1 backbone ASNs that only ever sit above another tier-1 are now treated as core peering and excluded, while a tier-1 that's genuinely your ISP's upstream is kept. The result is fewer bogus monitoring targets and a truer picture of where your transit horizon actually ends.
- **Tier-1 transit probes gated to the near-transit window** - Probing toward a well-known anycast IP always enters that provider's network near the probe destination, which used to make it look like your upstream even when it wasn't. These probes now only count when the provider lands within the first couple of hops past your ISP, and are dropped when they're three or more transitions out.
- **Collapsible ISP Health - ISP Network list** - The ISP Network hop list now caps at 5 entries with an expand/collapse toggle, with a smooth open/close animation, so long paths don't dominate the page.

## Fixes

- **SSH probe installs traceroute reliably** - A UniFi Console with stale or empty package lists couldn't install traceroute from a bare install command. We now refresh the package index first (and bumped the timeout to cover the fetch).
- **Adaptive SQM installs dependencies reliably** - Same fix for the bc/jq dependency install: refresh the package index first so a console with stale lists can resolve them.
- **Fixed broken CSS animations** - A couple of animations (toast fade-in and a purpose fade) were dead due to a double-`@` escaping issue in plain CSS. They animate properly again.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.21.3

More ISP Health depth and upstream-discovery accuracy. See the [v1.21.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.21.0) for what's new in v1.21.0+.

## Monitoring

### ISP Health

- **Fairer scoring for large access networks** - ISP access hops are now graded against where the internet actually sits, not just the nearest hop, so a regional ISP whose network spans a whole state no longer gets dinged for normal in-region distance.
- **Jitter graded by connection type** - jitter is measured against a per-technology baseline (cable runs a few ms by nature, fiber sub-ms, Starlink a bit more), so DOCSIS and LEO connections stop being penalized for jitter that's normal for the medium.
- **Flaky target detection** - when a monitored hop shows packet loss well above its peers (usually a router deprioritizing ICMP), ISP Health surfaces it in a panel above your Latency Targets and lets you disable it in one click so it stops skewing your score. A Live View banner points you to it.

### Upstream Discovery

- **Smarter first-hop detection** - 1.1.1.1 and 8.8.8.8 (UniFi's WAN SLA ping targets) are no longer mistaken for your ISP's first hop; discovery prefers the actual on-link WAN gateway, and any saved by mistake get cleaned up automatically.
- **Stricter target selection** - a target must answer a full quick ping burst before it's auto-selected (relaxed for fixed-wireless and cellular), keeping flaky routers out of your monitoring set.
- **Level 3 transit visibility** - when your path crosses Level 3 (Lumen) but none of its routers answer, 4.2.2.2 is monitored as a stand-in so you still get transit health for that hop.
- **Cleaner discovery list** - transit hops group by network (nearest first), and renaming a target during review no longer occasionally loses the edit.

## Dashboard

- **Security Findings** - renamed the "Active Alerts" stat and "Recent Audit Issues" panel to "Security Findings" to better reflect what they show.

## Fixes

- **Realtek ONT login** - fixed sign-in on Realtek-based ONT sticks that use different login field names across firmware variants.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.21.2

More refinements to ISP Health outage reporting. See the [v1.21.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.21.0) for what's new in the 1.21 line, and [v1.21.1](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.21.1) for the last patch.

## Monitoring

### ISP Health
- **Per-hop outage waterfall** - Access ISP hops are broken out per target, so you can see which hop dropped and which recovered first (the inside-out heal), with ASN-based row labels and internet endpoints trimmed to two.
- **More accurate outage boundaries** - A target with no data during an outage no longer shows as a spurious "stayed up" row, and a single outage that briefly clears during staggered recovery is no longer split into several separate outages.
- **ISP Network ordered by RTT** - The hop list now sorts by round-trip time, nearest first.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.21.1

Internet outage detection lands in ISP Health, and the LAN map now plays back what your network was actually doing - live and across the timeline. See the [v1.21.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.21.0) for what's new in v1.21.0.

## Monitoring

### ISP Health

- **Internet outage detection** - ISP Health now spots internet-unreachable outages and tells them apart from monitoring gaps: it only counts an outage when your internet targets all go dark while the Monitoring Agent keeps probing (if the gateway itself drops there are no samples, so that's a gap, not an outage). It pins where the break sat - your access OLT can stay reachable while everything upstream goes dark, which means an ISP-side fault, not your network - scores it by how long you were actually down, and draws a recovery-shape timeline. A brief blip barely moves your score; a multi-hour outage tanks it. Outage windows are kept out of the regular packet-loss grades so they don't double-count.
- **Speed hero links to WAN Speed Tests** - The "Speed vs Plan" section now links to the WAN Speed Tests page, with a subtle hover highlight.
- **Truer path-shift reporting** - Path RTT reverts now show their real magnitude instead of "0 ms", and a correlated path shift is labeled from the transit network it happened in rather than a CDN endpoint that just routes through it.
- **Cleaner transit names** - Hand-added transit hops now get the same household-name cleanup as auto-discovered ones (e.g. "Level 3", not "Level 3 Parent"), and a few providers show their familiar names (Arelion, Sparkle, and "Zayo" instead of "Zayo Bandwidth").

### LAN Map

- **Live and historic playback** - The 2D and 3D LAN maps now reflect what the network was actually doing instead of freezing the current snapshot. Device online/offline state plays back correctly through the timeline and updates live; offline devices dim and drop to zero throughput instead of holding their last sample.
- **Wi-Fi client stats over time** - Band, signal, and PHY link rate play back at the scrubbed instant rather than always showing current values.
- **Wi-Fi roam tracking** - A client now shows up on the AP it was actually connected to, live and during playback. A seamless roam (no disconnect) used to never move the client on the map until a disconnect or page refresh.
- **Map polish** - 3D throughput labels and client pipes respect the band/overlay/name filter (no orphaned pipes after a redraw); the 2D map fits tighter to the top with label-aware spacing.

## Security Audit

- **Power devices no longer flagged for tagged VLANs** - UPS, PDU, and RPS devices were getting a "Port Issue: Excessive Tagged VLANs" finding on their single internal management port, which isn't a real downstream port and can't be reconfigured. They're now skipped (the upstream switch port they plug into is still audited), which also clears an inconsistency where UPS-2U was skipped but USP-PDU-Pro wasn't.
- **Technitium DNS** - Recognized as a DNS provider, with a 1-second per-port probe timeout so detection doesn't hang.

## Device Support

- **EF-Core, UNVR-G2, UNVR-G2-Pro** - Three newly shipped UniFi devices now resolve with friendly names and icons: the Enterprise Firewall Core gateway and the Gen 2 / Gen 2 Pro Network Video Recorders. EF-Core is correctly treated as a gateway, not an AP, even when the API reports phantom radios.

## Performance Tweaks

- **Firmware support extended to UniFi OS 5.1.19** - All performance tweaks and patches, including SGMII+ 2.5 Gbps support, were vetted on a UCG-Fiber and by two community members on the new firmware.

## Fixes

- **Database concurrency errors** - Fixed recurring "second operation started on this context" / disposed-context errors that filled the logs over time. The threat dashboard now uses its own isolated database context per operation.
- **Alerts: jump to the form** - Adding an alert rule now scrolls to the Add Rule form once it renders, so it doesn't open off-screen.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.21.0

The big one this release is Monitoring Interfaces: Network Optimizer can now reach a modem or ONT that lives behind your WAN, so you can poll and view a device that was previously unreachable from the LAN.

## What's New

A recap of what landed across the 1.20.x patches, in case you're jumping up from 1.20.0 or earlier:

- **ISP Health loaded-latency scoring** - A series of refinements to how loaded latency is measured and graded, including a pooled global baseline across ISP, transit, and internet targets and per-target deltas, so the score better reflects what your line actually does under load.
- **Alerts for gateway, cable modem, ONT, and cellular** - New alert evaluators so you can get notified when these devices report trouble.
- **Data Usage pay-as-you-go mode** - A manual-reset bucket for plans that don't follow a fixed monthly cycle.
- **Kiosk mode** - Hide the side menu for a clean mini-display or wall-mount presentation.
- **DNS provider detection** - Auto-detects on-gateway NextDNS CLI and ControlD, with an expanded list of public DNS provider IPs.
- **More modem support** - Added Xfinity XB8/XB10, ARRIS Surfboard S33/S34, and Cox CGM4981.

## Monitoring

- **Monitoring Interfaces: reach an ONT or modem behind the WAN** - Some modems and ONTs have a management IP that sits on the WAN side, unreachable from your LAN. Monitoring Interfaces deploys a small, self-contained, idempotent script to your gateway (modeled on Adaptive SQM and Performance Tweaks) that makes that device reachable for polling and from the LAN. It includes preflight checks for network overlap and duplicate IPs, a "try a native UniFi static route first" callout, and optional VLAN-tagged WAN support for fiber ISPs that run the WAN on a tagged VLAN. Reachable from the CM/ONT/Cellular monitor forms and from their failure messages.
- **Quantum Fiber Q1000K SmartNID ONT** - New provider that polls the Q1000K's CGI JSON API for link health, PON type, full DDM optics (Rx/Tx power, temperature, voltage, bias), link uptime, and OLT identity.
- **Statistics tables on every monitoring tab** - SFP, ONT, CM, Cellular, and Device Stats tabs now show a sortable mean/min/max table below the charts, matching the latency stats pattern. Click any column to sort, click device names to filter, and the tables hold their scroll position on mobile when data refreshes.
- **Motorola HNAP modems connect reliably** - The MB8611 and siblings exposed a .NET-on-macOS TLS quirk that stalled HTTPS until timeout. We now auto-detect HTTP vs HTTPS so these modems poll cleanly.

### 3D LAN Map

- **3D map no longer collapses from one bad placement** - A single device placed far outside the cluster (bad geocode, mis-drag, stale placement) used to drive the whole scene scale and shrink real buildings to a speck. Outlier anchors that are both more than 6x the median distance and past 200 m are now ignored, while spread-out campus layouts are left untouched.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.7

More ISP Health scoring improvements and some monitoring polish. **If you're on v1.20.6, this release improves the loaded-latency estimator - we recommend updating.** See the [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for what's new in v1.20.0+.

## Monitoring - ISP Health

- **Smarter loaded-latency scoring** - Loaded latency now pools all monitored targets (ISP access hops, transit, and internet destinations), filters out noise below the jitter floor, and takes the lowest quartile as the result. This is robust to ICMP deprioritization at any hop, destination degradation, and poll timing differences - so one bad target or one load event can't swing your score. Still computed passively from whatever real load your connection sees, no bufferbloat test required.
- **Counter lag compensation** - SNMP interface counters lag behind real-time ping probes by several seconds. Loaded latency and loaded packet loss now compensate for this so the highest-latency samples land in the correct load-classified window instead of being misclassified as idle.
- **Adaptive SQM probe windows excluded** - Adaptive SQM briefly lifts the shaper to measure your true line speed, which looks like bufferbloat but isn't your shaped experience. Those windows are now carved out of the loaded-line analysis.
- **Retuned idle latency** - The idle baseline is more robust to outliers and the per-technology curves were retuned so a top score is genuinely earned.
- **Consistent primary-WAN resolution** - ISP Health, the 2D / 3D Live Views, and upstream discovery now agree on which WAN is your configured primary (by load-balance weight and failover priority), and rate and Adaptive SQM data resolve to the correct counter and data-path interfaces, including VLAN-tagged WANs. Live throughput cards still follow the active uplink so failover stats stay correct.
  - **NOTE for PPPoE users:** please report any breakage in a GitHub issue, as we refactored some of the code that controls WAN interface mapping.
- **Lighter footprint** - Added WAN summary caching so the app stops re-reading it on every request.

## Monitoring - 2D / 3D Live Views

- **Cleaner timeline playback** - Scrubbing back through history no longer paints latency on secondary WAN globes that aren't being monitored.

## Monitoring - Live View

- **WAN chart tooltip timezone** - Tooltips on the Live WAN throughput chart now show local time instead of UTC.

## Security Audit

- **More DNS providers recognized** - Detects on-gateway NextDNS CLI and ControlD, and recognizes more public DNS provider IPs.

## Fixes

- **Standalone UniFi Network Server (legacy)** - Self-hosted UniFi Network Server installs no longer fall back to UniFi OS API paths that don't exist on them. UniFi OS Server consoles were unaffected.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.6

More ISP Health scoring improvements and some monitoring polish. See the [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for what's new in v1.20.0+.

## Monitoring - ISP Health

- **Smarter loaded-latency scoring** - Loaded latency now cross-checks your ISP access hops against end-to-end internet targets, so a single router that deprioritizes ping under load, or one anycast destination having a bad night, no longer inflates the measured loaded latency and unfairly drags your score down. Still computed passively from whatever real load your connection sees, no bufferbloat test required.
- **Adaptive SQM probe windows excluded** - Adaptive SQM briefly lifts the shaper to measure your true line speed, which looks like bufferbloat but isn't your shaped experience. Those windows are now carved out of the loaded-line analysis.
- **Retuned idle latency** - The idle baseline is more robust to outliers and the per-technology curves were retuned so a top score is genuinely earned.
- **Consistent primary-WAN resolution** - ISP Health, the 2D / 3D Live Views, and upstream discovery now agree on which WAN is your configured primary (by load-balance weight and failover priority), and rate and Adaptive SQM data resolve to the correct counter and data-path interfaces, including VLAN-tagged WANs. Live throughput cards still follow the active uplink so failover stats stay correct.
  - **NOTE for PPPoE users:** please report any breakage in a GitHub issue, as we refactored some of the code that controls WAN interface mapping.
- **Lighter footprint** - Added WAN summary caching so the app stops re-reading it on every request.

## Monitoring - 2D / 3D Live Views

- **Cleaner timeline playback** - Scrubbing back through history no longer paints latency on secondary WAN globes that aren't being monitored.

## Security Audit

- **More DNS providers recognized** - Detects on-gateway NextDNS CLI and ControlD, and recognizes more public DNS provider IPs.

## Fixes

- **Standalone UniFi Network Server (legacy)** - Self-hosted UniFi Network Server installs no longer fall back to UniFi OS API paths that don't exist on them. UniFi OS Server consoles were unaffected.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.5

More monitoring and data-usage improvements, plus a 3D map stability fix. See [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for what's new in v1.20.0+

## Data Usage

- **Pay-as-you-go bucket mode** - Data usage tracking can now run as an open-ended bucket that accumulates until you manually reset it, instead of resetting on a calendar billing day. Built for prepaid balances that don't expire monthly. Hit "Reset bucket" when you top up to start a fresh count; the previous total is archived to history.

## Monitoring

- **LAN flow map: fixed blank 3D view** - On networks with no AP placements on the Signal Map, the 3D force layout could blow up to invalid positions and blank the whole scene with no error. The layout now stays bounded and recovers cleanly.
- **WAN live chart: smarter time labels** - The x-axis tick spacing now sizes to the chart's own width instead of the viewport, so half-view and mobile panels space their time labels out instead of overlapping.
- **CM / ONT / Cellular stats: hide orphaned series** - Deleting a modem, ONT, or cellular config no longer leaves phantom leftover series on the charts.
- **Added Cox CGM4981** - Recognized for cable modem stats (shares the Xfinity/Technicolor web UI).

## Network Tools

- **Moved to its own route** - Network Tools now lives at /network-tools so it no longer double-highlights the Monitoring section in the nav.

## Kiosk Mode

- **New kiosk display mode** - A per-device setting that forces the collapsed layout at any width and hides the side menu, so a mini-display shows just the content. Applied before render so the sidebar never flashes in. Find it under Settings -> UI / Display Settings.

## Performance Tweaks

- **Firmware support raised to UniFi OS 5.1.18** - Performance tweaks are now validated through UniFi OS 5.1.18.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.4

ISP Health gets a lot sharper this release: it now grades every hop on your ISP's path and can tell a genuinely congested router from one that just deprioritizes ping. Plus new alerts for your gateway, modem, ONT, and cellular WAN. See the [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for the bigger picture since v1.20.0.

## ISP Health

- **Every ISP hop is graded** - The ISP Network score now reflects packet loss and congestion on every hop in your provider's path, not just the nearest one. The closest hop still sets your idle-latency baseline.
- **Honest jitter, even across split paths** - When a clean upstream (a transit provider, a deeper ISP router, or a destination reached through a hop) proves the path is actually steady, ISP Health stops penalizing a router whose high "jitter" is really just ICMP deprioritization. It only does this when it can prove traffic truly flows through that router, so a clean detour can't hide a genuinely congested hop. Sub-0.05 ms differences are treated as noise.
- **Clearer cards** - Each provider card shows the effective jitter with an info icon explaining when a reading was absorbed and why, the RTT range across hops, and transit RTT as a winsorized mean so one bad probe doesn't skew it. Packet-loss expectations now scale with how loaded your WAN is.
- **A nudge to re-map your path** - If ISP Health doesn't have your hop layout yet, a banner points you to re-run Upstream Discovery, and it clears itself once you do.
- **Lighter on InfluxDB** - Watching Live View no longer kicks off a heavy ISP Health recompute every few minutes. The query runs far less often now, cutting periodic database CPU spikes. Same scores, computed more sparingly.

## Monitoring - Alerts

- **New modem / ONT alerts** - You can now get alerts on your gateway, cable modem, ONT, and cellular WAN, alongside the existing ones.

## Fixes / Improvements

- **Clearer IFB error** - When a device is missing its IFB interface, the message now explains the QoS-rule workaround instead of leaving you guessing.
- **Footer version links to release notes** - Click the version in the footer to jump to that release's notes.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.3

More fixes and polish for ISP Health and mobile UX. See [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for what's new in v1.20.0+

## Monitoring

- **Xfinity XB8/XB10 cable modem support** - SNMP-based monitoring for Xfinity gateway devices including signal levels, channel stats, and uptime.
- **ISP Health: reliable multi-network tooltips** - Per-Network RTT chart tooltip now consistently shows all ASN series at every point, not just one. Fixed by aligning all series to a shared time grid.
- **ISP Health: step-change detection tuning** - Lowered the detection threshold, improved transit ASN labeling, and fixed step-down detection after short-lived transit shifts so path changes are caught more reliably.

## Fixes

- **Mobile nav bar scroll behavior** - Fixed an edge case where the nav bar could get stuck hidden on short pages (like Client Dashboard tabs with no data). The bar now reappears automatically when switching to a tab with less content.
- **Touch tooltips on buttons** - Tapping buttons on mobile no longer leaves a tooltip stuck on screen after the action or after navigating away.

## Wi-Fi Optimizer

- **Clickable links from band distribution and AP load balance** - Client counts in band distribution and AP load balance now link directly to client stats.

## Documentation

- **Proxmox updating guide** - Added a clear "Updating" section to the Proxmox README and deployment guide.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
# or if you just need to update
pct exec <CT_ID> -- bash -c "cd /opt/network-optimizer && docker compose pull && docker compose up -d"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.2

More ISP Health tuning and a new "Dig deeper" section for BGP exploration. See [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for the ISP Health launch and [v1.20.1](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.1) for ARRIS Surfboard support and hero card improvements.

## ISP Health

- **"Dig deeper with BGP tools"** - A new collapsible section under the Per-Network RTT chart that links directly to your ISP's ASN on HE BGP Toolkit, bgp.tools, and RIPE RIPEstat, so you can explore peering, prefixes, and routing when you spot something interesting
- **More sensitive path/transit shift detection** - Lowered the step-change threshold from 2.0 ms to 1.5 ms and relaxed the relative gate from 15% to 6%, so smaller but real transit shifts on higher-latency paths are no longer filtered out

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.1

More ISP Health polish and ARRIS Surfboard HNAP support. See [v1.20.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.20.0) for what's new in v1.20.0+

## ISP Health

- **Plan speed in the hero card** - Best, Typical, and Plan speeds stacked so you can see how your connection compares to what you're paying for
- **Last updated timestamp** - Shows how fresh the report is in the hero card upper right
- **Idle latency scoring and findings** - Tuned the curve so normal-range values aren't penalized as harshly, and added a finding when first-hop latency exceeds the normal band for your access technology
- **Refresh picks up speed changes immediately** - Changing your ISP speeds in UniFi Network no longer takes minutes to show up
- **Mobile layout improvements** - Better chart fill, dimension gauges scale and wrap cleanly on narrow screens

## Cable Modem Monitoring

- **ARRIS Surfboard S33/S34 support** - New HNAP provider for Surfboard modems that use HNAP-over-HTTPS (S33/S34 firmware). Supports both SHA256 and MD5 login digests, with a raw-socket fallback for the S34's malformed HTTP headers.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.20.0

ISP Health is the headline of v1.20.0, and it's the payoff for everything the self-hosted Monitoring stack has been collecting. All that SNMP polling, latency and loss probing, WAN throughput tracking, and Upstream Path Discovery finally comes full circle: a single 0-100 score for how well your internet connection is actually performing.

New to Monitoring? It's worth catching up - ISP Health builds directly on top of it. See the [v1.18.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.18.0) for the self-hosted monitoring foundation (SNMP, latency/loss, Live View maps, Upstream Discovery) and the [v1.19.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.19.0) for access network monitoring (cable modem, fiber ONT, and cellular signal tracking).

## ISP Health

A new sub-feature of Monitoring that turns the data you're already collecting into one score for your internet connection. No new agents or probes - it reads your existing latency, loss, throughput, and discovered path back over a trailing 48-hour window and grades it.

- **Technology-aware scoring** - Thresholds are anchored to your access technology (GPON, XGS-PON, DOCSIS, DSL, fixed wireless, cellular, Starlink, and more), so a latency number that's healthy on DOCSIS doesn't read as a red flag on fiber. The score splits into equal thirds across your Access Layer, your ISP's network, and the Transit networks your traffic crosses, with a per-factor breakdown so a low score tells you exactly where the problem lives.
- **Per-ASN transit grading** - Every network in your path is graded on its own (latency stability, jitter, loss, and congestion), with co-located hops clustered so monitoring a deep hop never drags down a network's grade.
- **Congestion and path-shift detection** - Surfaces sustained latency and jitter under load (the bufferbloat / oversubscription tell, usually in the evenings) and flags path shifts where your traffic gets rerouted onto different infrastructure, kept informational since a BGP change isn't necessarily a problem.
- **Speed vs Plan** - Grades demonstrated WAN throughput against the plan speeds you've set in UniFi Network, showing best and typical.
- **SQM recommendations** - Points you at Smart Queues when loaded latency or loss crosses the line for your connection type, or recommends Adaptive SQM when it spots a recurring time-of-day congestion pattern.
- **Live tile** - A color-coded ISP Health score on the Dashboard and Monitoring live views, linking straight to the tab.
- **Upstream Discovery accuracy** - WAN L2-neighbor selection now prefers public over CGNAT over private and fresh over stale entries, and no longer proposes RFC1918 CPE LAN-side addresses as access hops.

Coming soon: multi-WAN support for both Monitoring and ISP Health. The per-WAN stats are already being collected; today the scoring and dashboards grade your primary connection.

## Monitoring

### Cable modems

- **Motorola HNAP login fixed (MB8611/MB8600)** - The provider failed to authenticate against current Motorola firmware and could trip the modem's failed-login lockout, which drops packets for 5 minutes and surfaced as connection timeouts. The login handshake now matches the firmware, sessions persist across polls instead of re-authenticating every cycle, and a failed login backs off for 5 minutes so the lockout can't be re-tripped. The timeout message now explains the lockout, and decimal-MHz channel frequencies parse correctly.

### WAN live chart

A round of accuracy and smoothness work on the WAN RTT chart. If you've ever reloaded the page and watched the latency line redraw at a different shape, or seen the left edge spike for no reason, this one's for you.

- **It reads the same on reload as it does live** - History and live samples used to weight your ISP and transit targets differently, so every reload or tab-refocus nudged the RTT line to a new level, and a 60s moving average quietly flattened real events (like a speed-test bufferbloat hump) right out of the primed history. Both now use the live feed's weighting, the warmup rows that skewed the oldest minute are gone, and short events survive a reload intact.
- **Scrolling is smooth** - The live window slides continuously instead of ticking forward a notch at a time, and historic playback interpolates between the once-per-second seeks. Draw-only, so no extra polling or fetches.
- **Labels stay put** - X-axis labels are pinned to a fixed 20s grid (60s on mobile) in 24-hour time and scroll with the data instead of re-snapping as the window slides. And scrubbing just behind live no longer leaves the first few minutes of the chart blank.

### Live View maps

A pass of consistency and interaction polish across the 3D and 2D Live View maps.

- **The two maps feel like one feature now** - The 2D map gained a collapsible Controls legend matching the 3D map's (limited to the interactions 2D actually supports), both maps share the same title-click collapse pattern for their Filter, Overlays, and Controls panels, and the 2D Overlays panel lines up with Filter on mobile.
- **Scrubbing and playback behave** - Keyboard scrub keys now register while the 2D map is on screen (camera WASD/QE keys still need the 3D canvas in view), pausing in live mode clearly shows "Live (Paused)" on both maps, and 2D playback-speed changes publish instantly instead of waiting for the next tick.

## Settings

- **Consistent manual add/edit form styling** - The Modem, Cable Modem, and ONT add forms share common styles with refined sizing and spacing.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.6

More monitoring improvements and a dashboard refresh. See [v1.19.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.19.0) for what's new in v1.19.0+

## Network Monitoring

- **Motorola MB8611 / MB8600 cable modem support** - New provider for Motorola DOCSIS modems using the HNAP protocol. Polls downstream/upstream channel stats and auto-detects the model from firmware. Select "Motorola MB8611, MB8600 (HNAP)" in CM Settings.
- **Smarter ONT detection** - AT&T gateway provider now identifies GPON vs XGS-PON from the SFP wavelength, records the BWP provisioned speed, and shows PON registration state with human-readable labels (e.g. "Connected (O5)").
- **Gateway latency fix** - Latency targets for gateways now use the LAN-side IP, fixing broken pings for users on PPPoE or CGNAT.
- **CM, ONT, and Cellular panels redesigned** - Metric boxes reorganized into Connection and Stats groupings. CM correctables/uncorrectables now in the right place. Fixed paging between SFP ONTs and external ONTs when both are configured.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.5

More fixes and polish for monitoring. See [v1.19.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.19.0) for what's new in v1.19.0+

## Network Monitoring

- **PPPoE WAN throughput** - WAN throughput charts were completely blank on PPPoE connections (#669). The interface resolver looked for the physical uplink port, which never yields the `ppp0` tunnel where the counters actually live. Fixed with a shared interface-selection helper that picks the right counter source per connection type (PPPoE, GRE-tunneled cellular, plain Ethernet). Existing data appears retroactively since SNMP was collecting it all along.
- **Corrupt SNMP counter rejection** - A single garbled SNMP read could produce terabit-per-second spikes on the chart (observed as 10 Tbps on a 2.5 G WAN port). Rates above 1.4x link speed are now discarded and the baseline recovers automatically.
- **Counter reset recovery** - SNMP rate computation now detects device reboots and firmware upgrades (counter resets) and reseeds the baseline instead of charting a spike.

## Client Stats

- **Clearer traffic direction labels** - Disconnect events now show "Device downloaded X / uploaded Y" instead of ambiguous up/down labels, and Wi-Fi rates are labeled "AP TX/RX Rate" to make the perspective explicit.
- **Client IP in detail header** - The detail banner shows the client IP next to the MAC address.

## Fixes

- **HTML instead of JSON from console** - During a console firmware upgrade (or other maintenance), the UniFi Console may serve an HTML page instead of JSON. The error now includes the page title and a clear explanation instead of a cryptic deserialization failure.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.4

More monitoring quality-of-life in this one. See [v1.19.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.19.0) for what's new in v1.19.0+

## Monitoring

- **Drag to zoom on stats charts** - Drag across any chart on the Network Performance, Device Stats, SFP Stats, CM Stats, ONT Stats, and Cellular Stats tabs to zoom into that window, Grafana style. Syncs with the time range selector and refetches at finer detail; live polling pauses until you pick a preset again.
- **Why readings differ from UniFi Network** - New info panel under Device Stats: CPU temp is the SoC die sensor over SNMP, memory excludes Linux page cache (matches htop). Our numbers are the raw truth, not the smoothed ones.
- **WAN live chart: faster and more accurate** - Polls twice as fast for snappier real-time feedback, and every SNMP sample is now plotted exactly once - no more duplicated or missed points making the line stutter or double back.

## Adaptive SQM

- **"Awaiting Status" panel state** - App cold starts briefly showed "Not Deployed" even with SQM enabled. Now shows "Awaiting Status" while polling; "Not Deployed" means no enabled config.

## Fixes

- **Proxmox installer: LXC template matches host architecture** - No longer assumes amd64.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.3

A hefty batch of Monitoring and dashboard improvements this round. See the [v1.19.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.19.0) for what's new in v1.19.0+.

## Monitoring

- **SNMP Devices list** - A new table under Monitoring -> Setup shows every device, whether SNMP looks enabled, whether we're actively polling it, and when it was last polled. Now it's obvious at a glance which devices are feeding data and which need a look.
- **Heads-up when your gateway isn't being polled** - If a key device like your gateway isn't reporting over SNMP, the Live view shows a banner that takes you straight to the device list, expands it, and scrolls right to it.
- **Faster recovery after reboots** - When a device stops answering SNMP (a firmware update or reboot, say), it's now set aside for 5 minutes instead of an hour, so it rejoins monitoring much sooner.

### Live Map

- **Open a client straight from the map** - Double-click any client on the 2D or 3D map to jump to its dashboard. Wi-Fi clients open right to the Signal tab.
- **Jump to the live map from your Dashboard** - The Live View card header on the Dashboard now links to the Monitoring Live tab.
- **Clearer device tooltips** - Tooltips now show a device's IP, and for wireless devices their Wi-Fi link rate. Throughput on access points and bridges (including UDBs) now reads from the network's perspective, toward the gateway, so it lines up with every other device. The layout is tidied up too: link speed sits right above the live throughput, and Network shows next to the SSID.

## Data Usage

- **Monthly usage history** - WAN data usage now keeps a permanent total for each past billing cycle, so you can look back month to month. Previously only the last couple of months of raw data were retained. It even backfills the cycles it already has data for.
- **Data Usage on the Monitoring page** - Added a Data Usage tab to Monitoring that links over to the existing one under Alerts.

## Client Dashboard

- **Clearer Wi-Fi rate labels** - The top-bar rates now read "AP RX" / "AP TX" to make clear they're measured at the access point.
- **All LAN speed tests show up** - Server-initiated iperf3 tests (where the app connects out to a device to test it), both scheduled and ones you run manually, now appear in the speed history alongside client-initiated and browser tests. Internet (WAN) tests still live elsewhere.

## Fixes

- **Accurate LAN latency on macOS** - macOS once again uses the native ping for sub-millisecond LAN latency, matching what you'd see in Terminal. Heads-up for Apple Silicon: there's an occasional harmless crash on startup from a .NET runtime bug, and the app recovers on its own.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.2

More mobile polish and chart fixes for the monitoring release.

## What's New in v1.19

- **Cable Modem Monitoring** - Poll DOCSIS modems for downstream/upstream power, SNR, and FEC error rates. Supports Netgear CM and ARRIS Surfboard families.
- **ONT Device Monitoring** - Poll fiber ONTs for RX/TX power, temperature, voltage, and bias current. Supports AT&T gateways, Realtek GPON sticks, and 8311 XGS-PON sticks.

## Mobile UX

- **Smoother nav bar** - No more content jump when the bar hides/shows on scroll
- **Client Dashboard auto-hide** - Nav bar auto-hides after 2 seconds, tab switches preserve scroll position

## Monitoring

- **Throughput labels on clients** - Wi-Fi and wired clients now show download/upload rate badges on the 2D flow view
- **Live WAN chart Y-axis fixed on mobile** - Packet loss and throughput axes were auto-scaling poorly on small screens
- **Chart switch-back lines fixed** - 30-day latency and device health charts no longer draw backwards lines
- **3D map fit button** - Reset camera to fit the full topology, matching the 2D map
- **Animated map panel collapse** - Filter and Overlays panels animate open/close

## Fixes

- **macOS ARM64 ping stability** - Switched ping method to reduce crashes on Apple Silicon
- **Stats panel CSS cleanup** - Consolidated duplicated styles across ONT, CM, and Cellular panels

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.1

Quick follow-up to v1.19.0 with 8311 ONT firmware support and several fixes. See [v1.19.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.19.0) for what's new in CM/ONT monitoring.

## ONT Monitoring

- **8311 community firmware support** - New provider for Lantiq/MaxLinear GPON and XGS-PON SFP sticks running 8311 firmware (WAS-110, PRX126, Nokia G-010S-P, and others). Scrapes the LuCI JSON endpoint for RX/TX power, temperature, voltage, and bias current. Defaults to HTTPS on port 443 with LuCI session auth.
- **Self-signed TLS cert bypass** - All ONT providers now accept self-signed certificates since these are local network devices. Fixes connection failures on sticks serving HTTPS with self-signed certs.
- **HTTP/HTTPS auto-fallback** - Providers try the port-based scheme first, then automatically try the opposite on connection or SSL failure. No manual configuration needed.

## Cellular Monitoring

- **LTE-only signal quality fix** - Signal quality wasn't written to InfluxDB when a cellular modem fell back to LTE-only mode. Charts now show signal quality regardless of whether the modem is on 5G, NSA, or LTE.

## Fixes

- **Device monitor services start at app launch** - CM, ONT, and Cellular monitor services now begin polling immediately on startup instead of waiting for the first page visit.
- **macOS ARM64 crash fix** - Disabled single-file compression that caused crashes on Apple Silicon Macs running the native install.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.19.0

Cable modem and fiber ONT monitoring - track your access network equipment's signal quality, power levels, and error rates over time.

## What's New

- **Cable Modem Monitoring** - Poll DOCSIS modems for downstream/upstream power, SNR, and FEC error rates. Supports Netgear CM (CM600, CM1000, CM1200, etc.) and ARRIS Surfboard (SB8200, SB6183) via HTTP scraping.
- **ONT Device Monitoring** - Poll fiber ONTs for RX/TX power, temperature, voltage, and bias current. Supports AT&T residential gateways (BGW320, BGW210) and Realtek-based GPON sticks (ODI DFP-34X-2C2, V-SOL V2801F, T&W TWCGPON657, and other RTL960x modules).
- **Dashboard Panels** - New Cable Modem Stats card and unified ONT Stats card that handles both SFP-based and device-polled ONTs with navigation between them.

## CM Stats

- New CM Stats tab on the Monitoring page with DS Power, DS SNR, US Power, and FEC Errors charts
- FEC error chart shows both correctable and uncorrectable error deltas per interval
- Settings section with provider selection, test connection, and polling interval

## ONT Stats

- New ONT Stats tab on the Monitoring page with RX/TX Power and Temperature charts
- Unified dashboard panel shows SFP-based ONTs or device-polled ONTs (or both) with prev/next navigation
- Empty state provides clear paths for SFP monitoring vs standalone ONT configuration
- Settings section with AT&T Gateway, Realtek ONT Stick, and Generic HTTP ONT providers

## Fixes

- **LanFlowMap startup resilience** - Per-device InfluxDB query timeout on startup prevents cascade crashes when InfluxDB is slow after a restart.
- **Proxmox arm64 install** - Skip AppArmor LXC config on hosts without AppArmor support, fixing installation on arm64 Proxmox (e.g., Raspberry Pi 5).

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.18.3

More polish for the live monitoring views. See [v1.18.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.18.0) for what's new in v1.18.0+

## Monitoring Live View

- **2D map relayouts on filter changes** - Toggling Wi-Fi/Wired overlays, band filters, or text search now rebuilds the tree layout so the map compacts to use the available space instead of leaving gaps where hidden clients were
- **Grid-wrap clients with infra siblings** - APs with downstream infra (like a UDB bridge) now grid-wrap their clients at 6 columns instead of one long horizontal line
- **Dark background pills on device labels** - Device name and throughput rate labels below network devices now have the same dark pill background as link speed labels, improving readability over connector lines
- **Smooth WAN chart scrolling** - The live WAN throughput chart now scrolls continuously instead of jumping on each poll cycle. Poll cadence aligned to the 5 s SNMP interval for consistent data
- **Tooltip stays while inspecting** - Hovering a data point on the WAN chart pauses updates so the tooltip doesn't disappear while you're reading it
- **WAN chart mobile full-width** - Y-axis labels hidden and padding optimized on mobile so the chart uses the full screen width
- **Tab refocus catch-up** - Alt-tabbing away and coming back reloads the WAN chart history so there's no gap in the data

## Fixes

- **Missing InfluxDB buckets handled gracefully** - Renamed, deleted, or inaccessible buckets no longer crash the app. Returns empty data and marks InfluxDB unhealthy with a banner linking to Setup.
- **Cellular Stats tab waits for InfluxDB** - Charts now wait for InfluxDB to be confirmed reachable before mounting, matching SFP tab behavior. Shows a loading spinner instead of empty charts during app startup.
- **Packet loss line breaks fixed** - Null loss values from the API no longer create gaps in the WAN chart loss line

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.18.2

Patch fix for the config import/export feature introduced in [v1.18.0](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.18.0). See [v1.18.0](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.18.0) and [v1.17.0](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) release notes for what's new in recent versions.

## Fixes

- **Config import no longer corrupts the database on restart** - Importing a .nopt backup replaced the database file but left stale SQLite WAL/SHM files from the previous database. On restart, SQLite replayed the old write-ahead log against the new database, corrupting the schema and crash-looping the app.

- **Import preview shows export date in local time** - The export timestamp on the import confirmation screen now displays in server-local time instead of UTC.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.18.1

More fixes for WAN monitoring and Docker compatibility. See [v1.18.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.18.0) for what's new in v1.18.0+

## Monitoring Live View

- **Packet loss accuracy** - Loss is now a flat average across all WAN targets per time window instead of per-target smoothed. Gives a cleaner, more representative loss signal on the live WAN chart.

## Client Speed Test

- **Health check fix for bridge networking** - The browser speed test availability check was hardcoded to `127.0.0.1`, which failed on Docker setups where the speedtest container port is bound to a specific IP. Now uses `HOST_IP` when set. Fixes #724.

## Fixes

- **Docker: Speedtest container starts on IPv4-only hosts** - The OpenSpeedTest container no longer crashes on hosts with IPv6 disabled. The entrypoint now detects missing IPv6 support and skips the IPv6 listen directive. Fixes #724.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.18.0

Significant update for cellular 5G / LTE modem monitoring and live WAN visibility.

## What's New

- **Live WAN chart** - Real-time download, upload, packet loss, and mean ISP/transit RTT on the Dashboard and Monitoring Live View. Pre-loads 5 min history, then polls every 3 seconds. Follows the map timeline scrubber during historic playback.
- **Cellular monitoring overhaul** - Multi-provider architecture for cellular modem polling, with support for Ubiquiti, Netgear Nighthawk, and GL-iNet/Quectel modems. Signal metrics charted over time via InfluxDB.
- **U5G-Backup support** - Full product database entries for the new UniFi U5G Backup modem (US and EU variants).

## Monitoring Live View

- **Map swap buttons** - Swap 3D and 2D map display order, persisted to settings.
- **Map mode: Off** - The 2D/3D toggle now cycles 2D, 3D, Off to hide the map entirely.
- **Add to Dashboard** - Button on Monitoring Live tab when Live View isn't on the dashboard.

## Cellular Monitoring

- **Netgear Nighthawk hotspot support** - New HTTP provider for M-series hotspots (thanks @jedis00 for PR #661).
- **GL-iNet / Quectel modem support** - SSH provider for third-party cellular routers using AT+QENG commands with per-modem credentials. Closes #158, reported by @kwschnei.
- **uiwwand polling** - All UniFi modems now poll via the uiwwand ubus daemon first, falling back to raw qmicli. Faster startup recovery after modem reboot. Closes #635, reported by @jimstrang.
- **Cellular Stats monitoring tab** - RSRP, RSRQ, SNR, and Signal Quality time-series charts with per-band per-device series, filter badges, and time range controls.
- **InfluxDB time series** - Signal metrics written to the longterm bucket with separate data points for LTE and NR5G in NSA dual-connectivity mode.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.19

More SFP monitoring improvements - this one's for the Active Ethernet / P2P fiber folks. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## SFP Monitoring

- **Active Ethernet support** - Users with AON / P2P fiber can now mark their SFP modules as Active Ethernet instead of the "pretend it's PON" workaround. Dedicated thresholds, health color bands, and alert rules tuned for point-to-point links where RX power should be much stronger than through a 1:32 splitter.
- **Dashboard card links to SFP chart** - Clicking the ONT Stats / Fiber Stats card on the dashboard jumps straight to the SFP Diagnostics chart in Monitoring, pre-filtered to the module you were viewing.
- **Dynamic card title** - Shows "ONT Stats (GPON / XGS-PON)" when all monitored modules are PON, switches to "Fiber Stats" when any AE module is present.
- **"Set ONT" replaces "Set PON"** - Clearer labeling in the Optical table, plus a new "Set AE" button for P2P modules.

## Performance Tweaks

- **Firmware gate raised to 5.1.15** - Performance Tweaks now supports UniFi OS through 5.1.15 (previously capped at 5.1.13).

## Fixes

- **SFP vendor name cleaning** - Corporate suffixes like "Inc", "Ltd", "Technologies" are stripped from vendor names on the dashboard.
- **Paging buttons on dashboard card** - Navigation arrows no longer accidentally trigger card click.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.18

More monitoring refinements. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **INDATEL/GLC transit probe** - Added INDATEL (AS30517, Everstream infra) as a new transit probe target. Small transit networks where the probe endpoint itself is the only hop in the ASN are now supported, gated by ASN proximity so only networks within 2 ASN transitions of your access ISP are proposed.
- **Tiered packet loss coloring** - Loss Mean and Loss Max in the stats table now use a 5-tier color scale with separate thresholds for each. Loss Mean is shown at 3 decimal places for more precision.
- **Loss chart scale** - Y-axis now defaults to 5% instead of 100%, expanding dynamically when data exceeds that. Small loss events are no longer invisible.
- **Active targets badge** - The "N active" badge on the Latency targets card no longer counts paused targets.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.17

Fix for database corruption on Unraid. See [v1.17.0](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) and the patch release notes since then for what's new in v1.17.

## Fixes

- **Database corruption on Unraid/FUSE filesystems** - SQLite's WAL journal mode requires shared-memory via mmap, which doesn't work correctly on Unraid's FUSE filesystem (shfs), mergerfs (common on OpenMediaVault), or network mounts (NFS, SMB). The app now detects these filesystems at startup and automatically switches to DELETE journal mode, which is fully safe. If you've been experiencing database corruption or data loss on Unraid, this should resolve it. For best performance, map your data volume to a cache drive path (e.g., `/mnt/cache/appdata/...` instead of `/mnt/user/appdata/...`) - this bypasses FUSE entirely and keeps the faster WAL mode.

- **Reduced log noise from SNMP monitoring** - Interface rejection messages during SNMP polling moved from Debug to Trace level.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.16

More improvements for upstream discovery and monitoring. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **AT&T transit probe** - New trace endpoint surfaces AT&T (AS7018) as a transit ASN during upstream discovery
- **Border router detection** - Discovery now walks each individual trace to detect where traffic exits the access ISP, catching multiple border routers when the ISP peers through different exits for different transit providers
- **Multi-hop transit candidates** - Up to 3 nearest responding hops per transit ASN proposed as candidates, with verified RTT shown
- **Target naming** - All targets follow a consistent `<Org> <PTR-derived-name>` format. Corporate suffixes stripped from ASN org names. User-edited names persist across re-discovery.
- **PTR resolution** - Explicit PTR lookup on proposed transit IPs, so Windows users get meaningful hostnames too
- **Split review UI** - Transit networks and path-end Internet hosts shown in separate sections with editable labels
- **DB reconciliation** - Existing targets matched on re-discovery: enabled targets pre-checked, disabled ones stay unchecked, unreachable targets clearly disabled
- **Access technology preserved** - Your selection carries forward across re-discovery runs

## Performance Tweaks

- **MongoDB on SSD data loss fix** - Stale-data detection now uses WiredTiger.turtle (written on every checkpoint) instead of WiredTiger (written once at creation), preventing unnecessary re-migrations that could lose data. Thanks to @coreclk (#704).

## Fixes

- **Fabric throughput** - Fixed ingress/egress calculation on new Live Dashboard panel that was only computing for the gateway instead of all fabric devices
- **Navigation guard** - Unsaved discovery warning now only fires when leaving the Network Performance tab, and clears immediately after saving
- **Status indicator min-width** - Prevents dot indicators from collapsing in flex layouts

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.15

More improvements for monitoring and network tools. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Dashboard

- **Live View panel** - New dashboard card that embeds the live 2D or 3D topology map alongside WAN rates, latency stats, and gateway health. Disabled by default; enable and toggle between 2D/3D in dashboard edit mode.

## Network Tools

- **WAN interface selection** - On multi-WAN gateways, a new dropdown lets you bind ping and traceroute to a specific WAN link by friendly name (e.g. "Comcast Cable (WAN1) - eth4"). Useful for isolating per-WAN latency and path.
- **Gateway SSH credential fix** - Probes from the gateway vantage now use gateway-specific SSH credentials instead of generic UniFi SSH creds, fixing auth failures on sites where the two differ.
- **Traceroute auto-install** - If traceroute isn't installed on the gateway, it's installed automatically via apt on first probe attempt.

## Fixes

- **Traceroute probe count** - Fixed the output parser showing doubled probe counts on successful hops (e.g. "3 / 6" instead of "3 / 3").
- **Live View mobile UX** - Touch interaction fixes, responsive layout improvements, iOS orientation change handling, and scroll behavior tuned for tablet landscape for the 2D/3D topology maps.
- **ONT/Cellular stats panels** - Fixed font-size override on ONT model display and centered metric rows in WAN panels.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.14

Monitoring improvements and chart polish. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **L2 neighbor as first-mile target** - Upstream discovery now proposes the gateway's directly connected L2 neighbor (OLT on GPON, CMTS on DOCSIS, BNG on PPPoE) as a monitoring target. Useful on GPON where the OLT is L2-transparent and invisible to traceroute but still responds to ICMP. Reachability check auto-disables it if it doesn't respond.
- **ISP RTT shows nearest hop** - The ISP RTT stat card and globe label now pick the lowest latency across all access hop targets instead of the deepest one, giving a better read on first-mile health.
- **Link rate gap fix** - Fixed intermittent zero-rate gaps on live map links caused by SNMP counter refresh lag vs poll cadence. Rates no longer show a sawtooth pattern.
- **SNMP health fallback** - Devices where SNMP is configured but doesn't return health OIDs (e.g. USW-Flex-XG) now get CPU/memory from the UniFi API instead of silently dropping the data.
- **WAN link labels at lower threshold** - WAN/transit flow labels now appear at 500 Kbps instead of 1 Mbps on both 2D and 3D maps.

## Charts

- **33-color chart palette** - New chart palette (Observable 10 + Tableau + D3 Paired) replaces the old 6-color rotation. All color pairs are perceptually distinct, and devices keep the same color across tabs and restarts.
- **Ctrl+Click filter badges** - Hold Ctrl (Cmd on Mac) when clicking a chart filter badge to toggle that single series. Normal click still does solo/show-all. Applied across Latency, Device Stats, SFP, WAN Speed Test, and Threat Dashboard.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.13

More monitoring improvements. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **Differential SNMP polling** - The SNMP poller now skips OID walks whose cached data hasn't expired. Traffic counters are walked every 5s, oper status and error counters every 30s, and static metadata (interface names, speeds) every 300s. Reduces per-device SNMP requests by ~60%, which adds up on larger fabrics with many switches.
- **Poller instance caching** - The SNMP poller is reused across polling cycles instead of being rebuilt every 5 seconds, preserving the V3 discovery cache and per-device state.
- **SNMP failure learning for all tiers** - Medium and slow polling tiers now skip devices that don't speak SNMP (like USW-Flex-Mini), matching the fast tier's existing behavior. Eliminates repeated timeouts against non-SNMP devices.
- **Per-device SNMP setup guidance** - The monitoring setup wizard and status page now explain that SNMP must be enabled on each UniFi device individually (Settings > SNMP > set Location or Contact), not just the global Console setting.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.12

Hotfix for v1.17.11. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **SNMP uptime fix** - Device uptime was always showing 0h in tooltips. The SNMP TimeTicks value wasn't being parsed correctly from the formatted string. Now extracts raw ticks directly, and uptime is included in historic playback.
- **Port rate data restored** - A device cache change in v1.17.11 caused port rate deltas to compute as zero most of the time, killing switch throughput data. Reverted to the original 4s cadence (the upstream API cache handles call reduction).
- **Historic playback performance** - Rewrote historic queries to skip InfluxDB's aggregateWindow and pivot (unnecessary at native 5s cadence), and added a 5-minute result cache so consecutive playback ticks don't re-query. Sustained InfluxDB CPU during playback drops from ~40% to near-zero between cache fills.
- **Scrubber fixes** - Fixed play button auto-pausing after scrub, historic-to-live transition flicker, scrub-during-playback not stopping the timer, and playback jumping backward after fast arrow scrubbing.
- **2D keyboard parity** - Arrow keys, Shift acceleration, and Space play/pause now work when the 2D scrubber is focused.
- **2D layout polish** - Tighter horizontal spacing, longer device name labels (24 chars), longer client name labels (32 chars), ISP expected rates in italic.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.11

More monitoring improvements and a new topology view. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **2D LAN Topology Flow Map** - A new interactive hierarchical map on the Live View tab showing your full network topology with live throughput rates, device health, and client connections. Pan, zoom, and hover for details.
- **Device health for non-SNMP devices** - Devices without SNMP (Flex Mini, devices with SNMP toggled off) now show CPU, memory, and temperature on Device Health charts, sourced from the UniFi API.
- **Switch temperature monitoring** - Switch temps now appear on the temperature chart. SNMP doesn't report switch temps, so these come from the UniFi API automatically.
- **Wired client throughput** - Wired clients behind non-SNMP switches now show live throughput on the 2D map, with InfluxDB storage for historic playback.

## WiFi Optimizer

- **Gateway-only console fix** - UDM-Beast, UDM-Pro, UDM-SE, and EFG were sometimes misclassified as access points when connected through a WAN Switch. These rack-mount consoles now always stay classified as gateways.

## Fixes

- **API call optimization** - Reduced redundant UniFi API device calls from ~7/min to ~2/min with a response cache. Network-only fetches save over 500 KB per call by skipping unnecessary device and client data.
- **Container startup hang** - Stale migration locks from interrupted startups are now cleared automatically, preventing the container from hanging on restart.
- **3D map stability** - Guard against NaN geometry when device placement data contains invalid coordinates.
- **Docker healthcheck** - Start period increased from 40s to 120s to accommodate larger databases during migration.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.10

More monitoring fixes. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **Device health charts now show all monitored devices** - Devices with latency probing disabled (manually or automatically) were missing from the temperature, CPU, and memory charts. Health data comes from SNMP, not latency probes, so these charts should always be visible regardless of latency settings.
- **Flex 2.5G-8 latency probing disabled by default** - USW-Flex-2.5G-8 switches don't respond reliably to ICMP latency probes, which generated noisy data. New Flex 2.5G targets now auto-discover with latency off, and existing ones are automatically migrated on upgrade.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.9

Self-Hosted Network Monitoring reliability and live 3D map improvements. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **SNMP resilience** - a transient SNMP error on one interface no longer zeroes all interface counters for the entire device. The poller now preserves partial data when a walk encounters a bad response, and recovers on the next cycle.

- **SNMP exclusion recovery** - devices excluded from SNMP polling (after consecutive failures) are now retried after 1 hour instead of staying excluded until app restart. The failure threshold was also raised from 3 to 10 consecutive failures to avoid false exclusions during brief outages.

- **PPPoE WAN throughput** - WAN rate lookups now fall back to the logical uplink interface when the physical port has no active SNMP counters, fixing missing WAN throughput on PPPoE connections.

- **Trunk link live rates** - switch-to-switch uplink links now update on the 5-second SNMP cadence instead of lagging behind and bursting every 30 seconds. The live tick reads per-port SNMP rates directly instead of a device-level aggregate that was never written for switches.

- **Port alias filter fix** - the SNMP interface filter was dropping any port whose alias starts with "Lo" (e.g., "Loft Lower", "Lobby") because the loopback filter used a prefix match on "lo". Rebuilt the filter from actual device data to use exact matches for kernel defaults and safe prefixes for bridges.

- **Upstream Discovery ping check** - discovered upstream targets are now pinged before being proposed, filtering out unreachable hops.

- **Upstream Discovery guidance** - the Live View now guides users to run Upstream Discovery when ISP or transit targets aren't configured, with a navigation guard to prevent losing unsaved results.

- **Packet Loss Events false positives** - the loss event navigator no longer finds old data from disabled/paused targets.

- **"Last verified" showing "just now"** - fixed a timezone bug on non-UTC servers where the relative time display always showed "just now" for old timestamps.


## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.8

More fixes for monitoring and the 3D map. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Monitoring

- **WAN speed now shows on UDM gateways** - Live stats cards were missing WAN Download/Upload on UDM-Pro, UDM-SE, and UDM-Pro-Max because SNMP reported hardware descriptions instead of Linux interface names for the physical NICs. The SNMP poller now prefers ifName when it's a real interface name and the alias isn't.
- **Gateway type filter expanded** - The WAN interface extraction now uses the canonical gateway classification, picking up UCG and USG devices that were previously skipped.
- **SNMP re-detection on page load** - The Monitoring page now re-detects SNMP settings every time you visit it, avoiding stale false positives (e.g., showing SNMP v3 when the device only supports v2c).

## 3D Map

- **Live scrubbing** - The 3D map and stat cards now update as you drag the timeline scrubber, not just when you release it.
- **Arrow key scrubbing improvements** - Better UX for arrow key scrubbing with hold-to-accelerate and Shift for fast scrub.

## Fixes

- **GeoLite2 database updates no longer fail** - Downloads now extract to a staging file and swap into place after closing the reader, preventing file-in-use errors.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.7

More DNS audit improvements and a fix for missing monitoring data and intermittent errors. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Security Audit

- **NextDNS CLI detection** - The audit now recognizes NextDNS CLI as a known DNS provider alongside Pi-hole and AdGuard Home. If your LAN DNS points to a local NextDNS CLI instance, the audit identifies it automatically and treats it as a trusted provider (no score penalty). Thanks to @jedis00 for the contribution (#655).
- **IP-based DoH/DoH3 blocking detection** - Firewall rules that block DoH by destination IP (via IP groups or inline IP lists) are now recognized. This is a common deployment pattern on UniFi gateways, especially for users who prefer IP-based rules over domain or DPI-app targeting. Thanks to @jedis00 (#656).
- **Stricter DoH provider matching** - DoH block rules now require coverage of all four major providers (Cloudflare, Google, Quad9, OpenDNS) to receive credit. Previously, a rule blocking just one or two providers could satisfy the check. This eliminates false positives from partial blocks and better reflects what a comprehensive DoH-bypass prevention setup looks like.

## Fixes

- **Database reliability after config import** - Importing a configuration backup could leave the database in DELETE journal mode instead of WAL, which could cause missing monitoring data, intermittent errors, or other seemingly random issues. The app now enforces WAL mode on every startup.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.6

Important performance fix for SNMP monitoring. When we ported the monitoring stack from our internal tooling, the batched SNMP APIs didn't make it over - so the poller was doing individual round-trips for every OID on every interface. If you have monitoring enabled, this release significantly reduces CPU and memory usage. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Monitoring

- **Fix N+1 SNMP polling** - The SNMP poller was issuing ~26 individual GET requests per interface per poll cycle, each blocking a thread pool thread on a UDP socket. Replaced with batched multi-OID GET (one packet for scalar metrics) and GETBULK walks (one walk per counter column). Static interface metadata (description, name, speed, type) is now cached for 60 seconds so only counters are re-walked on each tick. CPU usage drops substantially and working set drops from ~744 MB to ~310 MB.

- **V3 discovery cache** - SNMP v3 engine discovery is now cached for 60 seconds instead of re-running on every request.

- **Filter chipset pseudo-interfaces** - Qualcomm radio USB descriptors ("Device 17cb:1109" etc.), MII register, and traffic equalizer interfaces are now excluded from monitoring. These reported meaningless counter values that produced garbage throughput rates.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.5

More improvements to Self-Hosted Network Monitoring, faster traceroutes, and a community contribution for audit rules. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Self-Hosted Network Monitoring

- **Multi-WAN 3D map** - All active WANs now render as separate access globes with their own live throughput rates, speed test results, and friendly names from your UniFi Network configs.
- **WAN detection overhaul** - The upstream tracer now reads the device's wan1...wan6 objects directly instead of relying on port_table.is_uplink, which may not be set for PPPoE, VLAN-tagged, or GRE tunnel connections. Fixes #651.
- **Faster traceroute probes** - Reduced per-hop timeout and probe count so traces complete within the deadline even on paths with silent intermediate hops.
- **Access technology selector** - Set your access network technology (GPON, DOCSIS, Active Ethernet, etc.) during upstream discovery review.
- **Target deduplication** - Re-running upstream discovery no longer creates duplicate monitoring targets.
- **Right-click WAN globe** - Context menu navigates directly to upstream discovery.
- **Historic playback per-WAN** - Historic mode now resolves rates per-WAN. Speed test lookback extended to 30 days.
- **Timeline controls** - 10x scrubber resolution, arrow key scrubbing (shift for 10x), spacebar pause/play, 0.5x playback speed.
- **WASD sensitivity** - Reduced ~33% for smoother camera control.

## Security Audit

- **Mirror-port awareness** - Port-evaluating audit rules now skip mirror/span ports, avoiding false positives on monitoring ports. Thanks @jedis00! (#650)

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.4

More 3D Live Map work - buildings from your Wi-Fi Signal Map floor plans now render in 3D with material textures, and all device types can be repositioned.

## Self-Hosted Network Monitoring

- **3D floorplan buildings** - Floor plan buildings render on the 3D map with walls, floor planes, and pitched roofs. Wall materials match what you set in the Wi-Fi Signal Map with procedural textures (brick, siding, wood, concrete, glass, doors, windows). Interior and exterior faces render differently based on winding direction
- **WAN globe** - Wireframe lat/lng globe replaces the old cloud shapes for internet nodes
- **Device repositioning** - All device types can now be right-click repositioned, including Wi-Fi and wired clients
- **Overlay and camera persistence** - Toggle states and camera position save across sessions
- **RTT precision** - 3 decimal places in the statistics table, 2 on stat cards
- **Faster ping bursts** - 0.1 s interval on macOS, reduced process concurrency to mitigate a .NET 10 ARM64 runtime bug

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.3

More monitoring improvements - this time for the Live View timeline. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Monitoring

- **Historic playback for stat cards** - The stat cards above and below the 3D map (WAN rates, latency, gateway health, fabric load) now reflect the timeline position during playback, showing point-in-time values from InfluxDB instead of only live data
- **Full map data during playback** - The 3D map now shows correct historic data for all link types during playback, including uplinks, WAN, mesh backhaul, wired clients, and switch-behind-mesh-AP links. Node badges show historic CPU, memory, temperature, and fabric rates. Cloud stats show historic latency.
- **Playback speed control** - +/- buttons let you adjust playback speed from 1x (real-time) through 1440x, with the rate displayed between the buttons
- **Growing scrubber window** - The timeline's left edge is anchored at page load, so the window grows as you leave the page open instead of dropping older time periods
- **Historic badge** - Click the "Historic" badge to snap back to live. Tooltip only appears when in historic mode.
- **Investigation timestamps** - Packet loss and SFP anomaly investigation results now include the local date and time in parentheses alongside the relative "19h ago" format
- **GetWansAsync performance** - The WAN port table structure is now cached for 30 seconds instead of hitting the UniFi controller API on every 2-second live poll

## Fixes

- **SNMP concurrency limit** - Fast-tier and medium-tier SNMP polls previously fanned out to all devices with no concurrency limit, which could overwhelm the .NET runtime on macOS native installs. Now bounded to 8 concurrent SNMP operations across all tiers.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.2

More monitoring upgrades. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Monitoring

- **Tabbed navigation** - Monitoring is now organized into five tabs: Live View, Network Performance, Device Stats, SFP Stats, and Setup. Each tab mounts/unmounts its charts independently so switching is fast and resource-friendly.
- **Live View stat cards** - Real-time summary cards showing WAN download/upload (from SNMP), gateway RTT and packet loss, ISP and transit mean latency, gateway CPU/memory/temperature, and total fabric ingress/egress throughput.
- **Statistics table** - Per-target mean, min, max, P95, and P99 for RTT plus mean and max for loss, rendered below the latency charts. Updates with the selected time range and badge filters.
- **WAN throughput chart** - When viewing ISP, Transit, or Internet latency, a third chart shows summed WAN interface throughput over the same time window so you can correlate latency spikes with traffic patterns.
- **Packet loss investigation** - A "Packet Loss Events" button finds the most recent 1-minute-averaged loss event across all WAN targets and navigates the chart to it. Back/forward arrows step through events chronologically.
- **SFP threshold alerts** - New alert events for PON RX power below -25 dBm, TX power above 4 dBm, and temperature above 75 C (87 C for non-PON). Default rules auto-created on startup. Hysteresis prevents flapping.
- **SFP anomaly investigation** - Similar to packet loss, finds the most recent SFP temperature or signal anomaly and jumps the chart to it.

## Setup & UX

- **InfluxDB recovery flow** - When the InfluxDB connection fails (expired token, unreachable), the Setup tab now shows "Update Token" (links to Settings) and "Re-run Setup" (re-provisions inline) buttons instead of requiring manual navigation.
- **Wizard improvements** - The status card updates immediately when provisioning succeeds; Continue just collapses the wizard panel. Token field unlocks the provision button on input, not blur. Password managers no longer autofill the token field.
- **Tab availability after restart** - Tabs are available immediately based on persisted config, no waiting for health checks to complete. Setup tab auto-selects when there's a known error.

## Other

- **Event catalog** - The Alerts Event Type Patterns dialog now lists all monitoring events (target offline/recovered/sustained loss, SFP thresholds) and WAN data usage events.
- **Component extraction** - Latency Targets and SFP Modules cards extracted into standalone Razor components.
- **Chart cleanup** - Removed fullscreen coupling from chart JS modules (tabs handle lifecycle). Category switching preserves the selected time window. Popover inputs stay in sync on preset changes.
- **Upstream tracer** - Renamed "Access hop" to "ISP hop" for clarity.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.1

More monitoring polish. See [v1.17.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.17.0) for what's new in v1.17.0+

## Monitoring

- **SFP management** - All detected SFP modules now visible on the Monitoring page with controls to add or remove them from monitoring, and to tag modules as PON or standard SFP. Collapsible table with pagination, sorted by device IP.
- **SFP time-series charts** - RX/TX optical power and temperature charts for monitored SFPs, with the same date/time filtering and module selector badges as the latency and device health charts. Defaults to a 24-hour window.
- **Manual latency targets** - Add custom latency targets with configurable name, address, type (Custom, Internet, ISP, Transit), probe mode (ICMP or TCP), and polling interval.
- **Per-target probe cadence** - Change the polling interval on any latency target directly from the table (2 s to 5 m).
- **Chart polling optimization** - All chart modules now pause data fetching when scrolled out of view or when the 3D map is fullscreen, and catch up immediately when visible again. Reduces unnecessary API calls and fixes the stutter caused by background chart refreshes competing with the WebGL renderer.
- **GPON Rx power range** - Corrected the displayed healthy range from -3 to -25 dBm to the actual ITU-T spec range of -15 to -25 dBm typical.
- **Dashboard ONT Stats** - Now shows only PON modules (GPON / XGS-PON), not regular SFPs that happen to be monitored.
- **Aggregate window scaling** - InfluxDB queries now scale proportionally (~150 data points) regardless of time range, preventing browser memory issues on very wide custom date ranges.

## Fixes

- **Negative packet loss** - Duplicate ICMP replies no longer produce negative loss percentages. The parser now clamps received count to never exceed sent.
- **3D map WASD navigation** - Keyboard shortcuts no longer fire while typing in input fields.
- **Button tooltips** - Clicking a button no longer triggers its tooltip; tooltips are hover-only on all buttons.
- **Latency chart mobile layout** - Time range controls (arrows + presets) now wrap as a unit on narrow screens instead of splitting apart.
- **Input validation** - Manual latency target addresses are validated as IP or hostname before saving.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.17.0

The big one. Full time-series network monitoring with a 3D real-time traffic visualization, latency and device health charting, and automated upstream path discovery. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what came before.

## What's New

- **Network Monitoring** - SNMP-based polling with InfluxDB 2.x storage. Interface counters, device health, latency probes, SFP optical levels, and WiFi client snapshots - all with configurable retention and a setup wizard that handles bucket and token provisioning automatically.
- **3D LAN Flow Map** - Real-time Three.js visualization of your entire network topology with directional particle-flow traffic. WASD navigation, fullscreen mode, double-click any client to open their performance dashboard. Filter by band, network, or search by name.
- **Upstream Path Discovery** - Automated traceroute-based discovery of your ISP's access infrastructure, transit networks, and internet service endpoints. Identifies your OLT/CMTS, ISP edge routers, and transit ASNs with both ICMP and UDP probes.
- **SFP/ONT optical monitoring** - Live RX/TX power, temperature, voltage, and bias current for PON SFP modules. Auto-detects GPON vs XGS-PON from a database of common modules (Calix, Zyxel, Nokia, Leox, ODI, SourcePhotonics, and more). Shows a 2.5 Gbps upgrade hint for GPON modules on UCG/UXG-Fiber gateways.

## Latency & Packet Loss

- Time-series RTT and packet loss charts across four target categories - LAN fabric, ISP access hops, transit networks, and internet services
- Per-target filter badges with solo-click UX
- Time range presets (15m to 30d), shift arrows to pan the window, and a custom date range picker
- Sub-15 ms query performance via InfluxDB tag-indexed queries

## Device Health

- Temperature, CPU, and Memory charts per network device
- Gateway temperature via LM-SENSORS SNMP OID
- AP CPU collection via hrProcessorLoad walk (ssCpuIdle not supported on APs)
- Memory calculation excludes cache to show actual usage
- Dashboard device cards show live CPU, memory, and temperature at a glance

## Security Audit

- **DNS VIP support** - New TrustedDnsRedirectTargets setting lets operators allowlist virtual IPs (keepalived, HAProxy, anycast) as valid DNAT redirect targets. Thanks to @jedis00 for the contribution.

## Fixes

- **Firmware 5.1.12** - Bumped max supported firmware
- **Reverse proxy docs** - Clarified .env configuration for reverse proxy setups
- **Settings defaults** - InfluxDB bucket defaults now match the setup wizard
- **API endpoint refactor** - Moved from inline Program.cs to Endpoints/*.cs modules

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.11

Multiple WAN speed test server support and smarter Config Optimizer checks. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## Client WAN Speed Test

- **Multiple external speed test servers** - You can now configure more than one external OpenSpeedTest server in Settings. The speed test page shows a dropdown when you have multiple, with a configurable default.
- **Speed, Latency, and Jitter charts** - New tabbed charts with per-server series, a time slider from 1 hour to all time, and click-to-scroll from chart points to results in the table.
- **Server filter** - Filter the history table and charts by server, alongside the existing device filter.

## Config Optimizer

- **Trunk ports excluded from Flow Control check** - Ports connecting switches and/or gateways on both sides are no longer flagged when Flow Control is disabled. Disabling FC on high-speed inter-switch links is common and often optimal. Port profiles with "trunk" in the name are also excluded.

## Threat Dashboard

- **IPS v2 detection fix** - Sites running IPS v2 now correctly show threat data. Previously, a successful v2 response was being ignored in favor of the v1 endpoint. Thanks to @jedis00 for the fix!

## Performance Tweaks

- **Fan control standby PWM reverted to stock** - Left at the factory default (20) since the standby role isn't fully understood.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.10

Fixes and a navigation improvement. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## WAN Steering

- **Promoted to top-level nav item** - WAN Steering now has its own icon in the sidebar instead of being nested under Adaptive SQM.

## Config Optimizer

- **SQM firmware regression warning** - UCG-Fiber, UXG-Fiber, UCG-Max, and UXG-Max on firmware newer than 5.0.10 with WAN speeds above 500 Mbps now get a performance suggestion. SQM download throughput regressed to ~800 Mbps or less on these models with recent firmware.

## Fixes

- **Threat Dashboard client name resolution** - The UniFi API returns device fingerprinting fields as floats (e.g. `4.0` instead of `4`), which broke client list deserialization. The JSON converter now handles float-typed numbers.
- **WiFi Optimizer propagation data loading** - Fixed an error that occurred when the Blazor circuit ended while background health evaluation was still running.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.9

More audit fixes for advanced network setups. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+.

## Security Audit

- **L3 switch-routed VLAN support** - Networks routed by a switch (instead of the gateway) are now properly included in the audit. Previously, enabling L3 switching on a VLAN would cause it to disappear from the audit entirely, leading to false positives for cameras and missing firewall rule checks.

- **Inter-VLAN routing network excluded** - The system "Inter-VLAN routing" network (used internally by UniFi for L3 switching) is no longer shown in the Network Reference list or treated as a user network.

- **PPSK subnet mismatch false positives fixed** - Devices on PPSK SSIDs (where the AP assigns VLANs by password) no longer trigger incorrect "VLAN Subnet Mismatch" warnings when UniFi temporarily reports the wrong network assignment.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.8

More fixes and improvements. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## Security Audit

- **Cellular WAN DNS false positive fixed** - The DNS audit no longer flags cellular WAN interfaces (U5G, LTE modems) for missing static DNS. UniFi doesn't allow DNS configuration on cellular WANs, so the warning was a false positive.

## Wi-Fi Optimizer

- **Roaming Assistant reads SSID-level settings** - Newer UniFi Network versions moved Roaming Assistant from per-AP radio settings to per-SSID WLAN config. The optimizer now checks SSID-level settings first, with a fallback to per-AP for older controller versions. Supports both 5 GHz and 6 GHz bands.

## Fixes

- **IPv6 binding support** - The app now binds to both IPv4 and IPv6 interfaces instead of IPv4 only. Users on IPv6-only or dual-stack networks can now reach the web UI without extra configuration.
- **syslog-ng persist file moved to tmpfs** - The volatile log tweak now also redirects syslog-ng's persist file from eMMC to tmpfs, reducing unnecessary flash writes on UniFi gateways.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.7

More device support updates. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## Product Catalog

- **UDM-Beast support** - Added the new Dream Machine Beast (14-port, 25 Gbps rack console) to the product database with device icon
- **7 additional new products** - Added EAV-24-PoE, EAVAGG, EAVBRIDGE, ENVR-Core, U-AirWire, and gen2 hardware revisions for USW-Lite-16-PoE and USW-24-PoE from Ubiquiti's latest public.json catalog

## Performance Tweaks

- **Firmware gate bumped to UniFi OS 5.1.11** - PerfTweaks deployment now supported on the latest firmware

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.6

More Zyxel GPON stick compatibility fixes. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## SFP Tweaks

- **Recommend V2.50 firmware for Zyxel PMG3000-D20B** - The V1.00 firmware branch has an incomplete auto-negotiation state machine that can fail to converge at 2.5 G after host reboots. V2.50 fixes this and defaults to 2.5 G out of the box - no manual SFP configuration needed. The compatibility dialog now leads with this recommendation and links to the community firmware archive.
- **Fix Zyxel lanpcs command parameters** - Corrected the `onu lanpcs` command for V1.00 users who can't upgrade (parameter and frame size fixes based on firmware RE findings). The V1.00 workaround is still available but collapsed by default.
- **General GPON stick guidance** - Added a note that firmware upgrades may help other Lantiq and Realtek-based sticks with similar auto-negotiation issues.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.5

More SFP tweaks improvements and a Wi-Fi Optimizer fix. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## SFP Tweaks

- **Boot scripts wait for carrier before loading module** - SFPs like the Zyxel PMG3000 need ~15 seconds after boot to configure their SerDes for 2.5 G auto-negotiation. The boot scripts now wait up to 90 seconds for a 1 G link before loading the SGMII+ module, avoiding a race condition that could leave the link down. If no link appears (e.g., the SFP is hard-locked at 2.5 G), the module loads anyway. The script also backgrounds itself so it doesn't block other on_boot.d scripts.
- **Carrier wait status in UI** - After deploying or rebooting, the tweak card now shows an informational note explaining the link wait period instead of immediately showing an error state.
- **Zyxel frame size corrected** - Updated the `onu lanpcs` command in the Zyxel compatibility instructions to use frame size 9990 instead of 1518.

## Wi-Fi Optimizer

- **Channel Issues tab shows full details** - Issue entries on the Channel Issues tab now show their detail text, matching the behavior of the main audit issues list.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.4

More fixes for the SFP SGMII+ patch and Client Performance page. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## Performance Tweaks

- **GPON stick pre-flight instructions** - The SFP tweak cards now include a compatibility dialog with step-by-step instructions for sticks that won't negotiate 2.5 G cleanly with the UniFi host. Includes Zyxel PMG3000-D20B-specific commands for configuring auto-negotiation and persisting across reboots.

## Client Performance

- **Retry button actually retries** - The Retry button on "Device Not Found" and "Device Offline" screens now does a full page reload so it picks up your current IP. Previously it would retry within the same session, which couldn't detect a new IP after switching networks (e.g., from cellular to Wi-Fi).

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.3

Patch release for Performance Tweaks. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+

## Performance Tweaks

- **Fixed SSD usage display on UniFi OS v5.1+** - The MongoDB SSD status check used a path pattern that only matched old-style `/volume1` mounts, not the `/volume/<uuid>/` structure introduced in UniFi OS 5.1.
- **SFP+ tweak count no longer inflated** - Port 6 and Port 7 SFP+ patches are mutually exclusive for now, so the Active Tweaks counter counts them as a single slot instead of showing 2.
- **Clarified firmware/reset survival table** - Factory reset row now accurately states that boot scripts and custom modules will be wiped, with SSD data depending on reset options. OS upgrade action points to the status indicators rather than a manual CLI check. Table scrolls horizontally on mobile.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.2

Two additions - SFP+ Port 6 support for Performance Tweaks and a udm-boot safety check for WAN Steering. See [v1.16.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.16.0) for what's new in v1.16.0+.

## Performance Tweaks

- **SFP+ Port 6 (eth5) SGMII+ 2.5 G support** - The SGMII+ patch now supports both SFP+ ports on the UCG-Fiber and UXG-Fiber. Port 6 appears as its own card above the existing Port 7 card, with the same status checking, deploy, and remove flow. The two patches are mutually exclusive - each module independently saves and restores the MAC sync polling loop's port bitmap, so loading both would corrupt the restore state. The UI blocks deployment when the other port's patch is active and explains why.

## WAN Steering

- **UDM Boot status check** - WAN Steering now checks whether udm-boot is installed and shows a warning with a one-click install button when it's missing. Without udm-boot, the boot script that restores iptables rules won't run after a reboot or firmware update, silently breaking WAN Steering.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.1

Two fixes for Performance Tweaks.

- **SFP compatibility note for GPON sticks** - Added a warning on the SFP+ 2.5G SGMII+ Patch card noting that Zyxel PMG3000-D20B support is being tested, and that other GPON sticks may not negotiate 2.5G cleanly with the UniFi host. Feel free to try the patch, but be prepared to remove it if the link doesn't stabilize.
- **Fixed CRLF in perf tweak scripts on Windows** - Shell scripts embedded in the Windows MSI could be deployed with Windows line endings, breaking execution on the gateway. Scripts are now normalized to Unix line endings before deploying.

## What's New

For users upgrading from v1.15.0, here's what landed in the v1.15.x patches:

- **External WAN Speed Test Server** - Settings-driven deployment with a ready-to-copy deploy command, interactive deploy script with `--update` mode, and accurate HTTPS browser guidance.
- **SQM monitor reliability** - Replaced netcat HTTP server with busybox httpd, fixing a race condition that caused ~30 watchdog restarts per hour and hammered eMMC.
- **GPON/XGS-PON afternoon relief** - Congestion profiles model the 3-5 PM commute gap, and baselines interpolate at 15-minute intervals for smoother rate transitions.
- **WAN speed test throughput** - Raised TCP autotuning ceilings and enabled BBR congestion control in the speedtest container, fixing single-stream throughput caps on high-RTT links.
- **WAN link speed override** - Override auto-detected WAN port speed in SQM config for SFPs that report lower than actual.
- **VLAN-tagged and GRE WAN interfaces** - WAN Steering now discovers WANs on VLAN-tagged interfaces and GRE tunnels from LTE/5G modems.
- **Filter-to-device toggle** - Click the funnel icon next to any device in speed test history tables to filter results to that device.
- **UniFi OS Server compatibility** - Fixed string-typed integers in network config responses that broke Config Optimizer, Device SSH Test, and Adaptive SQM on some consoles.
- **Speedtest container BBR fallback** - Container now boots cleanly on kernels without the BBR module (Synology, QNAP, some Proxmox/LXC).

## Performance Tweaks

- **New gateway optimization system** - Deploy and monitor optimizations on UCG-Fiber, UXG-Fiber, and UCG-Max directly from the UI. Four tweaks: fan control PID tuning for earlier fan engagement, MongoDB offload from eMMC to NVMe SSD with automated backup, journald volatile logging with syslog-ng eMMC route disabling, and SFP+ 2.5G SGMII+/HSGMII kernel patch for GPON ONT modules. Each tweak knows which gateway models it supports.
- **On-demand health checks and safe deploy** - SSH-based health checks show fan speeds, CPU temps, bind mounts, SFP registers, and eMMC routes. Deploy confirmation with backup verification and warranty acknowledgment. Boot script version checking with one-click updates. Firmware gating through 5.1.10.
- **Removal and cleanup** - Every tweak has a proper removal path with confirmation: SDB stock reset for fan control, clean MongoDB SSD-to-eMMC migration, config restoration for journald/syslog-ng, and kernel module unload for SFP.

## Config Optimizer

- **Flow Control consistency check** - Flags individual switch ports and port profiles that have Flow Control explicitly disabled when the global setting is enabled. Helps catch accidental overrides that can cause packet loss on trunk links.

## Adaptive SQM

- **Configurable speedtest boot delay** - Optional per-WAN delay before the first speedtest after gateway boot. Useful for connections that take time to stabilize after a reboot - Starlink, cellular modems, GPON/XGS-PON SFP ONTs that need time to negotiate with the OLT.

## Security Audit

- **Improved UNAS detection** - UNAS devices share Ubiquiti OUI prefixes with Protect cameras, which made the MAC-based detector misclassify them. Now uses the V2 device API's drive_devices array to positively identify NAS devices at highest detection priority.
- **Cloudflare IP list tolerance** - Users who add a few personal management IPs alongside Cloudflare ranges in a port forward restriction were getting a misleading "consider restricting to Cloudflare IPs" recommendation. Now tolerates up to 10 individual host IPs without losing the "properly restricted" classification.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.16.0

v1.16.0 introduces the Performance Tweaks system - deploy and monitor gateway optimizations directly from the UI. Plus Flow Control consistency checking, configurable SQM boot delays, and improved device classification.

## What's New

For users upgrading from v1.15.0, here's what landed in the v1.15.x patches:

- **External WAN Speed Test Server** - Settings-driven deployment with a ready-to-copy deploy command, interactive deploy script with `--update` mode, and accurate HTTPS browser guidance.
- **SQM monitor reliability** - Replaced netcat HTTP server with busybox httpd, fixing a race condition that caused ~30 watchdog restarts per hour and hammered eMMC.
- **GPON/XGS-PON afternoon relief** - Congestion profiles model the 3-5 PM commute gap, and baselines interpolate at 15-minute intervals for smoother rate transitions.
- **WAN speed test throughput** - Raised TCP autotuning ceilings and enabled BBR congestion control in the speedtest container, fixing single-stream throughput caps on high-RTT links.
- **WAN link speed override** - Override auto-detected WAN port speed in SQM config for SFPs that report lower than actual.
- **VLAN-tagged and GRE WAN interfaces** - WAN Steering now discovers WANs on VLAN-tagged interfaces and GRE tunnels from LTE/5G modems.
- **Filter-to-device toggle** - Click the funnel icon next to any device in speed test history tables to filter results to that device.
- **UniFi OS Server compatibility** - Fixed string-typed integers in network config responses that broke Config Optimizer, Device SSH Test, and Adaptive SQM on some consoles.
- **Speedtest container BBR fallback** - Container now boots cleanly on kernels without the BBR module (Synology, QNAP, some Proxmox/LXC).

## Performance Tweaks

- **New gateway optimization system** - Deploy and monitor optimizations on UCG-Fiber, UXG-Fiber, and UCG-Max directly from the UI. Four tweaks: fan control PID tuning for earlier fan engagement, MongoDB offload from eMMC to NVMe SSD with automated backup, journald volatile logging with syslog-ng eMMC route disabling, and SFP+ 2.5G SGMII+/HSGMII kernel patch for GPON ONT modules. Each tweak knows which gateway models it supports.
- **On-demand health checks and safe deploy** - SSH-based health checks show fan speeds, CPU temps, bind mounts, SFP registers, and eMMC routes. Deploy confirmation with backup verification and warranty acknowledgment. Boot script version checking with one-click updates. Firmware gating through 5.1.10.
- **Removal and cleanup** - Every tweak has a proper removal path with confirmation: SDB stock reset for fan control, clean MongoDB SSD-to-eMMC migration, config restoration for journald/syslog-ng, and kernel module unload for SFP.

## Config Optimizer

- **Flow Control consistency check** - Flags individual switch ports and port profiles that have Flow Control explicitly disabled when the global setting is enabled. Helps catch accidental overrides that can cause packet loss on trunk links.

## Adaptive SQM

- **Configurable speedtest boot delay** - Optional per-WAN delay before the first speedtest after gateway boot. Useful for connections that take time to stabilize after a reboot - Starlink, cellular modems, GPON/XGS-PON SFP ONTs that need time to negotiate with the OLT.

## Security Audit

- **Improved UNAS detection** - UNAS devices share Ubiquiti OUI prefixes with Protect cameras, which made the MAC-based detector misclassify them. Now uses the V2 device API's drive_devices array to positively identify NAS devices at highest detection priority.
- **Cloudflare IP list tolerance** - Users who add a few personal management IPs alongside Cloudflare ranges in a port forward restriction were getting a misleading "consider restricting to Cloudflare IPs" recommendation. Now tolerates up to 10 individual host IPs without losing the "properly restricted" classification.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.10

More fixes for speed test path analysis, IPv6 support, and device classification. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## Speed Tests

- **CPU-bound disclaimer for device speed tests** - When iperf3 results to an AP or cellular modem are 25%+ below the link's line rate, the path analysis now shows a "results limited by device CPU, not network" disclaimer - the same one already used for gateway tests. Previously this only triggered for high-end APs exceeding 4.4 Gbps.

- **Bottleneck description now names the correct device** - The bottleneck label (e.g., "2.5 Gbps link at Switch Main (port 3)") was incorrectly attributing the port to the target device instead of the upstream switch or gateway. Now tracks which device actually owns each port, so the description always names the right one.

## Fixes

- **IPv6 ULA addresses recognized as local** - Users with IPv6 Unique Local Addresses (fc00::/7, typically fd00::/8) had their local hosts misclassified as public WAN IPs, affecting path analysis, geo enrichment, DNS detection, and threat filtering.

- **UNAS no longer misidentified as Protect camera** - The UniFi NAS (UNAS) was being flagged as a security camera needing Security VLAN placement because its model name (e.g., "UNAS-Pro") matched the "Pro" camera pattern.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.9

More Adaptive SQM and WAN Steering fixes. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## Adaptive SQM

- **WAN link speed override** - You can now override the auto-detected WAN port speed in the SQM config. Useful when your SFP supports a higher speed than the gateway reports (e.g., a 2.5 G SFP showing as 1 G). The override is used as the shaping ceiling.
- **Tighter speedtest probe rate** - The probe rate during speed tests is now 3% above your max shaping rate instead of 5% above line rate, so TC stays transparent without overshooting your actual link speed.
- **Dynamic burst sizing restored** - HTB burst now scales with your shaping rate again (1500-5000 bytes), eliminating drop_overmemory events at higher speeds.

## WAN Steering

- **VLAN-tagged and GRE interfaces now discovered** - WAN Steering wasn't picking up firewall marks for VLAN-tagged WANs (like `eth4.100`) or GRE tunnels from LTE/5G modems. These WANs showed up in the UI but couldn't actually steer traffic.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.8

More fixes for WAN speed testing. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## WAN Speed Test

- **Disabled WANs no longer attributed in speed tests** - If you had a secondary WAN that was disabled in UniFi, speed tests could still tag results with both WANs when download speeds exceeded the configured ISP rate. Now verifies which WANs are actually active on the gateway before attributing.
- **Speed-based multi-WAN detection less trigger-happy** - Added 25% tolerance so ISP overprovisioning and burst headroom don't falsely trigger multi-WAN attribution.
- **Fixed WAN name showing as "WAN1"** - A service registration bug caused WAN identification to silently fail on server-based speed tests, leaving the WAN name blank (displayed as "WAN1" in the UI).

## All Speed Tests

- **Filter-to-device toggle** - Click the funnel icon next to any device name in speed test history tables to filter results to just that device. Works on LAN Speed Test, Client Speed Test, and Client WAN Speed Test pages.
- **Map time range no longer filters the results table** - Changing the map's time range filter was incorrectly filtering the history table above it. Now only affects the map pins.

## Security

- **NuGet package updates** - Resolves known vulnerabilities in MailKit and System.Security.Cryptography.Xml (transitive via EF Core).

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.7

More fixes for Adaptive SQM. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## Adaptive SQM

- **Fixed shaping rate double-discount on connections near line rate** - GPON and XGS-PON connections provisioned just under physical link speed (e.g. 965 Mbps on a 1 GbE link) were being shaped 25+ Mbps lower than the UI displayed. The safety cap was being applied to a pre-clamped AbsoluteMax, stacking three ceilings multiplicatively. Link speed is now applied as a final clamp instead, so the congestion range displayed in the UI matches what gets deployed.

- **Reverted burst tuning to stock 1500b** - The scaled burst sizing (up to 5 KB) creates bursty HTB send patterns that increase fq_codel queue depth variance, showing up as latency jitter under load. Reverted to stock pending per-connection configurability.

- **Speedtest probe now runs 5% above line rate** - The TC rate set during the speedtest measurement is now always safely above physical line rate, so the probe runs truly unshaped. The UI parameter has been renamed from "Absolute Max" to "Speedtest Probe Rate" to reflect what it actually does.

- **Smart Queues validation now tolerates 1 Mbps difference** - UniFi Network EA/RC has a bug where Smart Queues breaks unless the rate is set to interface speed minus 1. The pre-deploy validation now accepts this.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.6

One fix this release: the speedtest container now boots cleanly on kernels that don't have the BBR TCP module loaded. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## Fixes

- **Speedtest container fails to start on kernels without BBR** - The speedtest container previously tried to enable BBR congestion control via Docker compose sysctls, which hard-failed `docker compose up` on hosts whose kernel doesn't ship the `tcp_bbr` module (Synology, QNAP, some Proxmox / LXC setups). The sysctl is gone, and the container now inherits whatever CC the host has configured. If bbr is loaded and set as the default on the host, speedtests still use it; the entrypoint prints the current CC and, if applicable, shows the exact host-side command to enable bbr (`modprobe tcp_bbr` or `sysctl -w net.ipv4.tcp_congestion_control=bbr`).

  **If you hit this error, grab the latest compose file and upgrade:**
  ```bash
  curl -o docker-compose.yml https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/docker/docker-compose.prod.yml
  docker compose pull && docker compose up -d
  ```

  (macOS with port mapping instead of host networking: `curl -O https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/docker/docker-compose.macos.yml && docker compose -f docker-compose.macos.yml pull && docker compose -f docker-compose.macos.yml up -d`)

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.5

More small fixes and a speed-test tuning improvement. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+.

## WAN Speed Test

- **Higher single-stream throughput on high-RTT links** - Raised TCP autotuning ceilings to 32 MB in the speedtest container and enabled BBR congestion control. Previously the container's bridge namespace started at kernel defaults, capping single-stream throughput around 225 Mbps on 100 ms RTT paths regardless of real link capacity. Measurements now reflect link capacity instead of being bound by cubic's loss-driven cwnd halving.

## Client Performance

- **Signal Map defaults to the client's band** - The Signal Map in Client Performance used to always default to 5 GHz, so Wi-Fi 6E clients on 6 GHz showed no map points until you manually switched the band. It now follows the connected client's band automatically and updates on roam. You can still override it from the dropdown.

## Fixes

- **Config Optimizer, Device SSH Test, and Adaptive SQM failing on some controllers** - Some UniFi Consoles return int fields in the network config response (`ipv6_ra_valid_lifetime`, `upload_kilobits_per_second`, etc.) as strings instead of numbers, which broke deserialization of the whole network config and cascaded into Config Optimizer, Device SSH Test, and Adaptive SQM's WAN rate detection. Every int field on the network config and the nested WAN provider capabilities object now accepts strings, empty strings, and nulls without throwing.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.4

Quick follow-up to v1.15.3 - replaced the SQM monitor's netcat HTTP server with busybox httpd to fix a long-standing race condition. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## Adaptive SQM

- **SQM monitor endpoint replaced with busybox httpd** - The netcat-based HTTP server could only handle one request at a time. With multiple consumers polling (Grafana, watchdog, the app), requests raced for a single slot - the watchdog would find the port dead during nc's restart gap and restart the service ~30 times/hour, hammering eMMC. Now uses busybox httpd + CGI, which handles concurrent connections properly. The watchdog cron is also removed since httpd doesn't have this problem.

- **GPON/XGS-PON afternoon relief window** - Congestion profiles now model the 3-5 PM commute gap where usage dips before the evening streaming peak. Baselines also interpolate between hours at 15-minute intervals for smoother rate transitions instead of stepping hourly.

## Fixes

- **UniFi OS Server boolean parsing** - UniFi OS Server returns some network config fields as strings ("true") instead of native booleans, which broke device discovery, AP fetching, wireless clients, and WAN interface detection. Added a flexible converter to handle both formats.

- **Gateway netcat compatibility** - SQM deploy now installs `netcat-openbsd` on gateways that only have the busybox version (e.g., UXG-Fiber). (Superseded by the httpd change above, but still included for users who deployed v1.15.3 - the netcat package remains harmless.)

- **Hardware Acceleration severity** - Upgraded from Info to Recommendation with a clearer description about the SFE fast forwarding path impact.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.3

More fixes and improvements for Adaptive SQM and gateway compatibility. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+

## Adaptive SQM

- **GPON/XGS-PON afternoon relief window** - Congestion profiles now model the 3-5 PM commute gap where usage dips before the evening streaming peak. Baselines also interpolate between hours at 15-minute intervals for smoother rate transitions instead of stepping hourly.

- **Gateway netcat compatibility** - SQM deploy now installs `netcat-openbsd` on gateways that only have the busybox version (e.g., UXG-Fiber). Busybox nc lacks the `-q` flag needed for clean connection teardown on the TC monitor endpoint.

## Fixes

- **UniFi OS Server boolean parsing** - UniFi OS Server returns some network config fields as strings ("true") instead of native booleans, which broke device discovery, AP fetching, wireless clients, and WAN interface detection. Added a flexible converter to handle both formats.

- **Hardware Acceleration severity** - Upgraded from Info to Recommendation with a clearer description about the SFE fast forwarding path impact.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.2

Quick patch for a dependency security update. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+.

## Security

- **Upgraded Scriban templating library** - Updated from 5.12.0/6.5.2 to 7.0.6, addressing multiple known vulnerabilities. Scriban is used internally for alert notification templates.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.1

Quick follow-up to v1.15.0. See [v1.15.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.15.0) for what's new in v1.15.0+.

## External WAN Speed Test Server

- **Settings-driven deploy** - Configure the external server in Settings once, and a ready-to-copy deploy command appears with everything pre-filled. No more double configuration.
- **Deploy script overhaul** - Interactive mode with guided prompts, `--update` mode for pulling new files without reconfiguring, and downloads via tarball instead of a brittle file list. Works on Linux and macOS.
- **Server ID linking** - Auto-generated identifier ties deployed containers to speed test results, foundation for multi-server support down the road.
- **Accurate HTTPS guidance** - Chrome and Edge enforce Private Network Access restrictions; Firefox and Safari don't. All warnings and docs updated to reflect tested browser behavior. Links to NetworkOptimizer-Proxy which has the WAN route pre-configured.

## Fixes

- **Card spacing on Settings and Security Audit** - Cards now have consistent spacing matching the Dashboard layout.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.15.0

v1.15.0 adds API key authentication for UniFi consoles and a bunch of improvements since v1.14.0.

## What's New

For users upgrading from v1.14.0, here's what landed in the v1.14.x patches:

- **WAN speed test accuracy overhaul** - 100 MB download chunks, TCP warmup, and more streams. Accuracy on congested links improved dramatically (565 Mbps to 812 Mbps on one test link). Plus tabbed WAN History charts for Speed, Latency, Loaded Latency, and Jitter.
- **Signal-adjusted heatmap** - Overlay real client signal measurements on the Signal Map and calibrate per-AP propagation models against measured data. Reveals obstructions and dead spots your model alone might miss.
- **Adaptive SQM GPON/XGS-PON profiles** - Separate congestion profiles for fiber types, congestion severity slider, editable latency threshold, and a non-linear latency response curve that's gentle on mild spikes but aggressive on sustained congestion. Ping adjustments now run every 1 minute instead of every 5, verified with no impact to gateway performance or packet routing.
- **WAN stability detection** - Wansteer detects WAN flapping and enters backoff mode to prevent kernel errors during failover. Plus SFE flush coalescing and reconciler drift fixes.
- **RF-aware load imbalance** - Load imbalance health checks use the Signal Map's propagation model to suppress false positives for APs in separate coverage zones.
- **Gateway-only consoles filtered** - UDM-Pro, UDM-SE, UDM-Pro-Max, and EFG no longer show phantom radio entries in the AP list.

## Settings

- **Network API Key authentication** - Connect to your UniFi Console using an API key instead of username and password. Generated in UniFi Network under Integrations -> Create New API Key. The key is encrypted at rest and never exposed in logs or the UI. Useful for sites where you don't necessarily want to create a Local Admin, or when you're using UniFi Fabrics which no longer lets you create Local Admin users.

## Client Speed Test

- **Personal best tracking** - Beat your highest download speed and you might see something fun.
- **Note for WAN speed test users** - If you run an [External WAN Speed Test Server](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md#external-wan-speed-test-server-optional), update it too so the client-side UI picks up the new features.

## Wi-Fi Optimizer

- **Roaming failure deep links** - Health score roaming failure issues now link directly to the affected AP pair in the Roaming tab, so you can investigate without hunting for it.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.11

More Adaptive SQM refinements - connection type profiles, congestion tuning, and smarter latency response. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## Adaptive SQM

- **GPON and XGS-PON profiles** - FTTH is now split into separate GPON and XGS-PON connection types with tailored congestion schedules. GPON dips to 96.5% during streaming prime time, while XGS-PON's 10G headroom means it barely needs to dip at all (98%). Auto-detection maps common fiber service names to the right profile.
- **Congestion severity slider** - New user-tunable slider (0.75x to 1.25x) that scales the magnitude of congestion schedule dips. Higher values make shaping more aggressive during peak hours, lower values soften the schedule.
- **Editable latency threshold** - The latency threshold is now an editable field instead of a fixed default. Only persists to the database when you override it, so future profile default changes are picked up automatically.
- **Non-linear latency response** - Latency adjustments now use an (n+1)^0.7 curve instead of linear scaling. Mild spikes (1-2 deviations) get a gentle nudge while sustained congestion (4+ deviations) still triggers aggressive shaping. GPON/XGS-PON default threshold lowered to 1.0 ms since fiber latency is clean enough to detect mild congestion.
- **Safety cap is now baseline-proportional** - For fiber types, the safety cap scales with the congestion schedule instead of being a flat ceiling. This eliminates the dead zone where latency spikes were detected but produced no visible rate change.
- **1-minute ping adjustment interval** - Down from 5 minutes for faster response to changing conditions.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.10

More Wi-Fi Optimizer improvements. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## Wi-Fi Optimizer

### Signal Map

- **Signal-adjusted heatmap** - Toggle the "Signal Data" button to overlay real client signal measurements on the propagation map, per AP-client connection. Each AP's model is calibrated against measured data, revealing problem spots, obstructions, and more accurately reflecting RF propagation where you have the data for it.
- **Signal data time filter** - Filter signal data markers by time range so you can focus on recent measurements or look at historical data.
- **Band persistence** - The selected band is remembered across sessions so you don't have to reselect it each time.

### Roaming

- **Deterministic roaming topology layout** - APs in the roaming topology diagram are now sorted by name, so the layout is consistent across page loads.

## Speed Test Map

- **LAN speed test results in AP popup** - AP markers on the speed test map now show recent LAN speed test results for that AP.

## Settings

- **SSH setup guide improvements** - Fixed mobile app SSH navigation paths and clarified SSH setup instructions.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.9

More fixes for Adaptive SQM and WAN Steering. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## Adaptive SQM

- **Fixed "No WAN Connections Detected" after session expiry** - When the UniFi session expired, several API methods didn't re-authenticate automatically, causing the SQM page to show no WAN interfaces and lock you out of configuration. Now all API paths handle expired sessions the same way - re-authenticate and retry transparently.

## WAN Steering

- **Fixed Active Rules stat card** - Was showing the raw iptables rule count instead of the number of active traffic classes, which was confusing.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.8

More fixes for WAN Steering and Adaptive SQM. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## WAN Steering

- **WAN stability detection and backoff** - When WAN interfaces flap (gateway reboots, GPON stick swaps, ISP outages), wansteer now detects rapid state changes and enters a backoff mode that suppresses SFE/conntrack flushes. This prevents a race condition with the gateway's own failover engine that was causing kernel errors and packet drops on SFP+ ports. Includes a 30-second startup grace period to let interfaces stabilize after boot.
- **SFE flush coalescing** - Minimum 10-second interval between SFE cache flushes prevents redundant flush pile-up during rapid state changes.
- **Reconciler drift fix** - The reconciliation cycle no longer false-detects rule drift when a WAN is down, eliminating unnecessary SFE flushes every 30 seconds during WAN outages.
- **Version display and mismatch warning** - The daemon status card now shows the deployed binary version. When the app detects the binary is outdated, a warning prompts you to redeploy. The warning clears immediately after a successful deploy, with a spinner while the new binary initializes.
- **Status metrics fix** - Uptime, active rules, and other daemon metrics were not displaying due to a parsing issue. Fixed.

## Adaptive SQM

- **Deploy with all WANs disabled** - You can now deploy with all WANs disabled to cleanly remove SQM from the gateway.

## Fixes

- **Client Performance nav link** - The sidebar link is now hidden when you're already on the Client Performance page.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.7

More fixes for WAN Steering and Adaptive SQM. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## WAN Steering

- **WAN stability detection and backoff** - When WAN interfaces flap (gateway reboots, GPON stick swaps, ISP outages), wansteer now detects rapid state changes and enters a backoff mode that suppresses SFE/conntrack flushes. This prevents a race condition with the gateway's own failover engine that was causing kernel errors and packet drops on SFP+ ports. Includes a 30-second startup grace period to let interfaces stabilize after boot.
- **SFE flush coalescing** - Minimum 10-second interval between SFE cache flushes prevents redundant flush pile-up during rapid state changes.
- **Reconciler drift fix** - The reconciliation cycle no longer false-detects rule drift when a WAN is down, eliminating unnecessary SFE flushes every 30 seconds during WAN outages.
- **Version display and mismatch warning** - The daemon status card now shows the deployed binary version. When the app detects the binary is outdated, a warning prompts you to redeploy.
- **Status metrics fix** - Uptime, active rules, and other daemon metrics were not displaying due to a parsing issue. Fixed.

## Adaptive SQM

- **Deploy with all WANs disabled** - You can now deploy with all WANs disabled to cleanly remove SQM from the gateway.

## Fixes

- **Client Performance nav link** - The sidebar link is now hidden when you're already on the Client Performance page.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.6

Fixes for the Wi-Fi Optimizer. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## Wi-Fi Optimizer

- **RF-aware load imbalance detection** - The "Significant Load Imbalance" health check now uses the Signal Map's propagation model to determine if APs are in separate coverage zones. If they're far apart and clients on the busy AP have strong signal, the warning is suppressed since load steering wouldn't help. Users without APs placed on the Signal Map get a hint to enable this.

- **Gateway-only consoles no longer appear as APs** - UDM-Pro, UDM-SE, UDM-Pro-Max, and EFG were incorrectly showing up in the AP list because the UniFi API reports phantom radio entries for these devices. They're now filtered out. Gateways with real Wi-Fi (UDM, UDR, UX, Dream Wall) are unaffected.

- **Fixed duplicate AP name in load imbalance message** - When two APs had the same client count, the health check could display the same AP name for both sides of the comparison (e.g., "AP-1 has 8 clients while AP-1 has only 8").

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.5

More fixes for speed test tracing and the security audit. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## Speed Tests

- **Link Aggregation in path trace** - Connector tooltip now shows "Link Aggregation: 2x 10 Gbps" when a link between switches uses LAG, so you can see aggregate capacity at a glance
- **Fixed gateway link speed in path trace** - Path traces involving the gateway could show the WAN port speed instead of the actual LAN link speed. For example, a 10 Gbps LAN link to the gateway would incorrectly show as 5 Gbps if the WAN port ran at that speed

## Security Audit

- **Fixed WAN DNS detection** - The "No DNS on WAN1" message could appear even when static DNS was configured. Now falls back to the network configuration API when the device port table doesn't populate the DNS array
- **Inactive port security gap** - Ports that were down but recently used (within the unused port grace period) weren't being flagged by either the unused port rule or the MAC restriction rule. Now flagged with context-aware advice: disable if no longer needed, or add a MAC restriction if still in use

## Wi-Fi Optimizer

- **Weak Signal count fix** - The stat card count now uses the same band-aware signal thresholds as the recommendations list, so the numbers match

## Adaptive SQM

- **Reduced gateway eMMC writes** - Replaced the SQM watchdog systemd timer with a cron job to reduce write cycles on the gateway's flash storage

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.4

More fixes for WAN Steering, Adaptive SQM, and the security audit. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## WAN Steering

- **Fix kernel race condition on Cloud Gateway Fiber** - Conntrack deletions during failover or config reloads could trigger kernel errors on IPQ9574 devices with SFE enabled. Now flushes the SFE cache first to prevent the race.

## Adaptive SQM

- **Reduce excessive kernel warnings on Cloud Gateway Fiber** - The minimum class rate was generating thousands of harmless "quantum is small" warnings, putting unnecessary write pressure on eMMC storage. Adjusted to eliminate the warnings with no change in traffic shaping behavior.

## Wi-Fi Optimizer

- **Smarter high TX retry detection** - A single client with high retries usually means a client-specific problem, not a systemic AP issue. Now requires at least 2 affected clients before raising an alert, and scales severity: Warning for 2-9 clients, Critical for 10+.

## Security Audit

- **Fix false positive subnet mismatch alerts** - The subnet mismatch check could use a stale IP from a previous VLAN config as a fallback. Now uses the most recent known IP, which avoids false positives when devices move between VLANs.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.3

More polish for the dashboard and Wi-Fi Optimizer. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## Wi-Fi Optimizer

- **Disabled and AFC band display** - Bands available on an AP but without an assigned channel now show as "Disabled" instead of blank stats. 6 GHz radios on AFC-enabled APs show "AFC" status.
- **Relaxed 2.4 GHz signal thresholds** - Shifted classification thresholds ~5 dB lower to better reflect real-world 2.4 GHz performance at range. A client at -70 dBm on 2.4 GHz now shows "fair" instead of "weak".

## Speed Tests

- **Test again button** - Speed test results now have a "Test again" button that re-runs the same test with the same settings, then scrolls to the progress area.
- **WAN History empty state** - The WAN History table now shows a helpful message when no results exist or current filters match nothing.

## Dashboard

- **Collapsible issue groups** - WiFi and Audit issue lists on the dashboard now group by category with collapsible headers when there are more than 3 issues. Keeps the dashboard compact without hiding information.
- **Layout and styling fixes** - Tightened gauge spacing, fixed alert group badge positioning, improved mobile layout for SQM cards and WiFi issue rows.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.2

New tabbed WAN History charts for latency, loaded latency, and jitter. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## WAN Speed Test

- **Tabbed WAN History charts** - The Speed History section is now "WAN History" with four tabs: Speed, Latency, Loaded Latency, and Jitter. All tabs share the same time slider and WAN filter badges. Loaded Latency shows base, loaded-down, and loaded-up series with distinct dash patterns so you can see bufferbloat at a glance.

- **Smoother progress bar** - Fixed the progress bar jumping backwards during gateway WAN speed tests, and trimmed about 2 seconds from the animation to better match actual test duration.

## Adaptive SQM

- **WAN Steering included in installers** - The wansteer gateway binary was missing from both Windows MSI and macOS native installers, so deploying WAN Steering would fail with "binary not found". Now included in both.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.1

Accuracy improvements for WAN speed testing, especially on congested links. See [v1.14.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.14.0) for what's new in v1.14.0+

## What's New in v1.14.0+

- **Customizable Dashboard** - Reorder, hide, show, resize, and stack dashboard cards. Your layout is saved per-instance and survives updates.
- **Live WiFiman signal polling** - Client Performance Dashboard polls at 1-second intervals for live signal, channel, band, and link rate updates when WiFiman is enabled.
- **Wi-Fi Optimizer dashboard card** - New card showing site-wide Wi-Fi health score and top issues at a glance.
- **Server network MAC restriction handling** - Server-purpose networks skip MAC restriction audits. Recommends 802.1X Multi-Host mode when supported.

## WAN Speed Test

- **100 MB download chunks** - Speed test servers were returning 200 KB per HTTP response, wasting ~90% of time on round-trips on high-latency links. Now requests 100 MB chunks, matching Ubiquiti's ui-speed behavior. On a congested GPON link (18 ms RTT), download went from ~565 Mbps to ~812 Mbps. No change on clean connections.
- **TCP warmup before measurement** - Connections now ramp for 2 seconds before sampling begins, so TCP slow-start and window scaling don't drag down the reported average.
- **Longer measurement window** - Bumped from 6 to 8 seconds for more steady-state data.
- **More streams in normal mode** - Default streams increased from 16 to 20 for better link saturation without needing Max Load.
- **Improved progress bar timing** - Progress animation now matches the actual test timeline (~23 seconds).

## Fixes

- **Schedule toggle not saving** - Toggling a schedule's enabled state could silently fail when a background task was running, due to an EF Core entity tracking conflict. Same fix as the alert rule toggle in v1.14.0.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.14.0

v1.14.0 adds a customizable dashboard layout and live WiFiman signal polling for the Client Performance Dashboard.

## What's New

For users upgrading from v1.13.0, here's what you missed in the v1.13.x patches:

- **Wi-Fi Optimizer channel recommendation fixes** (v1.13.1) - Fixed several edge cases where partial plan vetoes, external interference, and per-AP fallbacks could produce worse recommendations than the current state.
- **DNS audit accuracy** (v1.13.2) - Fixed false positive DNS IP mismatch for dual Pi-hole setups.
- **Adaptive SQM boot reliability** (v1.13.2) - Fixed boot script blocking udm-boot and xtables lock contention during startup.
- **Broad firewall rule accuracy** (v1.13.2) - Fixed false positives for MAC-based source rules and destination-IP-scoped rules.

## Customizable Dashboard

- **Edit Layout mode** - Reorder, hide, show, resize (half/full width), and stack dashboard cards. Your layout is saved per-instance and survives updates.
- **Wi-Fi Optimizer card** - New dashboard card showing your site-wide Wi-Fi health score and top issues at a glance.
- **Wi-Fi Health stat** - New quick stat in the stats row showing your overall Wi-Fi health score.
- **Unsaved changes warning** - Navigating away from edit mode prompts to confirm, so you don't lose changes.

## Client Performance Dashboard

- **Live WiFiman signal polling** - When WiFiman is enabled in UniFi Network (Settings -> WiFi -> WiFiman Support, on by default), the Client Performance Dashboard polls at 1-second intervals for live signal, channel, band, and link rate updates. Falls back to 5-second stat/sta polling when WiFiman isn't available.
- **LTTB chart downsampling** - Signal and speed charts now use Largest-Triangle-Three-Buckets downsampling for smooth, responsive charts even with thousands of data points.
- **WiFiman-enriched speed test snapshots** - Speed test path analysis uses WiFiman data for more accurate band, channel, and rate reporting during tests.

## Security Audit

- **Server network MAC restriction handling** - Server-purpose networks skip MAC restriction audits (VMs and containers make per-port MAC restriction impractical). Recommends 802.1X Multi-Host mode when the switch supports it.
- **DNS mismatch severity** - Lowered to Informational for isolation VLANs where DNS differences are expected by design.

## Fixes

- **Stale SQM status** - TC Monitor cache now expires after 3 consecutive poll failures instead of showing stale data indefinitely.
- **Alert rule editing** - Fixed EF Core tracking conflict when toggling then editing an alert rule in the same session.
- **SSH troubleshooting tooltip** - Improved CyberSecure IDS/IPS guidance with Detection Exclusions option and link to full troubleshooting docs.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.13.2

Fixes channel recommendations that could make interference worse, plus a DNS audit false positive. See [v1.13.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.13.0) for what's new in v1.13.0+

## Wi-Fi Optimizer

- **Channel recommendation engine overhaul** - The optimizer plans network-wide channel swaps, but per-AP filtering could veto some moves while approving others into the same channel, actually making things worse. Now re-validates all moves against the actual final plan, guards unchanged APs from degradation, and falls back to safe individual moves when the global plan collapses.

- **More accurate stress scaling** - Historical stress penalties were being zeroed out when internal co-channel APs moved away, ignoring external neighbor interference that doesn't go away. Stress now properly accounts for the external interference fraction.

- **Accurate recommended scores** - All APs now show scores reflecting the actual recommended plan, not the optimizer's ideal that may have been partially vetoed.

## Security Audit

- **Fix false positive DNS IP mismatch for dual Pi-hole setups** - Networks using the same pair of DNS IPs (e.g., two Pi-holes for HA) were incorrectly flagged as having inconsistent DNS. The analyzer now compares per-network IP sets instead of individual IPs.

## Fixes

- **Fix xtables lock contention on boot** - WAN Steering reconciler now uses `iptables-save` for rule checks instead of individual `iptables -C` calls, avoiding lock contention during startup.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.13.1

Fixes for WAN Steering boot persistence and a security audit false positive. See [v1.13.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.13.0) for what's new in v1.13.0+

## WAN Steering

- **Gateway boot persistence fixed** - the daemon failed to start after gateway reboot due to iptables lock contention with UniFi's own startup. Now uses `-w` flag to wait for the lock, and the boot script runs in a background subshell so it doesn't block other on_boot.d scripts.

## Security Audit

- **Fixed false positive on MAC-scoped firewall rules** - rules with a specific source MAC (like VoIP devices) were incorrectly flagged as "broad" even though the MAC narrows them to a single device. Also fixed the same gap for rules with specific destination IPs.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.13.0

v1.13.0 adds WAN Steering - load balance traffic across multiple WANs without leaving failover mode - and private WAN speed testing from any client on your network.

## What's New

For users upgrading from v1.12.0, here's what you missed in the v1.12.x patches:

- **Network-wide channel recommendation engine** (v1.12.1) - Analyzes interference graphs, RF scan data, and mesh constraints to recommend optimal channel assignments across all APs. Uses propagation-modeled weights, greedy + local search, and per-channel historical stress scoring.
- **Band-aware signal strength classification** (v1.12.1) - Signal quality thresholds adjust by band based on noise floor differences. A 6 GHz client at -75 dBm is no longer flagged as weak.
- **Mesh backhaul stats on AP cards** (v1.12.1) - Mesh APs show uplink signal and TX/RX rates; parent APs show per-child downlink stats.
- **Adaptive SQM performance tuning** (v1.12.5) - Scaled fq_codel memory, HTB burst tuning, and upstream shaping. Eliminates indiscriminate packet drops during heavy multi-stream downloads on gigabit connections.
- **Pull-to-refresh on mobile** (v1.12.4) - Pull down on any page to refresh data. Smart page-specific callbacks so only data reloads.
- **PWA install banner** (v1.12.4) - Dashboard prompts mobile users to install the app, with browser-aware instructions for iOS and Android.
- **Neighbor triangulation for channel recommendations** (v1.12.6) - APs pool neighbor observations across the site using the propagation model to estimate each neighbor's RF impact.
- **DNS audit and 802.1X accuracy improvements** (v1.12.7) - Fixed false positives around inverted source rules, multi-CIDR groups, Pi-hole cross-VLAN rules, and RADIUS-assigned VLANs.

## WAN Steering

Load balance the traffic you choose across multiple WANs - without leaving failover mode. Send your Steam downloads, Xbox updates, and OS patches across every link you're paying for, while gaming and video calls stay on your fastest WAN. Includes health-check failover and automatic rule recovery after gateway reprovisioning.

- **Traffic rules** - Match by source/destination IP, CIDR, range, MAC, protocol, and port, then assign to a target WAN with configurable probability.
- **Gateway daemon** - A Go daemon deployed directly to your gateway via SSH. Manages iptables mangle rules, runs per-WAN health checks with hysteresis, and reconciles rules automatically. Clean shutdown tears down all iptables changes.
- **Auto-discovery** - WAN interfaces detected automatically from the UniFi API and gateway routing tables. Boot persistence via `on_boot.d`.

## Client WAN Speed Test

- **Private external speed test server** - Host your own OpenSpeedTest instance on a VPS or cloud server and test real-world WAN speed from any client on your network. Results post back automatically with full path analysis.
- **Path trace with WAN hop** - Results show the full path from WAN through gateway, switches, and APs to the client. WiFi rate tooltips and efficiency calculations adjust for the WAN direction.
- **Standalone deploy script** - One-liner setup for the external server, downloads only the necessary files from GitHub.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.7

More audit accuracy fixes, especially around DNS and 802.1X. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## Security Audit

- **DNS audit false positive fixes** - Inverted source address rules (e.g., "not 192.168.1.220") were incorrectly flagged as single-IP DNAT coverage. These rules cover all networks except one IP, which is effectively full coverage. Also fixed handling of firewall address/port groups and `invert_address` in DNAT analysis.
- **VLAN isolation no longer flags DNS-only rules** - Cross-VLAN rules limited to port 53 (UDP or TCP+UDP) are now exempt from isolation bypass warnings, since Pi-hole cross-VLAN access is legitimate.
- **DNS IP consistency check** - Networks using a different third-party DNS IP than the majority now get flagged, helping catch misconfigurations. Gateway IPs and Corporate networks are excluded to avoid false positives.
- **Pi-hole/AdGuard Home detection improvements** - The management endpoint setting now accepts a full URL (e.g., `https://pihole.local`) in addition to a port number, for users behind a reverse proxy. Internal probing also skips SSL cert validation since container-internal certs aren't trusted.
- **Multi-CIDR firewall group coverage** - DNAT analysis now checks all CIDRs from firewall address groups instead of just the first, fixing false "Partial DNAT Coverage" warnings for multi-subnet groups.
- **802.1X port placement fixed** - Camera and IoT VLAN rules now use the client's effective network ID for 802.1X/RADIUS-secured ports instead of the unauthenticated VLAN config. Ports with no connected client are skipped since the RADIUS-assigned VLAN can't be determined.

## Config Optimizer

- **Co-channel interference scaled for dense deployments** - When a floor plan is set up and APs outnumber the non-overlapping channels for the band, co-channel warnings downgrade to Info severity since some overlap is unavoidable.

## Fixes

- **Third-party DNS detector no longer false-positives on malformed JSON** - Previously, a JSON parse failure could trigger a false "detected" result if the response body happened to contain the string "dns".
- **Settings validation** - Invalid DNS endpoint input now shows validation feedback instead of silently failing.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.6

More improvements to channel recommendations and Adaptive SQM. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## Channel Recommendations

- **Neighbor triangulation** - APs now pool neighbor observations across the site. An AP on channel 36 can learn about channel 149 neighbors from another AP that's already there. Uses the propagation model to estimate each neighbor's impact based on RF proximity, giving the optimizer a fuller picture of the RF environment when recommending channel changes.
- **Uncertainty handling for unobserved channels** - Channels with no direct neighbor data are treated conservatively. The optimizer won't assume an unobserved channel is interference-free just because no AP has checked it yet. Calibrated against real-world testing where triangulated estimates were ~3x lower than actual measured load.
- **Smarter per-AP move thresholds** - APs with low interference scores (below 2.0) are left alone. Channel moves also require both meaningful absolute improvement (1.0+) and relative improvement (30%+) to prevent chasing small gains that aren't worth the disruption.
- **Fix: stress scaling for arriving APs** - The stress penalty now correctly accounts for APs moving onto a channel, not just those leaving. Previously could understate interference when swapping co-channel pairs.

## Adaptive SQM

- **Fix: tc class ID parsing for hex values** - SQM scripts now correctly handle tc class IDs 10+ which Linux represents in hex (1:a, 1:b, etc.). Previously these classes weren't updated during rate changes.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.5

Adaptive SQM performance tuning for high-speed connections, plus speed test fixes. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## Adaptive SQM

This is a big one for anyone running SQM on a gig connection (or anything above 300 Mbps, really).

Stock UniFi SQM uses a 4 MB fq_codel memory limit, which is fine for slower connections but way too small for gigabit speeds. During heavy multi-stream downloads (think Steam updates, backups, multiple devices streaming), the queue runs out of memory and starts dropping packets indiscriminately from all flows - including traffic from other devices that aren't even part of the download. Testing showed ~10,000 indiscriminate packet drops per bufferbloat test at stock settings, causing 2.5-4.4% packet loss across all devices.

Adaptive SQM now scales fq_codel memory_limit based on your connection speed: 4 MB (stock) up to 300 Mbps, a linear ramp from 4 MB to 8 MB between 300-750 Mbps, and a flat 8 MB above 750 Mbps. HTB burst is tuned to 5 KB. Combined with shaping headroom below line rate (95% safety cap for fiber), this eliminated downstream packet drops entirely while improving bufferbloat from +1.9 ms (stock) to +0.83 ms (A+ grade) at identical shaping rates.

Upload support was also added - your configured upload speed is now applied as the upstream tc rate, and Adaptive SQM tunes the upstream interface's burst and memory parameters to match. This reduces upstream packet drops and CPU contention that was quietly degrading downstream performance.

What you'll notice: other devices stay responsive during heavy downloads, bufferbloat stays under 1 ms, and you don't have to configure anything. The tuning applies automatically based on your connection speed.

## LAN Speed Test

- **Accurate goodput measurement** - The iperf3 parser now uses sum_received instead of sum_sent, which gives you the actual throughput that made it across the wire.
- **Windows SSH speed tests fixed** - Speed tests from Windows installations now work correctly (was a shell compatibility issue with pwsh).

## Fixes

- **Console unreachable banner** - Fixed false "console unreachable" warnings and tightened up connection validation.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.4

More PWA and mobile polish. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## PWA / Mobile

- **Pull-to-refresh on mobile** - Pull down on any page to refresh data without a full page reload. Uses smart page-specific refresh callbacks so only the data reloads, not the whole app. Adaptive resistance so short pages are easy to pull and long scrollable pages don't trigger accidentally.
- **PWA install banner** - Dashboard shows a dismissible prompt encouraging mobile users to install the app to their home screen. Links to a dedicated install page with browser-aware instructions for iOS and Android, including guidance for unsupported browsers like Brave on iOS.

## Wi-Fi Optimizer

- **Channel recommendation disclaimer** - Added a note clarifying that UniFi neighbor scan data may not reflect all nearby networks, so channel recommendations should be taken as guidance rather than gospel.

## Fixes

- **Audit PDF no longer traps PWA users** - Downloading a PDF audit report in PWA standalone mode used to navigate away with no back button. Now uses a direct blob download that keeps you in the app.
- **Pull-to-refresh arrow polish** - Fixed arrowhead clipping, centering, and scaling so the pull indicator looks clean across devices.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.3

More path trace and mobile UX fixes. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## Speed Test

- **Mesh overhead factor corrected** - Adjusted from 55% overhead to 45%, which better reflects real-world mesh backhaul performance.
- **Smarter mesh bottleneck detection** - Now uses only the mesh-specific port speed when determining if mesh is the bottleneck, instead of mixing in the client wireless link speed from the other side of the hop.
- **Mesh speed capping** - When mesh is the bottleneck, directional max speeds are now capped to the mesh link's TX/RX rates instead of the client's faster direct Wi-Fi rates.
- **Signal bars on path trace** - Wireless links now show color-coded signal strength bars (band-aware) instead of a generic emoji, with signal tooltips on the client hop.
- **Port speed fallback for APs** - When an AP has no port table data, the path tracer now falls back to the other device's port speed for the same physical link, so wired hop speeds are no longer missing.
- **WAN hop shows network name** - WAN hops now display the configured network name (e.g., "AT&T Fiber") instead of a generic "WAN" label.
- **Client name fallback** - Client hops now properly fall back to hostname when the display name is empty.
- **Mobile path trace fixes** - Speed labels, notes, and bottleneck warnings display correctly on narrow screens.

## Mobile UX

- **Fixed bottom tab bar** - Tabs and time filter on Client Performance are now pinned to the bottom of the screen, always accessible without scrolling back up.
- **Auto-hide navigation** - Top bar hides after inactivity on Client Performance, giving more screen real estate.
- **Compact speed test table** - Results table fits on mobile without horizontal scrolling.
- **General layout and spacing fixes** across speed test results and device tables.
- **Fixed touch scroll locking** - Scrolling on device cards and other content no longer gets blocked by touch event handling. Increased scroll-up threshold so the nav bar doesn't pop back up too easily.
- **Horizontal scroll on tables and tabs** - All table and tab containers now allow proper horizontal scrolling on mobile.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.2

More path trace and mobile UX fixes. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## Speed Test

- **Mesh overhead factor corrected** - Adjusted from 55% overhead to 45%, which better reflects real-world mesh backhaul performance.
- **Smarter mesh bottleneck detection** - Now uses only the mesh-specific port speed when determining if mesh is the bottleneck, instead of mixing in the client wireless link speed from the other side of the hop.
- **Mesh speed capping** - When mesh is the bottleneck, directional max speeds are now capped to the mesh link's TX/RX rates instead of the client's faster direct Wi-Fi rates.
- **Signal bars on path trace** - Wireless links now show color-coded signal strength bars (band-aware) instead of a generic emoji, with signal tooltips on the client hop.
- **Port speed fallback for APs** - When an AP has no port table data, the path tracer now falls back to the other device's port speed for the same physical link, so wired hop speeds are no longer missing.
- **WAN hop shows network name** - WAN hops now display the configured network name (e.g., "AT&T Fiber") instead of a generic "WAN" label.
- **Client name fallback** - Client hops now properly fall back to hostname when the display name is empty.
- **Mobile path trace fixes** - Speed labels, notes, and bottleneck warnings display correctly on narrow screens.

## Mobile UX

- **Fixed bottom tab bar** - Tabs and time filter on Client Performance are now pinned to the bottom of the screen, always accessible without scrolling back up.
- **Auto-hide navigation** - Top bar hides after inactivity on Client Performance, giving more screen real estate.
- **Compact speed test table** - Results table fits on mobile without horizontal scrolling.
- **General layout and spacing fixes** across speed test results and device tables.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.1

Big Wi-Fi Optimizer release - a new network-wide channel recommendation engine, band-aware signal classification, mesh backhaul stats, and better mobile UX. See [v1.12.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.12.0) for what's new in v1.12.0+

## Wi-Fi Optimizer

- **Network-wide channel recommendation engine** - Analyzes interference graphs, RF scan data, historical radio stats, and mesh constraints to recommend optimal channel assignments across all APs. Uses propagation-modeled pairwise AP weights, greedy + local search with random restarts, and per-channel historical stress scoring.
- **Band-aware signal strength classification** - Signal quality thresholds now adjust by band based on noise floor differences (2.4 GHz is tightest, 6 GHz most lenient). A 6 GHz client at -75 dBm is no longer flagged as weak. Applied across Client Performance, Client Timeline, Airtime Fairness, and health rules.
- **Mesh backhaul stats on AP cards** - Mesh child APs show uplink signal and TX/RX rates; parent APs show per-child downlink stats from the parent's perspective.
- **AP lock indicators** - Lock icon with tooltip in the client list and "AP Locked" badge on the client detail page when a client has a fixed AP assignment.
- **DFS channel fixes** - Wide channel widths (80/160 MHz) now check the full bonding group for DFS channels, not just the primary. At 160 MHz where DFS avoidance is impossible, falls back to Include DFS with an explanatory notice.
- **Corrected AP catalog EIRP values** - Updated TX power and antenna gain for U7-Pro, U7-Pro-Max, U7-Pro-XG, U6-Enterprise, U6-Pro, U6-Mesh, U6-Mesh-Pro, U6-IW, U6-Extender, U6+, U7-IW, and U7-LR from spec sheets.
- **Channel recommendation deduplication** - Channels in the same bonding group (e.g., 149/153/157/161 at 80 MHz) are now treated as one option, preventing false "optimization" between co-channel assignments.
- **Mesh hop analysis fix** - Filters out 6 Mbps idle Wi-Fi management frame rate that was skewing mesh backhaul speed measurements.
- **Wi-Fi 4 protocol display** - Fixed "ng", "na", "a", "b", "g" radio protocols not resolving to their Wi-Fi generation names on Client Performance.

## Adaptive SQM

- **Fiber-aware safety cap** - Fiber connections now use a 98% safety cap instead of 95%, since the WAN link speed already constrains max throughput and the extra headroom was leaving performance on the table.

## Mobile

- **Redesigned mobile navigation** - Auto-hide nav bar on scroll down, show on scroll up with depth shadow. Sticky top bar, collapsible client identity bar, and proper fragment navigation handling.

## Fixes

- **Client info backfill** - Speed test path analysis now backfills missing client details when the UniFi API lookup fails.
- **Schedule drift for non-anchored tasks** - Next run time now truncates to minute boundaries, preventing sub-minute drift from accumulating across Security Audit runs.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.12.0

v1.12.0 brings interactive Wi-Fi Optimizer drill-downs, smarter CrowdSec threat intelligence, and RF propagation modeling to cut false interference warnings.

## What's New

For users upgrading from v1.11.0, here's what you missed in the v1.11.x patches:

- **ntfy.sh notifications** (v1.11.4) - Push notifications via ntfy.sh with markdown, priority mapping, and auth support
- **Hourly speed test scheduling** (v1.11.7) - Schedule speed tests at 1, 2, or 4 hour intervals
- **Per-device iperf3 overrides** (v1.11.8) - Custom parallel streams and duration per device
- **Editable scheduled tests** (v1.11.8) - Edit existing schedules inline with current settings populated
- **Wi-Fi heatmap improvements** (v1.11.7) - Elevation 0 antenna data for 2D heatmaps, orientation fixes, 50% higher resolution, U7-Mesh support
- **Media and Gaming network types** (v1.11.6) - New purpose types with proper trust hierarchy and device placement
- **Protect camera VLAN detection** (v1.11.2) - Cameras detected via Protect API for reliable VLAN audit checks
- **802.1X multi_host mode** (v1.11.3) - Recognized as a secured port mode
- **Traefik HTTPS for Proxmox** (v1.11.5) - Let's Encrypt via Cloudflare DNS-01 during install

## Wi-Fi Optimizer

- **Click-to-filter channel chips** - Click any channel chip in RF Environment to filter the view. Click AP rows in Channel Analysis to select channel details. Active filters show a blue ring.
- **Clickable AP card radio rows** - Band, channel, utilization, EIRP, and client count cells navigate directly to the relevant tab with filters pre-applied. Deep-linkable URLs with query params.
- **EIRP display** - Each radio row now shows transmit power in dBm.
- **Vendor in neighboring networks** - OUI manufacturer name column in the Neighboring Networks table.
- **Propagation-modeled interference filtering** - Co-channel and high power overlap rules now use ITU-R P.1238 indoor path loss modeling, eliminating false positives for multi-building deployments.
- **Collapsible health issue groups** - Issue categories collapse with count badges and chevrons for easier scanning.

## Client Stats

- **AP and band filters** - Filter the client list by access point and band using dropdown and pill controls.
- **Filter preservation** - AP and band filters persist when navigating to client detail and back.

## Threat Dashboard

- **Auto-enrich threat IPs** - CrowdSec CTI data loads automatically on page load, using up to half the daily quota.
- **Smarter rate limiting** - Burst throttles (transient 429s) no longer trigger unnecessary 1-hour lockouts. Daily quota exhaustion handled separately.
- **Background CTI hydration** - Enrichment runs in the background instead of blocking page load.
- **Benign reputation badge** - Known scanners like ONYPHE show a "benign" badge instead of "unknown".
- **Sensitive value redaction** - API keys and passwords redacted in system settings logs.

## Alerts & Schedule

- **WAN schedule reconciliation** - WAN speed test schedules auto-correct when UniFi reassigns WAN groups, using 2-of-3 field matching.
- **Smart chart grouping** - Custom WAN names group by name alone; generic names (WAN, WAN2) include the group to distinguish interfaces.
- **Schedule drift fix** - Next run time now anchors to the scheduled slot, not task completion time.
- **Stale WAN name sync** - Data Usage WAN names update when renamed in UniFi Console.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.8

Quality of life improvements for speed testing and scheduling. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.

## LAN Speed Test

- **Per-device iperf3 overrides** - You can now set custom parallel streams (-P) and duration (-t) per device, overriding the global defaults. Useful when specific devices need different test parameters. The progress bar also scales to the effective duration now.
- **SQM status in trace tooltips** - WAN hop icons and link connectors in the speed test trace now show whether Smart Queues (SQM) is enabled or disabled on hover.

## Alerts & Schedule

- **Edit scheduled tests** - Schedule cards now have an Edit button that shows the form inline with current settings populated. Save updates in place (preserving execution history).
- **Next run time shown immediately** - New schedules now display "Next run: in Xh Ym" right after creation, instead of waiting for the first execution to complete.

## Fixes

- **iperf3 override validation** - Per-device parallel streams clamped to 1-16 and duration to 1-300s, enforced at input, save, and runtime layers. Out-of-range values snap to bounds on blur.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.7

Wi-Fi heatmap accuracy improvements, hourly scheduling, and a LAG speed detection fix. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.

## Alerts & Schedule

- **Hourly speed test scheduling** - Schedule intervals now go as low as every 1 hour (previously 6 hours minimum). New options: 1, 2, and 4 hour intervals for audit, WAN, and LAN speed test schedules.

## Wi-Fi Heatmaps

- **Elevation 0 antenna data for 2D heatmaps** - Floor plan heatmaps now use extracted Elevation 0 deg cut data for more accurate horizontal coverage shapes. Extracted from Ubiquiti polar plot images for U7-Pro-XGS, U7-Outdoor, U7-Pro-Outdoor, U7-Mesh, E7, E7-Audience (narrow/wide), and E7-Campus - including all EU variants. More APs coming soon.
- **Antenna pattern orientation fixes** - Fixed ceiling, desktop, and wall mount orientation transforms. Ceiling mount uses 180 rotation + LR mirror, desktop uses 180 rotation, and mesh APs skip transforms that were incorrectly flipping their patterns.
- **50% higher heatmap resolution** - Grid resolution increased from 400x500 to 600x750 for sharper coverage visualization.
- **U7-Mesh antenna data** - Added to the antenna pattern catalog with 2.4 and 5 GHz patterns (omni 6 dBi + directional 10 dBi on 5 GHz).
- **E7 AP spec corrections** - Fixed 2.4 GHz gain (4 to 5 dBi) and TX power values for 5 GHz and 6 GHz bands to match the actual tech specs.

## LAN Speed Test

- **LAG speed detection in reversed paths** - When building network paths from gateway to server, the wrong port was used for speed lookups on LAG setups - checking a 2.5G downlink port instead of the 20G LAG uplink. Fixed all three reversed server chain loops.

## Fixes

- **MailKit bumped to 4.15.1** - Fixes CVE-2026-30227 (CRLF injection in SMTP).
- **Proxmox install prompt clarified** - The password prompt now explains the auto-generation behavior.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.6

Fixes and enhancements for the security audit and alerts system. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.

## Device Fingerprint

- **Media and Gaming network types** - New purpose types for entertainment networks (streaming, theater, A/V) and game console networks. Previously, Media auto-classified as IoT and Gaming as Home, which caused false-positive isolation findings when intentional allow rules existed. Trust hierarchy: Guest can access Media but not Trusted/IoT networks; Gaming has Home-level trust so consoles get UPnP access.
- **Correct device placement for Media and Gaming** - Streaming devices and smart TVs on a Media network are correctly placed (no audit finding), since Media is isolated like IoT. Game consoles on Gaming are also accepted.

## Security Audit

- **Fixed false-positive isolation issues on pre-zone-based firewall setups** - A recent change assigned "ANY" matching targets to firewall rules with empty source/dest fields, which caused infrastructure rules (Allow Established/Related, Drop Invalid State) to eclipse the real inter-VLAN block rule. Fixed at three layers: parser, evaluator, and VLAN analyzer.

## Alerts & Schedule

- **Audit severity no longer inflated by system issues** - System-category issues (e.g., fingerprint DB unavailable) are now excluded from critical counts, so a score-100 audit won't trigger Error-severity alerts.
- **Schedule error handling isolated** - A DB update failure after a successful task no longer triggers a false "task failed" alert.
- **Console reconnection before scheduled audits** - Prevents fingerprint cache failures on long schedule intervals where the session goes stale.
- **Source links on all alerts** - Alerts now link back to their source page (e.g., a specific speed test result or audit finding) with "View" buttons in the UI and links in all notification channels.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.5

More fixes and improvements. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.0+

## Security Audit

- **Fixed false positive inter-VLAN isolation warnings on legacy firewalls** - Legacy (pre-zone-based) "Allow Established/Related" rules were being treated as if they allowed all traffic, potentially eclipsing block rules below them. The parser now correctly reads connection state fields so these rules only match established/related connections, not new ones.

## Proxmox Installer

- **Traefik HTTPS reverse proxy option** - The Proxmox LXC installer now offers an optional Traefik setup that auto-provisions Let's Encrypt certificates via Cloudflare DNS-01. This enables geo location tagging and solves the HTTP/1.1 speed test requirement without manual reverse proxy setup.
- **VLAN tag support** - The installer now prompts for an optional VLAN tag when the bridge is VLAN-aware, preventing install failures when the default untagged VLAN doesn't have internet access.

## Fixes

- **Schedule form layout improvements** - Better alignment and sizing of form fields on mobile and desktop for the Alerts/Schedule page.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.4

More fixes and a new notification channel. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.0+.

## Notifications

- **ntfy.sh support** - You can now send alerts to [ntfy.sh](https://ntfy.sh) as a notification channel. Supports markdown messages, priority mapping, emoji tags, and both Bearer token and Basic auth. Great lightweight option if you don't want to set up a full webhook integration.

## Security Audit

- **Fixed false positives on ports staged for new WAN connections** - Ports being prepped for a future WAN connection could get flagged as unused because the forwarding mode field isn't present on WAN-assigned ports. Now correctly detects WAN assignment via `ethernet_overrides` on the device and skips these ports.

## Fixes

- **Notes cursor no longer jumps to end while typing** - Fixed the textarea/input cursor resetting to the end of the text during auto-save. Notes also now sync across detail and table views immediately.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.3

More audit accuracy improvements. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.0+.

## Security Audit

- **802.1X multi_host mode now recognized as secured** - Ports using 802.1X multi_host mode (authenticates the first MAC, then allows subsequent devices) are now correctly treated as secured. Previously only "auto" and "mac_based" modes were recognized, so multi_host ports were incorrectly flagged as unprotected in the audit and port security stats.

- **"Allow All" vs manually selecting all VLANs** - The excessive tagged VLANs rule now distinguishes between the blanket "Allow All" forwarding mode (which automatically includes any future VLANs) and manually selecting every VLAN in "Customize" mode (a deliberate choice that won't auto-include new VLANs). Previously both were treated the same, which could flag intentionally configured ports.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.2

More audit accuracy improvements and UI fixes. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.0+.

## Security Audit

- **Protect cameras now reliably detected for VLAN checks** - The camera VLAN rule previously relied on port names to identify cameras, so it only worked when ports were named something camera-related. Now detects them via the Protect API regardless of port naming, with a fallback for cameras that have no port data at all.
- **Cloudflare IP restriction on port forwards** - Port forwards restricted to Cloudflare IP ranges are now downgraded from Critical to Info since they're properly locked down. Other IP restrictions get Recommended severity with actionable steps to switch to Cloudflare. Issue descriptions now deep-link to the Threat Intelligence drilldown for the specific port.
- **DNS false-positive fix for non-default management VLANs** - Device DNS validation now checks each device's own subnet gateway rather than assuming VLAN 1. Admin-configured DHCP DNS servers (Pi-hole, AdGuard Home) are also accepted as valid targets.

## Fixes

- **Notes auto-save on paste** - Notes fields (speed test details, UPnP inspector) now save on paste and drag-and-drop, not just typing. Also saves immediately when the field loses focus.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.1

More improvements to WAN data usage tracking and audit accuracy. See [v1.11.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.11.0) for what's new in v1.11.0+.

## WAN Data Usage

- **Smarter baseline tracking** - Changing your billing day now recalculates the baseline automatically instead of using a stale value
- **Mid-cycle guidance** - When enabling tracking partway through a billing cycle, you'll see contextual hints about what to expect
- **Local timezone billing boundaries** - Billing cycle rollovers now use your local timezone instead of UTC

## Wi-Fi Optimizer

- **Channel width display** - Client cards now show the negotiated channel width (20/40/80/160/320 MHz) alongside the channel number
- **Wide channel width rule** - Wider channels raise the noise floor and reduce co-channel separation. Recommends stepping down from 320 to 160 MHz on 6 GHz, and from 160 to 80 MHz on 5 GHz when clients have weak signal.

## Security Audit

- **Smart speakers covered by media players setting** - Google Home, Amazon Echo, Sonos, and other smart speakers are now suppressed by "Allow all media players on main network" - previously only Apple HomePods were covered
- **Security/Management networks exempt from third-party DNS requirement** - If you run Pi-hole or AdGuard on most networks but leave your camera and management VLANs on gateway DNS, the audit no longer flags that as inconsistent. DNAT coverage is still checked for these networks since cameras are notorious for hardcoding their own DNS.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.11.0

v1.11.0 adds WAN data usage tracking with billing cycle alerts - useful if you're on a metered connection like Starlink, cellular, or a capped ISP plan.

## What's New

For users upgrading from v1.10.0, here's what you missed in the v1.10.x patches:

- **HTTPS reverse proxy** (v1.10.5) - Automatic Let's Encrypt certificates via Traefik. The Windows MSI includes an opt-in feature; Docker users can use the companion [NetworkOptimizer-Proxy](https://github.com/Ozark-Connect/NetworkOptimizer-Proxy) repo. Per-hostname TLS forces HTTP/1.1 for speed tests while keeping HTTP/2 for the app.
- **Threat search** (v1.10.4) - Search the full threat database by IP, CIDR, country, ASN, or org name
- **Service names for targeted ports** (v1.10.7) - The threat dashboard now shows service names (SSH, RDP, MSSQL, Docker API, etc.) for 60+ commonly targeted ports, with proper ICMP/GRE protocol handling
- **MITRE ATT&CK techniques** (v1.10.2) - CrowdSec CTI enrichment surfaces MITRE ATT&CK technique mappings in IP drilldowns
- **Noise filters suppress alerts** (v1.10.6) - Noise filters now suppress alert notifications for matching patterns, not just dashboard views. Attack pattern detections (brute force, DDoS, exploit campaigns) also trigger alerts with stable dedup to prevent repeat notifications
- **Adaptive SQM: WAN link speed cap and cellular profile** (v1.10.9) - Rates are now capped at the physical WAN port's link speed, with an editable baseline latency, a research-based 7-day cellular congestion profile, and auto-detection for Starlink/LTE/5G/Fiber/DSL
- **RADIUS/802.1X port security** (v1.10.4) - Audit recognizes RADIUS MAC Authentication and 802.1X port profiles, eliminating false "No MAC" warnings
- **Zone-based firewall isolation** (v1.10.3) - Audit recognizes custom firewall zones with block rules as proper network isolation
- **LAG aggregate speed** (v1.10.4) - Path visualization shows combined LAG bandwidth (e.g., 2x10G = 20G)
- **U7-Mesh and UCG-Industrial** (v1.10.9) - Added to the product database with device icons

## WAN Data Usage Tracking (Under Alerts & Schedule)

Track bandwidth consumption per WAN interface against your ISP's data cap. Useful for Starlink, cellular hotspots, or any metered connection where going over means throttling or overage charges.

- **Billing cycle awareness** - Configure your billing day (1-28) and the tracker calculates usage within the current cycle, rolling over automatically each month
- **Data cap alerts** - Set a cap in GB and a warning threshold (default 80%). Get alert notifications when you're approaching or exceeding your limit - one alert per cycle, not spam
- **Gateway reboot handling** - When the gateway reboots mid-cycle, the tracker uses uptime to determine that the raw byte counters represent all usage since boot, so you don't lose data
- **Usage adjustment** - If you enable tracking mid-cycle, enter how much data was already used. Negative values work too if the tracker overcounts. Resets automatically each billing cycle
- **Per-WAN configuration** - Each WAN gets its own cap, billing day, and tracking toggle. Supports multi-WAN setups

## Security Audit

- **802.1X ports with curated VLAN lists** - Ports secured with 802.1X/RADIUS that have a curated set of tagged VLANs (for dynamic VLAN assignment) are no longer flagged as "Excessive Tagged VLANs". Ports with "Allow All" are still flagged as informational.
- **Hardware acceleration + NetFlow** - The "Hardware Acceleration disabled" recommendation is now suppressed when NetFlow is enabled, since UniFi requires offloading to be off for NetFlow to work.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.10.9

Adaptive SQM improvements and new device support. See [v1.10.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.10.0) for what's new in v1.10.0+

## Adaptive SQM

- **Cap rates at WAN link speed** - MaxSpeed, MinSpeed, and AbsoluteMax are now capped at the physical WAN port's link rate (e.g., 1 Gbps for 1GbE), so SQM never shapes above what the link can actually carry. GRE tunnels and unknown link speeds are left uncapped.
- **Editable baseline latency** - You can now override the auto-calculated baseline latency directly in the calculated params grid. Your custom value persists across page loads.
- **Ratio-based latency coloring** - Ping latency color is now based on ratio to baseline (>1.5x warning, >3x danger) instead of a hardcoded 50ms threshold.
- **7-day cellular congestion profile** - Replaced the uniform daily pattern with a research-based 7x24 matrix that reflects real cellular tower load: weekday commute ramps, Friday evening out, Saturday worst evening (people on cellular at restaurants/events, not home on Wi-Fi), Sunday lightest day.
- **Auto-detect connection type** - Automatically selects the right connection profile when the WAN name contains Starlink, LTE, 5G, Cellular, Fiber, FTTH, FTTP, or DSL.
- **Reset fields on WAN change** - Switching WAN interface now resets connection type, nominal speeds, speedtest server, and ping host to appropriate defaults.

## Device Support

- **U7-Mesh and UCG-Industrial** - Added Wi-Fi 7 mesh AP (U7-Mesh) and Cloud Gateway Industrial (UCG-Industrial) to the product database with device icons.

## macOS Installation

- **Root-owned remnant cleanup** - The install script now detects files left behind by a previous `sudo` installation and fixes ownership automatically. It also refuses to run as root/sudo with a clear error message.

## What's New in v1.10

For users upgrading from an older version, here's what's been added since v1.10.0:

- **Threat Intelligence** (v1.10.0) - IPS event analysis with exposure reports, attack sequence detection, geographic breakdowns, CrowdSec CTI integration, and MITRE ATT&CK technique mapping. Recent updates added service names for 60+ commonly targeted ports (v1.10.7), proper ICMP/GRE protocol handling (v1.10.7), noise filters that suppress alert notifications (v1.10.6), and tighter port range grouping for scan patterns (v1.10.6).
- **Alerts & Scheduling** (v1.10.0) - Automated speed tests and security audits on a schedule, with email/webhook notifications for audit score drops, speed degradation, and attack chain detection. Attack pattern detections (brute force, DDoS, exploit campaigns) now trigger alerts (v1.10.6), incident status derives automatically from constituent alerts (v1.10.6), and stable dedup prevents repeat notifications for ongoing attacks (v1.10.6).
- **HTTPS Reverse Proxy** (v1.10.5) - Automatic HTTPS with Let's Encrypt via Traefik. The Windows MSI includes an opt-in feature; Docker users can use the companion [NetworkOptimizer-Proxy](https://github.com/Ozark-Connect/NetworkOptimizer-Proxy) repo. Per-hostname TLS options force HTTP/1.1 for speed tests while keeping HTTP/2 for the app.
- **Threat search** (v1.10.4) - Search the full threat database by IP, CIDR, country, ASN, or org name
- **RADIUS/802.1X port security** (v1.10.4) - Audit recognizes RADIUS MAC Authentication and 802.1X port profiles, eliminating false "No MAC" warnings
- **LAG aggregate speed** (v1.10.4) - Path visualization shows combined LAG bandwidth (e.g., 2x10G = 20G)
- **Zone-based firewall isolation** (v1.10.3) - Audit recognizes custom firewall zones with block rules as proper network isolation

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.10.8

Speed test map improvements and a geolocation fix. See [v1.10.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.10.0) for what's new in v1.10.0+

## What's New in v1.10

For users upgrading from an older version, here's what's been added since v1.10.0:

- **Threat Intelligence** (v1.10.0) - IPS event analysis with exposure reports, attack sequence detection, geographic breakdowns, CrowdSec CTI integration, and MITRE ATT&CK technique mapping. Recent updates added service names for 60+ commonly targeted ports (v1.10.7), proper ICMP/GRE protocol handling (v1.10.7), noise filters that suppress alert notifications (v1.10.6), and tighter port range grouping for scan patterns (v1.10.6).
- **Alerts & Scheduling** (v1.10.0) - Automated speed tests and security audits on a schedule, with email/webhook notifications for audit score drops, speed degradation, and attack chain detection. Attack pattern detections (brute force, DDoS, exploit campaigns) now trigger alerts (v1.10.6), incident status derives automatically from constituent alerts (v1.10.6), and stable dedup prevents repeat notifications for ongoing attacks (v1.10.6).
- **HTTPS Reverse Proxy** (v1.10.5) - Automatic HTTPS with Let's Encrypt via Traefik. The Windows MSI includes an opt-in feature; Docker users can use the companion [NetworkOptimizer-Proxy](https://github.com/Ozark-Connect/NetworkOptimizer-Proxy) repo. Per-hostname TLS options force HTTP/1.1 for speed tests while keeping HTTP/2 for the app.
- **Threat search** (v1.10.4) - Search the full threat database by IP, CIDR, country, ASN, or org name
- **RADIUS/802.1X port security** (v1.10.4) - Audit recognizes RADIUS MAC Authentication and 802.1X port profiles, eliminating false "No MAC" warnings
- **LAG aggregate speed** (v1.10.4) - Path visualization shows combined LAG bandwidth (e.g., 2x10G = 20G)
- **Zone-based firewall isolation** (v1.10.3) - Audit recognizes custom firewall zones with block rules as proper network isolation

## Wi-Fi Optimizer

- **AP markers on Client Dashboard map** - The speed test map on Client Dashboard now shows AP location markers (read-only), giving you a quick sense of where clients are relative to access points.
- **AP locations refresh on tab switch** - Editing AP locations on the Signal Map now immediately reflects on the Speed Map tab without needing a page reload.
- **Map time filter sync** - The map's internal time slider on Client Dashboard now syncs with the page-level time filter, so changing one updates the other.

## Fixes

- **Speed test geolocation timeout** - The browser geolocation prompt could hang the result POST indefinitely if the user hadn't responded to the permission dialog. Added a 3-second safety timeout so results always submit.
- **New speed test results not appearing on map** - Background enrichment (adding PathAnalysis to existing results) didn't trigger a map refresh. The map now tracks filtered count changes in addition to new result IDs.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

## 1.10.7

More Threat Intelligence improvements - the threat dashboard now identifies services by name for 60+ commonly targeted ports, and correctly handles portless protocols like ICMP and GRE. See [v1.10.0 release notes](https://github.com/Ozark-Connect/NetworkOptimizer/releases/tag/v1.10.0) for what's new in v1.10.0+

## Threat Intelligence

- **Service names for targeted ports** - The threat dashboard now shows service names (SSH, RDP, MSSQL, Docker API, Proxmox, etc.) for 60+ commonly targeted ports instead of just port numbers. When we get a generic service name, it falls back to the built-in port lookup for a more useful label.
- **ICMP and GRE protocol handling** - Portless protocols like ICMP and GRE previously showed as "Port 0" and were lumped together. They now display the protocol name and get separate rows in the targeted ports table.
- **Proper service name casing** - Service names like MSSQL, MySQL, MongoDB, and PostgreSQL now display with correct casing instead of all-lowercase.

## Fixes

- **Threat dashboard mobile overflow** - Fixed horizontal scrolling on mobile viewports in the threat dashboard.

## Installation

**Windows**: Download the MSI installer below

**Docker**:
```bash
docker compose pull && docker compose up -d
```

**macOS** (native, recommended for accurate speed tests vs Docker Desktop):
```bash
git clone https://github.com/Ozark-Connect/NetworkOptimizer.git && cd NetworkOptimizer && ./scripts/install-macos-native.sh
# or if you already have it cloned
cd NetworkOptimizer && git pull && ./scripts/install-macos-native.sh
```

**Proxmox**:
```bash
bash -c "$(curl -fsSL https://raw.githubusercontent.com/Ozark-Connect/NetworkOptimizer/main/scripts/proxmox/install.sh)"
```

For other platforms (Synology, QNAP, Unraid, native Linux), see the [Deployment Guide](https://github.com/Ozark-Connect/NetworkOptimizer/blob/main/docker/DEPLOYMENT.md).

