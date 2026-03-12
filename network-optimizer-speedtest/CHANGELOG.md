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

