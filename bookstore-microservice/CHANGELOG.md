# Báo cáo Cập nhật Bookstore Microservices
$env:TAG="v1.1.0"; docker compose up -d

## Tổng quan các thay đổi

Dự án đã được cập nhật với các tính năng mới theo yêu cầu:

### 1. Cập nhật Customer Service Model

#### Các trường mới được thêm vào Customer model:
- **fullname** (CharField): Họ tên đầy đủ của khách hàng
- **job** (CharField): Nghề nghiệp
- **address** (TextField): Địa chỉ chi tiết (đã có sẵn, được giữ nguyên)

#### Files đã sửa đổi:
- `customer-service/app/models.py`: Thêm các trường mới
- `customer-service/app/serializers.py`: Cập nhật serializers để bao gồm các trường mới
- `customer-service/app/migrations/0002_add_fullname_job.py`: Migration file mới

### 2. Chức năng Update Customer Profile

#### API Endpoint mới:
- **URL**: `PUT /api/customers/<id>/update/`
- **Mô tả**: Cập nhật thông tin profile của khách hàng
- **Request Body**:
```json
{
  "fullname": "Nguyễn Văn A",
  "job": "Software Engineer",
  "phone": "0123456789",
  "address": "123 ABC Street, Hanoi",
  "email": "user@example.com",
  "first_name": "Văn",
  "last_name": "Nguyễn",
  "date_of_birth": "1990-01-01"
}
```

#### Files đã sửa đổi:
- `customer-service/app/views.py`: Thêm `UpdateCustomerView`
- `customer-service/app/serializers.py`: Thêm `CustomerUpdateSerializer`
- `customer-service/app/urls.py`: Thêm route mới

### 3. Chức năng Update Cart

Cart service đã có sẵn các API để cập nhật giỏ hàng:

#### Existing Endpoints:
- `POST /api/carts/<customer_id>/add/`: Thêm sản phẩm vào giỏ
- `PUT /api/carts/<customer_id>/items/<item_id>/`: Cập nhật số lượng sản phẩm
- `DELETE /api/carts/<customer_id>/items/<item_id>/remove/`: Xóa sản phẩm
- `DELETE /api/carts/<customer_id>/clear/`: Xóa toàn bộ giỏ hàng

Các endpoint này đã đầy đủ cho việc quản lý giỏ hàng.

### 4. Giao diện người dùng (UI)

#### Trang mới:
- **URL**: `/profile/`
- **Template**: `api-gateway/templates/customer/profile.html`
- **Chức năng**:
  - Xem thông tin cá nhân
  - Cập nhật profile (fullname, job, phone, address, email, etc.)
  - Hiển thị thống kê khách hàng (điểm tích lũy, số đơn hàng, tổng chi tiêu)
  - Menu điều hướng nhanh (Profile, Đơn hàng, Giỏ hàng, Đăng xuất)

#### Files đã sửa đổi:
- `api-gateway/gateway/views.py`: Thêm `CustomerProfileView`
- `api-gateway/gateway/urls.py`: Thêm route `/profile/`
- `api-gateway/templates/base.html`: Thêm link "Thông tin cá nhân" vào dropdown menu
- `api-gateway/templates/customer/profile.html`: Template mới cho trang profile
- `api-gateway/templates/customer/register.html`: Cập nhật form đăng ký với các trường mới

### 5. Docker Compose với Parameterized Tags

#### Cập nhật docker-compose.yml:
- Tất cả services giờ đây hỗ trợ build với tag tùy chỉnh qua biến môi trường `TAG`
- Default tag: `latest`

#### Image names với tag:
- `bookstore-api-gateway:${TAG}`
- `bookstore-customer-service:${TAG}`
- `bookstore-book-service:${TAG}`
- `bookstore-cart-service:${TAG}`
- `bookstore-order-service:${TAG}`
- `bookstore-pay-service:${TAG}`
- `bookstore-ship-service:${TAG}`
- `bookstore-comment-rate-service:${TAG}`
- `bookstore-staff-service:${TAG}`

#### Scripts tiện ích:
1. **build-and-run.ps1** (Windows PowerShell)
2. **build-and-run.sh** (Linux/Mac Bash)

#### Cách sử dụng:

**Windows:**
```powershell
# Build với tag mặc định
.\build-and-run.ps1

# Build với tag cụ thể
.\build-and-run.ps1 v1.0.0
.\build-and-run.ps1 dev
```

**Linux/Mac:**
```bash
chmod +x build-and-run.sh
./build-and-run.sh v1.0.0
```

**Hoặc dùng docker compose trực tiếp:**
```powershell
# Windows
$env:TAG="v1.0.0"; docker compose up --build -d

# Linux/Mac
TAG=v1.0.0 docker compose up --build -d
```

## Hướng dẫn Deploy

### Bước 1: Build và Run
```powershell
# Windows
.\build-and-run.ps1 v1.0.0

# Hoặc
$env:TAG="v1.0.0"; docker compose up --build -d
```

### Bước 2: Tạo database migrations (nếu cần)
```bash
# Vào container customer-service
docker exec -it customer-service bash

# Chạy migrations
python manage.py makemigrations
python manage.py migrate
```

### Bước 3: Truy cập ứng dụng
- Web UI: http://localhost:8000
- API Gateway: http://localhost:8000/api/
- Customer Service: http://localhost:8001/api/

## Testing

### Test API Update Customer:
```bash
curl -X PUT http://localhost:8001/api/customers/1/update/ \
  -H "Content-Type: application/json" \
  -d '{
    "fullname": "Nguyễn Văn A",
    "job": "Software Engineer",
    "phone": "0123456789",
    "address": "123 ABC Street, Hanoi"
  }'
```

### Test API Register với các trường mới:
```bash
curl -X POST http://localhost:8001/api/register/ \
  -H "Content-Type: application/json" \
  -d '{
    "username": "testuser",
    "email": "test@example.com",
    "password": "password123",
    "password_confirm": "password123",
    "fullname": "Test User",
    "job": "Developer",
    "phone": "0123456789",
    "address": "123 Test Street"
  }'
```

### Test UI:
1. Truy cập http://localhost:8000
2. Đăng ký tài khoản mới với form đã cập nhật
3. Đăng nhập
4. Click vào dropdown menu username → "Thông tin cá nhân"
5. Cập nhật profile và lưu

## Files đã thay đổi

### Customer Service:
1. `models.py` - Thêm fields fullname, job
2. `serializers.py` - Thêm CustomerUpdateSerializer, cập nhật các serializers khác
3. `views.py` - Thêm UpdateCustomerView
4. `urls.py` - Thêm route update customer
5. `migrations/0002_add_fullname_job.py` - Migration file mới

### API Gateway:
1. `gateway/views.py` - Thêm CustomerProfileView
2. `gateway/urls.py` - Thêm route /profile/
3. `templates/base.html` - Thêm link profile trong menu
4. `templates/customer/profile.html` - Template mới
5. `templates/customer/register.html` - Cập nhật form đăng ký

### Docker:
1. `docker-compose.yml` - Thêm image tags với biến TAG
2. `build-and-run.ps1` - Script PowerShell
3. `build-and-run.sh` - Script Bash
4. `BUILD_GUIDE.md` - Hướng dẫn build và deploy

## Lưu ý

1. **Database Migration**: Sau khi deploy, cần chạy migrations để thêm các trường mới vào database
2. **Backward Compatibility**: Các trường mới đều có `blank=True, null=True` nên không ảnh hưởng đến dữ liệu cũ
3. **Tag Versioning**: Nên sử dụng semantic versioning (v1.0.0, v1.1.0, etc.) để quản lý versions
4. **Environment Variables**: Biến TAG có thể được set qua environment hoặc command line

## Kết luận

Tất cả các yêu cầu đã được hoàn thành:
✅ Thêm model fields: fullname, job, address
✅ Chức năng update customer profile
✅ Chức năng update cart (đã có sẵn, không cần thay đổi)
✅ Giao diện UI cho profile management
✅ Docker compose với parameterized tags
✅ Scripts tiện ích cho build và deploy
✅ Documentation đầy đủ
