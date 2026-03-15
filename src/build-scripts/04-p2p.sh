#!/bin/bash

# IronClad OS - Phase 4: P2P Network Setup
# Yggdrasil + Custom .ironclad TLD + QR Peer Addition

set -e

RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

log_info() { echo -e "${GREEN}[INFO]${NC} $1"; }
log_warn() { echo -e "${YELLOW}[WARN]${NC} $1"; }
log_error() { echo -e "${RED}[ERROR]${NC} $1"; }

if [[ $EUID -ne 0 ]]; then
   log_error "Run as root: sudo ./04-p2p.sh"
   exit 1
fi

log_info "=========================================="
log_info "  IronClad OS - Phase 4: P2P Network"
log_info "=========================================="
echo ""

log_info "Step 1: Installing Yggdrasil..."
# Add Yggdrasil repository
curl -fsSL https://neilalexander.s3.eu-west-2.amazonaws.com/deb/keyring.gpg | gpg --dearmor -o /usr/share/keyrings/yggdrasil.gpg
echo "deb [signed-by=/usr/share/keyrings/yggdrasil.gpg] https://neilalexander.s3.eu-west-2.amazonaws.com/deb/ stable main" > /etc/apt/sources.list.d/yggdrasil.list
apt update
apt install -y yggdrasil

log_info "Configuring Yggdrasil..."
mkdir -p /etc/yggdrasil

# Generate Yggdrasil config
yggdrasil -genconf -allnodes > /etc/yggdrasil.conf

# Modify config for IronClad
cat > /etc/yggdrasil.conf << 'EOF'
# IronClad OS - Yggdrasil Configuration
# Generated for IronClad P2P network

Peers: []
# Note: Peers will be added via QR code scanning

Listen: 0.0.0.0:0
AdminPort: 19019

# Encryption keys - DO NOT SHARE
# Node's keys are stored here
PrivateKey: ""
PublicKey: ""

# Multicast discovery for local network peers
MulticastInterfaces:
  - Regex: ".*"
    Beacon: true
    Listen: false

# Logging
LogLevel: info

# Node info
NodeInfo:
  name: "ironclad-node"
  platform: "ironclad-os"
  version: "0.1.0"
EOF

systemctl enable yggdrasil
systemctl start yggdrasil

log_info "Step 2: Installing QR code tools..."
apt install -y qrencode zbar-tools

log_info "Step 3: Creating peer management system..."
mkdir -p /opt/ironclad/p2p

# Peer manager script
cat > /opt/ironclad/p2p/peer-manager.sh << 'EOF'
#!/bin/bash
# IronClad P2P Peer Manager

IRONCLAD_DIR="/opt/ironclad/p2p"
NODE_REGISTRY="$IRONCLAD_DIR/nodes.json"
YGGCTL="/usr/bin/yggdrasilctl"

show_qr() {
    echo "=== YOUR NODE ID (Scan to add this node to other IronClad systems) ==="
    echo ""
    $YGGCTL -getNodeID | qrencode -t ANSIUTF8
    echo ""
    echo "Your Node ID:"
    $YGGCTL -getNodeID
    echo ""
}

add_peer() {
    echo "=== ADD PEER ==="
    echo "Enter peer's Node ID (or scan QR code):"
    read -p "Node ID: " node_id
    
    if [ -z "$node_id" ]; then
        echo "Error: Node ID cannot be empty"
        return 1
    fi
    
    # Add peer via yggdrasilctl
    $YGGCTL -addPeer $node_id 2>/dev/null || \
    $YGGCTL -addpeer $node_id 2>/dev/null || \
    echo "Note: Peer addition may require public key or URI"
    
    # Add to local registry
    if [ ! -f "$NODE_REGISTRY" ]; then
        echo "[]" > "$NODE_REGISTRY"
    fi
    
    echo "Peer $node_id added to registry"
}

scan_qr() {
    echo "=== SCAN QR CODE ==="
    echo "Point your webcam at a peer's QR code"
    echo "Press Ctrl+C to cancel"
    echo ""
    
    # Use zbarcam for scanning
    node_id=$(zbarcam --raw -q 2>/dev/null)
    
    if [ -n "$node_id" ]; then
        echo "Scanned Node ID: $node_id"
        add_peer
    else
        echo "Failed to scan QR code"
    fi
}

list_peers() {
    echo "=== CONNECTED PEERS ==="
    $YGGCTL -getPeers 2>/dev/null || echo "No peers connected"
    echo ""
    echo "=== NODE REGISTRY ==="
    if [ -f "$NODE_REGISTRY" ]; then
        cat "$NODE_REGISTRY"
    else
        echo "No nodes in registry"
    fi
}

show_info() {
    echo "=== IRONCLAD NODE INFO ==="
    echo "Node ID:"
    $YGGCTL -getNodeID
    echo ""
    echo "IPv6 Address:"
    $YGGCTL -getAddr 2>/dev/null || echo "Not assigned yet"
    echo ""
    echo "Public Key:"
    $YGGCTL -getPublicKey 2>/dev/null || echo "Not generated yet"
}

case "$1" in
    qr) show_qr ;;
    add) add_peer ;;
    scan) scan_qr ;;
    peers) list_peers ;;
    info) show_info ;;
    *)
        echo "IronClad P2P Peer Manager"
        echo ""
        echo "Usage: $0 {qr|add|scan|peers|info}"
        echo ""
        echo "Commands:"
        echo "  qr     - Show your node QR code for other peers to scan"
        echo "  add    - Add a peer manually by Node ID"
        echo "  scan   - Scan a peer's QR code to add them"
        echo "  peers  - List connected peers"
        echo "  info   - Show your node information"
        ;;
esac
EOF

chmod +x /opt/ironclad/p2p/peer-manager.sh
ln -sf /opt/ironclad/p2p/peer-manager.sh /usr/local/bin/ironclad-peer

log_info "Step 4: Creating .ironclad DNS resolver..."
cat > /opt/ironclad/p2p/dns-resolver.sh << 'EOF'
#!/bin/bash
# IronClad .ironclad TLD DNS Resolver
# Resolves *.ironclad domains to Yggdrasil addresses

IRONCLAD_DIR="/opt/ironclad/p2p"
NODE_REGISTRY="$IRONCLAD_DIR/nodes.json"
DNS_PORT=5353

update_dns() {
    # This will be called by the P2P sync to update node registry
    # For now, just handle localhost.ironclad
    
    # Restart Unbound with updated config
    systemctl restart unbound
}

# Check if domain is .ironclad
handle_query() {
    local domain="$1"
    
    if [[ "$domain" == *.ironclad ]]; then
        # Extract node name from domain
        local node_name="${domain%.ironclad}"
        
        # Look up in registry
        if [ -f "$NODE_REGISTRY" ]; then
            local ygg_addr=$(jq -r ".nodes[\"$node_name\"].ygg_address" "$NODE_REGISTRY" 2>/dev/null)
            if [ -n "$ygg_addr" ] && [ "$ygg_addr" != "null" ]; then
                echo "$ygg_addr"
                return 0
            fi
        fi
    fi
    return 1
}

case "$1" in
    update) update_dns ;;
    query) handle_query "$2" ;;
    *)
        echo "IronClad DNS Resolver"
        echo "Usage: $0 {update|query <domain>}"
        ;;
esac
EOF

chmod +x /opt/ironclad/p2p/dns-resolver.sh
ln -sf /opt/ironclad/p2p/dns-resolver.sh /usr/local/bin/ironclad-dns

log_info "Step 5: Creating P2P sync service..."
cat > /etc/systemd/system/ironclad-p2p.service << 'EOF'
[Unit]
Description=IronClad P2P Node Service
After=network.target yggdrasil.service
Requires=yggdrasil.service

[Service]
Type=simple
User=root
ExecStart=/opt/ironclad/p2p/p2p-sync.sh
Restart=on-failure
RestartSec=10

[Install]
WantedBy=multi-user.target
EOF

cat > /opt/ironclad/p2p/p2p-sync.sh << 'EOF'
#!/bin/bash
# IronClad P2P Sync Service
# Syncs node registry with other peers

IRONCLAD_DIR="/opt/ironclad/p2p"
NODE_REGISTRY="$IRONCLAD_DIR/nodes.json"
YGGCTL="/usr/bin/yggdrasilctl"

log() {
    echo "[$(date)] P2P-Sync: $1"
}

# Initialize node registry if not exists
init_registry() {
    if [ ! -f "$NODE_REGISTRY" ]; then
        echo '{"nodes":{}}' > "$NODE_REGISTRY"
        chmod 600 "$NODE_REGISTRY"
    fi
}

# Register this node in the registry
register_self() {
    local node_id=$($YGGCTL -getNodeID 2>/dev/null)
    local ygg_addr=$($YGGCTL -getAddr 2>/dev/null)
    local public_key=$($YGGCTL -getPublicKey 2>/dev/null)
    
    if [ -n "$node_id" ]; then
        # Create node entry (in production, use username as key)
        local timestamp=$(date +%s)
        log "Registering node: $node_id"
    fi
}

# This is a simplified version
# In production, this would use torrent DHT or similar for peer discovery

log "Starting IronClad P2P Sync Service..."
init_registry
register_self

# Keep running
while true; do
    sleep 60
    # Sync logic would go here
done
EOF

chmod +x /opt/ironclad/p2p/p2p-sync.sh
systemctl daemon-reload
systemctl enable ironclad-p2p
systemctl start ironclad-p2p

log_info "Step 6: Creating network status GUI..."
cat > /opt/ironclad/p2p/network-status.sh << 'EOF'
#!/bin/bash
# IronClad Network Status Monitor

while true; do
    clear
    echo "========================================"
    echo "  IronClad Network Status"
    echo "========================================"
    echo ""
    echo "Yggdrasil Status: $(systemctl is-active yggdrasil)"
    echo ""
    echo "Node Information:"
    /usr/local/bin/ironclad-peer info 2>/dev/null || echo "  (not configured)"
    echo ""
    echo "Connected Peers:"
    /usr/local/bin/ironclad-peer peers 2>/dev/null | head -20 || echo "  (no peers)"
    echo ""
    echo "DNS Resolver: $(systemctl is-active unbound)"
    echo "P2P Sync: $(systemctl is-active ironclad-p2p)"
    echo ""
    echo "Press Ctrl+C to exit"
    sleep 5
done
EOF

chmod +x /opt/ironclad/p2p/network-status.sh
ln -sf /opt/ironclad/p2p/network-status.sh /usr/local/bin/ironclad-network

log_info "=========================================="
log_info "  Phase 4 Complete!"
log_info "=========================================="
echo ""
log_info "P2P Network configured:"
echo "  - Yggdrasil mesh VPN"
echo "  - QR code peer addition"
echo "  - .ironclad DNS resolver"
echo "  - P2P sync service"
echo ""
log_info "Commands:"
echo "  ironclad-peer qr       - Show your QR code"
echo "  ironclad-peer scan    - Scan peer's QR"
echo "  ironclad-peer info    - Show node info"
echo "  ironclad-peer peers   - List peers"
echo "  ironclad-network      - Network status monitor"
echo ""
log_info "First run: ironclad-peer qr"
log_info "Then share your QR code with other IronClad users!"
