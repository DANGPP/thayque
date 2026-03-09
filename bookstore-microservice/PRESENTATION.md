# THUYẾT TRÌNH HỆ THỐNG BOOKSTORE MICROSERVICES

---

## 📑 NỘI DUNG THUYẾT TRÌNH

1. Giới thiệu Microservices
2. Kiến trúc hệ thống BookStore
3. Chi tiết các Service
4. Cách các Service gọi nhau
5. Luồng hoạt động chính
6. Lợi ích của Microservices
7. So sánh với Monolithic
8. Demo & Kết luận

---

## 1️⃣ MICROSERVICES LÀ GÌ?

### Định nghĩa
Microservices là một **phương pháp kiến trúc phần mềm** trong đó ứng dụng được chia thành các **dịch vụ nhỏ, độc lập**, mỗi dịch vụ:
- Chạy trong **tiến trình riêng**
- Giao tiếp qua **API (HTTP/REST)**
- Có **database riêng**
- Có thể **deploy độc lập**

### Ví dụ minh họa
```
┌─────────────────────────────────────────┐
│           MONOLITHIC APP                │
│  ┌─────┬─────┬─────┬─────┬─────┐       │
│  │User │Book │Cart │Order│ Pay │       │
│  └─────┴─────┴─────┴─────┴─────┘       │
│           Single Database               │
└─────────────────────────────────────────┘

              ↓ Chia nhỏ thành ↓

┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐ ┌───────┐
│ User  │ │ Book  │ │ Cart  │ │ Order │ │  Pay  │
│Service│ │Service│ │Service│ │Service│ │Service│
└───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘ └───┬───┘
    │         │         │         │         │
   DB1       DB2       DB3       DB4       DB5
```

---

## 2️⃣ KIẾN TRÚC HỆ THỐNG BOOKSTORE

### Sơ đồ tổng quan

```
                    ┌─────────────────────────────────┐
                    │         NGƯỜI DÙNG              │
                    │   (Browser/Mobile App)          │
                    └───────────────┬─────────────────┘
                                    │
                                    ▼
┌───────────────────────────────────────────────────────────────────┐
│                      API GATEWAY (Port 8000)                       │
│              Django + Templates + Session Management               │
│         Routing, Authentication, Load Balancing, UI Render         │
└───────────────────────────────┬───────────────────────────────────┘
                                │
        ┌───────────┬───────────┼───────────┬───────────┐
        ▼           ▼           ▼           ▼           ▼
┌─────────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐ ┌─────────┐
│  CUSTOMER   │ │  BOOK   │ │  CART   │ │  ORDER  │ │   PAY   │
│  SERVICE    │ │ SERVICE │ │ SERVICE │ │ SERVICE │ │ SERVICE │
│  Port 8001  │ │Port 8002│ │Port 8003│ │Port 8004│ │Port 8005│
└──────┬──────┘ └────┬────┘ └────┬────┘ └────┬────┘ └────┬────┘
       │             │           │           │           │
       ▼             ▼           ▼           ▼           ▼
  ┌────────┐   ┌────────┐  ┌────────┐  ┌────────┐  ┌────────┐
  │customer│   │ book   │  │ cart   │  │ order  │  │  pay   │
  │  _db   │   │  _db   │  │  _db   │  │  _db   │  │  _db   │
  └────────┘   └────────┘  └────────┘  └────────┘  └────────┘

        ┌───────────────────┬───────────────────┐
        ▼                   ▼                   ▼
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│    SHIP     │     │   COMMENT   │     │    STAFF    │
│   SERVICE   │     │   SERVICE   │     │   SERVICE   │
│  Port 8006  │     │  Port 8007  │     │  Port 8008  │
└──────┬──────┘     └──────┬──────┘     └──────┬──────┘
       │                   │                   │
       ▼                   ▼                   ▼
  ┌────────┐         ┌────────┐         ┌────────┐
  │ ship   │         │comment │         │ staff  │
  │  _db   │         │  _db   │         │  _db   │
  └────────┘         └────────┘         └────────┘
```

### Danh sách các Service

| # | Service | Port | Chức năng | Database |
|---|---------|------|-----------|----------|
| 1 | API Gateway | 8000 | Điều phối, UI, Routing | - |
| 2 | Customer Service | 8001 | Quản lý khách hàng | customer_db |
| 3 | Book Service | 8002 | Quản lý sách, danh mục | book_db |
| 4 | Cart Service | 8003 | Giỏ hàng | cart_db |
| 5 | Order Service | 8004 | Đơn hàng | order_db |
| 6 | Pay Service | 8005 | Thanh toán | pay_db |
| 7 | Ship Service | 8006 | Vận chuyển | ship_db |
| 8 | Comment Service | 8007 | Đánh giá sách | comment_db |
| 9 | Staff Service | 8008 | Quản lý nhân viên | staff_db |

---

## 3️⃣ CHI TIẾT TỪNG SERVICE

### 3.1 Customer Service (Port 8001)
**Chức năng:** Quản lý thông tin khách hàng

**Models:**
- `Customer` - Thông tin tài khoản (kế thừa AbstractUser)
- `CustomerProfile` - Thông tin bổ sung

**API Endpoints:**
```
POST /api/customers/register/    → Đăng ký tài khoản
POST /api/customers/login/       → Đăng nhập
GET  /api/customers/             → Danh sách khách hàng
GET  /api/customers/{id}/        → Chi tiết khách hàng
PUT  /api/customers/{id}/        → Cập nhật thông tin
```

**Giao tiếp với service khác:**
- Khi đăng ký → Gọi Cart Service tạo giỏ hàng mới

---

### 3.2 Book Service (Port 8002)
**Chức năng:** Quản lý sách và danh mục

**Models:**
- `Category` - Danh mục sách
- `Author` - Tác giả
- `Publisher` - Nhà xuất bản
- `Book` - Thông tin sách
- `BookImage` - Hình ảnh sách

**API Endpoints:**
```
GET  /api/books/                 → Danh sách sách (filter, search, sort)
GET  /api/books/{id}/            → Chi tiết sách
POST /api/books/                 → Thêm sách mới
PUT  /api/books/{id}/            → Cập nhật sách
GET  /api/categories/            → Danh mục
GET  /api/authors/               → Tác giả
PUT  /api/books/{id}/stock/      → Cập nhật tồn kho
```

---

### 3.3 Cart Service (Port 8003)
**Chức năng:** Quản lý giỏ hàng

**Models:**
- `Cart` - Giỏ hàng của khách
- `CartItem` - Sản phẩm trong giỏ

**API Endpoints:**
```
GET  /api/carts/{customer_id}/   → Lấy giỏ hàng
POST /api/carts/add/             → Thêm sách vào giỏ
PUT  /api/carts/items/{id}/      → Cập nhật số lượng
DELETE /api/carts/items/{id}/    → Xóa sản phẩm
POST /api/carts/{id}/clear/      → Xóa toàn bộ giỏ hàng
```

**Giao tiếp với service khác:**
- Gọi Book Service để validate thông tin sách và tồn kho

---

### 3.4 Order Service (Port 8004)
**Chức năng:** Quản lý đơn hàng (CORE SERVICE)

**Models:**
- `Order` - Đơn hàng
- `OrderItem` - Sản phẩm trong đơn
- `OrderStatusHistory` - Lịch sử trạng thái

**API Endpoints:**
```
POST /api/orders/                    → Tạo đơn hàng
GET  /api/orders/{order_number}/     → Chi tiết đơn hàng
PUT  /api/orders/{order_number}/status/ → Cập nhật trạng thái
GET  /api/orders/customer/{id}/      → Đơn hàng của khách
```

**Giao tiếp với service khác (SAGA Pattern):**
```
1. Cart Service    → Lấy sản phẩm trong giỏ
2. Book Service    → Kiểm tra & trừ tồn kho
3. Pay Service     → Tạo yêu cầu thanh toán
4. Ship Service    → Tạo đơn vận chuyển
5. Cart Service    → Xóa giỏ hàng sau khi đặt
```

---

### 3.5 Pay Service (Port 8005)
**Chức năng:** Xử lý thanh toán

**Models:**
- `Payment` - Thông tin thanh toán
- `PaymentHistory` - Lịch sử thanh toán
- `Refund` - Hoàn tiền

**API Endpoints:**
```
POST /api/payments/              → Tạo thanh toán
GET  /api/payments/{order}/      → Thông tin thanh toán
PUT  /api/payments/{id}/confirm/ → Xác nhận đã thanh toán
POST /api/refunds/               → Tạo hoàn tiền
```

---

### 3.6 Ship Service (Port 8006)
**Chức năng:** Quản lý vận chuyển

**Models:**
- `Shipment` - Đơn vận chuyển
- `ShipmentTracking` - Theo dõi vận chuyển

**API Endpoints:**
```
POST /api/shipments/             → Tạo đơn vận chuyển
GET  /api/shipments/{order}/     → Thông tin vận chuyển
PUT  /api/shipments/{id}/status/ → Cập nhật trạng thái giao hàng
```

---

### 3.7 Comment Service (Port 8007)
**Chức năng:** Đánh giá sản phẩm

**Models:**
- `Review` - Đánh giá
- `ReviewReply` - Phản hồi đánh giá
- `ReviewHelpful` - Vote hữu ích

**API Endpoints:**
```
GET  /api/reviews/book/{book_id}/    → Đánh giá của sách
POST /api/reviews/                   → Viết đánh giá
GET  /api/reviews/summary/{book_id}/ → Thống kê rating
```

**Giao tiếp với service khác:**
- Gọi Book Service để cập nhật rating trung bình của sách

---

### 3.8 Staff Service (Port 8008)
**Chức năng:** Quản lý nhân viên/admin

**Models:**
- `Staff` - Nhân viên (kế thừa AbstractUser)
- `StaffActivity` - Lịch sử hoạt động

**API Endpoints:**
```
POST /api/staff/login/           → Đăng nhập admin
GET  /api/staff/                 → Danh sách nhân viên
GET  /api/staff/{id}/            → Chi tiết nhân viên
```

---

## 4️⃣ CÁCH CÁC SERVICE GỌI NHAU

### 4.1 Giao tiếp qua REST API

```python
# Ví dụ: Cart Service gọi Book Service để kiểm tra sách

import requests

BOOK_SERVICE_URL = "http://book-service:8000"

def get_book_info(book_id):
    response = requests.get(f"{BOOK_SERVICE_URL}/api/books/{book_id}/")
    if response.status_code == 200:
        return response.json()
    return None

def check_stock(book_id, quantity):
    book = get_book_info(book_id)
    if book and book['stock'] >= quantity:
        return True
    return False
```

### 4.2 Service Discovery (Docker Network)

```yaml
# docker-compose.yml
services:
  cart-service:
    environment:
      - BOOK_SERVICE_URL=http://book-service:8000
    networks:
      - bookstore-network

  book-service:
    networks:
      - bookstore-network

networks:
  bookstore-network:
    driver: bridge
```

Các service có thể gọi nhau bằng tên service (book-service, cart-service...) nhờ Docker Network.

---

## 5️⃣ LUỒNG HOẠT ĐỘNG CHÍNH

### 5.1 Luồng Đăng ký tài khoản

```
┌────────┐      ┌─────────────┐      ┌──────────────┐      ┌─────────────┐
│ Client │──1──▶│ API Gateway │──2──▶│   Customer   │──3──▶│    Cart     │
│        │      │             │      │   Service    │      │   Service   │
└────────┘      └─────────────┘      └──────────────┘      └─────────────┘
                                            │                     │
                                            ▼                     ▼
                                     ┌────────────┐        ┌────────────┐
                                     │customer_db │        │  cart_db   │
                                     └────────────┘        └────────────┘

1. Client gửi form đăng ký → API Gateway
2. Gateway forward request → Customer Service
3. Customer Service tạo tài khoản → Gọi Cart Service tạo giỏ hàng
```

### 5.2 Luồng Đặt hàng (Quan trọng nhất - SAGA Pattern)

```
┌────────┐     ┌─────────┐     ┌───────┐     ┌──────┐     ┌─────┐     ┌──────┐     ┌──────┐
│ Client │────▶│ Gateway │────▶│ Order │────▶│ Cart │────▶│Book │────▶│ Pay  │────▶│ Ship │
└────────┘     └─────────┘     └───────┘     └──────┘     └─────┘     └──────┘     └──────┘
                                   │            │           │           │           │
                                   │            │           │           │           │
                                   ▼            ▼           ▼           ▼           ▼
                              ┌────────────────────────────────────────────────────────┐
                              │                    LUỒNG XỬ LÝ                         │
                              ├────────────────────────────────────────────────────────┤
                              │ Step 1: Lấy giỏ hàng từ Cart Service                   │
                              │ Step 2: Kiểm tra & trừ tồn kho từ Book Service         │
                              │ Step 3: Tạo đơn hàng trong Order DB                    │
                              │ Step 4: Tạo thanh toán từ Pay Service                  │
                              │ Step 5: Tạo đơn vận chuyển từ Ship Service             │
                              │ Step 6: Xóa giỏ hàng từ Cart Service                   │
                              └────────────────────────────────────────────────────────┘
```

### 5.3 Code minh họa - Order Service tạo đơn hàng

```python
# order-service/app/views.py

class CreateOrderView(APIView):
    def post(self, request):
        customer_id = request.data.get('customer_id')
        
        # Step 1: Lấy giỏ hàng
        cart = requests.get(f"{CART_SERVICE}/api/carts/{customer_id}/").json()
        
        if not cart['items']:
            return Response({'error': 'Giỏ hàng trống'}, status=400)
        
        # Step 2: Kiểm tra và trừ tồn kho
        for item in cart['items']:
            book = requests.get(f"{BOOK_SERVICE}/api/books/{item['book_id']}/").json()
            if book['stock'] < item['quantity']:
                return Response({'error': f'Sách {book["title"]} hết hàng'}, status=400)
            
            # Trừ tồn kho
            requests.put(
                f"{BOOK_SERVICE}/api/books/{item['book_id']}/stock/",
                json={'quantity': -item['quantity']}
            )
        
        # Step 3: Tạo đơn hàng
        order = Order.objects.create(
            customer_id=customer_id,
            total=cart['total_price']
        )
        
        # Step 4: Tạo thanh toán
        requests.post(f"{PAY_SERVICE}/api/payments/", json={
            'order_number': order.order_number,
            'amount': order.total
        })
        
        # Step 5: Tạo vận chuyển
        requests.post(f"{SHIP_SERVICE}/api/shipments/", json={
            'order_number': order.order_number,
            'address': request.data.get('address')
        })
        
        # Step 6: Xóa giỏ hàng
        requests.post(f"{CART_SERVICE}/api/carts/{cart['id']}/clear/")
        
        return Response({'order_number': order.order_number})
```

---

## 6️⃣ LỢI ÍCH CỦA MICROSERVICES

### ✅ 1. Độc lập phát triển & Deploy

```
┌─────────────────────────────────────────────────────────────┐
│ Team A          Team B          Team C          Team D      │
│    │               │               │               │        │
│    ▼               ▼               ▼               ▼        │
│ Customer       Book            Cart            Order        │
│ Service        Service         Service         Service      │
│    │               │               │               │        │
│    ▼               ▼               ▼               ▼        │
│ Deploy         Deploy          Deploy          Deploy       │
│ v2.0           v1.5            v3.0            v2.1         │
└─────────────────────────────────────────────────────────────┘

→ Mỗi team phát triển & deploy độc lập, không ảnh hưởng lẫn nhau
```

### ✅ 2. Khả năng Scale độc lập

```
Ngày thường:
[Customer: 1] [Book: 1] [Cart: 1] [Order: 1]

Ngày sale (traffic tăng 10x ở Order):
[Customer: 1] [Book: 2] [Cart: 3] [Order: 10] ← Scale riêng Order
```

### ✅ 3. Fault Isolation - Cô lập lỗi

```
┌──────────────────────────────────────────────────────────┐
│  Comment Service bị lỗi (die)                            │
│                  ↓                                        │
│  ❌ Comment Service                                       │
│  ✅ Customer Service vẫn hoạt động                       │
│  ✅ Book Service vẫn hoạt động                           │
│  ✅ Cart Service vẫn hoạt động                           │
│  ✅ Order Service vẫn hoạt động                          │
│                                                          │
│  → Khách hàng vẫn mua hàng được, chỉ không xem được      │
│    đánh giá                                              │
└──────────────────────────────────────────────────────────┘
```

### ✅ 4. Công nghệ đa dạng (Technology Diversity)

```
┌─────────────────┐  ┌─────────────────┐  ┌─────────────────┐
│ Customer Service│  │ Recommender AI  │  │ Search Service  │
│    Django       │  │    Python ML    │  │  Elasticsearch  │
│   PostgreSQL    │  │    TensorFlow   │  │                 │
└─────────────────┘  └─────────────────┘  └─────────────────┘

→ Mỗi service có thể dùng công nghệ phù hợp nhất
```

### ✅ 5. Dễ bảo trì & hiểu code

```
Monolithic: 100,000 dòng code trong 1 project
Microservices: 10 services × 10,000 dòng = dễ hiểu hơn nhiều
```

---

## 7️⃣ SO SÁNH MONOLITHIC VS MICROSERVICES

| Tiêu chí | Monolithic | Microservices |
|----------|------------|---------------|
| **Cấu trúc** | 1 ứng dụng lớn | Nhiều service nhỏ |
| **Database** | 1 database chung | Mỗi service 1 DB |
| **Deploy** | Deploy toàn bộ | Deploy từng service |
| **Scale** | Scale toàn bộ | Scale từng phần |
| **Lỗi** | Lỗi 1 chỗ → sập hết | Lỗi cô lập |
| **Team** | 1 team lớn | Nhiều team nhỏ |
| **Công nghệ** | 1 stack duy nhất | Đa dạng công nghệ |
| **Phức tạp** | Đơn giản ban đầu | Phức tạp hơn |
| **Phù hợp** | Dự án nhỏ | Dự án lớn, scale cao |

---

## 8️⃣ CÔNG NGHỆ SỬ DỤNG TRONG PROJECT

### Backend
- **Framework:** Django 4.2 + Django REST Framework
- **Language:** Python 3.11

### Database
- **PostgreSQL 15** - Mỗi service 1 database riêng

### Frontend (API Gateway)
- **Bootstrap 5** - UI Framework
- **Bootstrap Icons** - Icon library
- **Django Templates** - Server-side rendering

### Container & Orchestration
- **Docker** - Containerize từng service
- **Docker Compose** - Orchestrate local development

### Communication
- **REST API** - Giao tiếp giữa các service
- **HTTP/JSON** - Protocol & Data format

---

## 9️⃣ DEMO HỆ THỐNG

### Truy cập
- **Website:** http://localhost:8000
- **Admin Panel:** http://localhost:8000/admin-panel/

### Tài khoản Admin
- **Username:** admin
- **Password:** admin123

### Chạy Project
```bash
cd bookstore-microservice
docker-compose up --build
```

### Kiểm tra Services
```bash
docker ps -a   # Xem tất cả containers
docker logs book-service   # Xem logs
```

---

## 🎯 KẾT LUẬN

### Microservices phù hợp khi:
- ✅ Ứng dụng lớn, nhiều tính năng
- ✅ Cần scale từng phần riêng biệt
- ✅ Nhiều team phát triển song song
- ✅ Cần fault tolerance cao
- ✅ Muốn sử dụng đa công nghệ

### Microservices KHÔNG phù hợp khi:
- ❌ Dự án nhỏ, đơn giản
- ❌ Team nhỏ (1-3 người)
- ❌ Không có kinh nghiệm DevOps
- ❌ Yêu cầu latency cực thấp

### BookStore Microservices Demo:
- 9 services độc lập
- 8 databases riêng biệt
- REST API communication
- Docker containerization
- Saga Pattern cho Order flow

---

## 📚 TÀI LIỆU THAM KHẢO

1. Martin Fowler - Microservices
2. Sam Newman - Building Microservices
3. Django REST Framework Documentation
4. Docker Documentation

---

# CẢM ƠN ĐÃ LẮNG NGHE!

**Q&A - Hỏi đáp**
