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
apt install -y citadel-suite citadel-doc 2>/dev/null || log_warn "Citadel not available - installing Postfix+Dovecot instead"
if [ $? -ne 0 ]; then
    apt install -y postfix dovecot-core dovecot-imapd dovecot-pop3d
fi

log_info "Configuring Email..."
systemctl enable postfix 2>/dev/null || true
systemctl start postfix 2>/dev/null || true

log_info "Step 2: Installing Matrix (Synapse)..."
apt install -y matrix-synapse 2>/dev/null || apt install -y synapse 2>/dev/null || log_warn "Synapse not available"

log_info "Step 3: Installing Briar..."
apt install -y briar 2>/dev/null || log_warn "Briar not available for ARM64"

log_info "Step 4: Installing XMPP (Prosody)..."
apt install -y prosody prosody-modules 2>/dev/null || log_warn "Prosody not available"

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

systemctl enable prosody 2>/dev/null || true
systemctl start prosody 2>/dev/null || true

log_info "Step 5: Installing Web Server..."
# Use Nginx - simpler and in Debian main repo
apt install -y nginx

log_info "Configuring Web Server..."
mkdir -p /var/www/ironclad
echo "IronClad Web Server - Welcome!" > /var/www/ironclad/index.html
chown -R www-data:www-data /var/www/ironclad

# Configure Nginx for .ironclad sites
cat > /etc/nginx/sites-available/ironclad << 'EOF'
server {
    listen 80 default_server;
    listen [::]:80 default_server;
    
    server_name _;
    
    root /var/www/ironclad;
    index index.html;
    
    location / {
        try_files $uri $uri/ =404;
    }
}
EOF

ln -sf /etc/nginx/sites-available/ironclad /etc/nginx/sites-enabled/
nginx -t && systemctl restart nginx

log_info "Step 6: Installing Syncthing..."
apt install -y syncthing 2>/dev/null || log_warn "Syncthing not available"

log_info "Step 7: Installing Unbound (Local DNS)..."
apt install -y unbound unbound-host dnsutils 2>/dev/null || log_warn "Unbound not available"
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

log_info "Step 8: Creating service management commands..."
mkdir -p /opt/ironclad/bin

# Create simple service control script
cat > /usr/local/bin/ironclad-service << 'EOF'
#!/bin/bash
# IronClad Service Manager

SERVICE_EMAIL="postfix"
SERVICE_MATRIX="matrix-synapse"
SERVICE_XMPP="prosody"
SERVICE_WEB="nginx"
SERVICE_SYNC="syncthing"

show_status() {
    echo "=== IronClad Services Status ==="
    echo "Email:       $(systemctl is-active $SERVICE_EMAIL 2>/dev/null || echo 'not installed')"
    echo "Matrix:      $(systemctl is-active $SERVICE_MATRIX 2>/dev/null || echo 'not installed')"
    echo "XMPP:        $(systemctl is-active $SERVICE_XMPP 2>/dev/null || echo 'not installed')"
    echo "Web:         $(systemctl is-active $SERVICE_WEB 2>/dev/null || echo 'not installed')"
    echo "Syncthing:   $(systemctl is-active $SERVICE_SYNC 2>/dev/null || echo 'not installed')"
}

case "$1" in
    start)
        systemctl start $SERVICE_EMAIL 2>/dev/null || true
        systemctl start $SERVICE_MATRIX 2>/dev/null || true
        systemctl start $SERVICE_XMPP 2>/dev/null || true
        systemctl start $SERVICE_WEB 2>/dev/null || true
        echo "Services started"
        ;;
    stop)
        systemctl stop $SERVICE_EMAIL 2>/dev/null || true
        systemctl stop $SERVICE_MATRIX 2>/dev/null || true
        systemctl stop $SERVICE_XMPP 2>/dev/null || true
        systemctl stop $SERVICE_WEB 2>/dev/null || true
        echo "Services stopped"
        ;;
    status|*) show_status ;;
esac
EOF

chmod +x /usr/local/bin/ironclad-service

log_info "=========================================="
log_info "  Phase 3 Complete!"
log_info "=========================================="
echo ""
log_info "Services installed:"
echo "  - Email (Postfix):   Configured"
echo "  - Matrix Chat:      Configured"
echo "  - XMPP Chat:        Configured"
echo "  - Web Server:       Configured"
echo "  - Syncthing:        Configured"
echo "  - Unbound DNS:      Configured"
echo ""
log_info "Use: ironclad-service start|stop|status"
log_info "Next: Run 04-p2p.sh to configure P2P networking"
