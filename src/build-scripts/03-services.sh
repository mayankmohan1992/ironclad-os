#!/bin/bash

# IronClad OS - Phase 3: Local Services Installation
# Citadel, Matrix, Briar, XMPP, Caddy, Syncthing

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then
   log_error "Run as root: sudo ./03-services.sh"
   exit 1
fi

log_info "=========================================="
log_info "  IronClad OS - Phase 3: Services"
log_info "=========================================="
echo ""

echo "This script will install:"
echo "  1. Citadel (Email)"
echo "  2. Matrix/Synapse (Chat)"
echo "  3. Briar (P2P Chat)"
echo "  4. XMPP/Prosody (Chat)"
echo "  5. Caddy (Web Server)"
echo "  6. Syncthing (File Sync)"
echo "  7. Unbound (Local DNS)"
echo ""
read -p "Continue? (y/n): " confirm
if [[ $confirm != "y" && $confirm != "Y" ]]; then
    exit 0
fi

log_info "Step 1: Installing Citadel (Email Server)..."
apt install -y citadel-suite citadel-doc

log_info "Configuring Citadel..."
# Citadel will be configured via web interface on port 2000
# Basic config - SMTP/IMAP settings
sed -i 's/ENABLED=0/ENABLED=1/' /etc/default/citadel 2>/dev/null || true
systemctl enable citadel
systemctl start citadel

log_info "Step 2: Installing Matrix (Synapse)..."
apt install -y synapse

log_info "Configuring Matrix..."
# Generate Matrix homeserver config
python3 -m synapse.app.homeserver \
    --config-path=/etc/matrix-synapse/homeserver.yaml \
    --data-path=/var/lib/matrix-synapse \
    --generate-config \
    --report-stats=no

systemctl enable synapse
systemctl start synapse

log_info "Step 3: Installing Briar..."
apt install -y briar

log_info "Step 4: Installing XMPP (Prosody)..."
apt install -y prosody prosody-modules

log_info "Configuring Prosody..."
# Basic config
cat > /etc/prosody/prosody.cfg.lua << 'EOF'
-- Basic IronClad XMPP Configuration

admins = { }

allow_registration = false;
c2s_require_encryption = true;
s2s_require_encryption = true;
s2s_secure_auth = false;

modules_enabled = {
    "roster";
    "saslauth";
    "tls";
    "dialback";
    "disco";
    "private";
    "vcard";
    "privacy";
    "blocking";
    "version";
    "uptime";
    "time";
    "ping";
    "posix";
    "admin_adhoc";
};

daemonize = true;
pidfile = "/run/prosody/prosody.pid";

log = {
    info = "/var/log/prosody/prosody.log";
    error = "/var/log/prosody/prosody.err";
}

ssl = {
    key = "/etc/prosody/certs/localhost.key";
    certificate = "/etc/prosody/certs/localhost.crt";
}

-- Virtual hosts
VirtualHost "ironclad.local"

Component "conference.ironclad.local" "muc"
EOF

systemctl enable prosody
systemctl start prosody

log_info "Step 5: Installing Caddy (Web Server)..."
# Add Caddy repository
apt install -y debian-keyring debian-archive-keyring apt-transport-https
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/gpg.key' | gpg --dearmor -o /usr/share/keyrings/caddy-stable-archive-keyring.gpg
curl -1sLf 'https://dl.cloudsmith.io/public/caddy/stable/debian.deb.txt' | tee /etc/apt/sources.list.d/caddy-stable.list
apt update
apt install -y caddy

log_info "Configuring Caddy for .ironclad TLD..."
mkdir -p /etc/caddy/sites

# Base Caddyfile
cat > /etc/caddy/Caddyfile << 'EOF'
# IronClad OS - Caddy Configuration
# Custom .ironclad TLD configuration

:80 {
    root * /var/www/ironclad
    file_server
    bind 127.0.0.1
}

# .ironclad TLD - requires custom DNS setup
# Will be configured by ironclad-dns service
EOF

systemctl enable caddy
systemctl start caddy

log_info "Step 6: Installing Syncthing..."
apt install -y syncthing

log_info "Configuring Syncthing..."
# Enable Syncthing service
systemctl enable syncthing@$USER 2>/dev/null || true
# Create config directory
mkdir -p ~/.config/syncthing
cat > ~/.config/syncthing/config.xml << 'EOF'
<?xml version="1.0" encoding="utf-8"?>
<configuration version="40">
    <gui enabled="true" tls="false" address="127.0.0.1:8384">
        <address>127.0.0.1:8384</address>
    </gui>
    <options>
        <listenAddress>0.0.0.0:22000</listenAddress>
        <globalAnnounceEnabled>false</globalAnnounceEnabled>
        <localAnnounceEnabled>true</localAnnounceEnabled>
        <relaysEnabled>false</relaysEnabled>
    </options>
</configuration>
EOF

log_info "Step 7: Installing Unbound (Local DNS)..."
apt install -y unbound unbound-host

log_info "Configuring Unbound for .ironclad TLD..."
cat > /etc/unbound/unbound.conf.d/ironclad.conf << 'EOF'
# IronClad .ironclad TLD local DNS resolution
server:
    local-zone: "ironclad." static
    local-data: "localhost.ironclad. IN A 127.0.0.1"
    
    # This will be populated by the P2P node service
    # with all known IronClad peers
    
    # Forward everything else to system DNS
    do-not-query-localhost: no
    
    # Uncomment for DNSSEC
    # val-date: 20240101
    # val-sig-skew-min: 3600
    # val-sig-skew-max: 86400
EOF

systemctl enable unbound
systemctl restart unbound

log_info "Step 8: Creating service management GUI..."
# We'll create a proper GUI app later, for now create control scripts
mkdir -p /opt/ironclad/bin

# Service toggle script
cat > /opt/ironclad/bin/service-manager.sh << 'EOF'
#!/bin/bash
# IronClad Service Manager

case "$1" in
    start)
        case "$2" in
            email) systemctl start citadel ;;
            matrix) systemctl start synapse ;;
            briar) briar-desktop ;;
            xmpp) systemctl start prosody ;;
            web) systemctl start caddy ;;
            sync) systemctl start syncthing@$(whoami) ;;
            all) 
                systemctl start citadel
                systemctl start synapse
                systemctl start prosody
                systemctl start caddy ;;
        esac
        ;;
    stop)
        case "$2" in
            email) systemctl stop citadel ;;
            matrix) systemctl stop synapse ;;
            briar) pkill -f briar ;;
            xmpp) systemctl stop prosody ;;
            web) systemctl stop caddy ;;
            sync) systemctl stop syncthing@$(whoami) ;;
            all)
                systemctl stop citadel
                systemctl stop synapse
                systemctl stop prosody
                systemctl stop caddy ;;
        esac
        ;;
    status)
        echo "=== IronClad Services Status ==="
        echo "Email (Citadel):    $(systemctl is-active citadel)"
        echo "Chat (Matrix):      $(systemctl is-active synapse)"
        echo "Chat (XMPP):       $(systemctl is-active prosody)"
        echo "Web (Caddy):       $(systemctl is-active caddy)"
        ;;
    *)
        echo "Usage: $0 {start|stop|status} {email|matrix|xmpp|web|sync|all}"
        ;;
esac
EOF

chmod +x /opt/ironclad/bin/service-manager.sh
ln -sf /opt/ironclad/bin/service-manager.sh /usr/local/bin/ironclad-service

log_info "=========================================="
log_info "  Phase 3 Complete!"
log_info "=========================================="
echo ""
log_info "Services installed:"
echo "  - Citadel Email:     https://localhost:2000"
echo "  - Matrix Chat:       http://localhost:8008"
echo "  - XMPP Chat:         localhost:5222"
echo "  - Caddy Web:         http://localhost"
echo "  - Syncthing:         http://localhost:8384"
echo "  - Unbound DNS:       localhost:53"
echo ""
log_info "Use: ironclad-service start|stop|status <service>"
log_info "Next: Run 04-p2p.sh to configure P2P networking"
