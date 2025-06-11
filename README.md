# Raspberry Pi Modbus-TCP CPS Replay-Attack Lab

Hands-on industrial--protocol demo:  
a Raspberry Pi 5 emulates a PLC, drives an LED (GPIO 17) via Modbus-TCP,  
then shows how an attacker can **capture & replay** a single packet to toggle the output—  
and how a defender can detect it.

---

## Table of Contents
1. [Hardware](#hardware)
2. [Quick Start](#quick-start)
3. [Repo Layout](#repo-layout)
4. [Attack Flow](#attack-flow)
5. [MITRE ATT&CK Mapping](#mitre-attck-mapping)
6. [Defensive Ideas](#defensive-ideas)
7. [Demo Video](#demo-video)
8. [References](#references)

---

## Hardware
| Part | Qty | Purpose |
|------|-----|---------|
| Raspberry Pi 5 (4 GB) | 1 | PLC emulator & attack box |
| micro-SD card (16 GB+) | 1 | OS & code |
| Breadboard + jumpers | 1 | LED wiring |
| LED + 220 Ω resistor | 1 | Physical “actuator” |
| Ethernet cable | 1 | Low-latency Modbus traffic |

---

## Quick Start

### ① PLC server (on the Pi)

```bash
# one-time
sudo apt update && sudo apt install -y python3-pip
pip3 install lgpio gpiozero  # GPIO libs
# run
cd cps-modbus-replay/server
sudo python3 modbus_gpio_server.py
