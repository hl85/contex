#!/bin/bash
set -e

# Colors
GREEN='\033[0;32m'
RED='\033[0;31m'
NC='\033[0m'

echo -e "${GREEN}Building Contex Brain Docker Image...${NC}"

# Check if docker is running
if ! docker info > /dev/null 2>&1; then
    echo -e "${RED}Error: Docker is not running${NC}"
    exit 1
fi

# Build image from project root
docker build -t contex-brain:latest -f packages/brain/Dockerfile .

if [ $? -eq 0 ]; then
    echo -e "${GREEN}Build Successful! Image: contex-brain:latest${NC}"
else
    echo -e "${RED}Build Failed!${NC}"
    exit 1
fi
