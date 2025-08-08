#!/bin/bash

# Frontend Control Script - Graceful and Fast

FRONTEND_DIR="/mnt/d/Projects/P2P-V2/p2p-frontend-app"
LOG_FILE="$FRONTEND_DIR/frontend.log"

stop_frontend() {
    echo "🛑 Stopping frontend..."
    
    # Method 1: Kill by port (most reliable)
    PID=$(lsof -ti :5173 2>/dev/null)
    if [ ! -z "$PID" ]; then
        kill $PID
        echo "✅ Stopped process $PID using port 5173"
        return 0
    fi
    
    # Method 2: Kill by process name
    if pkill -f "vite" >/dev/null 2>&1; then
        echo "✅ Stopped vite processes"
        return 0
    fi
    
    echo "ℹ️  No frontend processes found"
}

start_frontend() {
    echo "🚀 Starting frontend..."
    cd "$FRONTEND_DIR" || exit 1
    
    # Clear old log
    > "$LOG_FILE"
    
    # Start with nohup
    nohup npm run dev > "$LOG_FILE" 2>&1 &
    
    echo "⏳ Waiting for startup..."
    
    # Wait for startup (max 10 seconds)
    for i in {1..20}; do
        if curl -s http://localhost:5173 >/dev/null 2>&1; then
            echo "✅ Frontend ready at http://localhost:5173"
            echo "📋 Startup time: $(grep "ready in" "$LOG_FILE" | tail -1)"
            return 0
        fi
        sleep 0.5
    done
    
    echo "❌ Frontend didn't start properly. Check $LOG_FILE"
    return 1
}

status_frontend() {
    echo "📊 Frontend Status:"
    
    PID=$(lsof -ti :5173 2>/dev/null)
    if [ ! -z "$PID" ]; then
        echo "✅ Running on port 5173 (PID: $PID)"
        if [ -f "$LOG_FILE" ]; then
            echo "📋 Last startup: $(grep "ready in" "$LOG_FILE" | tail -1)"
        fi
    else
        echo "❌ Not running"
    fi
}

case "$1" in
    start)
        start_frontend
        ;;
    stop)
        stop_frontend
        ;;
    restart)
        stop_frontend
        sleep 1
        start_frontend
        ;;
    status)
        status_frontend
        ;;
    *)
        echo "Usage: $0 {start|stop|restart|status}"
        exit 1
        ;;
esac