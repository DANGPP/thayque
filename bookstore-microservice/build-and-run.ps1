# Build and Run Bookstore Microservices with Custom Tag
# Usage: .\build-and-run.ps1 <tag>
# Example: .\build-and-run.ps1 v1.0.0
# Example: .\build-and-run.ps1 dev

param(
    [string]$Tag = "latest"
)

Write-Host "================================" -ForegroundColor Cyan
Write-Host "Bookstore Microservices Builder" -ForegroundColor Cyan
Write-Host "================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Building with tag: $Tag" -ForegroundColor Green
Write-Host ""

# Set the TAG environment variable
$env:TAG = $Tag

# Build and run with docker-compose
Write-Host "Running: docker compose up --build -d" -ForegroundColor Yellow
docker compose up --build -d

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "================================" -ForegroundColor Green
    Write-Host "Build and deployment successful!" -ForegroundColor Green
    Write-Host "================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "Images created with tag: $Tag" -ForegroundColor Cyan
    Write-Host ""
    Write-Host "Services are running at:" -ForegroundColor Cyan
    Write-Host "  - API Gateway:     http://localhost:8000" -ForegroundColor White
    Write-Host "  - Customer Service: http://localhost:8001" -ForegroundColor White
    Write-Host "  - Book Service:     http://localhost:8002" -ForegroundColor White
    Write-Host "  - Cart Service:     http://localhost:8003" -ForegroundColor White
    Write-Host "  - Order Service:    http://localhost:8004" -ForegroundColor White
    Write-Host "  - Pay Service:      http://localhost:8005" -ForegroundColor White
    Write-Host "  - Ship Service:     http://localhost:8006" -ForegroundColor White
    Write-Host "  - Comment Service:  http://localhost:8007" -ForegroundColor White
    Write-Host "  - Staff Service:    http://localhost:8008" -ForegroundColor White
    Write-Host ""
    Write-Host "View logs: docker compose logs -f" -ForegroundColor Yellow
    Write-Host "Stop services: docker compose down" -ForegroundColor Yellow
} else {
    Write-Host ""
    Write-Host "Build failed! Check the errors above." -ForegroundColor Red
}
