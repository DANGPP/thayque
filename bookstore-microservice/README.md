# BookStore Microservices

Hệ thống bán sách trực tuyến được xây dựng theo kiến trúc microservices với Django.

## Kiến trúc hệ thống

```
┌─────────────────────────────────────────────────────────────────┐
│                        API Gateway (8000)                        │
│                     (Django + Templates + REST)                  │
└────────────────────────────┬────────────────────────────────────┘
                             │
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│   Customer    │  │      Book       │  │      Cart       │
│  Service:8001 │  │  Service:8002   │  │  Service:8003   │
└───────────────┘  └─────────────────┘  └─────────────────┘
        
        ┌────────────────────┼────────────────────┐
        ▼                    ▼                    ▼
┌───────────────┐  ┌─────────────────┐  ┌─────────────────┐
│    Order      │  │    Payment      │  │    Shipping     │
│  Service:8004 │  │  Service:8005   │  │  Service:8006   │
└───────────────┘  └─────────────────┘  └─────────────────┘
        
        ┌────────────────────┴────────────────────┐
        ▼                                         ▼
┌───────────────┐                       ┌─────────────────┐
│ Comment/Rate  │                       │     Staff       │
│ Service:8007  │                       │  Service:8008   │
└───────────────┘                       └─────────────────┘
                             │
                             ▼
                   ┌─────────────────┐
                   │   PostgreSQL    │
                   │    (5432)       │
                   └─────────────────┘
```

## Cấu trúc Project

```
bookstore-microservice/
├── api-gateway/          # API Gateway với UI (Port 8000)
├── customer-service/     # Quản lý khách hàng (Port 8001)
├── book-service/         # Quản lý sách (Port 8002)
├── cart-service/         # Quản lý giỏ hàng (Port 8003)
├── order-service/        # Quản lý đơn hàng (Port 8004)
├── pay-service/          # Xử lý thanh toán (Port 8005)
├── ship-service/         # Quản lý vận chuyển (Port 8006)
├── comment-rate-service/ # Đánh giá sản phẩm (Port 8007)
├── staff-service/        # Quản lý nhân viên (Port 8008)
├── docker-compose.yml    # Docker compose configuration
└── init-db.sql           # Database initialization
```

## Yêu cầu hệ thống

- Docker & Docker Compose
- Python 3.11+ (nếu chạy local)
- PostgreSQL 15 (nếu chạy local)

## Hướng dẫn cài đặt

### Cách 1: Sử dụng Docker (Recommended)

```bash
# Clone và vào thư mục project
cd bookstore-microservice

# Build và chạy tất cả services
docker-compose up --build

# Hoặc chạy ngầm
docker-compose up -d --build
```

Truy cập:
- **Website**: http://localhost:8000
- **Admin Panel**: http://localhost:8000/admin-panel/

### Cách 2: Chạy Local (Development)

1. **Tạo database:**
```sql
-- Kết nối PostgreSQL: psql -U postgres -p 5432
-- Password: 1

CREATE DATABASE customer_db;
CREATE DATABASE book_db;
CREATE DATABASE cart_db;
CREATE DATABASE order_db;
CREATE DATABASE pay_db;
CREATE DATABASE ship_db;
CREATE DATABASE comment_db;
CREATE DATABASE staff_db;
```

2. **Chạy từng service:**
```bash
# Terminal 1 - Customer Service
cd customer-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8001

# Terminal 2 - Book Service
cd book-service
pip install -r requirements.txt
python manage.py migrate
python manage.py runserver 8002

# ... tương tự cho các service khác

# Terminal cuối - API Gateway
cd api-gateway
pip install -r requirements.txt
python manage.py runserver 8000
```

## Tính năng

### Người dùng (Customer)
- Đăng ký/Đăng nhập tài khoản
- Xem danh sách sách, tìm kiếm, lọc theo danh mục
- Xem chi tiết sách, đánh giá sản phẩm
- Thêm sách vào giỏ hàng
- Đặt hàng và theo dõi đơn hàng
- Viết đánh giá sản phẩm

### Admin (Staff)
- Dashboard với thống kê tổng quan
- Quản lý sách (CRUD)
- Quản lý danh mục, tác giả, NXB
- Quản lý đơn hàng (xác nhận, giao hàng, hoàn thành)
- Quản lý khách hàng
- Duyệt đánh giá sản phẩm

## API Endpoints

### Customer Service (8001)
- `POST /api/customers/register/` - Đăng ký
- `POST /api/customers/login/` - Đăng nhập
- `GET /api/customers/` - Danh sách khách hàng
- `GET /api/customers/{id}/` - Chi tiết khách hàng

### Book Service (8002)
- `GET /api/books/` - Danh sách sách
- `GET /api/books/{id}/` - Chi tiết sách
- `GET /api/categories/` - Danh mục
- `GET /api/authors/` - Tác giả
- `GET /api/publishers/` - NXB

### Cart Service (8003)
- `GET /api/carts/{customer_id}/` - Lấy giỏ hàng
- `POST /api/carts/add/` - Thêm vào giỏ
- `PUT /api/carts/items/{id}/` - Cập nhật số lượng
- `DELETE /api/carts/items/{id}/` - Xóa item

### Order Service (8004)
- `POST /api/orders/` - Tạo đơn hàng
- `GET /api/orders/{order_number}/` - Chi tiết đơn hàng
- `PUT /api/orders/{order_number}/status/` - Cập nhật trạng thái

### Payment Service (8005)
- `POST /api/payments/` - Tạo thanh toán
- `GET /api/payments/{order_number}/` - Thông tin thanh toán

### Shipping Service (8006)
- `POST /api/shipments/` - Tạo vận chuyển
- `GET /api/shipments/{order_number}/` - Thông tin vận chuyển

### Comment Service (8007)
- `GET /api/reviews/book/{book_id}/` - Đánh giá của sách
- `POST /api/reviews/` - Viết đánh giá

### Staff Service (8008)
- `POST /api/staff/login/` - Đăng nhập staff
- `GET /api/staff/` - Danh sách staff

## Công nghệ sử dụng

- **Backend**: Django 4.2, Django REST Framework
- **Database**: PostgreSQL 15
- **Frontend**: Bootstrap 5, Bootstrap Icons
- **Container**: Docker, Docker Compose

## Tác giả

BookStore Microservices Project - 2024
