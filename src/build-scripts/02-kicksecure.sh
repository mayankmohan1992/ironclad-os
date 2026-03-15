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
systemctl enable apparmor
systemctl start apparmor
aa-enforce /etc/apparmor.d/* 2>/dev/null || log_warn "Some profiles may need manual enforcement"

log_info "Step 2: Configuring firewall (iptables/nftables)..."
# Default deny all incoming
apt install -y iptables-persistent

# Flush existing rules
iptables -F
iptables -X

# Default policy: DROP incoming, ACCEPT outgoing
iptables -P INPUT DROP
iptables -P FORWARD DROP
iptables -P OUTPUT ACCEPT

# Allow loopback
iptables -A INPUT -i lo -j ACCEPT
iptables -A OUTPUT -o lo -j ACCEPT

# Allow established connections
iptables -A INPUT -m state --state ESTABLISHED,RELATED -j ACCEPT

# Allow SSH (user can change port)
iptables -A INPUT -p tcp --dport 22 -j ACCEPT

# Allow Yggdrasil
iptables -A INPUT -p tcp --dport 0:65535 -s 10.0.0.0/8 -j ACCEPT
iptables -A INPUT -p udp --dport 0:65535 -s 10.0.0.0/8 -j ACCEPT

# Save rules
iptables-save > /etc/iptables/rules.v4

log_info "Step 3: Installing USBGuard..."
apt install -y usbguard
systemctl enable usbguard
systemctl start usbguard

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
apt install -y fail2ban
systemctl enable fail2ban

log_info "Step 7: Installing TPM tools..."
apt install -y tpm2-tools tpm2-abrmd tpm2-eventlog
systemctl enable tpm2-abrmd

log_info "Step 8: Configuring RAM wipe on shutdown..."
cat > /etc/systemd/system/ram-wipe.service << 'EOF'
[Unit]
Description=Wipe RAM on shutdown
DefaultDependencies=no
After=shutdown.target
Before=final.target

[Service]
Type=oneshot
ExecStart=/bin/dd if=/dev/urandom of=/dev/mem bs=1M count=1024
ExecStart=/bin/sync

[Install]
WantedBy=final.target
EOF

systemctl daemon-reload
systemctl enable ram-wipe.service

log_info "Step 9: Disabling unnecessary services..."
# Disable Bluetooth
systemctl disable bluetooth 2>/dev/null || true
systemctl mask bluetooth

# Disable Avahi daemon (local network discovery)
systemctl disable avahi-daemon 2>/dev/null || true
systemctl mask avahi-daemon

log_info "Step 10: Configuring secure SSH..."
sed -i 's/^#*PermitRootLogin.*/PermitRootLogin no/' /etc/ssh/sshd_config
sed -i 's/^#*PasswordAuthentication.*/PasswordAuthentication no/' /etc/ssh/sshd_config
sed -i 's/^#*X11Forwarding.*/X11Forwarding no/' /etc/ssh/sshd_config
echo "AllowUsers ironclad" >> /etc/ssh/sshd_config
systemctl restart sshd

log_info "=========================================="
log_info "  Phase 2 Complete!"
log_info "=========================================="
echo ""
log_info "Security hardening applied."
log_info "Next: Run 03-services.sh to install local services"
