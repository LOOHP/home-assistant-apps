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

