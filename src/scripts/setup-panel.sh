#!/bin/bash
# IronClad LXQt Panel Configuration
# Adds Tor toggle and quick access icons to desktop panel

set -e

IRONCLAD_DIR="/opt/ironclad"
PANEL_CONFIG="$HOME/.config/lxqt/panel.conf"

echo "Configuring LXQt Panel for IronClad..."

# Create IronClad menu entries
mkdir -p "$HOME/.local/share/applications"

# Control Panel desktop entry
cat > "$HOME/.local/share/applications/ironclad-control-panel.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=IronClad Control Panel
Comment=Manage IronClad services
Icon=preferences-system
Exec=firefox-esr http://localhost:8807
Terminal=false
Categories=System;Settings;
EOF

# Peer Manager desktop entry
cat > "$HOME/.local/share/applications/ironclad-peer.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=IronClad Peer Manager
Comment=Connect with other IronClad users
Icon=network-server
Exec=firefox-esr http://localhost:8807/peer
Terminal=false
Categories=Network;
EOF

# Syncthing desktop entry
cat > "$HOME/.local/share/applications/ironclad-syncthing.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=IronClad Sync
Comment=File synchronization
Icon=folder-sync
Exec=firefox-esr http://localhost:8384
Terminal=false
Categories=Network;
EOF

echo "Created desktop entries..."

# Create Tor toggle script
mkdir -p "$IRONCLAD_DIR/bin"

cat > "$IRONCLAD_DIR/bin/tor-toggle.sh" << 'EOF'
#!/bin/bash
# IronClad Tor Toggle Script

check_tor() {
    if pgrep -x "tor" > /dev/null 2>&1 || ss -tlnp | grep -q ":9050"; then
        echo "on"
    else
        echo "off"
    fi
}

toggle_tor() {
    if [ "$(check_tor)" = "on" ]; then
        # Turn off Tor
        pkill -x tor
        notify-send "IronClad" "Tor disabled"
    else
        # Turn on Tor
        /usr/sbin/tor --runasdaemon 0
        notify-send "IronClad" "Tor enabled"
    fi
}

case "$1" in
    status) check_tor ;;
    toggle) toggle_tor ;;
    *) echo "Usage: $0 {status|toggle}" ;;
esac
EOF

chmod +x "$IRONCLAD_DIR/bin/tor-toggle.sh"

echo "Created Tor toggle script..."

# Create LXQt panel configuration
mkdir -p "$HOME/.config/lxqt"

# Add IronClad widgets to panel (using LXQt standard widgets)
# We'll create a custom launcher with important actions

# Create quick launchers directory
mkdir -p "$HOME/.config/lxqt/panel.d"

# Create 01-ironclad.conf for quick launchers
cat > "$HOME/.config/lxqt/panel.d/01-ironclad.conf" << 'EOF'
[General]
theme=default

[QuickLaunch]
# IronClad Quick Launchers
items=ironclad-control-panel.desktop,ironclad-peer.desktop,ironclad-syncthing.desktop
EOF

echo "Panel configured!"

# Copy to root as well for all users
sudo cp -r "$HOME/.local" /etc/skel/
sudo cp -r "$HOME/.config" /etc/skel/

echo "Applied to default user template!"

# Create autostart for IronClad services
mkdir -p "$HOME/.config/autostart"

cat > "$HOME/.config/autostart/ironclad-control-panel.desktop" << 'EOF'
[Desktop Entry]
Type=Application
Name=IronClad Control Panel
Exec=python3 /opt/ironclad/control-panel/app.py
Terminal=false
Hidden=false
X-LXQtModule=true
EOF

sudo cp "$HOME/.config/autostart/ironclad-control-panel.desktop" /etc/xdg/autostart/

echo "Auto-start configured!"

echo ""
echo "=== IronClad Panel Setup Complete ==="
echo ""
echo "To use:"
echo "1. Right-click on LXQt panel"
echo "2. Add Widget -> Quick Launch"
echo "3. Add: IronClad Control Panel, Peer Manager, Sync"
echo ""
echo "Tor toggle: $IRONCLAD_DIR/bin/tor-toggle.sh"
