#!/bin/bash

# IronClad OS - Main Build Script
# Phase 1: Foundation Setup

set -e

echo "=========================================="
echo "  IronClad OS - Phase 1: Foundation"
echo "=========================================="
echo ""

# Color codes
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

log_info() {
    echo -e "${GREEN}[INFO]${NC} $1"
}

log_warn() {
    echo -e "${YELLOW}[WARN]${NC} $1"
}

log_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Check if running as root
if [[ $EUID -ne 0 ]]; then
   log_warn "This script should be run as root for system installation"
   log_info "Run with: sudo ./01-setup.sh"
   exit 1
fi

# Detect if we're on Debian-based system
if [[ ! -f /etc/debian_version ]]; then
    log_error "This script requires a Debian-based system (Debian, Mint, Ubuntu)"
    exit 1
fi

log_info "Starting IronClad Foundation Setup..."
log_info "This script will:"
echo "  1. Update system packages"
echo "  2. Install build dependencies"
echo "  3. Set up Kicksecure repositories"
echo "  4. Configure US English only locale"
echo "  5. Configure US keyboard only"
echo "  6. Install base packages"
echo ""

read -p "Continue? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    log_info "Aborted."
    exit 0
fi

echo ""
log_info "Step 1: Updating package lists..."
apt update

echo ""
log_info "Step 2: Installing build dependencies..."
apt install -y \
    git \
    curl \
    wget \
    gnupg2 \
    apt-transport-https \
    ca-certificates \
    software-properties-common \
    debootstrap \
    grml-debootstrap \
    live-build \
    live-tools \
    squashfs-tools \
    xorriso \
    isolinux \
    syslinux-utils \
    dosfstools \
    parted \
    gdisk

echo ""
log_info "Step 3: Setting up Kicksecure repository..."
# Add Kicksecure repository
wget -q https://www.kicksecure.com/keys/derivative.asc -O- | apt-key add -
echo "deb https://deb.kicksecure.com/ bookworm main" > /etc/apt/sources.list.d/kicksecure.list

# Add Debian repository (if not present)
if ! grep -q "deb.debian.org" /etc/apt/sources.list 2>/dev/null; then
    echo "deb http://deb.debian.org/debian bookworm main contrib non-free" >> /etc/apt/sources.list
    echo "deb http://deb.debian.org/debian bookworm-updates main contrib non-free" >> /etc/apt/sources.list
    echo "deb http://deb.debian.org/debian-security bookworm-security main contrib non-free" >> /etc/apt/sources.list
fi

apt update

echo ""
log_info "Step 4: Installing Kicksecure packages..."
apt install -y \
    kicksecure-packages \
    security-misc \
    apparmor-profiles \
    apparmor-utils \
    apparmor-notify

echo ""
log_info "Step 5: Configuring US English locale..."
# Remove other locales
sed -i '/en_US.UTF-8/s/^# //g' /etc/locale.gen
sed -i '/en_US.UTF-8/s/ ^/#/' /etc/locale.gen 2>/dev/null || true
locale-gen en_US.UTF-8

# Set system locale
echo "LANG=en_US.UTF-8" > /etc/locale.conf
echo "LANGUAGE=en_US" >> /etc/locale.conf

echo ""
log_info "Step 6: Configuring US keyboard only..."
# Configure keyboard for X11
echo 'XKBMODEL="pc105"
XKBLAYOUT="us"
XKBVARIANT=""
XKBOPTIONS="terminate:ctrl_alt_bksp"
BACKSPACE="guess"' > /etc/default/keyboard

# Configure console keyboard
echo 'KEYMAP="us"' > /etc/vconsole.conf

echo ""
log_info "Step 7: Installing minimal base packages..."
apt install -y \
    nano \
    gedit \
    firefox-esr \
    network-manager \
    systemd \
    dbus

echo ""
log_info "Step 8: Configuring package removal (bloatware removal)..."
# Remove Snap (if present)
apt purge -y snapd 2>/dev/null || true

# Remove Ubuntu/Mint specific packages (if any)
apt purge -y \
    thunderbird* \
    libreoffice* \
    flatpak \
    ubuntu-report \
    ubuntu-client-launcher \
    mint-* \
    2>/dev/null || true

apt autoremove -y

echo ""
log_info "Step 9: Configuring network..."
# Disable IPv6 if desired (optional - currently enabled for Yggdrasil)
# echo "1" > /proc/sys/net/ipv6/conf/all/disable_ipv6

echo ""
log_info "Step 10: Setting up IronClad version file..."
echo "IronClad OS v0.1.0-alpha" > /etc/ironclad-version
echo "Base: Debian Bookworm + Kicksecure" >> /etc/ironclad-version

log_info "=========================================="
log_info "  Phase 1 Complete!"
log_info "=========================================="
echo ""
log_info "Next steps:"
echo "  1. Reboot your system"
echo "  2. Run: sudo ./02-kicksecure.sh"
echo ""
