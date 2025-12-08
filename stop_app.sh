#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${YELLOW}Stopping Serikali Yangu + AfyaTranslate Application${NC}\n"

# Stop Backend
if [ -f "backend.pid" ]; then
    BACKEND_PID=$(cat backend.pid)
    if kill -0 $BACKEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping backend (PID: $BACKEND_PID)...${NC}"
        kill $BACKEND_PID
        rm backend.pid
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend process not found${NC}"
        rm backend.pid
    fi
else
    # Try to find and kill uvicorn process
    if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -Pi :8001 -sTCP:LISTEN -t)
        echo -e "${YELLOW}Stopping backend on port 8001 (PID: $PID)...${NC}"
        kill $PID
        echo -e "${GREEN}✓ Backend stopped${NC}"
    else
        echo -e "${YELLOW}Backend is not running${NC}"
    fi
fi

# Stop Frontend
if [ -f "frontend.pid" ]; then
    FRONTEND_PID=$(cat frontend.pid)
    if kill -0 $FRONTEND_PID 2>/dev/null; then
        echo -e "${YELLOW}Stopping frontend (PID: $FRONTEND_PID)...${NC}"
        kill $FRONTEND_PID
        rm frontend.pid
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}Frontend process not found${NC}"
        rm frontend.pid
    fi
else
    # Try to find and kill vite process
    if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
        PID=$(lsof -Pi :5173 -sTCP:LISTEN -t)
        echo -e "${YELLOW}Stopping frontend on port 5173 (PID: $PID)...${NC}"
        kill $PID
        echo -e "${GREEN}✓ Frontend stopped${NC}"
    else
        echo -e "${YELLOW}Frontend is not running${NC}"
    fi
fi

echo -e "\n${GREEN}Application stopped!${NC}"

