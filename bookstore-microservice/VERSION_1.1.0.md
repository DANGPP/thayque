# Bookstore Microservices - Version 1.1.0

## 🚀 Nâng cấp lớn: Tách models thành các bảng riêng biệt

**Release Date**: March 10, 2026
**Tag**: v1.1.0

---

## 📋 Tổng quan thay đổi

Version 1.1.0 là bản nâng cấp kiến trúc lớn, tách các thông tin customer từ 1 bảng thành 4 bảng riêng biệt để dễ quản lý và mở rộng.

### Kiến trúc cũ (v1.0.0):
```
Customer
├── fullname (CharField)
├── job (CharField)
├── address (TextField)
└── ... other fields
```

### Kiến trúc mới (v1.1.0):
```
Customer (base info)
├── PersonalInfo (1-to-1)
│   ├── fullname
│   ├── nickname
│   └── gender
├── JobInfo (1-to-1)
│   ├── job_title
│   ├── company
│   ├── industry
│   └── years_of_experience
└── AddressInfo (1-to-1)
    ├── street_address
    ├── ward
    ├── district
    ├── city
    ├── country
    └── postal_code
```

---

## ✨ Tính năng mới

### 1. **PersonalInfo Model** 
Quản lý thông tin cá nhân chi tiết

**Fields:**
- `fullname` - Họ tên đầy đủ (required)
- `nickname` - Biệt danh (optional)
- `gender` - Giới tính (male/female/other)
- `created_at`, `updated_at` - Timestamps

**Database Table:** `personal_info`

### 2. **JobInfo Model**
Quản lý thông tin nghề nghiệp

**Fields:**
- `job_title` - Chức vụ/Nghề nghiệp (required)
- `company` - Tên công ty (optional)
- `industry` - Ngành nghề (optional)
- `years_of_experience` - Số năm kinh nghiệm (optional)
- `created_at`, `updated_at` - Timestamps

**Database Table:** `job_info`

### 3. **AddressInfo Model**
Quản lý thông tin địa chỉ chi tiết

**Fields:**
- `street_address` - Địa chỉ cụ thể (required)
- `ward` - Phường/Xã (optional)
- `district` - Quận/Huyện (optional)
- `city` - Tỉnh/Thành phố (optional)
- `country` - Quốc gia (default: Vietnam)
- `postal_code` - Mã bưu chính (optional)
- `is_default` - Địa chỉ mặc định (boolean)
- `full_address` - Property trả về địa chỉ đầy đủ
- `created_at`, `updated_at` - Timestamps

**Database Table:** `address_info`

---

## 🔧 API Changes

### Customer Serializer Response
```json
{
  "id": 1,
  "username": "johndoe",
  "email": "john@example.com",
  "phone": "0123456789",
  "personal_info": {
    "fullname": "Nguyễn Văn A",
    "nickname": "An",
    "gender": "male"
  },
  "job_info": {
    "job_title": "Software Engineer",
    "company": "Tech Corp",
    "industry": "Information Technology",
    "years_of_experience": 5
  },
  "address_info": {
    "street_address": "123 ABC Street",
    "ward": "Phường 1",
    "district": "Quận 1",
    "city": "TP. Hồ Chí Minh",
    "country": "Vietnam",
    "full_address": "123 ABC Street, Phường 1, Quận 1, TP. Hồ Chí Minh"
  },
  "profile": {
    "loyalty_points": 100,
    "total_orders": 5,
    "total_spent": 1500000
  }
}
```

### Update Customer API
**Endpoint**: `PUT /api/customers/<id>/update/`

**Request Body**:
```json
{
  "phone": "0987654321",
  "email": "newemail@example.com",
  "personal_info": {
    "fullname": "Nguyễn Văn B",
    "nickname": "Bình",
    "gender": "male"
  },
  "job_info": {
    "job_title": "Senior Developer",
    "company": "New Company",
    "industry": "IT"
  },
  "address_info": {
    "street_address": "456 XYZ Road",
    "ward": "Phường 2",
    "district": "Quận 2",
    "city": "Hà Nội"
  }
}
```

### Registration API
**Endpoint**: `POST /api/register/`

**Request Body**:
```json
{
  "username": "newuser",
  "email": "user@example.com",
  "password": "password123",
  "password_confirm": "password123",
  "phone": "0123456789",
  "fullname": "Nguyễn Văn C",
  "job_title": "Developer",
  "street_address": "789 Street"
}
```

---

## 🎨 UI Updates

### Profile Page (`/profile/`)

Trang profile được chia thành 4 sections rõ ràng:

1. **Thông tin cá nhân** (Personal Info) - màu primary
   - Họ tên đầy đủ
   - Biệt danh
   - Giới tính
   - Ngày sinh

2. **Thông tin nghề nghiệp** (Job Info) - màu success
   - Chức vụ/Nghề nghiệp
   - Công ty
   - Ngành nghề

3. **Thông tin địa chỉ** (Address Info) - màu info
   - Địa chỉ cụ thể
   - Phường/Xã
   - Quận/Huyện
   - Tỉnh/Thành phố

4. **Thông tin liên hệ** (Contact Info) - màu warning
   - Họ, Tên
   - Email
   - Số điện thoại

### Registration Page
Form đăng ký được cập nhật với trường `job_title` và `street_address` thay vì `job` và `address`.

---

## 🗄️ Database Changes

### New Tables Created:
1. `personal_info` - OneToOne with customers
2. `job_info` - OneToOne with customers
3. `address_info` - OneToOne with customers

### Migration Strategy:
- Clean database required (hoặc manual migration từ v1.0.0)
- Auto-created when running `python manage.py migrate`

---

## 📊 Admin Interface Updates

Django Admin được nâng cấp với:

### Customer Admin
- Inline editing cho PersonalInfo, JobInfo, AddressInfo
- Xem và chỉnh sửa tất cả thông tin liên quan trong 1 trang

### Separate Admin Views
- **PersonalInfo Admin**: Filter theo gender
- **JobInfo Admin**: Filter theo industry
- **AddressInfo Admin**: Filter theo city, is_default

---

## 🔄 Migration từ v1.0.0

### Option 1: Clean Install (Recommended)
```bash
docker compose down -v
TAG=v1.1.0 docker compose up -d
```

### Option 2: Data Migration (Manual)
Cần viết migration script để chuyển data từ:
- `customer.fullname` → `personal_info.fullname`
- `customer.job` → `job_info.job_title`
- `customer.address` → `address_info.street_address`

---

## 🚀 Deployment

### Build và Deploy với tag v1.1.0

**Windows (PowerShell):**
```powershell
.\build-and-run.ps1 v1.1.0
# hoặc
$env:TAG="v1.1.0"; docker compose up --build -d
```

**Linux/Mac:**
```bash
./build-and-run.sh v1.1.0
# hoặc
TAG=v1.1.0 docker compose up --build -d
```

### Verify Deployment
```bash
# Check images
docker images | grep "bookstore.*v1.1.0"

# Check containers
docker ps

# Check database tables
docker exec -it bookstore-postgres psql -U postgres -d customer_db -c "\dt"

# Test API
curl http://localhost:8001/api/health/
```

---

## 📝 Files Changed

### Customer Service
- `app/models.py` - Thêm PersonalInfo, JobInfo, AddressInfo models; xóa fullname, job, address từ Customer
- `app/serializers.py` - Thêm nested serializers cho 3 models mới
- `app/views.py` - Update imports
- `app/admin.py` - Thêm admin classes và inlines
- `app/migrations/0001_initial.py` - Auto-generated với tất cả models

### API Gateway
- `gateway/views.py` - Update CustomerProfileView để handle nested data
- `templates/customer/profile.html` - UI mới với 4 sections
- `templates/customer/register.html` - Update form fields

### Docker
- All services tagged as `v1.1.0`

---

## ⚠️ Breaking Changes

1. **API Response Structure**: Customer API giờ trả về nested objects thay vì flat structure
2. **Update Endpoint**: Yêu cầu nested data structure
3. **Registration**: Field names thay đổi từ `job` → `job_title`, `address` → `street_address`

---

## 🎯 Benefits

1. **Better Organization**: Dữ liệu được tổ chức theo nhóm logic
2. **Easier Maintenance**: Mỗi model có trách nhiệm rõ ràng
3. **Flexible Extension**: Dễ dàng thêm fields mới vào từng model
4. **Better Validation**: Validation rules riêng cho từng loại thông tin
5. **Improved Admin**: Quản lý dễ dàng hơn với inline editing

---

## 📈 Future Enhancements

1. Support multiple addresses per customer
2. Address history tracking
3. Job history timeline
4. Personal info verification system
5. Address validation with real postal services

---

## 🐛 Known Issues

None reported.

---

## 👥 Credits

Developed by: B22DCCN206
Version: 1.1.0
Date: March 10, 2026
