#!/bin/bash

PROFILE=$1
WHITELIST_IP="192.168.30.114"
CONTROL_PORT=9999
SSH_PORT=22

LOG_FILE="$(dirname "$0")/firewall_profiles.csv"

# Flush and reinitialize nftables
nft flush ruleset
nft add table inet firewall
nft add chain inet firewall input { type filter hook input priority 0 \; policy drop \; }
nft add chain inet firewall forward { type filter hook forward priority 0 \; policy drop \; }
nft add chain inet firewall output { type filter hook output priority 0 \; policy drop \; }

# Create log header
if [ ! -f "$LOG_FILE" ]; then
    echo "date,time,profile" > "$LOG_FILE"
fi

# Base rules (used in all profiles)
apply_common_rules() {
    nft add rule inet firewall input iif lo accept
    nft add rule inet firewall output oif lo accept

    # Allow outgoing traffic to RP5 and incoming response
    nft add rule inet firewall output ip daddr $WHITELIST_IP tcp dport $CONTROL_PORT ct state new,established accept
    nft add rule inet firewall input ip saddr $WHITELIST_IP tcp sport $CONTROL_PORT ct state established accept
}

apply_idle_profile() {
    echo "[*] Applying Idle Profile..."
    echo "$(date '+%Y-%m-%d'),$(date '+%H:%M:%S'),idle" >> "$LOG_FILE"
    apply_common_rules

    # Block ICMP (optional)
    nft add rule inet firewall input ip protocol icmp drop
}

apply_low_activity_profile() {
    echo "[*] Applying Low Activity Profile..."
    echo "$(date '+%Y-%m-%d'),$(date '+%H:%M:%S'),low" >> "$LOG_FILE"
    apply_common_rules
}

apply_high_activity_profile() {
    echo "[*] Applying High Activity Profile..."
    echo "$(date '+%Y-%m-%d'),$(date '+%H:%M:%S'),high" >> "$LOG_FILE"
    apply_common_rules

    # Enable connection tracking
    nft add rule inet firewall input ct state established,related accept
    nft add rule inet firewall output ct state established,related accept

    # SSH to RP5 allowed
    nft add rule inet firewall output ip daddr $WHITELIST_IP tcp dport $SSH_PORT ct state new,established accept
    nft add rule inet firewall input ip saddr $WHITELIST_IP tcp sport $SSH_PORT ct state established accept
}

apply_critical_profile() {
    echo "[*] Applying Critical Task Profile..."
    echo "$(date '+%Y-%m-%d'),$(date '+%H:%M:%S'),critical" >> "$LOG_FILE"
    apply_high_activity_profile

    # Restrict to only the RP5 IP
    nft add rule inet firewall input ip saddr != $WHITELIST_IP drop
    nft add rule inet firewall output ip daddr != $WHITELIST_IP drop

    systemctl restart suricata
}

case "$PROFILE" in
    idle)
        apply_idle_profile
        ;;
    low)
        apply_low_activity_profile
        ;;
    high)
        apply_high_activity_profile
        ;;
    critical)
        apply_critical_profile
        ;;
    *)
        echo "Usage: $0 {idle|low|high|critical}"
        exit 1
        ;;
esac

echo "[*] Firewall profile '$PROFILE' applied successfully."
