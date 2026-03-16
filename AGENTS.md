# IronClad OS - Agent Context Guide

This file provides context for AI agents continuing development of IronClad OS.

## Project Overview

**IronClad OS** is a privacy-first, decentralized operating system built on Debian 12 + Kicksecure. Each installation functions as both a daily-use desktop AND a server node in a P2P mesh network.

### Core Vision
- Total privacy, zero reliance on big tech
- Users own their data, host their own services
- P2P network for communication without central servers
- Decentralized website hosting (.ironclad domains)

---

## SSH Connection Instructions (CRITICAL)

This section is essential for connecting to the development VM.

### SSH Access Method

**Connection Details:**
- **IP Address**: 192.168.64.3
- **Port**: 22 (default SSH)
- **Username**: mayankmohan
- **Password**: 9300

### Using sshpass (RECOMMENDED)

The connection requires `sshpass` to automate password entry:

```bash
# Install sshpass on Mac
brew install sshpass

# Basic SSH connection
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "command"

# With sudo (required for system changes)
sshpass -p '9300' ssh -o StrictHostKeyChecking=no -t mayankmohan@192.168.64.3 "echo '9300' | sudo -S command"
```

### SSH Command Examples

```bash
# Simple command
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "hostname"

# Run with sudo
sshpass -p '9300' ssh -o StrictHostKeyChecking=no -t mayankmohan@192.168.64.3 "echo '9300' | sudo -S apt update"

# Copy files to VM
sshpass -p '9300' scp -o StrictHostKeyChecking=no file.txt mayankmohan@192.168.64.3:/tmp/

# Copy files from VM
sshpass -p '9300' scp -o StrictHostKeyChecking=no mayankmohan@192.168.64.3:/tmp/file.txt ./
```

### Common Issues & Fixes

1. **"No route to host"**
   - Wait a moment, VM may be restarting
   - Check VM is running in UTM

2. **"Permission denied"**
   - Password may be wrong - verify: 9300
   - SSH password auth may be disabled - enable it in VM:
     ```bash
     sudo sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication yes/' /etc/ssh/sshd_config
     sudo systemctl restart ssh
     ```

3. **"sudo: a terminal is required"**
   - Always use: `echo '9300' | sudo -S command`
   - Or use: `ssh -t` for terminal allocation

---

## Current Status

### Working Features
- Debian 12 base with Kicksecure hardening
- LXQt desktop environment
- Firefox ESR browser
- Yggdrasil P2P network (running, Node ID: `07ec0c99eff1ea08f817498ec6bdf623752803a899848c9f3708c5f65720cd71`)
- Tor proxy (can be toggled on/off)
- nginx web server
- Postfix email (SMTP)
- Prosody XMPP chat
- Unbound DNS server
- Syncthing file sync
- Control Panel web UI (port 8807)
- QR Code peer connection system
- .ironclad website hosting with seed phrase recovery

### Access Points (VM IP: 192.168.64.3)
- Control Panel: http://192.168.64.3:8807
- Syncthing: http://192.168.64.3:8384
- Website: http://[205:4fc:d984:385:7dc1:fa2d:9c4e:5082]/

### Registered User
- Username: `mayank`
- Website: `blog.mayank.ironclad`

---

## Key Scripts & Locations

| Script | Purpose |
|--------|---------|
| `/opt/ironclad/control-panel/app.py` | Flask web control panel |
| `/opt/ironclad/bin/tor-manager.py` | Per-app Tor rules manager |
| `/opt/ironclad/bin/ironclad-website.py` | Website hosting & username registry |
| `/opt/ironclad/scripts/health-check.py` | System health check & auto-fix |
| `/src/scripts/setup-panel.sh` | LXQt panel configuration |

---

## Important Configuration

### Services
- Tor listens on 127.0.0.1:9050
- Yggdrasil admin socket: /var/run/yggdrasil/yggdrasil.sock
- Control panel runs on port 8807 (not 598631 due to conflict)
- nginx serves /var/www/ironclad/

### DNS
- Unbound configured with .ironclad local zone
- Config file: /etc/unbound/unbound.conf.d/ironclad.conf

### Registry
- User registry: /opt/ironclad/registry/users.json
- Identity file: /opt/ironclad/registry/identity.json

---

## Build Environment

- **VM**: UTM on Mac M2 (Apple Silicon)
- **OS**: Debian 12 ARM64 (Bookworm)
- **Connection**: SSH on 192.168.64.3
- **Password**: 9300

---

## Common Commands

```bash
# Health check
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "python3 /opt/ironclad/scripts/health-check.py"

# Tor management
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "python3 /opt/ironclad/bin/tor-manager.py status"

# Website management
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "python3 /opt/ironclad/bin/ironclad-website.py status"

# Check service status
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "systemctl status nginx"

# Restart service
sshpass -p '9300' ssh -o StrictHostKeyChecking=no -t mayankmohan@192.168.64.3 "echo '9300' | sudo -S systemctl restart nginx"
```

---

## Issues to Address

1. **Port conflicts**: Control panel initially tried 598631 but used 8807
2. **Syncthing lock**: Had to remove lock files to start
3. **Yggdrasil config**: Required moving to /etc/yggdrasil/yggdrasil.conf
4. **Tor daemon**: Started manually via /usr/sbin/tor --runasdaemon 0
5. **Unbound DNS**: Required fixing config syntax

---

## Next Development Priorities

1. Per-app Tor rules - toggle which apps use Tor
2. System-wide Tor routing (iptables redirect)
3. Multiple websites per user (currently limited)
4. Syncthing integration for registry sync between peers
5. LXQt panel launcher icons setup
6. Seed phrase backup/restore UI
7. Create ISO/installer

---

## Documentation Files

- `README.md` - Project overview
- `TODO.md` - Features to implement
- `SUMMARY.md` - What's been done
- `docs/` - Detailed documentation

---

## GitHub Repository

https://github.com/mayankmohan1992/ironclad-os
