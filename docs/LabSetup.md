# 03 - Lab Setup

## 1 - Hardware Platform

A tri-node topology was chosen to mimic the separation frequently seen in real plants between engineering workstations, corporate laptops, and field devices. A MacBook Air acts as the attacking host. A Linux desktop, reachable over the same WiFi network, serves as the management console from which you will SSH into the Pi. The Raspberry Pi 5 plays the dual role of Modbus slave and IDS sensor. An LED wired to a physical pin through a 220-ohm resistor completes the cyber-physical feedback loop.

## 2 - Software Environment Configuration

The target system operates on Raspberry Pi OS Lite (32-bit), a Debian-based Linux distribution providing stability and extensive package availability while maintaining lightweight resource requirements. This choice reflects the Linux-based embedded systems commonly found in modern industrial controllers. The operating system requires minimal modification from default installation, with primary changes focused on network configuration and Python environment establishment for the Modbus server implementation.

Python serves as the implementation language for both attack and defense components. The custom Modbus TCP server implementation, rather than utilizing existing libraries, provides deep insight into protocol operations and vulnerabilities. This approach mirrors security research methodology where understanding fundamental protocol behavior is essential for identifying and exploiting weaknesses. The server implements core Modbus functions including coil reading and writing, sufficient to demonstrate the critical vulnerabilities while avoiding unnecessary complexity.

The attacker system requires Python 3.8 or later with the Scapy packet manipulation framework as the primary dependency. Scapy's capabilities for packet crafting, capture, and analysis make it ideal for demonstrating how legitimate protocol traffic can be captured, analyzed, and weaponized. Additional tools such as Wireshark for packet analysis and mbpoll for Modbus testing provide complementary capabilities for verification and demonstration.

## 3 - Intrusion Detection System Integration

The deployment of Suricata as the intrusion detection system on the target platform represents a realistic approach to retrofitting security monitoring onto existing industrial systems. This configuration, while introducing some performance overhead, accurately reflects real world scenarios where security measures must be integrated with minimal disruption to operational systems. Suricata's native support for Modbus protocol analysis and flexible rule language enables precise detection of the demonstrated attacks while illustrating both capabilities and limitations of signature-based detection in industrial contexts.

The custom rule set developed for this laboratory focuses on detecting anomalous patterns specific to the demonstrated attacks: excessive command frequency indicating replay attacks, rapid state changes suggesting denial of service attempts, and unusual timing patterns potentially indicating covert channel communication. 

The decision to operate Suricata in passive IDS mode rather than inline IPS mode reflects industrial security realities where blocking suspicious traffic could disrupt critical processes. This configuration demonstrates the fundamental tension between security and availability in operational technology environments, where maintaining process continuity often takes precedence over preventing potential attacks. 

## 4 - Laboratory Initialization and Verification

The initialization process begins with operating system installation on the Raspberry Pi, using Raspberry Pi Imager. Network configuration follows, establishing static IP addressing and verifying connectivity between all laboratory components. The physical LED circuit construction provides immediate visual feedback for verifying GPIO functionality and serves as an early diagnostic tool for the complete system.

Software component installation then follows, beginning with Python environment establishment and dependency installation. The custom Modbus server requires no compilation, simplifying deployment and modification for experimental purposes. Attack script deployment on the attacker system follows a similar pattern, with particular attention to Scapy installation which may require elevated privileges for packet capture capabilities. The modular design of attack scripts facilitates incremental testing and understanding of each vulnerability demonstration.

Verification testing progresses through multiple stages, beginning with physical layer verification using simple GPIO control scripts, proceeding through network connectivity confirmation, and culminating in Modbus protocol communication testing using industry standard tools. 


