#!/bin/bash

# Helper script to send verification email from Docker
# Usage: ./scripts/send_verification_email.sh <email>

if [ -z "$1" ]; then
    echo "❌ Error: Email address required"
    echo ""
    echo "Usage:"
    echo "  ./scripts/send_verification_email.sh <email>"
    echo ""
    echo "Example:"
    echo "  ./scripts/send_verification_email.sh user@example.com"
    echo ""
    echo "From Docker:"
    echo "  cd docker"
    echo "  docker-compose -f development_docker-compose.yml exec backend python scripts/send_verification_email.py user@example.com"
    exit 1
fi

EMAIL=$1

echo ""
echo "========================================================================"
echo "📧 Sending verification email via Docker container..."
echo "========================================================================"
echo "Target: $EMAIL"
echo "========================================================================"
echo ""

# Execute in Docker container
python scripts/send_verification_email.py "$EMAIL"
