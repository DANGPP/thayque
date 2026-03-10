#!/bin/bash
# Build and Run Bookstore Microservices with Custom Tag
# Usage: ./build-and-run.sh <tag>
# Example: ./build-and-run.sh v1.0.0
# Example: ./build-and-run.sh dev

TAG="${1:-latest}"

echo "================================"
echo "Bookstore Microservices Builder"
echo "================================"
echo ""
echo "Building with tag: $TAG"
echo ""

# Export TAG environment variable
export TAG

# Build and run with docker-compose
echo "Running: docker compose up --build -d"
docker compose up --build -d

if [ $? -eq 0 ]; then
    echo ""
    echo "================================"
    echo "Build and deployment successful!"
    echo "================================"
    echo ""
    echo "Images created with tag: $TAG"
    echo ""
    echo "Services are running at:"
    echo "  - API Gateway:      http://localhost:8000"
    echo "  - Customer Service: http://localhost:8001"
    echo "  - Book Service:     http://localhost:8002"
    echo "  - Cart Service:     http://localhost:8003"
    echo "  - Order Service:    http://localhost:8004"
    echo "  - Pay Service:      http://localhost:8005"
    echo "  - Ship Service:     http://localhost:8006"
    echo "  - Comment Service:  http://localhost:8007"
    echo "  - Staff Service:    http://localhost:8008"
    echo ""
    echo "View logs: docker compose logs -f"
    echo "Stop services: docker compose down"
else
    echo ""
    echo "Build failed! Check the errors above."
    exit 1
fi
