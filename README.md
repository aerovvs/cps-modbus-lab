# CPS Modbus Security Lab

![Status](https://img.shields.io/badge/status-active-brightgreen?style=flat-square) ![License](https://img.shields.io/badge/license-MIT-yellow?style=flat-square) [![Modbus Attacks](https://img.shields.io/badge/Modbus-Attacks-red)](docs/AttackMethodology.md)
[![ICS IDS](https://img.shields.io/badge/ICS-IDS-blue)](docs/DetectionStrategy.md)

> **Hardware in the loop testbed for learning, demonstrating, and defending against real world Modbus/TCP attacks on industrial control systems**

---

## Table of Contents

1. [Purpose](#purpose)
2. [System Architecture](#systemarchitecture)
3. [Key Features](#keyfeatures)
4. [Quick Start](#quickstart)
5. [Repository Layout](#repositorylayout)
6. [Attack Scenarios](#attackscenarios)
7. [Detection Strategy](#detectionstrategy)
8. [Hardware Wiring](#hardwarewiring)
9. [MITRE ATT\&CK Mapping](#mitreattckmapping)
10. [Contributing](#contributing)
11. [Disclaimer](#disclaimer)
12. [License](#license)

---

## Purpose

This project provides an end‑to‑end **Cyber‑Physical System (CPS)** lab that demonstrates:

* **Offensive techniques** — replay, command manipulation, timed logic bombs, and covert Morse signaling against a live Modbus process.
* **Defensive counter‑measures** — Suricata 7 IDS with custom, rate‑limited rules that reliably flag each attack class with ≤10 s mean detection latency.

Everything runs on inexpensive hardware (Raspberry Pi + LED) so you can reproduce the full kill chain at home without PLCs or SCADA gear.

---

## System Architecture

                      +------------------------------+
                      | Attacker – MacBook Air       |
                      | (Wi‑Fi)                      |
                      | Scapy attack scripts         |
                      +--------------+---------------+
                                     |  Wi‑Fi
                      +--------------v---------------+
                      |    Home / Lab Router / AP    |
                      +--------------+---------------+
                                     |  Ethernet
                      +--------------v---------------+
                      | Raspberry Pi 4 (Target & IDS)|
                      | (Ethernet)                   |
                      | modbus_server.py             |
                      | Suricata 7 IDS               |
                      | LED on GPIO17                |
                      +--------------+---------------+
                                     |
                                     v
                                   [ LED ]

| Role     | Host                 | Key Software                        |
| -------- | -------------------- | ----------------------------------- |
| Target   | Raspberry Pi 4 (ETH) | `server/modbus_server.py` (sockets) |
| Attacker | macOS laptop (Wi‑Fi) | `attack/*.py` (Scapy)               |
| IDS      | Raspberry Pi 4       | Suricata 7 + custom rules           |

---

## Key Features

* **Pure‑socket Modbus server** for transparent packet introspection.
* **Four purpose‑built attack scripts** showcasing different TTPs.
* **Custom Suricata rules** with `detection_filter` to catch replay, DoS bursts, manipulation blinks, and covert channels.
* **Automated validation harness** (`defense/scripts/test_all_attacks.sh`) to reproduce attacks + measure alert latency.

---

## Quick Start

```bash
# 1 Clone repo on both Pi and attacker
$ git clone https://github.com/aerovvs/cps-modbus-lab.git

# 2 On the Pi: start Modbus server and Suricata IDS
$ cd cps-modbus-lab/server && sudo python3 modbus_server.py &
$ cd ../defense/scripts && sudo ./start_ids.sh

# 3 On the attacker: launch an attack of your choice
$ cd cps-modbus-lab/attack && sudo python3 <attack>.py -i en0 -t <ip>
```

Logs land in `defense/logs/` and are parsed by `analyze_complete.py`.

---

## Repository Layout

```text
cps-modbus-lab/
├── server/            # pure socket Modbus daemon (target)
├── attack/            # Scapy attack scripts (attacker)
├── defense/
│   ├── rules/         # Suricata rule set
│   ├── scripts/       # IDS helpers + test harness
│   └── logs/          # EVE‑JSON alerts
├── docs/              # write‑ups
├── README.md          # this file
```

---

## Attack Scenarios

| Script                     | MITRE ID | Effect on LED | Detection Rule |
| -------------------------- | -------- | ------------- | -------------- |
| `continuous_attack.py`     | T0855    | Holds LED ON  | `SID 100001`   |
| `blinking_attack.py`       | T0836    | Rapid blink   | `SID 100002`   |
| `timed_attack.py`          | T0858    | Delayed burst | `SID 100003`   |
| `secret_message_attack.py` | T0820    | Morse code    | `SID 100004`   |

---

## Detection Strategy

Suricata runs in **AF‑Packet** mode with a dedicated rule file `defense/rules/modbus-attacks.rules`.
Each rule leverages `detection_filter` for rate‑based anomaly detection - see detailed breakdown in **docs/05\_Detection\_Strategy.md**.

---

## Hardware Wiring

Your Pi‑controlled LED stands in for a real process actuator (valve, pump, relay).

| Qty | Component                   | Notes                              |
| --- | --------------------------- | ---------------------------------- |
|  1  | Red Led                     | Acts as ICS field device indicator |
|  1  | 220 Ω resistor              | Limits current                     |
|  1  | Breadboard                  | A half board is fine               |
|  1  | Male-to-male jumper wires   | Acts as a bridge                   |
|  2  | Male-to-female jumper wires | Connection to GPIO pins            |

---

## MITRE ATT\&CK Mapping

| Attack Technique         | ID    |
| ------------------------ | ----- |
| Unauthorized Command     | T0855 |
| Change Operating Mode    | T0858 |
| Modify Parameter         | T0836 |
| Exploitation for Evasion | T0820 |

Full mapping in **MITRE\_ATTACK\_MAPPING.md**.

---

## Contributing

Pull requests are welcome, especially additional attack modules, Suricata rule optimisations, or documentation improvements. Open an issue first to discuss major changes.

---

## Disclaimer

Ctrl + C on attack and server scripts not working. Workaround is Ctrl + Z and then kill process. 

---

## License

Distributed under the **MIT License**. See `LICENSE` for details.
