# IronClad OS

A privacy-first, decentralized operating system built on Debian + Kicksecure.

## Overview

IronClad OS is not just a desktop operating system - it's a complete decentralized internet platform. Each IronClad machine functions as both a daily-use computer AND a server node in a P2P mesh network.

## Key Features

### Daily Use Desktop
- LXQt desktop environment
- LibreWolf browser (privacy-hardened Firefox fork)
- Nano + Gedit text editors
- Full Linux software compatibility via APT

### Built-in Decentralized Services
- **Email**: Citadel email server (SMTP/IMAP)
- **Chat**: Matrix + Briar + XMPP
- **File Sync**: Syncthing (P2P)
- **Web Hosting**: Caddy web server for *.ironclad sites

### P2P Network
- Yggdrasil mesh VPN for encrypted P2P connections
- Torrent-style DHT peer discovery
- Custom .ironclad TLD for decentralized websites
- QR code peer addition for manual network joining

### Security (Kicksecure Hardening)
- AppArmor mandatory access control
- Default-deny firewall
- TPM encryption support
- RAM wipe on shutdown
- USBGuard

## System Requirements

- **RAM**: 8 GB minimum (16 GB recommended for running all services)
- **Storage**: 500 GB minimum
- **Architecture**: x86_64 (legacy + modern hardware support)

## Documentation

See `/docs` for detailed documentation.

## License

This project is fully open source. Anyone can use, edit, and distribute without permission or attribution.

See LICENSE file for details.

## Building from Source

See docs/build-guide.md for build instructions.

## Support

- Website: ironclad-os.github.io (placeholder)
- Community: (to be established)

---

**Philosophy**: Total privacy, zero reliance on big tech, own your data, own your services.
