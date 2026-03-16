# IronClad OS - Development Summary

## What Was Built

This document summarizes what was accomplished in the first development session.

---

## SSH Connection (CRITICAL!)

To connect to the VM:

```bash
# Install sshpass
brew install sshpass

# Connect
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3

# Run command with sudo
sshpass -p '9300' ssh -o StrictHostKeyChecking=no -t mayankmohan@192.168.64.3 "echo '9300' | sudo -S command"
```

**VM Details:**
- IP: 192.168.64.3
- Username: mayankmohan
- Password: 9300

---

## Session Overview

**Duration**: ~4 hours
**Platform**: Debian 12 ARM64 (via UTM on Mac M2)
**Connection**: SSH to 192.168.64.3

---

## Completed Milestones

### 1. Base System Installation
- Installed Debian 12 (Bookworm) ARM64
- Added Kicksecure repositories
- Configured US English locale
- Configured US keyboard only
- Removed bloat packages

### 2. Desktop Environment
- Installed LXQt
- Configured LightDM display manager
- Added Firefox ESR
- Added Gedit editor

### 3. Core Services
| Service | Port | Status |
|---------|------|--------|
| nginx | 80 | ✅ Running |
| Postfix | 25 | ✅ Running |
| Prosody (XMPP) | 5222 | ✅ Running |
| Unbound | 53 | ✅ Running |
| Syncthing | 8384 | ✅ Running |
| Yggdrasil | - | ✅ Running |
| Tor | 9050 | ✅ Running |

### 4. P2P Network
- Installed Yggdrasil 0.5.13
- Generated Node ID: `07ec0c99eff1ea08f817498ec6bdf623752803a899848c9f3708c5f65720cd71`
- IPv6: `205:4fc:d984:385:7dc1:fa2d:9c4e:5082`
- Created QR code peer system

### 5. Control Panel (Flask)
- Built beautiful web UI with card-style layout
- Shows all service statuses
- Toggle buttons for services
- QR code peer page
- Running on port 8807

### 6. Website Hosting System
- Created username registry: `/opt/ironclad/registry/users.json`
- Implemented first-come-first-serve registration
- Created BIP39-like seed phrase (12 words) for recovery
- Website claiming system with 5/week limit
- DNS resolution for .ironclad via Unbound

### 7. User Registration
- Username: `mayank`
- Seed phrase: Generated and stored
- Website: `blog.mayank.ironclad`

### 8. Health Check Script
- Pretty colored output
- Checks all 8 services
- Auto-fixes common issues
- Shows system info (hostname, uptime, RAM, disk)
- Network connectivity checks

---

## Technical Challenges Solved

### Issue 1: Port Conflicts
- **Problem**: Control panel initially tried port 598631 but something else was using it
- **Solution**: Changed to port 8807

### Issue 2: Syncthing Lock Files
- **Problem**: Syncthing failed with "Failed to acquire lock"
- **Solution**: Removed lock files from ~/.config/syncthing/

### Issue 3: Yggdrasil Config Location
- **Problem**: yggdrasilctl couldn't find config file
- **Solution**: Moved config to /etc/yggdrasil/yggdrasil.conf

### Issue 4: Tor Service
- **Problem**: systemd service for Tor wouldn't start reliably
- **Solution**: Started manually via `/usr/sbin/tor --runasdaemon 0`

### Issue 5: Unbound DNS Syntax
- **Problem**: Initial .ironclad DNS config had syntax errors
- **Solution**: Fixed local-data entries, removed invalid local-data-ptr

### Issue 6: SSH Connection
- **Problem**: Needed passwordless sudo for automation
- **Solution**: Used sshpass with password, configured sudo to not require password for specific commands

---

## File Structure Created

```
ironclad-os/
├── src/
│   ├── build-scripts/
│   │   ├── 01-setup.sh       # Base system
│   │   ├── 02-kicksecure.sh # Security
│   │   ├── 03-services.sh   # Services
│   │   ├── 04-p2p.sh        # P2P network
│   │   └── 05-desktop.sh    # Desktop
│   ├── control-panel/
│   │   ├── app.py           # Flask app
│   │   └── templates/
│   │       ├── index.html   # Main UI
│   │       └── peer.html   # QR code
│   └── scripts/
│       ├── health-check.py         # Health check
│       ├── tor-manager.py          # Tor rules
│       ├── ironclad-website.py    # Website hosting
│       └── setup-panel.sh         # LXQt panel
├── docs/
│   ├── architecture/
│   └── build-guide.md
├── AGENTS.md         # Context for AI agents
├── TODO.md           # Features list
└── SUMMARY.md        # This file
```

---

## Commands Learned/Used

```bash
# SSH with password
sshpass -p '9300' ssh user@host

# Copy files
sshpass -p '9300' scp file user@host:/path

# Run sudo without password
echo 'password' | sudo -S command

# Check service status
systemctl is-active service

# Check process
pgrep -x processname

# Check port
ss -tlnp | grep :port

# Start Tor
/usr/sbin/tor --runasdaemon 0

# Generate QR code
qrencode -t utf8 "text"

# DNS lookup
nslookup domain localhost
```

---

## Access Points

| Service | URL |
|---------|-----|
| Control Panel | http://192.168.64.3:8807 |
| Syncthing | http://192.168.64.3:8384 |
| Website | http://[205:4fc:d984:385:7dc1:fa2d:9c4e:5082]/ |
| XMPP | localhost:5222 |
| SMTP | localhost:25 |

---

## What Was Learned

1. **Debian ARM64 on UTM** - Works well on Mac M2
2. **Systemd vs manual** - Some services (Tor, Yggdrasil) work better started manually
3. **Flask for UIs** - Quick to build, easy to extend
4. **Unbound DNS** - Can create local zones for custom TLDs
5. **Yggdrasil** - P2P IPv6 mesh network, works well
6. **SSH automation** - Requires passwordless sudo or sshpass

---

## Next Steps (For Next Session)

1. Per-app Tor rules with UI
2. System-wide Tor routing
3. Fix .ironclad DNS to work system-wide
4. HTTPS for .ironclad sites
5. Syncthing folder management
6. Seed phrase backup UI
7. LXQt panel setup
8. ISO builder

---

## Statistics

- **Files created**: 20+
- **Scripts written**: 4 Python, 5 Bash
- **Services configured**: 8
- **Hours**: ~4
- **Commits**: 10+

---

*Generated: 2026-03-16*
*Project: IronClad OS*
*Repository: https://github.com/mayankmohan1992/ironclad-os*
