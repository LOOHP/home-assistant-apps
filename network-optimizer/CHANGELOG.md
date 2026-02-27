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

