# IronClad OS - TODO List

## Project Objective
Build a privacy-first, decentralized OS where users own their data, host their own services, and communicate without relying on big tech.

---

## SSH Connection (CRITICAL - Read First!)

To connect to the VM, use:

```bash
# Install sshpass first
brew install sshpass

# Basic connection
sshpass -p '9300' ssh -o StrictHostKeyChecking=no mayankmohan@192.168.64.3 "command"

# With sudo (for system changes)
sshpass -p '9300' ssh -o StrictHostKeyChecking=no -t mayankmohan@192.168.64.3 "echo '9300' | sudo -S command"
```

**VM Details:**
- IP: 192.168.64.3
- Username: mayankmohan
- Password: 9300

---

## Completed Features ✅

### Phase 1: Foundation
- [x] Debian 12 base installation
- [x] Kicksecure security hardening (partial)
- [x] LXQt desktop environment
- [x] Firefox ESR browser
- [x] US English locale & keyboard only
- [x] Remove bloat (Snap, Flatpak)

### Phase 2: Services
- [x] nginx web server
- [x] Postfix email (SMTP)
- [x] Prosody XMPP chat
- [x] Unbound DNS server
- [x] Syncthing file sync

### Phase 3: P2P Network
- [x] Yggdrasil P2P mesh VPN
- [x] QR code peer generation
- [x] Manual peer addition via Node ID

### Phase 4: Control Panel
- [x] Flask web control panel (port 8807)
- [x] Service status display
- [x] Service toggle buttons
- [x] Tor status display
- [x] QR code peer page

### Phase 5: Website Hosting
- [x] Username registry (file-based)
- [x] First-come-first-serve registration
- [x] Seed phrase generation (BIP39-like)
- [x] Seed phrase recovery
- [x] Website claiming (5/week limit)
- [x] DNS resolution for .ironclad
- [x] nginx virtual hosting

### Phase 6: Utilities
- [x] Unified health check script
- [x] Auto-fix capabilities
- [x] Pretty colored output
- [x] System information display

---

## Incomplete Features 🚧

### Tor System
- [ ] Per-app Tor rules (toggle which apps use Tor)
- [ ] System-wide Tor routing (iptables redirect all traffic)
- [ ] DNS leak protection
- [ ] Auto-fallback to direct connection
- [ ] Per-app config UI in control panel

### Website Hosting
- [ ] Multiple websites per user (limit enforcement)
- [ ] HTTPS with internal CA
- [ ] Website template selection
- [ ] Auto-update DNS when Yggdrasil IP changes

### Syncthing Integration
- [ ] Pre-configured default sync folder
- [ ] Control panel sync status
- [ ] Add device via Node ID UI
- [ ] Multiple sync folders management

### LXQt Panel
- [ ] Quick launcher icons setup
- [ ] Tor status indicator in panel
- [ ] Desktop shortcuts

### Seed Phrase
- [ ] Backup seed phrase UI
- [ ] Restore seed phrase UI
- [ ] Export/import identity

### Installation
- [ ] ISO builder
- [ ] Installer (Calamares or simple)
- [ ] Live USB creation

### Testing
- [ ] Feature-specific test scripts
- [ ] Unit tests
- [ ] Integration tests

---

## Known Issues

1. **Port 598631 conflict** - Control panel runs on 8807
2. **Syncthing lock files** - May need manual removal
3. **Tor starts manually** - Not as systemd service
4. **.ironclad DNS** - Only resolves via Unbound, not system-wide

---

## Feature Priority (Next Session)

### High Priority
1. Per-app Tor rules + UI
2. System-wide Tor routing
3. Fix DNS resolution for .ironclad

### Medium Priority
4. HTTPS for .ironclad sites
5. Syncthing integration
6. Seed phrase backup UI

### Low Priority
7. LXQt panel icons
8. ISO builder
9. Testing scripts

---

## Architecture Decisions

| Component | Choice | Rationale |
|-----------|--------|-----------|
| P2P Network | Yggdrasil | IPv6 mesh, encrypted |
| DNS | Unbound | Local resolution for .ironclad |
| Registry | File-based JSON | Simple, first implementation |
| Recovery | BIP39 seed phrase | Standard crypto recovery |
| Control Panel | Flask | Easy to extend, Python |
| Web Server | nginx | Lightweight, reliable |

---

## References

- Control Panel: http://192.168.64.3:8807
- GitHub: https://github.com/mayankmohan1992/ironclad-os
- VM IP: 192.168.64.3
- Yggdrasil IPv6: 205:4fc:d984:385:7dc1:fa2d:9c4e:5082
