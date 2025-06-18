#!/bin/bash
# Complete IDS startup with logging

echo "╔════════════════════════════════════════╗"
echo "║   CPS Modbus IDS - Full Monitoring     ║"
echo "╚════════════════════════════════════════╝"
echo

# Create log directory with timestamp
TIMESTAMP=$(date +%Y%m%d_%H%M%S)
LOG_DIR=~/cps-modbus-lab/defense/logs/$TIMESTAMP
mkdir -p $LOG_DIR

echo "[+] Log directory: $LOG_DIR"

# Kill any running Suricata
sudo pkill suricata
sleep 2

# Clean old logs
sudo rm -f /var/log/suricata/*.log
sudo rm -f /var/log/suricata/*.json

# Start Suricata
echo "[+] Starting Suricata on eth0..."
sudo suricata -c /etc/suricata/suricata.yaml -i eth0 -S /etc/suricata/rules/modbus-attacks.rules &
SPID=$!

echo "[+] Suricata PID: $SPID"
echo "[+] Waiting for initialization..."
sleep 5

# Save PID for later
echo $SPID > $LOG_DIR/suricata.pid

# Monitor with colors and logging
echo -e "\n[+] Monitoring attacks (also saving to $LOG_DIR/alerts.log)\n"

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m'

# Monitor and save alerts
sudo tail -f /var/log/suricata/fast.log | while IFS= read -r line; do
    # Display with colors
    if [[ $line == *"Replay Attack"* ]]; then
        echo -e "${RED}[REPLAY]${NC} $line"
    elif [[ $line == *"DoS"* ]]; then
        echo -e "${RED}[DOS]${NC} $line"
    elif [[ $line == *"Covert"* ]]; then
        echo -e "${YELLOW}[COVERT]${NC} $line"
    elif [[ $line == *"Write"* ]]; then
        echo -e "${GREEN}[WRITE]${NC} $line"
    else
        echo "$line"
    fi
    
    # Also save to log
    echo "$line" >> $LOG_DIR/alerts.log
done
