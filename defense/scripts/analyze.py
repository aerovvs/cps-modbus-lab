#!/usr/bin/env python3
import json
from collections import Counter

print("=== Modbus Attack Analysis ===")

alerts = Counter()
total = 0

try:
    with open('/var/log/suricata/eve.json', 'r') as f:
        for line in f:
            try:
                event = json.loads(line)
                if event.get('event_type') == 'alert':
                    alerts[event['alert']['signature']] += 1
                    total += 1
            except:
                continue
except:
    print("No alerts found yet!")
    exit()

print(f"\nTotal Alerts: {total}")
print("\nAttack Types:")
for attack, count in alerts.most_common():
    print(f"  {attack}: {count}")
