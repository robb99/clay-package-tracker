# clay-package-tracker 📦

Track UPS, FedEx, and USPS packages with Clay. Get voice and desktop notifications when packages are delivered!

## Features

- 📦 **Multi-carrier support** - UPS, FedEx, USPS
- 🔔 **Delivery notifications** - Voice announcements via clay-voice + desktop notifications
- 📋 **Package list** - Track multiple packages with descriptions
- 🔄 **Status checking** - Check current delivery status
- 🤖 **HA integration** - Works with Home Assistant for delivery alerts

## Installation

```bash
# Clone or use from workspace
cd projects/clay-package-tracker

# Or symlink to tools
ln -s ../projects/clay-package-tracker/clay_package_tracker.py ../tools/clay_package_tracker.py
```

## Usage

### Add a package

```bash
# Auto-detect carrier
python3 clay_package_tracker.py add "1Z999999999999999999"

# Specify carrier
python3 clay_package_tracker.py add "123456789012" --carrier fedex

# With description
python3 clay_package_tracker.py add "940011189922345678901" --carrier usps --desc "Amazon order"
```

### List packages

```bash
python3 clay_package_tracker.py list
```

Output:
```
📦 Tracked Packages
======================================================================

📦 1Z999999999999999999
   Carrier: UPS
   Description: Package from UPS
   Status: In Transit
   Last checked: 2026-09-26T23:45:00
   Latest: 2026-09-26 10:30 AM - Louisville, KY
           Out for delivery
```

### Check status

```bash
# Check all packages
python3 clay_package_tracker.py check

# Check specific package
python3 clay_package_tracker.py check "1Z999999999999999999"

# JSON output
python3 clay_package_tracker.py check --json
```

### Quick status

```bash
python3 clay_package_tracker.py status
# Output: 📦 Package Summary: 3 total, 1 delivered, 2 in transit
```

### Remove package

```bash
python3 clay_package_tracker.py remove "1Z999999999999999999"
```

## Configuration

Packages are stored in `~/.clay/packages.json`

## Integration with Home Assistant

The package tracker can work with clay-ha-listener to announce deliveries:

1. Set up tracking with carrier APIs (UPS/FedEx/USPS require API keys for real tracking)
2. Run clay_package_tracker.py check periodically (via cron)
3. When status changes to "delivered", clay-voice announces it

## Carrier Detection

The tool auto-detects carriers from tracking number format:
- **UPS**: Starts with `1Z`
- **FedEx**: 12 or 15 digits
- **USPS**: 20+ digits (with dashes)

## Real Tracking APIs

For production use, you'll need API keys from each carrier:
- UPS: UPS Tracking API
- FedEx: FedEx Track API  
- USPS: USPS Tracking API

Current version uses mock data - real API integration coming soon!

## Requirements

- Python 3.8+
- requests (for future API integration)

## Related Clay Projects

- [clay-voice](https://github.com/robb99/clay-voice) - Voice announcements
- [clay-notify](https://github.com/robb99/clay-notify) - Desktop notifications
- [clay-ha-listener](https://github.com/robb99/clay-ha-listener) - HA event monitoring
