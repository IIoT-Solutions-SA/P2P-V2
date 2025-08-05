#!/bin/bash
# Script to start Docker containers and update status log

LOG_FILE="/mnt/d/Projects/P2P-V2/p2p-backend-app/docker-status.log"

# Function to log status
log_status() {
    echo "[$(date '+%Y-%m-%d %H:%M:%S')] $1: $2 ($3)" >> "$LOG_FILE"
}

# Start Docker Compose
log_status "ALL_SERVICES" "STARTING" "Initiating docker-compose up"
docker-compose up -d

# Check status of each service
sleep 5
for service in postgres mongodb redis supertokens backend; do
    if docker-compose ps | grep -q "${service}.*Up"; then
        log_status "$service" "UP" "Container running"
    else
        log_status "$service" "FAILED" "Container not running"
    fi
done

# Check overall health
if docker-compose ps | grep -q "Up" | wc -l | grep -q "5"; then
    log_status "ALL_SERVICES" "READY" "All containers running"
else
    log_status "ALL_SERVICES" "PARTIAL" "Some containers failed"
fi

# Test API endpoint
if curl -s http://localhost:8000/health > /dev/null; then
    log_status "API_HEALTH" "OK" "Backend responding"
else
    log_status "API_HEALTH" "FAILED" "Backend not responding"
fi

echo "Docker startup complete. Check $LOG_FILE for status."