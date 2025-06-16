#!/usr/bin/env python3
"""
Complete Modbus Attack Analysis with Statistics
"""
import json
import sys
from datetime import datetime
from collections import Counter, defaultdict
import os

class ModbusAnalyzer:
    def __init__(self, eve_log='/var/log/suricata/eve.json'):
        self.eve_log = eve_log
        self.alerts = []
        self.modbus_events = []
        self.stats = {
            'start_time': None,
            'end_time': None,
            'total_alerts': 0,
            'unique_attackers': set(),
            'attack_timeline': []
        }
    
    def parse_logs(self):
        """Parse Suricata EVE JSON logs"""
        print("[+] Parsing Suricata logs...")
        
        try:
            with open(self.eve_log, 'r') as f:
                for line in f:
                    try:
                        event = json.loads(line)
                        timestamp = event.get('timestamp')
                        
                        # Track time range
                        if not self.stats['start_time']:
                            self.stats['start_time'] = timestamp
                        self.stats['end_time'] = timestamp
                        
                        # Categorize events
                        if event.get('event_type') == 'alert':
                            self.alerts.append(event)
                            src_ip = event.get('src_ip')
                            if src_ip:
                                self.stats['unique_attackers'].add(src_ip)
                                
                        elif event.get('event_type') == 'modbus':
                            self.modbus_events.append(event)
                            
                    except json.JSONDecodeError:
                        continue
                        
        except FileNotFoundError:
            print(f"[!] Log file not found: {self.eve_log}")
            return False
        
        self.stats['total_alerts'] = len(self.alerts)
        return True
    
    def analyze_attacks(self):
        """Detailed attack analysis"""
        attack_types = Counter()
        attack_sources = Counter()
        attack_timeline = defaultdict(list)
        
        for alert in self.alerts:
            # Get attack details
            signature = alert['alert']['signature']
            src_ip = alert.get('src_ip', 'unknown')
            timestamp = alert['timestamp']
            
            attack_types[signature] += 1
            attack_sources[src_ip] += 1
            
            # Create timeline
            time_key = timestamp.split('.')[0]  # Group by second
            attack_timeline[time_key].append(signature)
        
        return attack_types, attack_sources, attack_timeline
    
    def generate_report(self):
        """Generate comprehensive report"""
        print("\n" + "="*60)
        print("     CPS MODBUS SECURITY ANALYSIS REPORT")
        print("="*60)
        
        print(f"\n[SCAN PERIOD]")
        print(f"Start: {self.stats['start_time']}")
        print(f"End:   {self.stats['end_time']}")
        
        print(f"\n[SUMMARY]")
        print(f"Total Alerts: {self.stats['total_alerts']}")
        print(f"Unique Attackers: {len(self.stats['unique_attackers'])}")
        print(f"Total Modbus Events: {len(self.modbus_events)}")
        
        # Attack breakdown
        attack_types, attack_sources, timeline = self.analyze_attacks()
        
        print(f"\n[ATTACK BREAKDOWN]")
        print("-" * 40)
        for attack, count in attack_types.most_common():
            percentage = (count / self.stats['total_alerts'] * 100) if self.stats['total_alerts'] > 0 else 0
            print(f"{attack}:")
            print(f"  Count: {count} ({percentage:.1f}%)")
            
            # Find which IPs performed this attack
            attackers_for_this = []
            for alert in self.alerts:
                if alert['alert']['signature'] == attack:
                    src = alert.get('src_ip', 'unknown')
                    if src not in attackers_for_this:
                        attackers_for_this.append(src)
            print(f"  Sources: {', '.join(attackers_for_this)}")
        
        print(f"\n[ATTACKER ANALYSIS]")
        print("-" * 40)
        for ip, count in attack_sources.most_common():
            print(f"{ip}: {count} attacks")
            
            # What attacks did this IP perform?
            ip_attacks = Counter()
            for alert in self.alerts:
                if alert.get('src_ip') == ip:
                    ip_attacks[alert['alert']['signature']] += 1
            
            for attack, cnt in ip_attacks.most_common():
                print(f"  - {attack}: {cnt}")
        
        print(f"\n[MODBUS FUNCTION ANALYSIS]")
        print("-" * 40)
        if self.modbus_events:
            functions = Counter()
            for event in self.modbus_events:
                if 'modbus' in event:
                    func = event['modbus'].get('function_code', 'unknown')
                    functions[func] += 1
            
            for func, count in functions.most_common():
                print(f"Function Code {func}: {count} times")
        else:
            print("No Modbus events captured")
        
        # Attack timeline sample
        print(f"\n[ATTACK TIMELINE] (First and Last 5)")
        print("-" * 40)
        
        sorted_timeline = sorted(timeline.items())
        if len(sorted_timeline) > 10:
            # Show first 5
            for time, attacks in sorted_timeline[:5]:
                print(f"{time}: {', '.join(attacks)}")
            print("...")
            # Show last 5
            for time, attacks in sorted_timeline[-5:]:
                print(f"{time}: {', '.join(attacks)}")
        else:
            # Show all
            for time, attacks in sorted_timeline:
                print(f"{time}: {', '.join(attacks)}")
    
    def save_report(self, output_dir):
        """Save detailed report to file"""
        report_file = os.path.join(output_dir, 'analysis_report.txt')
        
        # Redirect stdout to file
        orig_stdout = sys.stdout
        with open(report_file, 'w') as f:
            sys.stdout = f
            self.generate_report()
        sys.stdout = orig_stdout
        
        print(f"\n[+] Report saved to: {report_file}")
        
        # Also save JSON summary
        summary = {
            'scan_period': {
                'start': self.stats['start_time'],
                'end': self.stats['end_time']
            },
            'total_alerts': self.stats['total_alerts'],
            'unique_attackers': list(self.stats['unique_attackers']),
            'alert_types': dict(Counter(a['alert']['signature'] for a in self.alerts))
        }
        
        summary_file = os.path.join(output_dir, 'summary.json')
        with open(summary_file, 'w') as f:
            json.dump(summary, f, indent=2)
        
        print(f"[+] JSON summary saved to: {summary_file}")

def main():
    # Get log directory from command line or use latest
    if len(sys.argv) > 1:
        log_dir = sys.argv[1]
    else:
        # Find latest log directory
        base_dir = os.path.expanduser('~/cps-modbus-lab/defense/logs/')
        try:
            dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]
            log_dir = os.path.join(base_dir, sorted(dirs)[-1])
        except:
            log_dir = base_dir
    
    print(f"[+] Analyzing logs from: {log_dir}")
    
    # Create analyzer
    analyzer = ModbusAnalyzer()
    
    # Parse logs
    if analyzer.parse_logs():
        # Generate report
        analyzer.generate_report()
        
        # Save to log directory
        analyzer.save_report(log_dir)
        
        # Quick stats
        print(f"\n[QUICK STATS]")
        print(f"Total Alerts: {analyzer.stats['total_alerts']}")
        print(f"Unique Attackers: {len(analyzer.stats['unique_attackers'])}")
        print(f"Log Directory: {log_dir}")

if __name__ == "__main__":
    main()
