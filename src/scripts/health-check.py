#!/usr/bin/env python3
"""
IronClad Health Check + Auto-Fix Script
Checks all services and attempts to fix common issues
"""

import subprocess
import json
import os
import sys
from datetime import datetime

# Colors for pretty output
class Colors:
    GREEN = '\033[92m'
    YELLOW = '\033[93m'
    RED = '\033[91m'
    BLUE = '\033[94m'
    BOLD = '\033[1m'
    END = '\033[0m'

def print_header(text):
    print(f"\n{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{text}{Colors.END}")
    print(f"{Colors.BOLD}{Colors.BLUE}{'='*60}{Colors.END}\n")

def print_success(text):
    print(f"{Colors.GREEN}✓ {text}{Colors.END}")

def print_warning(text):
    print(f"{Colors.YELLOW}⚠ {text}{Colors.END}")

def print_error(text):
    print(f"{Colors.RED}✗ {text}{Colors.END}")

def print_info(text):
    print(f"{Colors.BLUE}ℹ {text}{Colors.END}")

def run_command(cmd, timeout=30):
    """Run shell command and return output"""
    try:
        result = subprocess.run(
            cmd, shell=True, capture_output=True, 
            text=True, timeout=timeout
        )
        return result.returncode, result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return -1, "", "Command timed out"
    except Exception as e:
        return -1, "", str(e)

def check_service(service_name, display_name):
    """Check if a service is running"""
    print(f"Checking {display_name}...", end=" ")
    rc, stdout, _ = run_command(f"systemctl is-active {service_name}")
    if rc == 0 and stdout.strip() == "active":
        print_success(f"Running")
        return True
    else:
        print_error(f"Not running")
        return False

def check_process(process_name, port=None):
    """Check if a process is running"""
    rc, stdout, _ = run_command(f"pgrep -x '{process_name}'")
    if rc == 0:
        if port:
            rc2, _, _ = run_command(f"ss -tlnp | grep ':{port}'")
            if rc2 == 0:
                return True
        return True
    return False

def check_port(port):
    """Check if a port is listening"""
    rc, stdout, _ = run_command(f"ss -tlnp | grep ':{port}'")
    return rc == 0

def fix_service(service_name, display_name):
    """Attempt to fix a service"""
    print_info(f"Attempting to fix {display_name}...")
    rc, _, stderr = run_command(f"sudo systemctl restart {service_name}")
    if rc == 0:
        print_success(f"Fixed {display_name}")
        return True
    else:
        print_error(f"Could not fix {display_name}: {stderr[:100]}")
        return False

def check_yggdrasil():
    """Check Yggdrasil P2P"""
    print("Checking Yggdrasil P2P...", end=" ")
    if check_process("yggdrasil"):
        # Try to get node info
        rc, stdout, _ = run_command("/usr/bin/yggdrasilctl -json getSelf 2>/dev/null")
        if rc == 0:
            try:
                data = json.loads(stdout)
                node_id = data.get('key', 'N/A')[:16] + "..."
                print_success(f"Running (ID: {node_id})")
                return True
            except:
                pass
    print_error("Not running")
    return False

def check_tor():
    """Check Tor proxy"""
    print("Checking Tor Proxy...", end=" ")
    if check_process("tor") or check_port(9050):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def check_nginx():
    """Check Nginx web server"""
    print("Checking Nginx...", end=" ")
    if check_port(80):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def check_syncthing():
    """Check Syncthing"""
    print("Checking Syncthing...", end=" ")
    if check_process("syncthing") or check_port(8384):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def check_unbound():
    """Check Unbound DNS"""
    print("Checking Unbound DNS...", end=" ")
    if check_process("unbound") or check_port(53):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def check_postfix():
    """Check Postfix email"""
    print("Checking Postfix...", end=" ")
    if check_process("postfix") or check_port(25):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def check_prosody():
    """Check Prosody XMPP"""
    print("Checking XMPP (Prosody)...", end=" ")
    if check_process("prosody") or check_port(5222):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def check_control_panel():
    """Check Control Panel"""
    print("Checking Control Panel...", end=" ")
    if check_port(8807) or check_port(598631):
        print_success("Running")
        return True
    print_error("Not running")
    return False

def get_system_info():
    """Get system information"""
    print_header("System Information")
    
    # Hostname
    rc, stdout, _ = run_command("hostname")
    print_info(f"Hostname: {stdout.strip()}")
    
    # Uptime
    rc, stdout, _ = run_command("uptime -p")
    print_info(f"Uptime: {stdout.strip()}")
    
    # Memory
    rc, stdout, _ = run_command("free -h | grep Mem")
    print_info(f"Memory: {stdout.strip()}")
    
    # Disk
    rc, stdout, _ = run_command("df -h / | tail -1 | awk '{print $3 \" / \" $2}'")
    print_info(f"Disk: {stdout.strip()}")
    
    # Yggdrasil IP
    rc, stdout, _ = run_command("/usr/bin/yggdrasilctl -json getSelf 2>/dev/null | grep -o '\"address\":\"[^\"]*\"' | cut -d'\"' -f4")
    if rc == 0 and stdout.strip():
        print_info(f"Yggdrasil IP: {stdout.strip()}")

def main():
    print(f"\n{Colors.BOLD}{Colors.BLUE}")
    print("╔════════════════════════════════════════════════════════════╗")
    print("║         IronClad OS - Health Check & Auto-Fix            ║")
    print("║                                                            ║")
    print(f"║              {datetime.now().strftime('%Y-%m-%d %H:%M:%S')}{' '*26}║")
    print("╚════════════════════════════════════════════════════════════╝")
    print(Colors.END)
    
    services_status = {}
    
    # System Info
    get_system_info()
    
    # Check all services
    print_header("Service Status")
    
    services = [
        ("yggdrasil", check_yggdrasil),
        ("tor", check_tor),
        ("nginx", check_nginx),
        ("postfix", check_postfix),
        ("prosody", check_prosody),
        ("unbound", check_unbound),
        ("syncthing", check_syncthing),
        ("control-panel", check_control_panel),
    ]
    
    for name, check_func in services:
        services_status[name] = check_func()
    
    # Network Info
    print_header("Network Status")
    
    # Check internet connectivity
    print("Checking Internet Connectivity...", end=" ")
    rc, _, _ = run_command("ping -c 1 -W 2 8.8.8.8 > /dev/null 2>&1")
    if rc == 0:
        print_success("Connected")
    else:
        print_warning("No internet")
    
    # Check Yggdrasil connectivity
    print("Checking Yggdrasil Network...", end=" ")
    rc, stdout, _ = run_command("/usr/bin/yggdrasilctl -json getSelf 2>/dev/null | grep -o '\"address\":\"[^\"]*\"'")
    if rc == 0 and stdout:
        print_success("Connected to P2P network")
    else:
        print_warning("Not connected to P2P network")
    
    # Summary
    print_header("Summary")
    
    total = len(services_status)
    running = sum(services_status.values())
    stopped = total - running
    
    print_info(f"Total Services: {total}")
    print_success(f"Running: {running}")
    
    if stopped > 0:
        print_error(f"Stopped: {stopped}")
        
        print("\n")
        print_warning("Attempting to fix stopped services...")
        
        # Try to fix common issues
        if not services_status.get("nginx"):
            fix_service("nginx", "Nginx")
        
        if not services_status.get("syncthing"):
            print_info("Starting Syncthing manually...")
            run_command("nohup syncthing --no-browser --no-restart > /dev/null 2>&1 &")
        
        if not services_status.get("control-panel"):
            print_info("Restarting Control Panel...")
            run_command("cd /opt/ironclad/control-panel && nohup python3 app.py > /tmp/flask.log 2>&1 &")
        
        # Re-check
        print("\n")
        print_info("Re-checking services...")
        services_status["syncthing"] = check_syncthing()
        services_status["control-panel"] = check_control_panel()
        
        running = sum(services_status.values())
        print_info(f"After fix - Running: {running}/{total}")
    
    else:
        print_success("All services running!")
    
    # Quick Actions
    print_header("Quick Actions")
    
    actions = [
        ("Open Control Panel", "xdg-open http://localhost:8807 2>/dev/null"),
        ("Open Syncthing", "xdg-open http://localhost:8384 2>/dev/null"),
        ("View Yggdrasil QR", "qrencode -t utf8 $(/usr/bin/yggdrasilctl -json getSelf 2>/dev/null | grep -o '\"key\":\"[^\"]*\"' | cut -d'\"' -f4)"),
    ]
    
    for i, (name, cmd) in enumerate(actions, 1):
        print(f"{i}. {name}")
    
    print(f"\n{Colors.BOLD}Health check complete!{Colors.END}\n")

if __name__ == "__main__":
    main()
