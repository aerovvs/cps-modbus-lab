# MITRE ATT&CK for ICS Mapping

## Overview

This document maps each attack demonstrated in the CPS Modbus Security Lab to corresponding MITRE ATT&CK for ICS techniques. Each mapping includes the technique ID, name, and a brief explanation of how our attack demonstrates this technique.

## Attack 1: Continuous Replay Attack (continuous_attack.py)

### Primary Techniques

**T0855 - Unauthorized Command Message**
- **What it is:** Sending control commands without proper authorization
- **How we did it:** Replayed captured Modbus commands every 2 seconds
- **Why it worked:** Modbus has no authentication mechanism

**T0814 - Denial of Control**
- **What it is:** Preventing operators from controlling the process
- **How we did it:** Continuous commands overrode operator inputs
- **Why it worked:** Our commands sent faster than manual override attempts

**T0858 - Change Operating Mode**
- **What it is:** Modifying how the control system operates
- **How we did it:** Forced LED to remain in ON state regardless of operator commands
- **Why it worked:** No validation of command source or intent

### Supporting Techniques

**T0869 - Standard Application Layer Protocol**
- Used legitimate Modbus TCP protocol (port 502)
- No custom protocols or exploits needed

## Attack 2: Blinking DOS Attack (blinking_attack.py)

### Primary Techniques

**T0836 - Modify Parameter**
- **What it is:** Changing system parameters to cause impact
- **How we did it:** Modified captured packet from 0xFF00 (ON) to 0x0000 (OFF)
- **Why it worked:** No integrity checking on Modbus packets

**T0815 - Denial of View**
- **What it is:** Preventing operators from seeing true system state
- **How we did it:** Rapid state changes made actual state unclear
- **Why it worked:** LED changing too fast for human observation

**T0803 - Block Command Message**
- **What it is:** Preventing legitimate commands from having effect
- **How we did it:** Rapid conflicting commands blocked stable state
- **Why it worked:** System processed our commands faster than responses

### Supporting Techniques

**T0885 - Commonly Used Port**
- Exploited standard Modbus port (502)
- Blended with legitimate traffic

## Attack 3: Timing Attack (timing_attack.py)

### Primary Techniques

**T0873 - Project File Infection**
- **What it is:** Malware that waits before executing
- **How we did it:** 10-second delay before payload activation
- **Why it worked:** Mimics logic bomb behavior in infected control logic

**T0853 - Scripting**
- **What it is:** Using scripts for attack automation
- **How we did it:** Python script automated the timing and execution
- **Why it worked:** Scripting enabled precise timing control

**T0856 - Spoof Reporting Message**
- **What it is:** Sending false information about system state
- **How we did it:** System appeared normal during dormant period
- **Why it worked:** No activity during wait looked like idle connection

### Attack Chain
1. Initial Access → Wait (dormant) → Execution (burst) → Impact (LED stuck on)

## Attack 4: Pattern Attack - Covert Channel (pattern_attack.py)

### Primary Techniques

**T0820 - Exploitation for Evasion**
- **What it is:** Exploiting systems to avoid detection
- **How we did it:** Used LED timing patterns to transmit data
- **Why it worked:** Physical output not monitored for data exfiltration

**T0889 - Modify Program**
- **What it is:** Changing control logic behavior
- **How we did it:** LED control logic repurposed for communication
- **Why it worked:** Timing patterns encoded information (Morse code)

**T0851 - Rootkit**
- **What it is:** Hiding malicious functionality
- **How we did it:** Covert channel hidden in legitimate-looking LED control
- **Why it worked:** Individual commands appeared normal

### Data Exfiltration Method
- Short flash (0.2s) = Morse dot
- Long flash (0.6s) = Morse dash  
- Transmitted "SOS" and custom messages

## Common Techniques Across All Attacks

### Network Reconnaissance

**T0846 - Remote System Discovery**
- All attacks began with network scan for port 502
- Identified target as Modbus device

**T0888 - Remote System Information Discovery**
- Passive observation revealed:
  - Modbus function codes in use
  - Register/coil addresses
  - Normal timing patterns

### Persistence

**T0859 - Valid Accounts**
- No accounts needed - Modbus allows anonymous access
- Persistence achieved through lack of authentication

### Command and Control

**T0869 - Standard Application Layer Protocol**
- All C2 traffic used standard Modbus TCP
- Blended with legitimate industrial traffic

## Real-World Incident Parallels

| Our Attack | Real Incident | Technique Used |
|------------|---------------|----------------|
| Continuous Replay | Ukrainian Power Grid 2015 | T0855, T0814 |
| Blinking DOS | Stuxnet centrifuge damage | T0836, T0858 |
| Timing Attack | Triton/TRISIS safety system | T0873, T0853 |
| Covert Channel | Flame malware data exfil | T0820, T0889 |

## Detection Opportunities

Each technique creates detection opportunities:

- **T0855**: Unusual source IPs sending commands
- **T0836**: Parameters changing outside normal ranges  
- **T0814**: Operators unable to execute commands
- **T0820**: Unusual timing patterns in normal operations

## Key Takeaways

1. **No Authentication = Easy Exploitation**
   - Most techniques possible due to missing authentication
   - T0859 (Valid Accounts) irrelevant when anonymous access allowed

2. **Physical Access Not Required**
   - All attacks executed remotely over network
   - No techniques requiring local access used

3. **Standard Protocols Enable Attacks**
   - T0869 throughout - legitimate protocol abuse
   - No malware or exploits needed

4. **Simple Techniques Sufficient**
   - No advanced techniques required
   - Basic replay and modification achieved full compromise

## MITRE ATT&CK Techniques NOT Needed

Interestingly, many sophisticated techniques were unnecessary:

- **T0865 - Spearphishing Attachment**: Direct access available
- **T0866 - Exploitation of Remote Services**: No vulnerabilities needed
- **T0842 - Network Sniffing**: Protocol unencrypted by design
- **T0845 - Program Download**: Existing functions sufficient

This highlights that Modbus systems are vulnerable to even basic attacks, making sophisticated techniques overkill.
