4.1 Objective
Students must decompose a monolithic BookStore into microservices using Django REST
Framework.
4.2 Required Services
1. staff-service
2. manager-service
3. customer-service
4. catalog-service
5. book-service
6. cart-service
7. order-service
8. ship-service
9. pay-service
10. comment-rate-service
11. recommender-ai-service
12. api-gateway
4.3 Functional Requirements
1. Customer registration automatically creates a cart.
2. Staff manages books.
3. Customer adds books to cart, view cart, update cart.
4. Order triggers payment and shipping, customer select pay, ship.
5. Customer can rate books.
4.4 Technical Requirements
ˆ
ˆ
ˆ
ˆ
Django REST Framework
REST inter-service calls
Docker Compose
Independent databases
5
4.5 Deliverables
1. GitHub repository
2. Architecture diagram for each service
3. API documentation
4. 10-minute demo video
5. 8–12 page technical report
5 ASSIGNMENT 06–Industry-LevelMicroservices
This assignment upgrades Assignment 05 to production-level architecture.
1. JWT Authentication Service
ˆ
ˆ
ˆ
Central auth-service
Role-based access control
Token validation at API Gateway
2. Saga Pattern for Distributed Transactions
Order creation must use Saga orchestration:
1. Create order (Pending)
2. Reserve payment
3. Reserve shipping
4. Confirm order
5. Compensate if failure
3. Event Bus Integration
Replace direct REST coupling with asynchronous messaging.
Suggested tools:
ˆ
ˆ
RabbitMQ
Kafka
4. API Gateway Responsibilities
ˆ
ˆ
ˆ
ˆ
Routing
Authentication validation
Logging
Rate limiting
6
5. Observability
ˆ
ˆ
ˆ
Centralized logging
Health endpoints
Metrics endpoint
Advanced Deliverables
1. Implement Saga pattern
2. Integrate message broker
3. Implement JWT
4. Provide fault simulation
5. Provide load testing results
6. Architecture justification report
6 Conclusion
This tutorial guided students through:
ˆ
ˆ
ˆ
ˆ
ˆ
Monolithic architecture limitations
Microservice principles
Domain-Driven Design decomposition
Academic-level implementation
Industry-grade distributed system architecture
Students completing ASSIGNMENT 06 will understand real-world distributed archi
tecture design.
7
7 APPENDIX
Software Architecture and Design
BookStore Microservice Implementation for Assignment 05
7.1 Project Structure
bookstore-microservice/
|
|-- customer-service/
|-- book-service/
|-- cart-service/
|-- api-gateway/
‘-- docker-compose.yml
Each service is an independent Django project.
7.2 Step 1: Create Root Folder
mkdir bookstore-microservice
cd bookstore-microservice
7.3 Customer Service
7.3.1 Create Service
mkdir customer-service
cd customer-service
python-m venv venv
source venv/bin/activate
pip install django djangorestframework requests
django-admin startproject customer_service .
python manage.py startapp app
7.3.2 settings.py
INSTALLED_APPS = [
’rest_framework’,
’app’,
]
7.3.3 models.py
from django.db import models
class Customer(models.Model):
8
name = models.CharField(max_length=255)
email = models.EmailField(unique=True)
7.3.4 serializers.py
from rest_framework import serializers
from .models import Customer
class CustomerSerializer(serializers.ModelSerializer):
class Meta:
model = Customer
fields = ’__all__’
7.3.5 views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Customer
from .serializers import CustomerSerializer
import requests
CART_SERVICE_URL = "http://cart-service:8000"
class CustomerListCreate(APIView):
def get(self, request):
customers = Customer.objects.all()
serializer = CustomerSerializer(customers, many=True)
return Response(serializer.data)
def post(self, request):
serializer = CustomerSerializer(data=request.data)
if serializer.is_valid():
customer = serializer.save()
# Call cart-service
requests.post(
f"{CART_SERVICE_URL}/carts/",
json={"customer_id": customer.id}
)
return Response(serializer.data)
return Response(serializer.errors)
7.3.6 urls.py
from django.urls import path
from .views import CustomerListCreate
9
urlpatterns = [
path(’customers/’, CustomerListCreate.as_view()),
]
7.4 Book Service
7.4.1 Create Service
cd ..
mkdir book-service
cd book-service
python-m venv venv
source venv/bin/activate
pip install django djangorestframework
django-admin startproject book_service .
python manage.py startapp app
7.4.2 models.py
from django.db import models
class Book(models.Model):
title = models.CharField(max_length=255)
author = models.CharField(max_length=255)
price = models.DecimalField(max_digits=10, decimal_places=2)
stock = models.IntegerField()
7.4.3 views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Book
from .serializers import BookSerializer
class BookListCreate(APIView):
def get(self, request):
books = Book.objects.all()
serializer = BookSerializer(books, many=True)
return Response(serializer.data)
def post(self, request):
serializer = BookSerializer(data=request.data)
if serializer.is_valid():
serializer.save()
return Response(serializer.data)
return Response(serializer.errors)
10
7.5 Cart Service
7.5.1 Create Service
cd ..
mkdir cart-service
cd cart-service
python-m venv venv
source venv/bin/activate
pip install django djangorestframework requests
django-admin startproject cart_service .
python manage.py startapp app
7.5.2 models.py
from django.db import models
class Cart(models.Model):
customer_id = models.IntegerField()
class CartItem(models.Model):
cart = models.ForeignKey(Cart, on_delete=models.CASCADE)
book_id = models.IntegerField()
quantity = models.IntegerField()
7.5.3 views.py
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer
import requests
BOOK_SERVICE_URL = "http://book-service:8000"
class CartCreate(APIView):
def post(self, request):
serializer = CartSerializer(data=request.data)
if serializer.is_valid():
serializer.save()
return Response(serializer.data)
class AddCartItem(APIView):
def post(self, request):
book_id = request.data["book_id"]
r = requests.get(f"{BOOK_SERVICE_URL}/books/")
books = r.json()
11
if not any(b["id"] == book_id for b in books):
return Response({"error": "Book not found"})
serializer = CartItemSerializer(data=request.data)
if serializer.is_valid():
serializer.save()
return Response(serializer.data)
class ViewCart(APIView):
def get(self, request, customer_id):
cart = Cart.objects.get(customer_id=customer_id)
items = CartItem.objects.filter(cart=cart)
serializer = CartItemSerializer(items, many=True)
return Response(serializer.data)
7.6 Inter-Service REST Communication
7.6.1 Customer Creation Flow
POST /customers/-> save customer-> call cart-service POST /carts/-> cart created
7.6.2 Add Cart Item Flow
POST /cart-items/-> cart-service checks book-service-> if exists-> add item
8 API Gateway (Web Interface)
8.0.1 Create Gateway
cd ..
django-admin startproject api_gateway
8.0.2 Staff Book Management View
from django.shortcuts import render
import requests
BOOK_SERVICE_URL = "http://book-service:8000"
def book_list(request):
r = requests.get(f"{BOOK_SERVICE_URL}/books/")
return render(request, "books.html", {"books": r.json()})
12
8.0.3 books.html
<h2>Book List</h2>
<ul>
{% for book in books %}
<li>{{ book.title }}- {{ book.price }}</li>
{% endfor %}
</ul>
8.0.4 Customer Cart View
CART_SERVICE_URL = "http://cart-service:8000"
def view_cart(request, customer_id):
r = requests.get(f"{CART_SERVICE_URL}/carts/{customer_id}/")
return render(request, "cart.html", {"items": r.json()})
8.0.5 cart.html
<h2>Your Cart</h2>
<ul>
{% for item in items %}
<li>Book ID: {{ item.book_id }} | Qty: {{ item.quantity }}</li>
{% endfor %}
</ul>
8.1 Docker Compose
services:
customer-service:
build: ./customer-service
ports:- "8001:8000"
book-service:
build: ./book-service
ports:- "8002:8000"
cart-service:
build: ./cart-service
ports:- "8003:8000"
api-gateway:
build: ./api-gateway
13
ports:- "8000:8000"
Run:
docker-compose up--buil