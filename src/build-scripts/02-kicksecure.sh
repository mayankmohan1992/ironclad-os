#!/bin/bash

# IronClad OS - Phase 2: Kicksecure Hardening
# Applies security hardening features

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then
   log_error "Run as root: sudo ./02-kicksecure.sh"
   exit 1
fi

log_info "=========================================="
log_info "  IronClad OS - Phase 2: Security"
log_info "=========================================="
echo ""

log_info "Step 1: Configuring AppArmor..."
apt install -y apparmor apparmor-profiles apparmor-utils 2>/dev/null || log_warn "AppArmor not available"
systemctl enable apparmor 2>/dev/null || true
systemctl start apparmor 2>/dev/null || true
aa-enforce /etc/apparmor.d/* 2>/dev/null || log_warn "Some profiles may need manual enforcement"

log_info "Step 2: Configuring firewall (nftables)..."
# Debian 12 uses nftables by default
apt install -y nftables || apt install -y iptables-persistent

# Create basic firewall rules
nft flush ruleset 2>/dev/null || true

# Default policy: drop incoming, accept outgoing
nft add table inet filter 2>/dev/null || true
nft add chain inet filter input '{ policy drop; }' 2>/dev/null || true
nft add chain inet filter forward '{ policy drop; }' 2>/dev/null || true
nft add chain inet filter output '{ policy accept; }' 2>/dev/null || true

# Allow loopback
nft add rule inet filter input iif lo accept 2>/dev/null || true

# Allow established connections  
nft add rule inet filter input ct state established,related accept 2>/dev/null || true

# Allow SSH
nft add rule inet filter input tcp dport 22 accept 2>/dev/null || true

# Allow Yggdrasil
nft add rule inet filter input ip saddr 10.0.0.0/8 accept 2>/dev/null || true

log_info "Step 3: Installing USBGuard..."
apt install -y usbguard 2>/dev/null || log_warn "USBGuard not available - skipping"
systemctl enable usbguard 2>/dev/null || true
systemctl start usbguard 2>/dev/null || true

log_info "Step 4: Configuring kernel hardening..."
# Disable core dumps
echo "* soft core 0" >> /etc/security/limits.conf
echo "* hard core 0" >> /etc/security/limits.conf
echo "kernel.core_uses_pid = 1" >> /etc/sysctl.conf
echo "kernel.dmesg_restrict = 1" >> /etc/sysctl.conf
echo "kernel.kptr_restrict = 2" >> /etc/sysctl.conf

# Disable unused filesystems
echo "install cramfs /bin/true" >> /etc/modprobe.d/disable-filesystems.conf
echo "install freevxfs /bin/true" >> /etc/modprobe.d/disable-filesystems.conf
echo "install jffs2 /bin/true" >> /etc/modprobe.d/disable-filesystems.conf
echo "install hfs /bin/true" >> /etc/modprobe.d/disable-filesystems.conf
echo "install hfsplus /bin/true" >> /etc/modprobe.d/disable-filesystems.conf
echo "install squashfs /bin/true" >> /etc/modprobe.d/disable-filesystems.conf
echo "install udf /bin/true" >> /etc/modprobe.d/disable-filesystems.conf

log_info "Step 5: Configuring network hardening..."
# Disable IP forwarding
echo "net.ipv4.ip_forward = 0" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding = 0" >> /etc/sysctl.conf

# Disable ICMP redirect acceptance
echo "net.ipv4.conf.all.accept_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv4.conf.default.accept_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.accept_redirects = 0" >> /etc/sysctl.conf
echo "net.ipv6.conf.default.accept_redirects = 0" >> /etc/sysctl.conf

# Enable TCP SYN cookies
echo "net.ipv4.tcp_syncookies = 1" >> /etc/sysctl.conf

# Apply sysctl changes
sysctl -p

log_info "Step 6: Configuring brute-force protection..."
apt install -y fail2ban 2>/dev/null || log_warn "fail2ban not available"
systemctl enable fail2ban 2>/dev/null || true

log_info "Step 7: Installing TPM tools..."
apt install -y tpm2-tools libtss2-tcti-mssim 2>/dev/null || log_warn "TPM tools not available"

log_info "Step 8: Configuring network hardening..."
# Disable IP forwarding
echo "net.ipv4.ip_forward = 0" >> /etc/sysctl.conf
echo "net.ipv6.conf.all.forwarding = 0" >> /etc/sysctl.conf

# Apply sysctl changes
sysctl -p 2>/dev/null || true

log_info "Step 9: Disabling unnecessary services..."
# Disable Bluetooth
systemctl disable bluetooth 2>/dev/null || true
systemctl mask bluetooth 2>/dev/null || true

# Disable Avahi daemon (local network discovery)
systemctl disable avahi-daemon 2>/dev/null || true
systemctl mask avahi-daemon 2>/dev/null || true

log_info "Step 10: Configuring secure SSH..."
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config 2>/dev/null || true
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config 2>/dev/null || true
systemctl restart sshd 2>/dev/null || true

log_info "=========================================="
log_info "  Phase 2 Complete!"
log_info "=========================================="
echo ""
log_info "Security hardening applied."
log_info "Next: Run 03-services.sh to install local services"
