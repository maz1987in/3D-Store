#!/bin/bash

# 3D Store Application Startup Script

echo "🚀 Starting 3D Store Application..."
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Check if backend is already running
if lsof -Pi :5000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Backend already running on port 5000"
else
    echo "${BLUE}Starting Backend...${NC}"
    cd backend
    source venv/bin/activate
    python run.py > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo "${GREEN}✅ Backend started (PID: $BACKEND_PID)${NC}"
    cd ..
fi

echo ""

# Check if frontend is already running
if lsof -Pi :4200 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo "⚠️  Frontend already running on port 4200"
else
    echo "${BLUE}Starting Frontend...${NC}"
    cd frontend
    ng serve --port 4200 > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo "${GREEN}✅ Frontend started (PID: $FRONTEND_PID)${NC}"
    cd ..
fi

echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "${GREEN}🎉 Application Started Successfully!${NC}"
echo ""
echo "📱 Frontend: http://localhost:4200"
echo "🔧 Backend:  http://localhost:5000"
echo ""
echo "📋 Logs:"
echo "   Backend:  tail -f backend.log"
echo "   Frontend: tail -f frontend.log"
echo ""
echo "🛑 To stop: Run ./stop_app.sh"
echo ""
echo "━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━"
echo ""
echo "⏳ Waiting for servers to initialize (30 seconds)..."
sleep 30

# Check if servers are responding
echo ""
echo "🔍 Checking server health..."

if curl -s http://localhost:4200 > /dev/null 2>&1; then
    echo "${GREEN}✅ Frontend is responding${NC}"
else
    echo "⚠️  Frontend is still starting... (check frontend.log)"
fi

if curl -s http://localhost:5000 > /dev/null 2>&1; then
    echo "${GREEN}✅ Backend is responding${NC}"
else
    echo "⚠️  Backend is still starting... (check backend.log)"
fi

echo ""
echo "${GREEN}🚀 Ready! Open http://localhost:4200 in your browser${NC}"

