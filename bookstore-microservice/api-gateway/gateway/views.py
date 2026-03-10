from django.shortcuts import render, redirect
from django.http import JsonResponse
from django.views import View
from django.contrib import messages
import json

from .services import ServiceClient


# ==================== CUSTOMER VIEWS ====================

class HomeView(View):
    """Trang chủ"""
    def get(self, request):
        books = ServiceClient.get('book', 'books/', {'featured': 'true'}) or []
        categories = ServiceClient.get('book', 'categories/') or []
        
        context = {
            'featured_books': books[:8],
            'categories': categories,
            'customer': request.session.get('customer'),
        }
        return render(request, 'customer/home.html', context)


class BookListView(View):
    """Danh sách sách"""
    def get(self, request):
        params = {
            'search': request.GET.get('search', ''),
            'category': request.GET.get('category', ''),
            'sort': request.GET.get('sort', '-created_at'),
        }
        books = ServiceClient.get('book', 'books/', params) or []
        categories = ServiceClient.get('book', 'categories/') or []
        
        context = {
            'books': books,
            'categories': categories,
            'params': params,
            'customer': request.session.get('customer'),
        }
        return render(request, 'customer/books.html', context)


class BookDetailView(View):
    """Chi tiết sách"""
    def get(self, request, pk):
        book = ServiceClient.get('book', f'books/{pk}/')
        if not book:
            messages.error(request, 'Không tìm thấy sách')
            return redirect('home')
        
        reviews = ServiceClient.get('comment', f'reviews/?book_id={pk}') or []
        rating_summary = ServiceClient.get('comment', f'books/{pk}/rating/') or {}
        
        context = {
            'book': book,
            'reviews': reviews,
            'rating_summary': rating_summary,
            'customer': request.session.get('customer'),
        }
        return render(request, 'customer/book_detail.html', context)


class CustomerRegisterView(View):
    """Đăng ký khách hàng"""
    def get(self, request):
        return render(request, 'customer/register.html')
    
    def post(self, request):
        data = {
            'username': request.POST.get('username'),
            'email': request.POST.get('email'),
            'password': request.POST.get('password'),
            'password_confirm': request.POST.get('password_confirm'),
            'first_name': request.POST.get('first_name'),
            'last_name': request.POST.get('last_name'),
            'phone': request.POST.get('phone'),
        }
        
        result, status_code = ServiceClient.post('customer', 'register/', data)
        
        if status_code == 201:
            messages.success(request, 'Đăng ký thành công! Vui lòng đăng nhập.')
            return redirect('customer_login')
        else:
            messages.error(request, result.get('error', 'Đăng ký thất bại'))
            return render(request, 'customer/register.html', {'data': data})


class CustomerLoginView(View):
    """Đăng nhập khách hàng"""
    def get(self, request):
        return render(request, 'customer/login.html')
    
    def post(self, request):
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }
        
        result, status_code = ServiceClient.post('customer', 'login/', data)
        
        if status_code == 200 and result.get('customer'):
            request.session['customer'] = result['customer']
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('home')
        else:
            messages.error(request, 'Tên đăng nhập hoặc mật khẩu không đúng')
            return render(request, 'customer/login.html')


class CustomerLogoutView(View):
    """Đăng xuất"""
    def get(self, request):
        request.session.flush()
        messages.success(request, 'Đã đăng xuất')
        return redirect('home')


class CustomerProfileView(View):
    """Xem và cập nhật profile khách hàng"""
    def get(self, request):
        customer = request.session.get('customer')
        if not customer:
            messages.warning(request, 'Vui lòng đăng nhập')
            return redirect('customer_login')
        
        # Lấy thông tin customer chi tiết
        customer_detail = ServiceClient.get('customer', f"customers/{customer['id']}/")
        if customer_detail:
            request.session['customer'] = customer_detail
            customer = customer_detail
        
        context = {
            'customer': customer,
        }
        return render(request, 'customer/profile.html', context)
    
    def post(self, request):
        customer = request.session.get('customer')
        if not customer:
            return redirect('customer_login')
        
        # Prepare nested data structure for new API
        data = {
            'phone': request.POST.get('phone', ''),
            'email': request.POST.get('email', ''),
            'first_name': request.POST.get('first_name', ''),
            'last_name': request.POST.get('last_name', ''),
            'date_of_birth': request.POST.get('date_of_birth', ''),
        }
        
        # Personal info
        personal_info = {}
        if request.POST.get('fullname'):
            personal_info['fullname'] = request.POST.get('fullname')
        if request.POST.get('nickname'):
            personal_info['nickname'] = request.POST.get('nickname')
        if request.POST.get('gender'):
            personal_info['gender'] = request.POST.get('gender')
        if personal_info:
            data['personal_info'] = personal_info
        
        # Job info
        job_info = {}
        if request.POST.get('job_title'):
            job_info['job_title'] = request.POST.get('job_title')
        if request.POST.get('company'):
            job_info['company'] = request.POST.get('company')
        if request.POST.get('industry'):
            job_info['industry'] = request.POST.get('industry')
        if job_info:
            data['job_info'] = job_info
        
        # Address info
        address_info = {}
        if request.POST.get('street_address'):
            address_info['street_address'] = request.POST.get('street_address')
        if request.POST.get('ward'):
            address_info['ward'] = request.POST.get('ward')
        if request.POST.get('district'):
            address_info['district'] = request.POST.get('district')
        if request.POST.get('city'):
            address_info['city'] = request.POST.get('city')
        if address_info:
            data['address_info'] = address_info
        
        result, status_code = ServiceClient.put('customer', f"customers/{customer['id']}/update/", data)
        
        if status_code == 200:
            # Cập nhật session
            request.session['customer'] = result.get('customer', customer)
            messages.success(request, 'Cập nhật thông tin thành công!')
        else:
            messages.error(request, result.get('error', 'Cập nhật thất bại'))
        
        return redirect('customer_profile')


class CartView(View):
    """Xem giỏ hàng"""
    def get(self, request):
        customer = request.session.get('customer')
        if not customer:
            messages.warning(request, 'Vui lòng đăng nhập')
            return redirect('customer_login')
        
        cart = ServiceClient.get('cart', f"carts/{customer['id']}/") or {'items': []}
        
        context = {
            'cart': cart,
            'customer': customer,
        }
        return render(request, 'customer/cart.html', context)


class AddToCartView(View):
    """Thêm vào giỏ hàng"""
    def post(self, request):
        customer = request.session.get('customer')
        if not customer:
            # Kiểm tra AJAX request
            if request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json':
                return JsonResponse({'error': 'Vui lòng đăng nhập'}, status=401)
            messages.error(request, 'Vui lòng đăng nhập để thêm vào giỏ hàng')
            return redirect('customer_login')
        
        data = {
            'book_id': request.POST.get('book_id'),
            'quantity': int(request.POST.get('quantity', 1)),
        }
        
        result, status_code = ServiceClient.post('cart', f"carts/{customer['id']}/add/", data)
        
        # Kiểm tra AJAX request
        is_ajax = request.headers.get('X-Requested-With') == 'XMLHttpRequest' or request.content_type == 'application/json'
        
        if status_code == 201:
            if is_ajax:
                return JsonResponse({'success': True, 'cart': result})
            messages.success(request, 'Đã thêm sách vào giỏ hàng!')
            # Redirect về trang trước đó hoặc trang giỏ hàng
            return redirect(request.META.get('HTTP_REFERER', 'cart'))
        
        if is_ajax:
            return JsonResponse({'error': 'Thêm vào giỏ hàng thất bại'}, status=400)
        messages.error(request, 'Thêm vào giỏ hàng thất bại')
        return redirect(request.META.get('HTTP_REFERER', 'customer_books'))


class UpdateCartView(View):
    """Cập nhật giỏ hàng"""
    def post(self, request, item_id):
        customer = request.session.get('customer')
        if not customer:
            return JsonResponse({'error': 'Vui lòng đăng nhập'}, status=401)
        
        data = {'quantity': int(request.POST.get('quantity', 1))}
        result, status_code = ServiceClient.put('cart', f"carts/{customer['id']}/items/{item_id}/", data)
        
        if status_code == 200:
            return JsonResponse({'success': True, 'cart': result})
        return JsonResponse({'error': 'Cập nhật thất bại'}, status=400)


class RemoveCartItemView(View):
    """Xóa sản phẩm khỏi giỏ"""
    def post(self, request, item_id):
        customer = request.session.get('customer')
        if not customer:
            return JsonResponse({'error': 'Vui lòng đăng nhập'}, status=401)
        
        success = ServiceClient.delete('cart', f"carts/{customer['id']}/items/{item_id}/remove/")
        
        if success:
            return JsonResponse({'success': True})
        return JsonResponse({'error': 'Xóa thất bại'}, status=400)


class CheckoutView(View):
    """Thanh toán"""
    def get(self, request):
        customer = request.session.get('customer')
        if not customer:
            messages.warning(request, 'Vui lòng đăng nhập')
            return redirect('customer_login')
        
        cart = ServiceClient.get('cart', f"carts/{customer['id']}/") or {'items': []}
        
        if not cart.get('items'):
            messages.warning(request, 'Giỏ hàng trống')
            return redirect('cart')
        
        context = {
            'cart': cart,
            'customer': customer,
        }
        return render(request, 'customer/checkout.html', context)
    
    def post(self, request):
        customer = request.session.get('customer')
        if not customer:
            return redirect('customer_login')
        
        data = {
            'customer_id': customer['id'],
            'customer_name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer['username'],
            'customer_email': customer['email'],
            'customer_phone': request.POST.get('phone'),
            'shipping_address': request.POST.get('address'),
            'shipping_method': request.POST.get('shipping_method', 'standard'),
            'payment_method': request.POST.get('payment_method', 'cod'),
            'notes': request.POST.get('notes', ''),
        }
        
        result, status_code = ServiceClient.post('order', 'orders/create/', data)
        
        if status_code == 201:
            messages.success(request, f"Đặt hàng thành công! Mã đơn: {result['order_number']}")
            return redirect('order_detail', order_number=result['order_number'])
        else:
            messages.error(request, result.get('error', 'Đặt hàng thất bại'))
            return redirect('checkout')


class OrderHistoryView(View):
    """Lịch sử đơn hàng"""
    def get(self, request):
        customer = request.session.get('customer')
        if not customer:
            return redirect('customer_login')
        
        orders = ServiceClient.get('order', f"orders/?customer_id={customer['id']}") or []
        
        context = {
            'orders': orders,
            'customer': customer,
        }
        return render(request, 'customer/orders.html', context)


class OrderDetailView(View):
    """Chi tiết đơn hàng"""
    def get(self, request, order_number):
        customer = request.session.get('customer')
        order = ServiceClient.get('order', f'orders/number/{order_number}/')
        
        if not order:
            messages.error(request, 'Không tìm thấy đơn hàng')
            return redirect('order_history')
        
        context = {
            'order': order,
            'customer': customer,
        }
        return render(request, 'customer/order_detail.html', context)


class WriteReviewView(View):
    """Viết đánh giá"""
    def post(self, request, book_id):
        customer = request.session.get('customer')
        if not customer:
            return JsonResponse({'error': 'Vui lòng đăng nhập'}, status=401)
        
        data = {
            'book_id': book_id,
            'customer_id': customer['id'],
            'customer_name': f"{customer.get('first_name', '')} {customer.get('last_name', '')}".strip() or customer['username'],
            'rating': int(request.POST.get('rating')),
            'title': request.POST.get('title', ''),
            'comment': request.POST.get('comment'),
        }
        
        result, status_code = ServiceClient.post('comment', 'reviews/create/', data)
        
        if status_code == 201:
            messages.success(request, 'Đánh giá thành công!')
        else:
            messages.error(request, result.get('error', 'Đánh giá thất bại'))
        
        return redirect('book_detail', pk=book_id)


# ==================== ADMIN VIEWS ====================

class AdminLoginView(View):
    """Đăng nhập admin"""
    def get(self, request):
        return render(request, 'admin/login.html')
    
    def post(self, request):
        data = {
            'username': request.POST.get('username'),
            'password': request.POST.get('password'),
        }
        
        result, status_code = ServiceClient.post('staff', 'login/', data)
        
        if status_code == 200 and result.get('staff'):
            request.session['staff'] = result['staff']
            messages.success(request, 'Đăng nhập thành công!')
            return redirect('admin_dashboard')
        else:
            messages.error(request, 'Đăng nhập thất bại')
            return render(request, 'admin/login.html')


class AdminLogoutView(View):
    """Đăng xuất admin"""
    def get(self, request):
        if 'staff' in request.session:
            del request.session['staff']
        messages.success(request, 'Đã đăng xuất')
        return redirect('admin_login')


class AdminDashboardView(View):
    """Dashboard admin"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        # Get stats
        books = ServiceClient.get('book', 'books/') or []
        orders = ServiceClient.get('order', 'orders/') or []
        customers = ServiceClient.get('customer', 'customers/') or []
        
        pending_orders = [o for o in orders if o.get('status') == 'pending']
        
        context = {
            'staff': staff,
            'total_books': len(books),
            'total_orders': len(orders),
            'total_customers': len(customers),
            'pending_orders': len(pending_orders),
            'recent_orders': orders[:5],
        }
        return render(request, 'admin/dashboard.html', context)


class AdminBooksView(View):
    """Quản lý sách"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        books = ServiceClient.get('book', 'books/') or []
        categories = ServiceClient.get('book', 'categories/') or []
        authors = ServiceClient.get('book', 'authors/') or []
        
        context = {
            'staff': staff,
            'books': books,
            'categories': categories,
            'authors': authors,
        }
        return render(request, 'admin/books.html', context)


class AdminBookCreateView(View):
    """Thêm sách"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        categories = ServiceClient.get('book', 'categories/') or []
        authors = ServiceClient.get('book', 'authors/') or []
        publishers = ServiceClient.get('book', 'publishers/') or []
        
        context = {
            'staff': staff,
            'categories': categories,
            'authors': authors,
            'publishers': publishers,
        }
        return render(request, 'admin/book_form.html', context)
    
    def post(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        data = {
            'title': request.POST.get('title'),
            'slug': request.POST.get('slug'),
            'isbn': request.POST.get('isbn'),
            'description': request.POST.get('description'),
            'price': request.POST.get('price'),
            'discount_price': request.POST.get('discount_price') or None,
            'stock': request.POST.get('stock'),
            'category': request.POST.get('category') or None,
            'author': request.POST.get('author') or None,
            'publisher': request.POST.get('publisher') or None,
            'cover_image': request.POST.get('cover_image'),
            'is_active': bool(request.POST.get('is_active')),
            'is_featured': bool(request.POST.get('is_featured')),
        }
        
        result, status_code = ServiceClient.post('book', 'books/', data)
        
        if status_code == 201:
            messages.success(request, 'Thêm sách thành công!')
            return redirect('admin_books')
        else:
            messages.error(request, 'Thêm sách thất bại')
            return redirect('admin_book_create')


class AdminOrdersView(View):
    """Quản lý đơn hàng"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        status_filter = request.GET.get('status', '')
        orders = ServiceClient.get('order', f'orders/?status={status_filter}') or []
        
        context = {
            'staff': staff,
            'orders': orders,
            'status_filter': status_filter,
        }
        return render(request, 'admin/orders.html', context)


class AdminOrderDetailView(View):
    """Chi tiết đơn hàng admin"""
    def get(self, request, pk):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        order = ServiceClient.get('order', f'orders/{pk}/')
        
        if not order:
            messages.error(request, 'Không tìm thấy đơn hàng')
            return redirect('admin_orders')
        
        context = {
            'staff': staff,
            'order': order,
        }
        return render(request, 'admin/order_detail.html', context)
    
    def post(self, request, pk):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        new_status = request.POST.get('status')
        data = {
            'status': new_status,
            'note': request.POST.get('note', ''),
            'created_by': staff['username'],
        }
        
        result, status_code = ServiceClient.put('order', f'orders/{pk}/status/', data)
        
        if status_code == 200:
            messages.success(request, 'Cập nhật trạng thái thành công!')
        else:
            messages.error(request, 'Cập nhật thất bại')
        
        return redirect('admin_order_detail', pk=pk)


class AdminCustomersView(View):
    """Quản lý khách hàng"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        customers = ServiceClient.get('customer', 'customers/') or []
        
        context = {
            'staff': staff,
            'customers': customers,
        }
        return render(request, 'admin/customers.html', context)


class AdminCategoriesView(View):
    """Quản lý danh mục"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        categories = ServiceClient.get('book', 'categories/') or []
        authors = ServiceClient.get('book', 'authors/') or []
        publishers = ServiceClient.get('book', 'publishers/') or []
        
        context = {
            'staff': staff,
            'categories': categories,
            'authors': authors,
            'publishers': publishers,
        }
        return render(request, 'admin/categories.html', context)
    
    def post(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        data = {
            'name': request.POST.get('name'),
            'slug': request.POST.get('slug'),
            'description': request.POST.get('description'),
        }
        
        result, status_code = ServiceClient.post('book', 'categories/', data)
        
        if status_code == 201:
            messages.success(request, 'Thêm danh mục thành công!')
        else:
            messages.error(request, 'Thêm danh mục thất bại')
        
        return redirect('admin_categories')


class AdminReviewsView(View):
    """Quản lý đánh giá"""
    def get(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        reviews = ServiceClient.get('comment', 'reviews/') or []
        
        context = {
            'staff': staff,
            'reviews': reviews,
        }
        return render(request, 'admin/reviews.html', context)


class AdminAddAuthorView(View):
    """Thêm tác giả"""
    def post(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        data = {
            'name': request.POST.get('name'),
            'bio': request.POST.get('bio', ''),
        }
        
        result, status_code = ServiceClient.post('book', 'authors/', data)
        
        if status_code == 201:
            messages.success(request, 'Thêm tác giả thành công!')
        else:
            messages.error(request, 'Thêm tác giả thất bại')
        
        return redirect('admin_categories')


class AdminAddPublisherView(View):
    """Thêm nhà xuất bản"""
    def post(self, request):
        staff = request.session.get('staff')
        if not staff:
            return redirect('admin_login')
        
        data = {
            'name': request.POST.get('name'),
        }
        
        result, status_code = ServiceClient.post('book', 'publishers/', data)
        
        if status_code == 201:
            messages.success(request, 'Thêm NXB thành công!')
        else:
            messages.error(request, 'Thêm NXB thất bại')
        
        return redirect('admin_categories')


# ==================== API PROXY ====================

class APIProxyView(View):
    """API proxy cho frontend"""
    def get(self, request, service, path):
        result = ServiceClient.get(service, path, dict(request.GET))
        if result:
            return JsonResponse(result, safe=False)
        return JsonResponse({'error': 'Service unavailable'}, status=503)
    
    def post(self, request, service, path):
        data = json.loads(request.body) if request.body else {}
        result, status_code = ServiceClient.post(service, path, data)
        return JsonResponse(result or {'error': 'Failed'}, status=status_code)
