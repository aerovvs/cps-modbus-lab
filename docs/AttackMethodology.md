
# 05 - Attack Methodology

## Understanding the Attack Surface

When I first started researching industrial control system vulnerabilities, I expected to find complex, sophisticated weaknesses requiring advanced exploitation techniques. What I discovered instead was almost surprisingly simple: these systems were designed in an era when security wasn't a thought at all. The Modbus protocol, still widely deployed across critical infrastructure, embodies this perfectly. It's like finding a bank vault with a screen door for security.

The attack surface of a Modbus/TCP system is essentially its entire network interface. There's no authentication handshake to bypass, no encrypted session to break. If you can send packets to port 502, you can control the system. This simplicity is actually what makes these systems so dangerous from a security perspective. You either have no access or complete control.

My methodology focused on demonstrating four distinct categories of attacks, each highlighting a different aspect of industrial control system vulnerabilities. These weren't chosen randomly but represent real attack patterns observed in actual incidents against critical infrastructure. The progression from simple replay to sophisticated covert channels mirrors how threat actors escalate their capabilities when targeting industrial systems.

## The Replay Attack

The first attack I implemented was a basic replay attack. The process was straightforward: capture a legitimate command, save it, and send it again whenever you want. No modification needed, no reverse engineering required, just copy and paste at the network level. Yet this trivial technique completely compromised the system's integrity.

The attack began with passive reconnaissance, listening to network traffic to understand normal operations. Using tcpdump and Wireshark, I captured Modbus traffic between a legitimate client and the server. The packets were small, making them easy to analyze and understand. The structure was consistent and predictable: transaction ID, protocol identifier, length field, unit ID, function code, and data. No complexity, no obfuscation, just raw commands transmitted in clear text.

Once I captured a "write coil" command that turned on the LED, the replay attack was easy to implement. A simple Python script read the captured packet and retransmitted it every two seconds. The server had no way to distinguish between legitimate commands and replayed ones. There were no sequence numbers to track or no timestamps to validate. Each command was processed in isolation. In a real industrial setting, this could mean being unable to stop a pump, close a valve, or shut down a dangerous process. 

## Packet Manipulation

The second attack built upon the first by introducing packet manipulation. If I could replay commands, could I modify them to create new ones? This attack demonstrated that not only could commands be replayed, but they could be altered to create entirely new control sequences. The simplicity of the Modbus protocol made this modification effortless.

The key insight was recognizing that Modbus commands are essentially just structured data without any integrity protection. The command to turn on the LED differed from the command to turn it off by only two bytes - 0xFF00 for on versus 0x0000 for off. Modifying packets was as simple as changing values in a byte array.

This led to the creation of a DoS attack through rapid state changes. By alternating between on and off commands every second, the LED began blinking rapidly. This attack pattern represents a serious threat to industrial equipment. Mechanical systems like valves, motors, and relays have physical limitations on how quickly they can change states. Rapid cycling causes excessive wear, heat buildup, and premature failure. What appears as a simple blinking light in my lab could translate to destroyed equipment in an industrial facility.

## Timed Attacks

The third attack category explored temporal aspects of compromise. Real advanced persistent threats (APTs) don't always strike immediately upon gaining access. They wait, they watch and choose their moment for maximum impact. My timed attack simulated this behavior, demonstrating how logic bomb malware could lie dormant before executing its payload.

The attack script would wait ten seconds before taking any action. During this delay, the system appeared completely normal. An operator checking system status would see nothing amiss. Log files would show a connection but no commands. This dormant period mirrors how sophisticated malware like Stuxnet operated, hiding in systems for months before activating.

When the payload finally triggered, ten rapid fire commands caused the LED to flash before settling into a steady on state. The sudden burst of activity after a period of calm demonstrates how timing attacks can bypass human vigilance. Operators become accustomed to normal patterns and may not notice a new connection if it doesn't immediately cause problems. By the time the attack payload activates, the initial compromise may have scrolled off active monitoring screens or been forgotten.

The timed attack also demonstrates the challenge of correlating events in industrial systems. The initial connection and the eventual payload execution are separated by time, potentially appearing in different log files or monitoring windows. Without proper correlation and long term log retention, identifying the relationship between these events becomes difficult. This temporal separation is a key technique used by advanced adversaries to evade detection.

## Covert Channels

The fourth and most sophisticated attack transformed the LED from a simple status indicator into a data transmission device. This covert channel attack represents a paradigm shift in thinking about industrial systems; physical outputs designed for process control become unintended communication channels capable of bridging air gaps.

By implementing Morse code transmission through LED state changes, I could send arbitrary messages using nothing but the timing of on/off transitions. The default "SOS" pattern was clearly recognizable, but any message could be encoded and transmitted.

In real ICS, this technique could use any observable physical output. Motor speeds could encode data in their RPM variations. Valve positions could transmit information through partial openings. Temperature controllers could modulate heating elements to create data carrying thermal patterns.

This attack is particularly insidious because it bypasses traditional network security entirely. Data can be exfiltrated from air gapped networks through physical observations. A camera watching status lights, a microphone listening to equipment sounds, or even a human observer could receive these covert transmissions. Conversely, malware inside an air gapped network could receive commands through monitored physical inputs, such as light sensors, temperature probes, or vibration monitors become command channels.

## Attack Patterns and Real World Parallels

Throughout developing these attacks, I was fascinated by how closely they paralleled real world incidents. The replay attack mirrors the simplicity of early industrial cyber incidents where attackers simply replayed captured commands. The packet manipulation resembles techniques used in the 2015 Ukrainian power grid attack where breakers were rapidly opened and closed. The timed attack is similar to Stuxnet's patient approach, lying dormant until specific conditions were met. Additionally, the covert channel reminds us that Stuxnet reportedly used infected systems to communicate.

The modular nature of these attacks also show how they could be combined into more sophisticated campaigns. A real attacker might use covert channels for reconnaissance, timed attacks for synchronized disruption across multiple targets, replay attacks to maintain persistence, and packet manipulation to cause physical damage. The simple building blocks I created could be assembled into complex, multi-stage attacks.
