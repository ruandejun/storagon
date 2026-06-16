#!/bin/bash
# Storagon Web Server Watchdog Script
# Path: /root/watchdog.sh

URL="http://localhost/dashboard/login/"
LOG_FILE="/root/watchdog.log"
TIMEOUT=10

# Check if server is responding with HTTP 200 or 302
RESPONSE=$(curl -s -o /dev/null -w "%{http_code}" --max-time $TIMEOUT "$URL")

if [ "$RESPONSE" != "200" ] && [ "$RESPONSE" != "302" ]; then
    echo "$(date '+%Y-%m-%d %H:%M:%S') - ERROR: Web server returned HTTP $RESPONSE (or timed out). Restarting Docker containers..." >> "$LOG_FILE"
    
    # Restart the docker compose project
    cd /root/storagon && docker compose restart
    
    echo "$(date '+%Y-%m-%d %H:%M:%S') - Containers restarted successfully." >> "$LOG_FILE"
else
    exit 0
fi
