# 🗃️ REPOSITORY PATTERN TRONG DJANGO MICROSERVICES

## 📌 Tổng quan

Trong Django REST Framework, **KHÔNG có tầng Repository riêng biệt** như trong Spring Boot hoặc .NET. Thay vào đó, Django sử dụng **ORM (Object-Relational Mapping)** tích hợp sẵn với các thành phần sau:

```
┌─────────────────────────────────────────────────────┐
│              DJANGO REST FRAMEWORK                  │
├─────────────────────────────────────────────────────┤
│  views.py        →  Controller + Service Layer      │
│  models.py       →  Entity + Repository (ORM)       │
│  serializers.py  →  DTO (Data Transfer Object)      │
│  urls.py         →  Router                          │
└─────────────────────────────────────────────────────┘
```

---

## 📁 Các Files Giao Tiếp Với Database

### 1️⃣ **models.py** - Model Layer (Entity + Repository)

#### Vai trò:
- Định nghĩa **schema** của database tables
- Cung cấp **ORM methods** để truy vấn (`.objects.get()`, `.filter()`, etc.)
- Chứa **business logic** liên quan đến entity (properties, methods)

#### Ví dụ: `cart-service/app/models.py`

```python
from django.db import models

class Cart(models.Model):
    """Giỏ hàng của khách hàng"""
    customer_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    # ========== BUSINESS LOGIC ==========
    @property
    def total_items(self):
        """Tính tổng số items trong giỏ"""
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        """Tính tổng giá trị giỏ hàng"""
        return sum(item.subtotal for item in self.items.all())

class CartItem(models.Model):
    """Sản phẩm trong giỏ hàng"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=500)
    book_price = models.DecimalField(max_digits=10, decimal_places=2)
    quantity = models.IntegerField(default=1)
    
    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'book_id']
    
    @property
    def subtotal(self):
        """Tính tổng tiền của item"""
        return self.book_price * self.quantity
```

**Mapping SQL:**
```sql
CREATE TABLE carts (
    id SERIAL PRIMARY KEY,
    customer_id INTEGER UNIQUE,
    created_at TIMESTAMP,
    updated_at TIMESTAMP
);

CREATE TABLE cart_items (
    id SERIAL PRIMARY KEY,
    cart_id INTEGER REFERENCES carts(id),
    book_id INTEGER,
    book_title VARCHAR(500),
    book_price DECIMAL(10,2),
    quantity INTEGER,
    UNIQUE(cart_id, book_id)
);
```

---

### 2️⃣ **views.py** - Service Layer (Repository Caller)

#### Vai trò:
- **Business logic** của ứng dụng
- **Gọi ORM** để CRUD database (đây là nơi "repository pattern" được thực thi)
- **Orchestrate** các operations phức tạp
- **Handle transactions**

#### Ví dụ: `cart-service/app/views.py`

```python
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from .models import Cart, CartItem

class AddToCartView(APIView):
    def post(self, request, customer_id):
        # ========== REPOSITORY OPERATIONS ==========
        
        # 1. Get or Create cart (Repository pattern)
        cart, created = Cart.objects.get_or_create(customer_id=customer_id)
        # SQL: SELECT * FROM carts WHERE customer_id = 1;
        # Nếu không có: INSERT INTO carts (customer_id) VALUES (1);
        
        # 2. Get or Create cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={
                'book_title': 'Python Book',
                'book_price': 135000,
                'quantity': 1
            }
        )
        # SQL: SELECT * FROM cart_items WHERE cart_id=1 AND book_id=10;
        # Nếu không có: INSERT INTO cart_items (...) VALUES (...);
        
        # 3. Update existing item
        if not created:
            cart_item.quantity += 1
            cart_item.save()
            # SQL: UPDATE cart_items SET quantity=2 WHERE id=5;
        
        return Response({'message': 'Added to cart'})
```

#### **Các ORM Methods phổ biến** (Repository pattern methods):

| Django ORM Method | SQL Equivalent | Mô tả |
|-------------------|----------------|-------|
| `.objects.all()` | `SELECT * FROM table` | Lấy tất cả records |
| `.objects.get(id=1)` | `SELECT * FROM table WHERE id=1` | Lấy 1 record |
| `.objects.filter(name='A')` | `SELECT * FROM table WHERE name='A'` | Lọc records |
| `.objects.create(...)` | `INSERT INTO table (...) VALUES (...)` | Tạo mới |
| `.save()` | `UPDATE table SET ... WHERE id=1` | Cập nhật |
| `.delete()` | `DELETE FROM table WHERE id=1` | Xóa |
| `.get_or_create()` | `SELECT` + `INSERT` nếu không có | Get hoặc tạo mới |
| `.update_or_create()` | `SELECT` + `UPDATE` hoặc `INSERT` | Update hoặc tạo mới |
| `.count()` | `SELECT COUNT(*) FROM table` | Đếm số records |
| `.exists()` | `SELECT 1 FROM table WHERE ... LIMIT 1` | Kiểm tra tồn tại |

---

### 3️⃣ **serializers.py** - Data Transfer Layer

#### Vai trò:
- **Chuyển đổi** giữa Model instances ↔ JSON
- **Validate** input data
- **Nested serialization** cho foreign keys

#### Ví dụ: `cart-service/app/serializers.py`

```python
from rest_framework import serializers
from .models import Cart, CartItem

class CartItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'book_id', 'book_title', 'book_price', 'quantity', 'subtotal']

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)  # Nested serialization
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model = Cart
        fields = ['id', 'customer_id', 'items', 'total_items', 'total_price']
```

**Process:**
```python
# Model → JSON (Serialization)
cart = Cart.objects.get(id=1)
serializer = CartSerializer(cart)
json_data = serializer.data
# Output: {'id': 1, 'customer_id': 5, 'items': [...], 'total_price': 135000}

# JSON → Model (Deserialization)
serializer = CartSerializer(data=json_data)
if serializer.is_valid():
    cart = serializer.save()  # Gọi Cart.objects.create() hoặc cart.save()
```

---

## 🔍 So sánh với các Framework khác

### Django REST Framework (hiện tại):
```
views.py  →  Kết hợp Controller + Service + Repository caller
models.py →  Entity + ORM methods (built-in repository)
```

### Spring Boot (Java):
```
Controller.java    →  Handle HTTP requests
Service.java       →  Business logic
Repository.java    →  Database operations (JPA)
Entity.java        →  Model definition
```

### .NET Core:
```
Controller.cs      →  Handle HTTP requests
Service.cs         →  Business logic  
Repository.cs      →  Database operations (Entity Framework)
Model.cs           →  Entity definition
```

---

## 📊 Flow: Client Request → Database

```
┌─────────────┐
│   Client    │
└──────┬──────┘
       │ HTTP POST /api/carts/1/add/
       ↓
┌─────────────────────────────────────────────────────┐
│              CART SERVICE                           │
├─────────────────────────────────────────────────────┤
│                                                     │
│  1. urls.py                                        │
│     path('carts/<id>/add/', AddToCartView)         │
│                  ↓                                  │
│  2. views.py (AddToCartView)                       │
│     - Validate input với Serializer                │
│     - Business logic                               │
│     - Call ORM:                                    │
│       cart = Cart.objects.get_or_create(...)       │
│       item = CartItem.objects.create(...)          │
│                  ↓                                  │
│  3. models.py (Django ORM)                         │
│     - Django ORM tự động generate SQL              │
│     - Execute SQL queries                          │
│                  ↓                                  │
│  4. PostgreSQL Database                            │
│     - INSERT/UPDATE/SELECT operations              │
│                  ↓                                  │
│  5. serializers.py                                 │
│     - Convert model instance → JSON                │
│                  ↓                                  │
│  6. Response                                       │
│     - Return JSON to client                        │
│                                                     │
└─────────────────────────────────────────────────────┘
```

---

## 📁 File Structure Trong Mỗi Service

### Cart Service:
```
cart-service/
├── app/
│   ├── models.py           ⭐ Entity + ORM (Repository)
│   ├── views.py            ⭐ Service Layer (Repository Caller)
│   ├── serializers.py      ⭐ DTO Layer
│   ├── urls.py             📌 Router
│   ├── admin.py            📌 Admin interface
│   └── migrations/         📌 Database schema versions
```

### Book Service:
```
book-service/
├── app/
│   ├── models.py           ⭐ Book, Category, Author, Publisher models
│   ├── views.py            ⭐ BookListView, BookDetailView, etc.
│   ├── serializers.py      ⭐ BookSerializer, CategorySerializer
│   └── urls.py             📌 API endpoints
```

### Customer Service:
```
customer-service/
├── app/
│   ├── models.py           ⭐ Customer, CustomerProfile models
│   ├── views.py            ⭐ Registration, Login, Update views
│   ├── serializers.py      ⭐ CustomerSerializer, LoginSerializer
│   └── urls.py             📌 Customer API routes
```

---

## 🎯 Ví dụ Cụ thể: Các Database Operations

### **1. CREATE (Insert)**

```python
# File: cart-service/app/views.py

# Cách 1: Dùng .create()
cart = Cart.objects.create(
    customer_id=1
)
# SQL: INSERT INTO carts (customer_id) VALUES (1);

# Cách 2: Dùng model instance + .save()
cart = Cart(customer_id=1)
cart.save()
# SQL: INSERT INTO carts (customer_id) VALUES (1);
```

### **2. READ (Select)**

```python
# File: book-service/app/views.py

# Lấy 1 record
book = Book.objects.get(id=1)
# SQL: SELECT * FROM books WHERE id = 1;

# Lấy nhiều records
books = Book.objects.filter(category_id=5)
# SQL: SELECT * FROM books WHERE category_id = 5;

# Lấy tất cả
all_books = Book.objects.all()
# SQL: SELECT * FROM books;

# Với join (foreign key)
books = Book.objects.select_related('category', 'author').all()
# SQL: SELECT * FROM books 
#      LEFT JOIN categories ON books.category_id = categories.id
#      LEFT JOIN authors ON books.author_id = authors.id;
```

### **3. UPDATE**

```python
# File: cart-service/app/views.py

# Cách 1: Get + Save
cart_item = CartItem.objects.get(id=1)
cart_item.quantity = 5
cart_item.save()
# SQL: UPDATE cart_items SET quantity = 5 WHERE id = 1;

# Cách 2: Bulk update
CartItem.objects.filter(cart_id=1).update(quantity=0)
# SQL: UPDATE cart_items SET quantity = 0 WHERE cart_id = 1;
```

### **4. DELETE**

```python
# File: cart-service/app/views.py

# Delete 1 record
cart_item = CartItem.objects.get(id=1)
cart_item.delete()
# SQL: DELETE FROM cart_items WHERE id = 1;

# Delete nhiều records
CartItem.objects.filter(cart_id=1).delete()
# SQL: DELETE FROM cart_items WHERE cart_id = 1;
```

### **5. COMPLEX QUERIES**

```python
# File: book-service/app/views.py

from django.db.models import Q, Count, Avg

# OR condition
books = Book.objects.filter(
    Q(category_id=1) | Q(category_id=2)
)
# SQL: SELECT * FROM books WHERE category_id = 1 OR category_id = 2;

# Aggregate
avg_price = Book.objects.aggregate(Avg('price'))
# SQL: SELECT AVG(price) FROM books;

# Group by + Count
category_counts = Book.objects.values('category_id').annotate(
    total=Count('id')
)
# SQL: SELECT category_id, COUNT(id) as total 
#      FROM books GROUP BY category_id;
```

---

## 🔧 Django Model Manager (Built-in Repository)

Django cung cấp **Model Manager** (`.objects`) như một built-in repository:

```python
# Default manager
Cart.objects.all()  # Lấy tất cả carts

# Custom manager
class ActiveBookManager(models.Manager):
    def get_queryset(self):
        return super().get_queryset().filter(is_active=True, stock__gt=0)

class Book(models.Model):
    # ... fields ...
    
    objects = models.Manager()  # Default manager
    active = ActiveBookManager()  # Custom manager

# Usage
all_books = Book.objects.all()       # Tất cả sách
available_books = Book.active.all()  # Chỉ sách còn hàng
```

---

## 💡 Best Practices

### 1. **Tách Business Logic ra khỏi Views (Optional)**

Nếu muốn có tầng Service riêng:

```python
# File: cart-service/app/services.py
class CartService:
    @staticmethod
    def add_to_cart(customer_id, book_id, quantity):
        """Business logic for adding to cart"""
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={'quantity': quantity}
        )
        if not created:
            cart_item.quantity += quantity
            cart_item.save()
        return cart

# File: cart-service/app/views.py
from .services import CartService

class AddToCartView(APIView):
    def post(self, request, customer_id):
        book_id = request.data.get('book_id')
        quantity = request.data.get('quantity', 1)
        
        cart = CartService.add_to_cart(customer_id, book_id, quantity)
        
        return Response(CartSerializer(cart).data)
```

### 2. **Sử dụng Transactions**

```python
from django.db import transaction

@transaction.atomic
def create_order(customer_id):
    """Đảm bảo atomic operations"""
    cart = Cart.objects.get(customer_id=customer_id)
    order = Order.objects.create(customer_id=customer_id)
    
    for item in cart.items.all():
        OrderItem.objects.create(
            order=order,
            book_id=item.book_id,
            quantity=item.quantity
        )
    
    cart.items.all().delete()  # Clear cart
    return order
```

### 3. **Optimize Queries (N+1 Problem)**

```python
# ❌ BAD: N+1 queries
carts = Cart.objects.all()
for cart in carts:
    print(cart.items.all())  # Query mới cho mỗi cart!

# ✅ GOOD: Prefetch related
carts = Cart.objects.prefetch_related('items').all()
for cart in carts:
    print(cart.items.all())  # Không query thêm
```

---

## 📚 Tóm tắt

| Component | File | Vai trò | SQL Equivalent |
|-----------|------|---------|----------------|
| **Entity** | `models.py` | Define tables & relationships | `CREATE TABLE` |
| **Repository** | `models.py` (ORM) | Database operations | `SELECT/INSERT/UPDATE/DELETE` |
| **Service** | `views.py` | Business logic | Application logic |
| **DTO** | `serializers.py` | Data transformation | JSON ↔ Objects |
| **Router** | `urls.py` | API endpoints | Route mapping |

**Kết luận:**
- Trong Django, **views.py** đóng vai trò gọi repository (ORM)
- **models.py** định nghĩa entities VÀ cung cấp ORM methods
- **Django ORM** chính là built-in Repository pattern
- Không cần tạo Repository classes riêng như Spring Boot!
