#!/bin/bash
# preflight_check_central_security.sh
# Purpose: Verify all dependencies, services, and configurations for central_security.sh
# Usage: ./preflight_check_central_security.sh
# Note: Run as a regular user; sudo is used where needed

# Log file for preflight check
LOG_FILE="/var/log/preflight_check_central_security.log"

# Helper function to log messages
log_message() {
    echo "$(date '+%Y-%m-%d %H:%M:%S') - $1" | tee -a "$LOG_FILE"
}

# Helper function to check for errors
check_error() {
    if [ $? -ne 0 ]; then
        log_message "Error: $1"
        echo "Fix: $2"
        exit 1
    fi
}

# Initialize log file
touch "$LOG_FILE" 2>/dev/null || {
    echo "Error: Cannot create log file $LOG_FILE"
    exit 1
}
chmod 644 "$LOG_FILE"
log_message "Starting preflight check for central_security.sh..."

# Step 1: Check required commands
log_message "Checking required commands..."
for cmd in nft suricata suricata-update systemctl crontab tee chmod touch bash; do
    if command -v "$cmd" &> /dev/null; then
        log_message "$cmd: OK"
    else
        log_message "$cmd: MISSING"
        echo "Fix: Install $cmd (e.g., 'sudo apt install nftables suricata systemd cron coreutils')"
        exit 1
    fi
done

# Step 2: Check nftables and suricata services
log_message "Checking services..."
for svc in nftables suricata; do
    if systemctl status "$svc" &> /dev/null; then
        log_message "$svc service: OK"
    else
        log_message "$svc service: NOT FOUND"
        echo "Fix: Ensure $svc is installed (e.g., 'sudo apt install $svc') and service file exists"
        exit 1
    fi
done

# Step 3: Check network interface (wlan0)
log_message "Checking network interface..."
NETWORK_IFACE="wlan0"
EXPECTED_IP="192.168.30.110"
if ip link | grep -q "$NETWORK_IFACE"; then
    log_message "Interface $NETWORK_IFACE: OK"
    # Check if wlan0 has the expected IP
    if ip addr show "$NETWORK_IFACE" | grep -q "$EXPECTED_IP"; then
        log_message "IP $EXPECTED_IP on $NETWORK_IFACE: OK"
    else
        log_message "IP $EXPECTED_IP on $NETWORK_IFACE: NOT FOUND"
        echo "Fix: Configure $NETWORK_IFACE with IP $EXPECTED_IP (e.g., 'sudo ip addr add $EXPECTED_IP/24 dev $NETWORK_IFACE')"
        exit 1
    fi
else
    log_message "Interface $NETWORK_IFACE: NOT FOUND"
    echo "Fix: Verify Wi-Fi adapter is connected and interface name is correct (use 'ip link' to list interfaces)"
    exit 1
fi

# Step 4: Check log directories and permissions
log_message "Checking log directories and permissions..."
for path in /var/log/suricata /var/log/central_security.log; do
    if [ -e "$path" ]; then
        log_message "$path: OK"
        # Check permissions
        if [ "$path" = "/var/log/suricata" ]; then
            perms=$(stat -c %a "$path")
            if [ "$perms" = "755" ]; then
                log_message "$path permissions (755): OK"
            else
                log_message "$path permissions ($perms): INCORRECT"
                echo "Fix: Set correct permissions (sudo chmod 755 /var/log/suricata)"
                exit 1
            fi
        else
            perms=$(stat -c %a "$path")
            if [ "$perms" = "644" ]; then
                log_message "$path permissions (644): OK"
            else
                log_message "$path permissions ($perms): INCORRECT"
                echo "Fix: Set correct permissions (sudo chmod 644 /var/log/central_security.log)"
                exit 1
            fi
        fi
    else
        log_message "$path: MISSING"
        echo "Fix: Create $path (e.g., 'sudo mkdir -p /var/log/suricata; sudo touch /var/log/central_security.log; sudo chmod 755 /var/log/suricata; sudo chmod 644 /var/log/central_security.log')"
        exit 1
    fi
done

# Step 5: Check sudo privileges
log_message "Checking sudo privileges..."
if sudo -l &> /dev/null; then
    log_message "Sudo: OK"
else
    log_message "Sudo: NO ACCESS"
    echo "Fix: Ensure user has sudo privileges (e.g., 'sudo usermod -aG sudo $USER')"
    exit 1
fi

# Step 6: Check cron functionality
log_message "Checking cron functionality..."
if crontab -l &> /dev/null; then
    log_message "Cron: OK"
else
    log_message "Cron: NOT FUNCTIONAL"
    echo "Fix: Ensure cron is installed and running (e.g., 'sudo apt install cron; sudo systemctl enable cron')"
    exit 1
fi

# Step 7: Check Suricata rules
log_message "Checking Suricata rules..."
if [ -f /var/lib/suricata/rules/suricata.rules ]; then
    log_message "Suricata rules (/var/lib/suricata/rules/suricata.rules): OK"
else
    log_message "Suricata rules: MISSING"
    echo "Fix: Run 'sudo suricata-update' to download rules"
    exit 1
fi

# Step 8: Check nftables configuration file
log_message "Checking nftables configuration file..."
if [ -f /etc/nftables.conf ]; then
    log_message "/etc/nftables.conf: OK"
else
    log_message "/etc/nftables.conf: MISSING"
    echo "Fix: Create an empty /etc/nftables.conf (e.g., 'sudo touch /etc/nftables.conf')"
    exit 1
fi

# Step 9: Final verification
log_message "All checks passed! central_security.sh is ready to run."
echo "Preflight check completed successfully. Logs at $LOG_FILE"
echo "You can now run: sudo ./central_security.sh"
