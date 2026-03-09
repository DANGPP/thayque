# SLIDES CHO BÀI THUYẾT TRÌNH
# (Copy nội dung vào PowerPoint/Google Slides)

================================================================================
SLIDE 1: TRANG BÌA
================================================================================
# HỆ THỐNG BOOKSTORE MICROSERVICES

## Xây dựng hệ thống bán sách trực tuyến với kiến trúc Microservices

- Công nghệ: Django + PostgreSQL + Docker
- Sinh viên: [Tên SV]
- GVHD: [Thầy/Cô]

[Hình: Logo hoặc hình minh họa microservices]

================================================================================
SLIDE 2: NỘI DUNG THUYẾT TRÌNH
================================================================================
# NỘI DUNG

1. Microservices là gì?
2. Kiến trúc hệ thống BookStore
3. Chi tiết các Service
4. Cách các Service giao tiếp
5. Luồng đặt hàng (Flow)
6. Lợi ích của Microservices
7. Demo hệ thống
8. Kết luận

================================================================================
SLIDE 3: MICROSERVICES LÀ GÌ?
================================================================================
# MICROSERVICES LÀ GÌ?

## Định nghĩa
Kiến trúc chia ứng dụng thành **nhiều dịch vụ nhỏ, độc lập**

## Đặc điểm chính
✅ Chạy trong **tiến trình riêng**
✅ Giao tiếp qua **REST API**
✅ Có **database riêng**
✅ **Deploy độc lập**

[Hình: Sơ đồ so sánh Monolithic vs Microservices]

================================================================================
SLIDE 4: MONOLITHIC VS MICROSERVICES
================================================================================
# SO SÁNH MONOLITHIC VS MICROSERVICES

| Monolithic              | Microservices            |
|-------------------------|--------------------------|
| 1 ứng dụng lớn          | Nhiều service nhỏ        |
| 1 database chung        | Database riêng/service   |
| Deploy toàn bộ          | Deploy từng service      |
| Scale toàn bộ           | Scale từng phần          |
| Lỗi 1 → sập hết         | Lỗi cô lập               |

[Hình: 2 sơ đồ so sánh visual]

================================================================================
SLIDE 5: KIẾN TRÚC HỆ THỐNG BOOKSTORE
================================================================================
# KIẾN TRÚC TỔNG QUAN

                    [BROWSER]
                        │
                        ▼
              ┌─────────────────┐
              │   API GATEWAY   │  ← UI + Routing
              │    Port 8000    │
              └────────┬────────┘
                       │
    ┌──────┬──────┬────┼────┬──────┬──────┐
    ▼      ▼      ▼    ▼    ▼      ▼      ▼
[Customer][Book][Cart][Order][Pay][Ship][Comment][Staff]
  8001    8002  8003  8004  8005 8006   8007    8008
    │      │      │     │     │    │      │       │
   DB1    DB2    DB3   DB4   DB5  DB6    DB7     DB8

================================================================================
SLIDE 6: DANH SÁCH SERVICE
================================================================================
# 9 SERVICES TRONG HỆ THỐNG

| Service | Port | Chức năng |
|---------|------|-----------|
| 🌐 API Gateway | 8000 | UI, Routing, Auth |
| 👤 Customer | 8001 | Quản lý khách hàng |
| 📚 Book | 8002 | Quản lý sách |
| 🛒 Cart | 8003 | Giỏ hàng |
| 📦 Order | 8004 | Đơn hàng |
| 💳 Pay | 8005 | Thanh toán |
| 🚚 Ship | 8006 | Vận chuyển |
| ⭐ Comment | 8007 | Đánh giá |
| 👨‍💼 Staff | 8008 | Nhân viên |

================================================================================
SLIDE 7: CHI TIẾT - BOOK SERVICE
================================================================================
# BOOK SERVICE (Port 8002)

## Models
- Category (Danh mục)
- Author (Tác giả)
- Publisher (NXB)
- Book (Sách)

## API Endpoints
```
GET  /api/books/        → Danh sách sách
GET  /api/books/{id}/   → Chi tiết sách
POST /api/books/        → Thêm sách
PUT  /api/books/{id}/   → Cập nhật
```

================================================================================
SLIDE 8: CHI TIẾT - ORDER SERVICE
================================================================================
# ORDER SERVICE (Port 8004) - CORE

## Chức năng
Xử lý đơn hàng - Service quan trọng nhất

## Giao tiếp với các service khác
1. Cart Service → Lấy giỏ hàng
2. Book Service → Kiểm tra & trừ kho
3. Pay Service → Tạo thanh toán
4. Ship Service → Tạo vận chuyển

================================================================================
SLIDE 9: CÁCH SERVICE GỌI NHAU
================================================================================
# GIAO TIẾP GIỮA CÁC SERVICE

## REST API qua HTTP

```python
# Order Service gọi Book Service
import requests

BOOK_SERVICE = "http://book-service:8000"

# Lấy thông tin sách
response = requests.get(
    f"{BOOK_SERVICE}/api/books/{book_id}/"
)
book = response.json()
```

## Docker Network
- Các service gọi nhau qua tên container
- Ví dụ: `http://book-service:8000`

================================================================================
SLIDE 10: LUỒNG ĐẶT HÀNG - SEQUENCE DIAGRAM
================================================================================
# LUỒNG ĐẶT HÀNG (SAGA PATTERN)

[Client] → [Gateway] → [Order Service]
                              │
            ┌─────────────────┼─────────────────┐
            ▼                 ▼                 ▼
       [1. Cart]         [2. Book]         [3. Pay]
       Lấy giỏ hàng      Trừ tồn kho       Thanh toán
                              │
                              ▼
                         [4. Ship]
                         Vận chuyển
                              │
                              ▼
                        [5. Clear Cart]

================================================================================
SLIDE 11: CODE MINH HỌA - TẠO ĐƠN HÀNG
================================================================================
# CODE TẠO ĐƠN HÀNG

```python
def create_order(customer_id):
    # 1. Lấy giỏ hàng
    cart = requests.get(f"{CART}/carts/{customer_id}/")
    
    # 2. Kiểm tra & trừ kho
    for item in cart['items']:
        requests.put(f"{BOOK}/books/{item['book_id']}/stock/",
                     json={'quantity': -item['quantity']})
    
    # 3. Tạo đơn hàng
    order = Order.objects.create(...)
    
    # 4. Tạo thanh toán
    requests.post(f"{PAY}/payments/", json={...})
    
    # 5. Tạo vận chuyển
    requests.post(f"{SHIP}/shipments/", json={...})
```

================================================================================
SLIDE 12: LỢI ÍCH #1 - DEPLOY ĐỘC LẬP
================================================================================
# LỢI ÍCH 1: DEPLOY ĐỘC LẬP

## Mỗi team deploy riêng
```
Team A → Customer Service (v2.0)
Team B → Book Service (v1.5)
Team C → Cart Service (v3.0)
Team D → Order Service (v2.1)
```

✅ Không cần deploy cả hệ thống
✅ Giảm downtime
✅ Nhanh hơn, an toàn hơn

================================================================================
SLIDE 13: LỢI ÍCH #2 - SCALE ĐỘC LẬP
================================================================================
# LỢI ÍCH 2: SCALE ĐỘC LẬP

## Ngày thường
[Customer: 1] [Book: 1] [Cart: 1] [Order: 1]

## Ngày SALE (Order traffic x10)
[Customer: 1] [Book: 2] [Cart: 3] [Order: 10]
                                      ↑
                              Scale riêng Order!

✅ Tiết kiệm tài nguyên
✅ Chi phí tối ưu

================================================================================
SLIDE 14: LỢI ÍCH #3 - CÔ LẬP LỖI
================================================================================
# LỢI ÍCH 3: CÔ LẬP LỖI (FAULT ISOLATION)

## Comment Service bị lỗi

❌ Comment Service - DOWN
✅ Customer Service - RUNNING
✅ Book Service - RUNNING
✅ Cart Service - RUNNING
✅ Order Service - RUNNING

**→ Khách vẫn mua hàng được!**
  (Chỉ không xem được đánh giá)

================================================================================
SLIDE 15: LỢI ÍCH #4 - CÔNG NGHỆ ĐA DẠNG
================================================================================
# LỢI ÍCH 4: CÔNG NGHỆ ĐA DẠNG

Mỗi service có thể dùng công nghệ phù hợp nhất:

| Service | Ngôn ngữ | Database |
|---------|----------|----------|
| Customer | Django | PostgreSQL |
| Search | Node.js | Elasticsearch |
| AI Recommend | Python | TensorFlow |
| Cache | Go | Redis |

================================================================================
SLIDE 16: CÔNG NGHỆ SỬ DỤNG
================================================================================
# CÔNG NGHỆ TRONG PROJECT

## Backend
🐍 Django 4.2 + REST Framework
🐍 Python 3.11

## Database
🐘 PostgreSQL 15 (8 databases)

## Frontend
🎨 Bootstrap 5
🎨 Django Templates

## DevOps
🐳 Docker
🐳 Docker Compose

================================================================================
SLIDE 17: DEMO
================================================================================
# DEMO HỆ THỐNG

## URLs
- Website: http://localhost:8000
- Admin: http://localhost:8000/admin-panel/

## Tài khoản Admin
- Username: **admin**
- Password: **admin123**

## Chạy project
```bash
cd bookstore-microservice
docker-compose up --build
```

[DEMO TRỰC TIẾP]

================================================================================
SLIDE 18: KẾT LUẬN
================================================================================
# KẾT LUẬN

## BookStore Microservices
✅ 9 services độc lập
✅ 8 PostgreSQL databases
✅ REST API communication
✅ Docker containerization
✅ Beautiful UI (Bootstrap 5)

## Microservices phù hợp cho:
- Ứng dụng lớn, nhiều tính năng
- Cần scale từng phần
- Nhiều team phát triển
- Yêu cầu fault tolerance cao

================================================================================
SLIDE 19: Q&A
================================================================================

# CẢM ƠN ĐÃ LẮNG NGHE!

## HỎI ĐÁP

[Hình nền đẹp]

Contact: [email/phone]

================================================================================
