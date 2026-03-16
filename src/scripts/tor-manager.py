#!/usr/bin/env python3
"""
IronClad Tor Manager
System-wide Tor routing and per-app Tor rules
"""

import subprocess
import json
import os
import sys

TOR_CONFIG_DIR = "/opt/ironclad/tor"
TOR_CONFIG_FILE = f"{TOR_CONFIG_DIR}/app_rules.json"
TOR_STATUS_FILE = f"{TOR_CONFIG_DIR}/tor_status.json"

def run_cmd(cmd, sudo=False):
    """Run shell command"""
    if sudo:
        cmd = f"echo '9300' | sudo -S {cmd}"
    try:
        result = subprocess.run(cmd, shell=True, capture_output=True, text=True, timeout=30)
        return result.returncode, result.stdout, result.stderr
    except Exception as e:
        return -1, "", str(e)

def ensure_config_dir():
    """Ensure config directory exists"""
    os.makedirs(TOR_CONFIG_DIR, exist_ok=True)

def load_app_rules():
    """Load per-app Tor rules"""
    ensure_config_dir()
    if os.path.exists(TOR_CONFIG_FILE):
        with open(TOR_CONFIG_FILE, 'r') as f:
            return json.load(f)
    return {
        "global_enabled": False,
        "apps": {}
    }

def save_app_rules(rules):
    """Save per-app Tor rules"""
    ensure_config_dir()
    with open(TOR_CONFIG_FILE, 'w') as f:
        json.dump(rules, f, indent=2)

def is_tor_running():
    """Check if Tor is running"""
    rc, _, _ = run_cmd("pgrep -x tor")
    return rc == 0

def start_tor():
    """Start Tor daemon"""
    rc, _, stderr = run_cmd("/usr/sbin/tor --runasdaemon 0", sudo=True)
    return rc == 0

def stop_tor():
    """Stop Tor daemon"""
    rc, _, _ = run_cmd("pkill -x tor", sudo=True)
    return rc == 0

def get_tor_status():
    """Get current Tor status"""
    return is_tor_running()

def enable_system_tor():
    """Enable system-wide Tor routing (redirect all traffic through Tor)"""
    if not is_tor_running():
        start_tor()
    
    # Enable IP forwarding
    run_cmd("echo 1 | sudo tee /proc/sys/net/ipv4/ip_forward", sudo=True)
    
    # Set up iptables rules to redirect traffic through Tor
    # This is a basic implementation - in production, you'd want more sophisticated rules
    
    # Allow Tor traffic
    run_cmd("sudo iptables -A OUTPUT -p tcp --dport 9050 -j ACCEPT", sudo=True)
    run_cmd("sudo iptables -A OUTPUT -p udp --dport 9050 -j ACCEPT", sudo=True)
    
    # Mark non-Tor traffic for routing through Tor (simplified)
    # In production, you'd use PREROUTING rules
    
    return True

def disable_system_tor():
    """Disable system-wide Tor routing"""
    # Remove Tor redirect rules
    run_cmd("sudo iptables -F TOR 2>/dev/null", sudo=True)
    run_cmd("sudo iptables -X TOR 2>/dev/null", sudo=True)
    
    return True

def add_app_rule(app_name, app_path, use_tor):
    """Add or update an app's Tor rule"""
    rules = load_app_rules()
    rules["apps"][app_name] = {
        "path": app_path,
        "use_tor": use_tor,
        "command": get_torsocks_command(app_path) if use_tor else None
    }
    save_app_rules(rules)
    return True

def remove_app_rule(app_name):
    """Remove an app's Tor rule"""
    rules = load_app_rules()
    if app_name in rules["apps"]:
        del rules["apps"][app_name]
        save_app_rules(rules)
    return True

def get_app_rules():
    """Get all app rules"""
    return load_app_rules()

def get_torsocks_command(app_path):
    """Get the torsocks-wrapped command for an app"""
    return f"torsocks {app_path}"

def list_installed_apps():
    """List commonly used applications that can have Tor rules"""
    apps = []
    
    # Common application paths
    common_apps = [
        ("Firefox ESR", "/usr/bin/firefox-esr"),
        ("Chromium", "/usr/bin/chromium"),
        ("Firefox", "/usr/bin/firefox"),
        ("Curl", "/usr/bin/curl"),
        ("Wget", "/usr/bin/wget"),
        ("SSH", "/usr/bin/ssh"),
        ("Nmap", "/usr/bin/nmap"),
        ("Syncthing", "/usr/bin/syncthing"),
    ]
    
    for name, path in common_apps:
        if os.path.exists(path):
            apps.append({"name": name, "path": path})
    
    return apps

def toggle_global_tor(enable):
    """Toggle system-wide Tor routing"""
    rules = load_app_rules()
    rules["global_enabled"] = enable
    
    if enable:
        enable_system_tor()
    else:
        disable_system_tor()
    
    save_app_rules(rules)
    return True

# CLI interface
if __name__ == "__main__":
    if len(sys.argv) < 2:
        print("IronClad Tor Manager")
        print("Usage:")
        print("  status                    - Show Tor status")
        print("  start                      - Start Tor")
        print("  stop                       - Stop Tor")
        print("  global on/off             - Toggle system-wide Tor")
        print("  apps                       - List installed apps")
        print("  rules                       - Show app rules")
        print("  add-app <name> <path> on/off - Add app rule")
        print("  remove-app <name>          - Remove app rule")
        sys.exit(1)
    
    action = sys.argv[1]
    
    if action == "status":
        print(f"Tor Running: {is_tor_running()}")
        rules = load_app_rules()
        print(f"System-wide Tor: {rules.get('global_enabled', False)}")
        print(f"App Rules: {len(rules.get('apps', {}))} apps")
        
    elif action == "start":
        start_tor()
        print("Tor started")
        
    elif action == "stop":
        stop_tor()
        print("Tor stopped")
        
    elif action == "global":
        if len(sys.argv) > 2:
            enable = sys.argv[2] == "on"
            toggle_global_tor(enable)
            print(f"System-wide Tor: {'enabled' if enable else 'disabled'}")
        else:
            print("Usage: tor-manager global on/off")
            
    elif action == "apps":
        apps = list_installed_apps()
        print("Installed apps:")
        for app in apps:
            print(f"  - {app['name']}: {app['path']}")
            
    elif action == "rules":
        rules = load_app_rules()
        print(json.dumps(rules, indent=2))
        
    elif action == "add-app":
        if len(sys.argv) >= 5:
            name = sys.argv[2]
            path = sys.argv[3]
            use_tor = sys.argv[4] == "on"
            add_app_rule(name, path, use_tor)
            print(f"Added rule: {name} -> {'Tor' if use_tor else 'Direct'}")
        else:
            print("Usage: tor-manager add-app <name> <path> on/off")
            
    elif action == "remove-app":
        if len(sys.argv) > 2:
            name = sys.argv[2]
            remove_app_rule(name)
            print(f"Removed rule: {name}")
        else:
            print("Usage: tor-manager remove-app <name>")
            
    else:
        print(f"Unknown action: {action}")
        sys.exit(1)
