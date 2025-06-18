# CPS Modbus Security Lab: My Walkthrough and Experience

## Introduction

This document details my journey building and exploiting a cyber-physical system (CPS) to understand industrial control system vulnerabilities. As I just recently graduated with my Computer Science degree from Cal Poly Pomona, I wanted to gain hands-on experience with OT/ICS security, which is a field that fascinates me but isn't typically covered in traditional CS programs. Without formal internships in this area, I created this lab to demonstrate my ability to identify, exploit, and defend against real-world industrial control system vulnerabilities.

## Lab Environment Setup

I started by setting up a realistic CPS using a Raspberry Pi 5 as my target industrial controller. The Pi would simulate a programmable logic controller (PLC) commonly found in industrial environments, with a simple LED representing a critical industrial output: perhaps a valve, pump, or circuit breaker in a real facility. The physical setup required careful attention to GPIO wiring, using a 220Ω resistor to protect the LED connected to GPIO pin 17.

![](https://github.com/aerovvs/cps-modbus-lab/blob/main/media/pi_setup.jpg)

The network architecture consisted of my Raspberry Pi connected via Ethernet, while my MacBook attacker machine operated over WiFi. This mixed setup actually mirrors many real industrial networks where legacy wired systems interact with modern wireless human-machine interfaces. I discovered this created interesting network dynamics during my attacks.

The adventure started with a blank microSD. I flashed Raspberry Pi OS Lite (32‑bit) using Raspberry Pi Imager. A quick ssh pi@<ip> proved the network path was alive.

Wiring took two minutes using this guide:
https://magazine.raspberrypi.com/articles/breadboard-tutorial


## Building the Modbus server

Rather than using existing libraries like PyModbus, I decided to implement my own Modbus TCP server from scratch. This decision came after struggling with version compatibility issues, a frustration that turned into an invaluable learning opportunity. Building the protocol handler myself forced me to understand every byte of the Modbus protocol.

The moment I tried to run my Modbus server, Python answered with lgpio.error: 'GPIO busy'. I learned two things fast:

RPi.GPIO doesn’t recognise the Pi 5 SOC: it fails with “Cannot determine SOC peripheral base.”

Hitting Ctrl‑Z leaves the interpreter suspended but still owning /dev/gpiochip0.

Removing RPi.GPIO, installing rpi‑lgpio 0.6, and adding a defensive lgpio.gpio_free(chip, 17) before each claim cured the problem. A quick sudo pkill -f python3 cleaned it up.

The server implementation revealed the shocking simplicity of Modbus. Each packet follows a straightforward structure: transaction ID, protocol identifier, length, unit ID, function code, and data. No authentication headers, no encryption, no session management, just raw commands. When I first successfully controlled the LED through my custom server, I experienced a lot of excitement.

![](https://github.com/aerovvs/cps-modbus-lab/blob/main/media/start_modbus_server.png)

mbpoll became the client. One command turned the LED on (0xFF00), another turned it off (0x0000). The Pi logs showed GPIO17 -> 1 and GPIO17 -> 0 exactly on cue, and Wireshark captured a pristine Function‑Code 05 frame. I saved that as pcap/legit_write_coil.pcap—a

![](https://github.com/aerovvs/cps-modbus-lab/blob/main/media/capture_led_on_pcap.png)

## Developing the Attacks
### Replay Attack Discovery
My first attack came from a simple observation: if Modbus has no authentication or timestamps, what prevents me from replaying a captured command? I used tcpdump and Wireshark to capture a legitimate "LED ON" command from mbpoll, then wrote a Python script to replay it continuously.

image

### Packet Manipulation and Physical Impact
Building on the replay attack, I discovered I could create new commands by modifying captured packets. By changing just two bytes in the payload (0xFF00 to 0x0000), I could create an OFF command from an ON command. This led to my second attack: rapid state changes designed to cause physical wear.

image

### Simulating APTs
The timed attack simulated how sophisticated malware like Stuxnet operates. Instead of immediate action, my code waited 10 seconds before launching a rapid sequence of commands. This delay could represent malware waiting for shift changes, specific dates, or operational conditions.

image

### Covert Channel
My favorite attack demonstrated data exfiltration through physical means. Using Morse code transmitted via LED blinks, I could leak information. The implementation required precise timing control to ensure readable patterns.

Testing with "SOS" as my message, the LED blinked three short, three long, three short. In a real facility, this could be any controllable output. 

## Implementing Defense Mechanisms
After successfully compromising my own system, I switched perspectives to defense.

image

The replay attack detection rule looked for five identical packets within ten secondss. DoS detection triggered on ten state changes within five seconds, far exceeding normal operational tempos.

## Detection Results
Running all four attacks while monitoring with Suricata provided fascinating results. The IDS successfully detected every attack. However, detection isn't prevention. Despite generating alerts for every attack, the LED continued responding to malicious commands. This gap between detection and prevention mirrors real industrial environments where stopping suspicious traffic might halt critical processes.

image

## Discoveries
Checking Shodan revealed over 800,000+ Modbus devices exposed to the internet. Each one potentially vulnerable to the exact attacks I had just demonstrated. Water treatment plants, power generation facilities, manufacturing systems, which are all using the same insecure protocol.

image

