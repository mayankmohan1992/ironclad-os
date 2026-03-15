# IronClad OS Build Guide

## Prerequisites

### Hardware Requirements
- **Build Machine**: Linux Mint (or Debian-based) with 8GB+ RAM, 50GB+ free space
- **Target Machine**: 8GB RAM, 500GB HDD, x86_64

### Software Requirements
- Linux Mint 21+ (or Debian 12+)
- Root/sudo access
- Internet connection

## Quick Start

### Method 1: Install on Existing System (Recommended for Testing)

1. Clone/fork the repository:
```bash
git clone https://github.com/yourusername/ironclad-os.git
cd ironclad-os
```

2. Run Phase 1 - Foundation:
```bash
sudo ./src/build-scripts/01-setup.sh
```

3. Reboot:
```bash
sudo reboot
```

4. Run Phase 2 - Security:
```bash
sudo ./src/build-scripts/02-kicksecure.sh
```

5. Run Phase 3 - Services:
```bash
sudo ./src/build-scripts/03-services.sh
```

6. Run Phase 4 - P2P Network:
```bash
sudo ./src/build-scripts/04-p2p.sh
```

### Method 2: Build ISO from Scratch (Advanced)

This requires additional tools and is documented in the Derivative-Maker wiki:
- https://www.kicksecure.com/wiki/Dev/Build_Documentation

## First-Time Setup

### After Installation

1. **Set up your user account**:
```bash
# Create your IronClad identity
ironclad-peer info
```

2. **Start services**:
```bash
# Start all services
ironclad-service start all

# Or individual services
ironclad-service start email
ironclad-service start matrix
```

3. **Configure Citadel Email**:
- Open browser: https://localhost:2000
- Follow setup wizard
- Configure your external SMTP credentials (for sending to Gmail/Outlook)

4. **Join P2P Network**:
```bash
# Show your QR code for others to scan
ironclad-peer qr

# Scan a friend's QR code
ironclad-peer scan
```

5. **Start your .ironclad website**:
```bash
# Place HTML files in /var/www/ironclad/
# Accessible at: yourname.ironclad
```

## Service Management

### Control Commands

```bash
# Start/Stop services
ironclad-service start {email|matrix|xmpp|web|sync|all}
ironclad-service stop {email|matrix|xmpp|web|sync|all}

# Check status
ironclad-service status

# Network status
ironclad-network
```

### Default Ports

| Service | URL |
|---------|-----|
| Citadel Email | https://localhost:2000 |
| Matrix Chat | http://localhost:8008 |
| Syncthing | http://localhost:8384 |
| Local Web | http://localhost |

## Troubleshooting

### Services won't start
```bash
# Check service status
systemctl status citadel
systemctl status synapse

# View logs
journalctl -u citadel -n 50
```

### P2P network issues
```bash
# Check Yggdrasil status
systemctl status yggdrasil

# View connected peers
ironclad-peer peers
```

### DNS resolution issues
```bash
# Check Unbound
systemctl status unbound
dig localhost.ironclad
```

## Building an ISO

For production ISO builds, use the Derivative-Maker system:
1. Fork: https://github.com/derivative-maker/derivative-maker
2. Modify configurations in build config
3. Run build with: `sudo ./derivative-maker --target virtualbox --flavor ironclad`

## Contributing

See LICENSE for open source license terms.
