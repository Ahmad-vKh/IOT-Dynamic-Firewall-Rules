#!/bin/bash

fix_suricata_yaml() {
    echo "[*] Checking Suricata configuration file..."

    if ! suricata -T -c /etc/suricata/suricata.yaml > /dev/null 2>&1; then
        echo "[!] Suricata config is broken! Replacing with default safe config..."

        sudo mv /etc/suricata/suricata.yaml /etc/suricata/suricata.yaml.bak

        # Now correctly add the YAML header first
        sudo bash -c 'cat > /etc/suricata/suricata.yaml' <<EOF
%YAML 1.1
---

vars:
  address-groups:
    HOME_NET: "[192.168.0.0/16]"
    EXTERNAL_NET: "!HOME_NET"

default-rule-path: /etc/suricata/rules

rule-files:
  - suricata.rules

outputs:
  - console:
      enabled: yes
      type: fast

EOF

        echo "[+] New suricata.yaml created successfully."
    else
        echo "[+] Suricata configuration is OK."
    fi
}

fix_suricata_yaml
sudo suricata-update

