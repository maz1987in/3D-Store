#!/bin/bash

# 3D Store Application Stop Script

echo "🛑 Stopping 3D Store Application..."
echo ""

# Colors
RED='\033[0;31m'
GREEN='\033[0;32m'
NC='\033[0m'

# Stop backend (port 5000)
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    BACKEND_PID=$(lsof -Pi :5000 -sTCP:LISTEN -t)
    kill -9 $BACKEND_PID 2>/dev/null
    echo "${GREEN}✅ Backend stopped (PID: $BACKEND_PID)${NC}"
else
    echo "⚠️  Backend not running"
fi

# Stop frontend (port 4200)
if lsof -Pi :4200 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    FRONTEND_PID=$(lsof -Pi :4200 -sTCP:LISTEN -t)
    kill -9 $FRONTEND_PID 2>/dev/null
    echo "${GREEN}✅ Frontend stopped (PID: $FRONTEND_PID)${NC}"
else
    echo "⚠️  Frontend not running"
fi

echo ""
echo "${GREEN}✅ Application stopped successfully!${NC}"

