# 05 - Detection Strategy

## The Challenge of Industrial Intrusion Detection

Implementing intrusion detection for industrial control systems presents unique challenges that don't exist in traditional IT security. When I began developing detection rules for my Modbus attacks, I quickly discovered that the line between normal operations and malicious activity can be surprisingly thin. A command to open a valve is legitimate when sent by an operator but malicious when sent by an attacker, and at the protocol level, they're identical. This ambiguity forces us to look beyond individual packets to patterns, timing, and context.

The fundamental tension in industrial intrusion detection lies between sensitivity and reliability. In regular IT environments, false positives are annoying but manageable. In industrial settings, false positives can shut down production lines. 

## Developing Detection Rules

The first rule I developed targeted the replay attack. The key insight was that legitimate operations rarely involve sending identical commands at regular intervals. Operators might turn a pump on or off, but they don't typically send "turn on" commands every two seconds indefinitely. This led to a detection strategy based on command frequency and repetition:

alert tcp any any -> any 502 (msg:"Modbus Replay Attack - Continuous"; 
flow:to_server,established; 
detection_filter:track by_src, count 5, seconds 10; 
sid:1000001;)

This rule triggers when five Modbus commands arrive from the same source within ten seconds. The rule's effectiveness comes from recognizing that attacks often exhibit mechanical regularity that human operations lack.

The DoS detection required a different approach. Rather than looking for command frequency alone, this rule needed to identify rapid state changes that could damage equipment. The challenge was distinguishing between legitimate testing or maintenance activities and malicious rapid cycling. The solution involved tighter thresholds and focusing on write operations specifically:

alert tcp any any -> any 502 (msg:"Modbus DOS - Rapid State Changes";
flow:to_server,established;
detection_filter:track by_src, count 10, seconds 5;
sid:1000002;)

Ten commands in five seconds represents a rate that would be unusual for manual operation but typical for automated attacks. The key was recognizing that human operators have physical limitations. They simply can't click buttons fast enough to trigger this rule accidentally.

## Advanced Detection

Detecting the timed attack presented a more complex challenge. The attack's dormant period made it invisible to simple rate based detection, and its burst activity might be mistaken for legitimate automation. This required a more sophisticated approach combining multiple detection strategies.

The solution involved correlating connection events with subsequent command patterns. A new connection that remains idle before suddenly bursting into activity represents anomalous behavior worth investigating. While Suricata's rule language made expressing this correlation challenging, the combination of connection tracking and command monitoring proved effective:

alert tcp any any -> any 502 (msg:"Modbus Suspicious Burst Activity";
flow:to_server,established;
detection_filter:track by_src, count 8, seconds 2;
sid:1000003;)

This tighter threshold catches the rapid burst of the timed attack's payload while being unlikely to trigger during normal operations. The rule exemplifies how understanding attack behavior enables targeted detection, by recognizing that the timed attack produces a characteristic burst pattern, we can detect it specifically without impacting legitimate rapid command sequences that might occur during different operational phases.

The covert channel attack pushed detection capabilities to their limits. How do you identify data hidden in timing patterns of otherwise legitimate commands? Traditional signature-based detection fails here because each individual command is valid. The solution required statistical analysis of command timing patterns.

My approach focused on detecting unusual regularity in command timing. Morse code transmission creates distinctive patterns: consistent short and long intervals that differ from the variable timing of human operations. While perfect detection of all possible combinations is impossible, the regular timing patterns of most practical covert channels make them detectable:

alert tcp any any -> any 502 (msg:"Modbus Covert Channel - Unusual Timing";
flow:to_server,established;
detection_filter:track by_src, count 20, seconds 30;
sid:1000004;)

This rule identifies sustained sequences of commands that might indicate encoded communications. Twenty commands in thirty seconds isn't necessarily malicious, but it warrants investigation, especially if timing analysis reveals suspicious regularity.

## The Reality of Detection Performance

Testing these rules against my attacks yielded impressive results. Every attack triggered appropriate alerts within seconds of initiation. The replay attack consistently triggered alerts after the fifth command. The DoS attack was detected even faster, usually within three seconds. The timed attack's burst phase triggered immediate alerts, though the initial dormant connection went unnoticed. The covert channel took longest to detect.

However, these perfect results come with important caveats. My lab environment lacks the noise and complexity of real industrial networks. Production systems generate vast amounts of legitimate traffic that could mask attacks or trigger false positives. My attacks were designed to be demonstrative. A real adversary would likely use more intricate evasion techniques. 

The detection latency, while measured in seconds, raises critical questions for industrial environments. In IT security, detecting an attack within 10 seconds would be considered excellent. In industrial contexts, 10 seconds might be too late. This challenge highlights why prevention, not just detection, remains crucial for industrial security.

## Integration Challenges and Operational Considerations

Deploying intrusion detection in industrial environments faces technical and organizational challenges beyond rule development. The technical challenges begin with network visibility. Many industrial networks use managed switches that don't support port mirroring, making packet capture difficult. The Raspberry Pi's limited processing power also represents a realistic constraint, as many industrial sites use embedded devices for security monitoring rather than dedicated servers.

The organizational challenges proved equally significant. Who monitors IDS alerts in an industrial facility? IT staff often lack understanding of industrial processes to distinguish normal from anomalous. Operations staff focus on production, not security monitoring. This gap between IT and OT creates blind spots that attackers exploit. My lab setup, with everything on one desk, doesn't capture this organizational complexity that often proves more challenging than technical issues.

Alert fatigue represents another critical challenge. During extended testing, even my relatively simple environment generated hundreds of alerts. In a production facility with dozens or hundreds of Modbus devices, alert volumes could be overwhelming. This necessitates careful tuning, priority schemes, and possibly automated response system, which each add complexity and potential failure points.

## Lessons in Defensive Strategy

Developing and testing this detection strategy revealed fundamental truths about industrial cybersecurity. First, detection without prevention is like a smoke alarm in a building without sprinklers. Every one of my attacks succeeded despite being detected. 

Second, effective detection requires deep understanding of both normal operations and attack patterns. Generic IDS rules designed for IT networks fail in industrial contexts. The rules that succeeded were specifically crafted based on understanding Modbus protocol behavior and industrial operational patterns. This specialization requirement makes industrial security challenging. You can't just deploy standard signatures and expect protection.

Third, the speed of detection versus speed of impact creates a fundamental challenge. Physical processes often can't be instantly reversed even after detecting an attack. If malicious commands open a valve, detection ten seconds later doesn't undo the release. This asymmetry between attack and defense favors adversaries in industrial environments.

## The Path Forward for Industrial Detection

My research shows that effective detection of industrial cyber attacks is achievable with current technology, but it requires careful implementation and realistic expectations. Signature-based detection works for known attack patterns, but novel attacks or slight variations might evade detection. This suggests a layered approach combining signature detection with anomaly detection and machine learning techniques.

The future of industrial intrusion detection likely lies in hybrid systems that understand both cyber and physical aspects of industrial processes. Detecting cyber attacks is important, but correlating those attacks with physical anomalies (unexpected pressure changes, temperature variations) provides higher confidence and faster response. This cyber-physical correlation requires new tools and techniques beyond traditional network monitoring.

Most importantly, this research reinforces that detection is just one layer of a comprehensive security strategy. The ease with which I compromised the Modbus server despite detection highlights the critical need for preventive controls. Network segmentation, access control, and encrypted communications must complement detection capabilities. In industrial environments where safety and availability are the most important, hoping to detect and respond to attacks isn't enough. We must prevent them from succeeding in the first place.
