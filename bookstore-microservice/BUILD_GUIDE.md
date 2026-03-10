# Bookstore Microservices - Hướng dẫn Build và Deploy với Tag

## Tổng quan

Project đã được cập nhật để hỗ trợ build Docker images với tag tùy chỉnh. Điều này giúp quản lý versions và deploy dễ dàng hơn.

## Cách 1: Sử dụng Scripts có sẵn

### Windows (PowerShell):
```powershell
# Build với tag mặc định (latest)
.\build-and-run.ps1

# Build với tag cụ thể
.\build-and-run.ps1 v1.0.0
.\build-and-run.ps1 dev
.\build-and-run.ps1 prod
```

### Linux/Mac (Bash):
```bash
# Cấp quyền thực thi (chỉ cần làm 1 lần)
chmod +x build-and-run.sh

# Build với tag mặc định (latest)
./build-and-run.sh

# Build với tag cụ thể
./build-and-run.sh v1.0.0
./build-and-run.sh dev
./build-and-run.sh prod
```

## Cách 2: Sử dụng Docker Compose trực tiếp

### Build với tag mặc định (latest):
```bash
docker compose up --build -d
```

### Build với tag tùy chỉnh:

**Windows (PowerShell):**
```powershell
$env:TAG="v1.0.0"; docker compose up --build -d
```

**Linux/Mac (Bash):**
```bash
TAG=v1.0.0 docker compose up --build -d
```

**Windows (CMD):**
```cmd
set TAG=v1.0.0 && docker compose up --build -d
```

## Các Images được tạo

Khi build, các Docker images sau sẽ được tạo với tag đã chỉ định:

- `bookstore-api-gateway:${TAG}`
- `bookstore-customer-service:${TAG}`
- `bookstore-book-service:${TAG}`
- `bookstore-cart-service:${TAG}`
- `bookstore-order-service:${TAG}`
- `bookstore-pay-service:${TAG}`
- `bookstore-ship-service:${TAG}`
- `bookstore-comment-rate-service:${TAG}`
- `bookstore-staff-service:${TAG}`

## Xem danh sách images:
```bash
docker images | findstr bookstore  # Windows
docker images | grep bookstore     # Linux/Mac
```

## Các lệnh quản lý hữu ích

### Xem logs:
```bash
# Tất cả services
docker compose logs -f

# Service cụ thể
docker compose logs -f customer-service
docker compose logs -f api-gateway
```

### Dừng services:
```bash
docker compose down
```

### Dừng và xóa volumes:
```bash
docker compose down -v
```

### Khởi động lại một service:
```bash
docker compose restart customer-service
```

## Cập nhật Customer Service

### Các trường mới đã thêm vào Customer model:
- `fullname`: Họ tên đầy đủ
- `job`: Nghề nghiệp
- `address`: Địa chỉ (đã có sẵn, giữ nguyên)

### API Endpoints mới:
- `PUT /api/customers/<id>/update/`: Cập nhật thông tin customer

### Giao diện mới:
- `/profile/`: Trang thông tin cá nhân và cập nhật profile

## Ví dụ API Usage

### Cập nhật thông tin customer:
```bash
curl -X PUT http://localhost:8001/api/customers/1/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "Nguyễn Văn A",
    "job": "Software Engineer",
    "phone": "0123456789",
    "address": "123 ABC Street, Hanoi",
    "email": "nguyenvana@email.com"
  }'
```

### Đăng ký customer mới (với các trường mới):
```bash
curl -X POST http://localhost:8001/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "nguyenvana",
    "email": "nguyenvana@email.com",
    "password": "password123",
    "password_confirm": "password123",
    "fullname": "Nguyễn Văn A",
    "job": "Developer",
    "phone": "0123456789",
    "address": "123 ABC Street"
  }'
```

## Truy cập ứng dụng

- **Web UI**: http://localhost:8000
- **API Gateway**: http://localhost:8000/api/
- **Customer Service API**: http://localhost:8001/api/

## Troubleshooting

### Nếu gặp lỗi port đã được sử dụng:
```bash
# Dừng tất cả containers
docker compose down

# Kiểm tra processes đang dùng port
netstat -ano | findstr :8000  # Windows
lsof -i :8000                 # Linux/Mac
```

### Nếu cần rebuild hoàn toàn:
```bash
# Xóa tất cả containers, networks, volumes
docker compose down -v

# Rebuild lại từ đầu
docker compose up --build -d
```

### Nếu cần xóa tất cả images cũ:
```bash
# Xem images
docker images | grep bookstore

# Xóa image cụ thể
docker rmi bookstore-customer-service:old-tag

# Xóa tất cả images không được sử dụng
docker image prune -a
```
