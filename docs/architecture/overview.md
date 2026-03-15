# IronClad OS Architecture

## Overview

IronClad OS is a privacy-first, decentralized operating system that combines:
1. Daily-use desktop (LXQt + LibreWolf)
2. Self-hosted services (Email, Chat, Web)
3. P2P mesh networking (Yggdrasil)
4. Security hardening (Kicksecure)

## Layer Architecture

```
┌─────────────────────────────────────────────┐
│ Layer 1: Desktop Environment                 │
│ - LXQt Desktop                              │
│ - LibreWolf browser                         │
│ - Nano + Gedit editors                       │
│ - Any Linux software (apt)                  │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Layer 2: Local Services                      │
│ - Citadel (Email SMTP/IMAP)                 │
│ - Matrix/Synapse (Chat)                     │
│ - Briar (P2P Chat)                          │
│ - XMPP/Prosody (Chat)                       │
│ - Caddy (Web Server)                       │
│ - Syncthing (File Sync)                     │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Layer 3: P2P Network                         │
│ - Yggdrasil (Mesh VPN)                      │
│ - Custom .ironclad TLD                      │
│ - QR Code peer addition                     │
│ - Node Registry (distributed)               │
└─────────────────────────────────────────────┘
                    │
                    ▼
┌─────────────────────────────────────────────┐
│ Layer 4: Security Hardening                  │
│ - AppArmor (Mandatory Access Control)      │
│ - Firewall (default deny)                   │
│ - TPM encryption support                    │
│ - RAM wipe on shutdown                      │
│ - USBGuard                                  │
└─────────────────────────────────────────────┘
```

## Component Details

### Desktop Layer
- **LXQt**: Lightweight Qt desktop environment
- **LibreWolf**: Privacy-hardened Firefox fork
- **Nano/Gedit**: Terminal and GUI text editors

### Services Layer
Each service can be enabled/disabled via service-manager:
```
ironclad-service start|stop {email|matrix|xmpp|web|sync|all}
```

#### Email (Citadel)
- Full email server with SMTP/IMAP
- Web interface: https://localhost:2000
- Users configure their own external SMTP relay
- Internal @ironclad.local addresses

#### Chat (Matrix + Briar + XMPP)
- **Matrix/Synapse**: Federated chat, Discord-like
- **Briar**: P2P encrypted messaging, works offline
- **XMPP/Prosody**: Classic federated chat

#### Web Hosting (.ironclad)
- Caddy web server
- Custom .ironclad TLD
- Resolves to Yggdrasil IPv6 addresses
- Each user gets: username.ironclad

### P2P Network Layer

#### Yggdrasil
- Mesh VPN over IPv6
- End-to-end encryption
- Automatic peer discovery via multicast
- Manual peer addition via QR codes

#### Node Registry
- JSON file storing all known IronClad nodes
- Distributed via P2P sync
- Format:
```json
{
  "nodes": {
    "alice": {
      "ygg_address": "xxx::xxx",
      "public_key": "xxx",
      "last_seen": 1234567890
    }
  }
}
```

#### DNS Resolution
- Local Unbound DNS server
- Intercepts .ironclad TLD queries
- Returns Yggdrasil IPv6 addresses

### Security Layer

Inherits all Kicksecure hardening:
- AppArmor mandatory access control
- Default-deny iptables firewall
- Kernel hardening (kptr_restrict, dmesg_restrict)
- Brute-force protection (fail2ban)
- USBGuard
- TPM 2.0 tools
- RAM wipe on shutdown

## Build System

IronClad uses a phased build approach:
1. **01-setup.sh**: Debian + Kicksecure base
2. **02-kicksecure.sh**: Security hardening
3. **03-services.sh**: Local services
4. **04-p2p.sh**: P2P networking

## Network Ports

| Service | Port | Protocol |
|---------|------|----------|
| Citadel (HTTP) | 2000 | TCP |
| Citadel (SMTP) | 25 | TCP |
| Citadel (IMAP) | 143 | TCP |
| Matrix | 8008 | TCP |
| XMPP | 5222 | TCP |
| Caddy (HTTP) | 80 | TCP |
| Syncthing | 22000 | TCP |
| Yggdrasil | Dynamic | TCP/UDP |

## Data Storage

- **System**: Standard Debian filesystem
- **Services**: /var/lib/* (each service)
- **P2P Registry**: /opt/ironclad/p2p/nodes.json
- **Websites**: /var/www/ironclad/

## Future Enhancements

- Video hosting (PeerTube)
- Social network
- Office suite integration
- Mobile companion app
