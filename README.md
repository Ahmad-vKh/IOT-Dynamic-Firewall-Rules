# 🔥 Adaptive Firewall Profile Selection for IoT Systems

A senior design project for Princess Sumaya University for Technology that implements a **centralized, adaptive firewall management system** for securing IoT networks using lightweight edge devices such as Raspberry Pi.

## 📌 Overview

IoT environments are highly heterogeneous, comprising devices with limited CPU, memory, and power. Traditional static firewalls are insufficient. This project introduces a **resource-aware firewall selection scheme** that:

- Monitors real-time metrics (CPU, RAM, traffic)
- Dynamically assigns one of four firewall profiles (Idle, Low, High, Critical)
- Uses `nftables` and `ASCON-128a` encryption for secure, efficient management
- Operates through a centralized controller (RP5)

## 🧠 System Design

The system is composed of:

- **1 Central Node (RP5)** – Coordinates, analyzes, and assigns profiles
- **3+ Edge Nodes (RP4s)** – Simulate IoT devices under variable workloads
- **Smart Plugs (Tapo P110)** – Measure power usage for energy efficiency validation

📊 Metrics collected:
- CPU usage
- RAM usage
- Simulated traffic

🔐 Security:
- ASCON-128a (lightweight encryption)
- HKDF key derivation
- JSON over TCP sockets
- Pre-shared symmetric key for session encryption

## 🛡️ Firewall Profiles

| Profile        | Use Case                             | Features                                                                 |
|----------------|---------------------------------------|--------------------------------------------------------------------------|
| Idle           | Device underutilized (low load)       | Deny-all traffic, minimal exposure                                       |
| Low Activity   | Light workloads, e.g., wearable data  | Stateless filtering, whitelisted IPs                                     |
| High Activity  | Intensive workload, e.g., ventilator  | Stateful inspection, connection tracking, rate limiting                  |
| Critical Task  | Sensitive operations, e.g., imaging   | DPI via Suricata, high-security rules, IDS/IPS                           |

## 🧪 Test Scenarios

| Scenario      | Description                                       | Expected Behavior                           |
|---------------|---------------------------------------------------|---------------------------------------------|
| Idle          | Lightweight tasking                               | Idle profile assigned                        |
| Random Load   | Dynamic CPU/RAM variation                         | Profiles shift according to load             |
| Critical Load | High, sustained CPU/RAM usage                     | Critical Task profile enforced               |

## 🛠️ Tech Stack

- **Hardware**: Raspberry Pi 5 (Central), Raspberry Pi 4 (Edge), TP-Link P110 Smart Plugs
- **Languages**: Python 3, Bash
- **Tools & Libraries**:
  - `nftables` – Firewall rule engine
  - `psutil` – Resource monitoring
  - `pycryptodome` – Cryptography (ASCON)
  - `Suricata` – Intrusion detection for Critical profile
  - `python-kasa` – Smart plug energy logging

