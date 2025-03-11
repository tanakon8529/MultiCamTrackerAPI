#!/bin/bash

# Set colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

# Print banner
echo -e "${GREEN}"
echo "====================================================="
echo "        MultiCamTrackerAPI - Startup Script          "
echo "====================================================="
echo -e "${NC}"

# Check if .env file exists
if [ ! -f .env ]; then
    echo -e "${YELLOW}No .env file found. Creating from .env.example...${NC}"
    
    # Check if .env.example exists
    if [ ! -f .env.example ]; then
        echo -e "${RED}Error: .env.example file not found. Cannot create .env file.${NC}"
        exit 1
    fi
    
    # Copy .env.example to .env
    cp .env.example .env
    echo -e "${GREEN}.env file created successfully.${NC}"
    echo -e "${YELLOW}Please review the .env file and update any necessary configuration.${NC}"
    echo -e "You can edit it now if needed, or press Enter to continue with default values."
    read -p "Press Enter to continue..."
else
    echo -e "${GREEN}.env file already exists.${NC}"
fi

# Check if uploads directory exists
if [ ! -d "uploads" ]; then
    echo -e "${YELLOW}Creating uploads directory...${NC}"
    mkdir -p uploads
    echo -e "${GREEN}Uploads directory created.${NC}"
else
    echo -e "${GREEN}Uploads directory already exists.${NC}"
fi

# Build and start Docker containers
echo -e "${GREEN}Building and starting Docker containers...${NC}"
docker-compose down
docker-compose build
docker-compose up -d

# Check if containers started successfully
if [ $? -eq 0 ]; then
    echo -e "${GREEN}"
    echo "====================================================="
    echo "  MultiCamTrackerAPI is now running!"
    echo "  API: http://localhost:8000"
    echo "  API Documentation: http://localhost:8000/docs"
    echo "====================================================="
    echo -e "${NC}"
    
    # Display container status
    echo -e "${GREEN}Container Status:${NC}"
    docker-compose ps
else
    echo -e "${RED}Error: Failed to start Docker containers.${NC}"
    exit 1
fi

# Show logs option
echo -e "${YELLOW}To view logs, run: docker-compose logs -f${NC}"
echo -e "${YELLOW}To stop the server, run: docker-compose down${NC}"
