#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo "Checking service health..."

# Check PostgreSQL
if docker-compose exec -T postgres pg_isready > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} PostgreSQL is healthy"
else
    echo -e "${RED}✗${NC} PostgreSQL is not responding"
fi

# Check MongoDB
if docker-compose exec -T mongodb mongosh --eval "db.adminCommand('ping')" > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} MongoDB is healthy"
else
    echo -e "${RED}✗${NC} MongoDB is not responding"
fi

# Check Redis
if docker-compose exec -T redis redis-cli ping > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} Redis is healthy"
else
    echo -e "${RED}✗${NC} Redis is not responding"
fi

# Check SuperTokens
if curl -f http://localhost:3567/hello > /dev/null 2>&1; then
    echo -e "${GREEN}✓${NC} SuperTokens is healthy"
else
    echo -e "${RED}✗${NC} SuperTokens is not responding"
fi

echo "Health check complete!"