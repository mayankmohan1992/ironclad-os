#!/bin/bash

# IronClad OS - Desktop Environment Installation
# Install LXQt desktop + LibreWolf + tools

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then
   log_warn "Run as root: sudo ./05-desktop.sh"
   exit 1
fi

log_info "=========================================="
log_info "  IronClad OS - Desktop Environment"
log_info "=========================================="
echo ""

log_info "Step 1: Installing LXQt Desktop Environment..."
apt update
apt install -y \
    lxqt \
    lightdm \
    sddm \
    xorg \
    xserver-xorg-core \
    xserver-xorg-video-qxl \
    xserver-xorg-video-vmware \
    xserver-xorg-video-fbdev \
    x11-utils \
    x11-xserver-utils \
    arandr \
    lxterminal \
    pcmanfm-qt \
    qterminal

log_info "Step 2: Installing LibreWolf browser..."
# Add LibreWolf repository
apt install -y wget gnupg2
wget -q https://deb.librewolf.net/keyring.gpg -O /usr/share/keyrings/librewolf.gpg
echo "deb [signed-by=/usr/share/keyrings/librewolf.gpg] https://deb.librewolf.net/debian bookworm main" > /etc/apt/sources.list.d/librewolf.list
apt update
apt install -y librewolf

log_info "Step 3: Installing essential GUI applications..."
apt install -y \
    gedit \
    firefox-esr \
    file-roller \
    galculator \
    lxappearance \
    lxhotkey \
    lxinput \
    lxrandr \
    lxsession-edit \
    lxtask \
    lxweather \
    network-manager-gnome \
    nm-connection-editor \
    policykit-1-gnome \
    qt5ct \
    qt5-style-plugins

log_info "Step 4: Installing additional tools..."
apt install -y \
    ark \
    bind9-utils \
    chrony \
    curl \
    dnsutils \
    fdisk \
    gdisk \
    git \
    htop \
    iotop \
    lm-sensors \
    nano \
    net-tools \
    network-manager \
    nmap \
    rsync \
    sudo \
    sysstat \
    tree \
    unzip \
    vim \
    wget \
    zip

log_info "Step 5: Configuring display manager..."
systemctl enable lightdm
systemctl set-default graphical.target

log_info "Step 6: Creating IronClad branding..."
mkdir -p /usr/share/icons/hicolor/256x256/apps
cat > /usr/share/icons/hicolor/256x256/apps/ironclad.png << 'EOF'
EOF

# Create simple menu entry
mkdir -p /etc/xdg/menus
cat > /etc/xdg/menus/applications-merged/ironclad.menu << 'EOF'
<!DOCTYPE Menu>
<Menu>
    <Name>IronClad</Name>
    <Menu>
        <Name>Internet</Name>
        <Include>
            <Category>Network</Category>
        </Include>
    </Menu>
</Menu>
EOF

log_info "=========================================="
log_info "  Desktop Installation Complete!"
log_info "=========================================="
echo ""
log_info "To start desktop, run:"
echo "  sudo systemctl start lightdm"
echo "  sudo reboot"
echo ""
log_info "Or: sudo init 5"
