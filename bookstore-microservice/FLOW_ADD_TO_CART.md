# 🛒 FLOW HOÀN CHỈNH: THÊM SÁCH VÀO GIỎ HÀNG

## 📋 Tổng quan Flow

```
User Interface (Browser)
    ↓
API Gateway (Port 8000)
    ↓
Cart Service (Port 8003)
    ↓
Book Service (Port 8002)
    ↓
PostgreSQL Database
```

---

## 🔄 Chi tiết từng bước

### **BƯỚC 1: Frontend - User Interface**

#### 📁 File: `api-gateway/templates/customer/book_detail.html`
#### 📍 Dòng: 96-105

**Hành động:** User nhấn nút "Thêm vào giỏ"

```html
<form method="post" action="{% url 'add_to_cart' %}" class="mb-3">
    {% csrf_token %}
    <input type="hidden" name="book_id" value="{{ book.id }}">
    <div class="input-group mb-3">
        <button class="btn btn-outline-secondary" type="button" onclick="changeQty(-1)">-</button>
        <input type="number" name="quantity" id="quantity" class="form-control text-center" value="1" min="1" max="{{ book.stock }}">
        <button class="btn btn-outline-secondary" type="button" onclick="changeQty(1)">+</button>
    </div>
    <button type="submit" class="btn btn-primary w-100 mb-2">
        <i class="bi bi-cart-plus me-2"></i>Thêm vào giỏ
    </button>
</form>
```

**Request được gửi đi:**
- Method: `POST`
- URL: `http://localhost:8000/cart/add/`
- Data: 
  ```
  book_id: 1
  quantity: 1
  csrfmiddlewaretoken: <token>
  ```

---

### **BƯỚC 2: API Gateway - Router**

#### 📁 File: `api-gateway/gateway/urls.py`
#### 📍 Dòng: 27

```python
path('cart/add/', AddToCartView.as_view(), name='add_to_cart'),
```

**Routing:** Request được route đến `AddToCartView`

---

### **BƯỚC 3: API Gateway - View Handler**

#### 📁 File: `api-gateway/gateway/views.py`
#### 📍 Class: `AddToCartView` (dòng ~220-260)

```python
class AddToCartView(View):
    """Thêm vào giỏ hàng"""
    def post(self, request):
        # 1. Kiểm tra đăng nhập
        customer = request.session.get('customer')
        if not customer:
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest':
                return JsonResponse({'error': 'Vui lòng đăng nhập'}, status=401)
            messages.error(request, 'Vui lòng đăng nhập để thêm vào giỏ hàng')
            return redirect('customer_login')
        
        # 2. Chuẩn bị data
        data = {
            'book_id': request.POST.get('book_id'),
            'quantity': int(request.POST.get('quantity', 1)),
        }
        
        # 3. Gọi Cart Service qua ServiceClient
        result, status_code = ServiceClient.post('cart', f"carts/{customer['id']}/add/", data)
        
        # 4. Xử lý response
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest'
        
        if status_code == 201:
            if is_ajax:
                return JsonResponse({'success': True, 'cart': result})
            messages.success(request, 'Đã thêm sách vào giỏ hàng!')
            return redirect(request.META.get('HTTP_REFERER', 'cart'))
        
        if is_ajax:
            return JsonResponse({'error': 'Thêm vào giỏ hàng thất bại'}, status=400)
        messages.error(request, 'Thêm vào giỏ hàng thất bại')
        return redirect(request.META.get('HTTP_REFERER', 'customer_books'))
```

**Xử lý:**
1. ✅ Kiểm tra customer đã login chưa
2. ✅ Lấy `book_id` và `quantity` từ POST data
3. ✅ Gọi ServiceClient để communicate với Cart Service
4. ✅ Xử lý response và redirect

---

### **BƯỚC 4: API Gateway - Service Client**

#### 📁 File: `api-gateway/gateway/services.py`
#### 📍 Method: `ServiceClient.post()` (dòng 29-36)

```python
@classmethod
def post(cls, service, endpoint, data=None, timeout=10):
    # Tạo URL đến Cart Service
    url = f"{cls.SERVICES[service]}/api/{endpoint}"
    # url = "http://cart-service:8000/api/carts/1/add/"
    
    try:
        # Gửi POST request đến Cart Service
        response = requests.post(url, json=data, timeout=timeout)
        return response.json(), response.status_code
    except Exception as e:
        logger.error(f"Service {service} error: {e}")
        return None, 500
```

**Request gửi đến Cart Service:**
- URL: `http://cart-service:8000/api/carts/1/add/`
- Method: `POST`
- Headers: `Content-Type: application/json`
- Body:
  ```json
  {
    "book_id": 1,
    "quantity": 1
  }
  ```

---

### **BƯỚC 5: Cart Service - Router**

#### 📁 File: `cart-service/app/urls.py`
#### 📍 Dòng: 12

```python
path('carts/<int:customer_id>/add/', AddToCartView.as_view(), name='cart-add'),
```

**Routing:** Request được route đến `AddToCartView` trong Cart Service

---

### **BƯỚC 6: Cart Service - View Handler**

#### 📁 File: `cart-service/app/views.py`
#### 📍 Class: `AddToCartView` (dòng ~45-90)

```python
class AddToCartView(APIView):
    """Thêm sách vào giỏ hàng"""
    def post(self, request, customer_id):
        # 1. Validate input
        serializer = AddToCartSerializer(data=request.data)
        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        
        book_id = serializer.validated_data['book_id']
        quantity = serializer.validated_data['quantity']
        
        # 2. Get or create cart cho customer
        cart, _ = Cart.objects.get_or_create(customer_id=customer_id)
        
        # 3. Gọi Book Service để lấy thông tin sách
        try:
            book_url = getattr(settings, 'BOOK_SERVICE_URL', 'http://book-service:8000')
            response = requests.get(f"{book_url}/api/books/{book_id}/", timeout=5)
            if response.status_code != 200:
                return Response({'error': 'Không tìm thấy sách'}, status=status.HTTP_404_NOT_FOUND)
            book_data = response.json()
        except requests.RequestException as e:
            logger.error(f"Failed to get book info: {e}")
            return Response(
                {'error': 'Không thể kết nối đến book service'}, 
                status=status.HTTP_503_SERVICE_UNAVAILABLE
            )
        
        # 4. Kiểm tra stock
        if book_data.get('stock', 0) < quantity:
            return Response({'error': 'Không đủ hàng trong kho'}, status=status.HTTP_400_BAD_REQUEST)
        
        # 5. Thêm hoặc cập nhật cart item
        cart_item, created = CartItem.objects.get_or_create(
            cart=cart,
            book_id=book_id,
            defaults={
                'book_title': book_data.get('title', ''),
                'book_price': book_data.get('discount_price') or book_data.get('price'),
                'book_image': book_data.get('cover_image'),
                'quantity': quantity
            }
        )
        
        if not created:
            # Nếu item đã tồn tại, cộng thêm quantity
            cart_item.quantity += quantity
            cart_item.book_price = book_data.get('discount_price') or book_data.get('price')
            cart_item.save()
        
        # 6. Trả về cart data
        return Response(CartSerializer(cart).data, status=status.HTTP_201_CREATED)
```

**Các bước xử lý:**
1. ✅ Validate dữ liệu đầu vào với `AddToCartSerializer`
2. ✅ Lấy hoặc tạo Cart cho customer
3. ✅ Gọi Book Service để lấy thông tin sách
4. ✅ Kiểm tra số lượng tồn kho
5. ✅ Thêm hoặc cập nhật CartItem trong database
6. ✅ Serialize và trả về cart data

---

### **BƯỚC 7: Cart Service → Book Service**

#### Request gửi đến Book Service:
- URL: `http://book-service:8000/api/books/1/`
- Method: `GET`

#### 📁 File: `book-service/app/views.py`
#### 📍 Class: `BookDetailView`

```python
class BookDetailView(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response(
                {'error': 'Không tìm thấy sách'}, 
                status=status.HTTP_404_NOT_FOUND
            )
```

**Response trả về Cart Service:**
```json
{
  "id": 1,
  "title": "Python Programming",
  "price": 150000,
  "discount_price": 135000,
  "stock": 50,
  "cover_image": "http://...",
  "author_name": "Nguyễn Văn A",
  "category_name": "Lập trình",
  "publisher_name": "NXB Trẻ",
  ...
}
```

---

### **BƯỚC 8: Cart Service - Database Operations**

#### 📁 File: `cart-service/app/models.py`

**Model: Cart**
```python
class Cart(models.Model):
    customer_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**Model: CartItem**
```python
class CartItem(models.Model):
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=500)
    book_price = models.DecimalField(max_digits=10, decimal_places=2)
    book_image = models.URLField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
```

**SQL Queries được thực thi:**

1. **Get or Create Cart:**
```sql
SELECT * FROM carts WHERE customer_id = 1;
-- Nếu không tồn tại:
INSERT INTO carts (customer_id, created_at, updated_at) 
VALUES (1, NOW(), NOW());
```

2. **Get or Create CartItem:**
```sql
SELECT * FROM cart_items 
WHERE cart_id = 1 AND book_id = 1;

-- Nếu không tồn tại:
INSERT INTO cart_items 
(cart_id, book_id, book_title, book_price, book_image, quantity, created_at, updated_at)
VALUES (1, 1, 'Python Programming', 135000, 'http://...', 1, NOW(), NOW());

-- Nếu đã tồn tại:
UPDATE cart_items 
SET quantity = quantity + 1, 
    book_price = 135000,
    updated_at = NOW()
WHERE id = <cart_item_id>;
```

---

### **BƯỚC 9: Cart Service - Serializer Response**

#### 📁 File: `cart-service/app/serializers.py`

```python
class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_items = serializers.IntegerField(read_only=True)
    total_price = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)
```

**Response gửi về API Gateway:**
```json
{
  "id": 1,
  "customer_id": 1,
  "items": [
    {
      "id": 1,
      "book_id": 1,
      "book_title": "Python Programming",
      "book_price": 135000,
      "book_image": "http://...",
      "quantity": 1,
      "subtotal": 135000,
      "created_at": "2026-03-10T10:30:00Z"
    }
  ],
  "total_items": 1,
  "total_price": 135000,
  "created_at": "2026-03-10T10:30:00Z",
  "updated_at": "2026-03-10T10:30:00Z"
}
```

---

### **BƯỚC 10: API Gateway - Response Handling**

#### 📁 File: `api-gateway/gateway/views.py`
#### 📍 Class: `AddToCartView.post()` (tiếp)

```python
# Nhận response từ Cart Service
result, status_code = ServiceClient.post('cart', f"carts/{customer['id']}/add/", data)

# Xử lý response
if status_code == 201:
    messages.success(request, 'Đã thêm sách vào giỏ hàng!')
    return redirect(request.META.get('HTTP_REFERER', 'cart'))
```

**Hành động:**
1. ✅ Nhận JSON response từ Cart Service
2. ✅ Kiểm tra status code (201 = success)
3. ✅ Hiển thị success message cho user
4. ✅ Redirect về trang trước đó hoặc trang giỏ hàng

---

### **BƯỚC 11: Frontend - UI Update**

User được redirect về trang trước đó với:
- ✅ Success message: "Đã thêm sách vào giỏ hàng!"
- ✅ Cart badge cập nhật số lượng items
- ✅ Giỏ hàng đã có sản phẩm mới

---

## 📊 Sequence Diagram

```
┌──────────┐     ┌─────────────┐     ┌──────────────┐     ┌──────────────┐     ┌──────────┐
│  Browser │     │ API Gateway │     │ Cart Service │     │ Book Service │     │PostgreSQL│
└─────┬────┘     └──────┬──────┘     └──────┬───────┘     └──────┬───────┘     └────┬─────┘
      │                 │                    │                    │                  │
      │ POST /cart/add/ │                    │                    │                  │
      │────────────────>│                    │                    │                  │
      │                 │                    │                    │                  │
      │                 │ POST /carts/1/add/ │                    │                  │
      │                 │───────────────────>│                    │                  │
      │                 │                    │                    │                  │
      │                 │                    │ GET /books/1/      │                  │
      │                 │                    │───────────────────>│                  │
      │                 │                    │                    │                  │
      │                 │                    │                    │ SELECT book      │
      │                 │                    │                    │─────────────────>│
      │                 │                    │                    │<─────────────────│
      │                 │                    │                    │  book data       │
      │                 │                    │<───────────────────│                  │
      │                 │                    │  book JSON         │                  │
      │                 │                    │                    │                  │
      │                 │                    │ INSERT/UPDATE CartItem                │
      │                 │                    │──────────────────────────────────────>│
      │                 │                    │<──────────────────────────────────────│
      │                 │                    │                                       │
      │                 │<───────────────────│                                       │
      │                 │  cart JSON         │                                       │
      │<────────────────│                    │                                       │
      │  Redirect + Msg │                    │                                       │
      │                 │                    │                                       │
```

---

## 🗂️ Danh sách Files liên quan

### API Gateway:
1. `api-gateway/templates/customer/book_detail.html` - Form HTML
2. `api-gateway/gateway/urls.py` - URL routing
3. `api-gateway/gateway/views.py` - View class `AddToCartView`
4. `api-gateway/gateway/services.py` - Service client để gọi microservices

### Cart Service:
5. `cart-service/app/urls.py` - Cart API routing
6. `cart-service/app/views.py` - View class `AddToCartView`
7. `cart-service/app/models.py` - Models: `Cart`, `CartItem`
8. `cart-service/app/serializers.py` - Serializers cho Cart data

### Book Service:
9. `book-service/app/urls.py` - Book API routing
10. `book-service/app/views.py` - View class `BookDetailView`
11. `book-service/app/models.py` - Model: `Book`
12. `book-service/app/serializers.py` - Serializer cho Book data

---

## 💾 Database Tables

### Cart Service Database (cart_db):
- `carts` - Lưu giỏ hàng của từng customer
- `cart_items` - Lưu các item trong giỏ hàng

### Book Service Database (book_db):
- `books` - Lưu thông tin sách
- `categories` - Danh mục sách
- `authors` - Tác giả
- `publishers` - Nhà xuất bản

---

## ⚡ Performance & Best Practices

### 1. **Service Timeout**
- API Gateway → Cart Service: 10s timeout
- Cart Service → Book Service: 5s timeout

### 2. **Error Handling**
- ✅ Validate input với Serializers
- ✅ Try-catch cho requests giữa services
- ✅ Logging errors
- ✅ Fallback responses

### 3. **Database Optimization**
- ✅ `get_or_create()` để tránh duplicate
- ✅ Foreign key relationships
- ✅ Indexes trên `customer_id`, `book_id`

### 4. **Caching Opportunities** (Có thể cải thiện):
- Cache book info để giảm calls đến Book Service
- Cache cart count cho navbar
- Redis cho session storage

---

## 🔐 Security Considerations

1. **Authentication:**
   - ✅ Kiểm tra customer login trước khi cho phép add to cart
   - ✅ Session-based authentication

2. **CSRF Protection:**
   - ✅ CSRF token trong form POST

3. **Input Validation:**
   - ✅ Validate `book_id` và `quantity`
   - ✅ Check stock availability
   - ✅ Prevent negative quantities

4. **Service-to-Service:**
   - ⚠️ Hiện tại chưa có authentication giữa services
   - 💡 Nên thêm API keys hoặc JWT tokens

---

## 📈 Monitoring Points

1. **Metrics cần theo dõi:**
   - Response time từ API Gateway → Cart Service
   - Response time từ Cart Service → Book Service
   - Success/failure rate của add to cart
   - Database query performance

2. **Logs cần ghi:**
   - Request/Response giữa services
   - Errors và exceptions
   - Stock validation failures
   - Database operations

---

## 🎯 Kết luận

Flow "Add to Cart" là mộtví dụ điển hình của **Microservice Architecture** với:

✅ **Separation of Concerns**: Mỗi service chỉ quản lý domain của nó
✅ **Service Communication**: REST API calls giữa services
✅ **Data Consistency**: Validate và check constraints
✅ **Error Handling**: Graceful degradation khi service unavailable
✅ **Scalability**: Có thể scale từng service độc lập

**Total time:** ~200-500ms (phụ thuộc network và DB)
**Services involved:** 3 services (Gateway, Cart, Book)
**Database queries:** 3-4 queries (get cart, get book, insert/update cart_item)
