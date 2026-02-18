#!/bin/bash
# AOCROS GPIO Controller startup script
# Run on Pi 5 boot

LOG_FILE="/home/aocros/logs/gpio_controller.log"
PID_FILE="/var/run/aocros_gpio.pid"

# Ensure pigpio daemon is running
if ! pgrep -x "pigpiod" > /dev/null; then
    echo "Starting pigpiod..."
    sudo pigpiod
    sleep 1
fi

# Create log directory
mkdir -p /home/aocros/logs

# Run controller
cd /home/aocros/hardware
nohup python3 gpio_controller.py > "$LOG_FILE" 2>&1 &
echo $! > "$PID_FILE"

echo "AOCROS GPIO controller started (PID: $(cat $PID_FILE))"
echo "Logs: $LOG_FILE"
