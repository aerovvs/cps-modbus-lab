#!/bin/bash
# test all four attacks and capture results

echo "╔════════════════════════════════════════╗"
echo "║   Testing All Modbus Attacks          ║"
echo "╚════════════════════════════════════════╝"
echo

# get current log directory
LOG_DIR=$(ls -td ~/cps-modbus-lab/defense/logs/*/ | head -1)
echo "[+] Logging to: $LOG_DIR"

# function to wait and show progress
wait_with_progress() {
    local duration=$1
    local message=$2
    echo -n "$message"
    for i in $(seq 1 $duration); do
        echo -n "."
        sleep 1
    done
    echo " Done!"
}

echo -e "\n[!] Make sure:"
echo "    1. Modbus server is running (Terminal 1)"
echo "    2. Suricata IDS is running (Terminal 2)"
echo "    3. You're ready to run attacks from Mac"
echo
read -p "Press Enter when ready..."

# Track attacks
echo -e "\n[ATTACK SEQUENCE]"
echo "=================="

echo -e "\n1. Continuous Replay Attack"
echo "   Run: python3 continuous_attack.py raspberrypi.local"
echo "   Let it run for 30 seconds..."
read -p "   Press Enter when attack is running..."
wait_with_progress 30 "   Capturing"

echo -e "\n2. Blinking Attack (DOS)"
echo "   Run: python3 blinking_attack.py raspberrypi.local"
echo "   Let it run for 30 seconds..."
read -p "   Press Enter when attack is running..."
wait_with_progress 30 "   Capturing"

echo -e "\n3. Timed Attack"
echo "   Run: python3 timed_attack.py raspberrypi.local"
echo "   This runs once (waits 10 seconds then flashes)"
read -p "   Press Enter when attack is running..."
wait_with_progress 20 "   Capturing"

echo -e "\n4. Pattern Attack"
echo "   Run: python3 secret_message_attack.py raspberrypi.local SOS"
echo "   This sends SOS in Morse code"
read -p "   Press Enter when attack is running..."
wait_with_progress 30 "   Capturing"

echo -e "\n[+] All attacks completed!"
echo "[+] Copying Suricata logs..."

# Copy logs
sudo cp /var/log/suricata/eve.json $LOG_DIR/
sudo cp /var/log/suricata/fast.log $LOG_DIR/
sudo chown -R siage:siage $LOG_DIR

echo "[+] Logs saved to: $LOG_DIR"
echo -e "\n[!] You can now:"
echo "    1. Stop Suricata (Ctrl+C in Terminal 2)"
echo "    2. Run analysis: python3 ~/cps-modbus-lab/defense/scripts/analyze_complete.py"
