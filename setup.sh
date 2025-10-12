#!/bin/bash

echo "==================================="
echo "AI Resume Optimizer - Quick Setup"
echo "==================================="
echo ""

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

# Check if Docker is installed
if ! command -v docker &> /dev/null; then
    echo -e "${RED}Error: Docker is not installed${NC}"
    echo "Please install Docker from https://www.docker.com/get-started"
    exit 1
fi

# Check if Docker Compose is installed
if ! command -v docker-compose &> /dev/null; then
    echo -e "${RED}Error: Docker Compose is not installed${NC}"
    echo "Please install Docker Compose"
    exit 1
fi

echo -e "${GREEN}✓ Docker and Docker Compose found${NC}"
echo ""

# Create project structure
echo "Creating project structure..."
mkdir -p backend
mkdir -p frontend/src

echo -e "${GREEN}✓ Project directories created${NC}"
echo ""

# Setup backend
echo "Setting up backend..."
cd backend

# Create .env file for local development
if [ ! -f .env ]; then
    echo "Creating .env file..."
    cat > .env << EOF
DATABASE_URL=postgresql://postgres:postgres@postgres:5432/resume_optimizer
JWT_SECRET_KEY=dev-secret-key-change-in-production
FLASK_ENV=development
EOF
    echo -e "${GREEN}✓ .env file created${NC}"
fi

# Start Docker containers
echo ""
echo "Starting Docker containers..."
echo -e "${YELLOW}This may take a few minutes on first run...${NC}"
docker-compose up -d --build

# Wait for services to be ready
echo ""
echo "Waiting for services to start..."
sleep 10

# Check if backend is running
if curl -s http://localhost:5000/api/health > /dev/null; then
    echo -e "${GREEN}✓ Backend is running at http://localhost:5000${NC}"
else
    echo -e "${RED}✗ Backend failed to start${NC}"
    echo "Check logs with: docker-compose logs backend"
fi

echo ""
echo "==================================="
echo "Setup Complete!"
echo "==================================="
echo ""
echo "Backend API: http://localhost:5000"
echo ""
echo "Next steps for frontend:"
echo "1. cd ../frontend"
echo "2. npm install recharts"
echo "3. Replace src/App.jsx with the React component"
echo "4. npm start"
echo ""
echo "Useful commands:"
echo "  - View logs: docker-compose logs -f"
echo "  - Stop services: docker-compose down"
echo "  - Restart: docker-compose restart"
echo ""
echo -e "${GREEN}Happy coding!${NC}"