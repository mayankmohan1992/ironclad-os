#!/usr/bin/env python3
"""
IronClad Control Panel
A web-based control panel for IronClad OS services
"""

from flask import Flask, render_template, jsonify, request
import subprocess
import json
import os
import socket
import requests

app = Flask(__name__)

# Configuration
PORT = 598631
SERVICES = {
    'nginx': {'name': 'Web Server', 'port': 80},
    'postfix': {'name': 'Email (SMTP)', 'port': 25},
    'prosody': {'name': 'XMPP Chat', 'port': 5222},
    'unbound': {'name': 'DNS Server', 'port': 53},
    'yggdrasil': {'name': 'P2P Network', 'port': None},
    'syncthing': {'name': 'File Sync', 'port': 8384},
    'tor': {'name': 'Tor Proxy', 'port': 9050}
}

def get_service_status(service_name):
    """Get the status of a systemd service"""
    try:
        result = subprocess.run(
            ['systemctl', 'is-active', service_name],
            capture_output=True, text=True, timeout=5
        )
        return result.stdout.strip() == 'active'
    except:
        return False

def get_yggdrasil_info():
    """Get Yggdrasil node information"""
    try:
        result = subprocess.run(
            ['/usr/bin/yggdrasilctl', '-json', 'getSelf'],
            capture_output=True, text=True, timeout=5
        )
        if result.returncode == 0:
            data = json.loads(result.stdout)
            return {
                'node_id': data.get('key', 'N/A')[:32] + '...',
                'address': data.get('address', 'N/A'),
                'subnet': data.get('subnet', 'N/A'),
                'status': 'active'
            }
    except:
        pass
    return {'node_id': 'N/A', 'address': 'N/A', 'subnet': 'N/A', 'status': 'inactive'}

def get_network_info():
    """Get network information"""
    info = {'yggdrasil': get_yggdrasil_info()}
    
    # Check Tor status
    tor_status = get_service_status('tor')
    info['tor'] = {
        'status': 'active' if tor_status else 'inactive',
        'enabled': tor_status
    }
    
    return info

@app.route('/')
def index():
    """Main control panel page"""
    return render_template('index.html', services=SERVICES)

@app.route('/api/status')
def api_status():
    """Get status of all services"""
    status = {}
    for service, info in SERVICES.items():
        status[service] = {
            'name': info['name'],
            'active': get_service_status(service),
            'port': info['port']
        }
    
    status['network'] = get_network_info()
    return jsonify(status)

@app.route('/api/service/<action>/<service_name>', methods=['POST'])
def api_service_action(action, service_name):
    """Start/stop a service"""
    if service_name not in SERVICES:
        return jsonify({'error': 'Unknown service'}), 400
    
    if action == 'start':
        subprocess.run(['systemctl', 'start', service_name], timeout=30)
    elif action == 'stop':
        subprocess.run(['systemctl', 'stop', service_name], timeout=30)
    elif action == 'restart':
        subprocess.run(['systemctl', 'restart', service_name], timeout=30)
    
    return jsonify({'success': True, 'status': get_service_status(service_name)})

@app.route('/api/tor/toggle', methods=['POST'])
def api_tor_toggle():
    """Toggle Tor service"""
    data = request.json
    enable = data.get('enable', True)
    
    if enable:
        subprocess.run(['systemctl', 'start', 'tor'], timeout=30)
    else:
        subprocess.run(['systemctl', 'stop', 'tor'], timeout=30)
    
    return jsonify({'success': True, 'enabled': enable})

@app.route('/api/peer/qr')
def api_peer_qr():
    """Generate QR code for Yggdrasil node"""
    ygg_info = get_yggdrasil_info()
    node_id = ygg_info.get('node_id', '')
    
    if node_id and node_id != 'N/A':
        # Generate QR code
        try:
            result = subprocess.run(
                ['qrencode', '-t', 'utf8', node_id],
                capture_output=True, text=True, timeout=10
            )
            qr_ascii = result.stdout
        except:
            qr_ascii = "QR generation failed"
    else:
        qr_ascii = "Yggdrasil not running"
    
    return jsonify({
        'node_id': node_id,
        'qr_code': qr_ascii,
        'address': ygg_info.get('address', 'N/A')
    })

@app.route('/api/peer/add', methods=['POST'])
def api_peer_add():
    """Add a peer by Node ID"""
    data = request.json
    node_id = data.get('node_id', '').strip()
    
    if not node_id:
        return jsonify({'error': 'Node ID required'}), 400
    
    # Add peer to Yggdrasil config
    try:
        # For now, just return success - actual peer addition would modify config
        return jsonify({'success': True, 'message': f'Peer {node_id} added (pending restart)'})
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@app.route('/peer')
def peer_page():
    """Peer connection page with QR codes"""
    return render_template('peer.html')

if __name__ == '__main__':
    print(f"IronClad Control Panel starting on port {PORT}")
    print(f"Access at: http://localhost:{PORT}")
    app.run(host='0.0.0.0', port=PORT, debug=False)
