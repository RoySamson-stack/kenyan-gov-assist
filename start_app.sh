#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}Starting Serikali Yangu + AfyaTranslate Application${NC}\n"

# Check if Ollama is running
echo -e "${YELLOW}Checking Ollama...${NC}"
if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
    echo -e "${RED}Ollama is not running!${NC}"
    echo -e "${YELLOW}Starting Ollama in background...${NC}"
    ollama serve > /dev/null 2>&1 &
    sleep 3
    if ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; then
        echo -e "${RED}Failed to start Ollama. Please start it manually: ollama serve${NC}"
        exit 1
    fi
fi
echo -e "${GREEN}✓ Ollama is running${NC}\n"

# Check if model is available
echo -e "${YELLOW}Checking for llama3.2:1b model...${NC}"
if ! ollama list | grep -q "llama3.2:1b"; then
    echo -e "${YELLOW}Model not found. Pulling llama3.2:1b...${NC}"
    ollama pull llama3.2:1b
fi
echo -e "${GREEN}✓ Model is available${NC}\n"

# Start Backend
echo -e "${YELLOW}Starting Backend...${NC}"
cd "$(dirname "$0")/backend" || exit 1

if [ ! -d "venv" ]; then
    echo -e "${YELLOW}Creating virtual environment...${NC}"
    python3 -m venv venv
fi

source venv/bin/activate
pip install -q -r requirements.txt

# Check if backend is already running
if lsof -Pi :8001 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Backend is already running on port 8001${NC}"
else
    echo -e "${GREEN}Starting backend on http://localhost:8001${NC}"
    uvicorn app.main:app --host 0.0.0.0 --port 8001 --reload > ../backend.log 2>&1 &
    BACKEND_PID=$!
    echo $BACKEND_PID > ../backend.pid
    sleep 2
    echo -e "${GREEN}✓ Backend started (PID: $BACKEND_PID)${NC}"
fi

# Start Frontend
echo -e "\n${YELLOW}Starting Frontend...${NC}"
cd ../frontend || exit 1

if [ ! -d "node_modules" ]; then
    echo -e "${YELLOW}Installing frontend dependencies...${NC}"
    npm install
fi

# Check if frontend is already running
if lsof -Pi :5173 -sTCP:LISTEN -t >/dev/null 2>&1; then
    echo -e "${YELLOW}Frontend is already running on port 5173${NC}"
else
    echo -e "${GREEN}Starting frontend on http://localhost:5173${NC}"
    npm run dev > ../frontend.log 2>&1 &
    FRONTEND_PID=$!
    echo $FRONTEND_PID > ../frontend.pid
    sleep 2
    echo -e "${GREEN}✓ Frontend started (PID: $FRONTEND_PID)${NC}"
fi

echo -e "\n${GREEN}========================================${NC}"
echo -e "${GREEN}Application is running!${NC}"
echo -e "${GREEN}========================================${NC}"
echo -e "Frontend: ${GREEN}http://localhost:5173${NC}"
echo -e "Backend:  ${GREEN}http://localhost:8001${NC}"
echo -e "API Docs: ${GREEN}http://localhost:8001/docs${NC}"
echo -e "\n${YELLOW}To stop the application:${NC}"
echo -e "  ./stop_app.sh"
echo -e "  or kill the processes: kill \$(cat backend.pid frontend.pid)"
echo -e "\n${YELLOW}Logs:${NC}"
echo -e "  Backend:  tail -f backend.log"
echo -e "  Frontend: tail -f frontend.log"

