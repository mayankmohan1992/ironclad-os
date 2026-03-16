# 🛡️ IronClad OS

A privacy-first, decentralized operating system built on Debian + Kicksecure. Each IronClad machine functions as both a daily-use computer AND a server node in a P2P mesh network.

![Status](https://img.shields.io/badge/Status-Alpha-yellow)
![Base](https://img.shields.io/badge/Base-Debian%2012-blue)
![Arch](https://img.shields.io/badge/Arch-ARM64%20%7C%20x86__64-green)

## ✨ Features

### 🔐 Privacy & Security
- **Kicksecure Hardening** - Security-focused Debian
- **Tor Integration** - System-wide Tor routing (optional)
- **Per-App Tor Rules** - Choose which apps use Tor
- **AppArmor** - Mandatory access control

### 🌐 P2P Network
- **Yggdrasil** - Encrypted IPv6 mesh VPN
- **No Central Servers** - Peer-to-peer
- **QR Code Peering** - Easy network joining
- **Unique Identity** - Every user has a Node ID

### 📧 Self-Hosted Services
- **Email** - Postfix SMTP
- **Chat** - XMPP (Prosody)
- **File Sync** - Syncthing
- **DNS** - Unbound local resolver

### 🌐 Decentralized Websites
- **.ironclad Domains** - Host your own website
- **First-Come-First-Serve** - Unique usernames
- **Seed Phrase Recovery** - BIP39-like 12-word backup

### 🖥️ Desktop
- **LXQt** - Lightweight Qt desktop
- **Firefox ESR** - Privacy browser
- **Full Linux** - Install any apt package

## 🚀 Quick Access

| Service | URL |
|---------|-----|
| Control Panel | http://192.168.64.3:8807 |
| Syncthing | http://192.168.64.3:8384 |
| Website | http://[205:4fc:d984:385:7dc1:fa2d:9c4e:5082]/ |

## 🔌 SSH Connection (For Developers)

```bash
# Install sshpass
brew install sshpass

# Connect to VM
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3

# With sudo
sshpass -p '9300' ssh -o StrictHostKeyChecking=no -t mayankmohan@192.168.64.3 "echo '9300' | sudo -S command"
```

**VM**: IP 192.168.64.3 | User: mayankmohan | Pass: 9300

## 🔧 Commands

```bash
# Health check
python3 /opt/ironclad/scripts/health-check.py

# Tor management
python3 /opt/ironclad/bin/tor-manager.py status

# Website
python3 /opt/ironclad/bin/ironclad-website.py status
python3 /opt/ironclad/bin/ironclad-website.py claim mysite
```

## 📁 Structure

```
ironclad-os/
├── src/
│   ├── build-scripts/     # Install scripts
│   ├── control-panel/    # Flask UI
│   └── scripts/          # Utilities
├── docs/                 # Docs
├── AGENTS.md             # AI context
├── TODO.md              # Features
└── SUMMARY.md           # Progress
```

## 📋 Current Status

### Working ✅
- Debian 12 + Kicksecure
- LXQt Desktop
- Yggdrasil P2P
- Tor Proxy
- nginx, Postfix, Prosody, Unbound
- Syncthing
- Web Control Panel
- QR Code Peer System
- .ironclad Websites
- Seed Phrase Recovery

### In Progress 🚧
- Per-app Tor rules
- System-wide Tor
- HTTPS for .ironclad

## 🔗 Links

- **GitHub**: https://github.com/mayankmohan1992/ironclad-os

## 📄 License

Open source - anyone can use, edit, distribute.

---

**Philosophy**: Total privacy, zero reliance on big tech, own your data.
