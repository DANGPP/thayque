from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework import status
from rest_framework.permissions import AllowAny
from django.db.models import Q
from django.utils.text import slugify

from .models import Category, Author, Publisher, Book, BookImage
from .serializers import (
    CategorySerializer, AuthorSerializer, PublisherSerializer,
    BookSerializer, BookListSerializer, BookImageSerializer
)


class CategoryListCreateView(APIView):
    def get(self, request):
        categories = Category.objects.filter(is_active=True)
        serializer = CategorySerializer(categories, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = dict(request.data)
        # Auto-generate slug if not provided
        if not data.get('slug') and data.get('name'):
            data['slug'] = slugify(data['name'])
        
        serializer = CategorySerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class CategoryDetailView(APIView):
    def get(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category)
            return Response(serializer.data)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            serializer = CategorySerializer(category, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            category = Category.objects.get(pk=pk)
            category.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Category.DoesNotExist:
            return Response({'error': 'Category not found'}, status=status.HTTP_404_NOT_FOUND)


class AuthorListCreateView(APIView):
    def get(self, request):
        authors = Author.objects.all()
        serializer = AuthorSerializer(authors, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AuthorSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AuthorDetailView(APIView):
    def get(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
            serializer = AuthorSerializer(author)
            return Response(serializer.data)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
            serializer = AuthorSerializer(author, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            author = Author.objects.get(pk=pk)
            author.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Author.DoesNotExist:
            return Response({'error': 'Author not found'}, status=status.HTTP_404_NOT_FOUND)


class PublisherListCreateView(APIView):
    def get(self, request):
        publishers = Publisher.objects.all()
        serializer = PublisherSerializer(publishers, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = PublisherSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookListCreateView(APIView):
    def get(self, request):
        books = Book.objects.filter(is_active=True)
        
        # Search
        search = request.query_params.get('search')
        if search:
            books = books.filter(
                Q(title__icontains=search) | 
                Q(author__name__icontains=search) |
                Q(isbn__icontains=search)
            )
        
        # Filter by category
        category = request.query_params.get('category')
        if category:
            books = books.filter(category_id=category)
        
        # Filter by author
        author = request.query_params.get('author')
        if author:
            books = books.filter(author_id=author)
        
        # Filter featured
        featured = request.query_params.get('featured')
        if featured == 'true':
            books = books.filter(is_featured=True)
        
        # Sort
        sort = request.query_params.get('sort', '-created_at')
        if sort in ['price', '-price', 'title', '-title', 'avg_rating', '-avg_rating', '-total_sold']:
            books = books.order_by(sort)
        
        serializer = BookListSerializer(books, many=True)
        return Response(serializer.data)

    def post(self, request):
        data = dict(request.data)
        # Auto-generate slug if not provided
        if not data.get('slug') and data.get('title'):
            data['slug'] = slugify(data['title'])
        
        serializer = BookSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class BookDetailView(APIView):
    def get(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book)
            return Response(serializer.data)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    def put(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            serializer = BookSerializer(book, data=request.data, partial=True)
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data)
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)

    def delete(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            book.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


class BookStockUpdateView(APIView):
    """Cập nhật stock khi đặt hàng"""
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            quantity = request.data.get('quantity', 0)
            action = request.data.get('action', 'decrease')  # decrease or increase
            
            if action == 'decrease':
                if book.stock < quantity:
                    return Response({'error': 'Không đủ hàng trong kho'}, status=status.HTTP_400_BAD_REQUEST)
                book.stock -= quantity
                book.total_sold += quantity
            else:
                book.stock += quantity
            
            book.save()
            return Response({'stock': book.stock, 'total_sold': book.total_sold})
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


class BookRatingUpdateView(APIView):
    """Cập nhật rating khi có review mới"""
    def post(self, request, pk):
        try:
            book = Book.objects.get(pk=pk)
            book.avg_rating = request.data.get('avg_rating', book.avg_rating)
            book.total_reviews = request.data.get('total_reviews', book.total_reviews)
            book.save()
            return Response({'avg_rating': float(book.avg_rating), 'total_reviews': book.total_reviews})
        except Book.DoesNotExist:
            return Response({'error': 'Book not found'}, status=status.HTTP_404_NOT_FOUND)


class HealthCheckView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        return Response({'status': 'healthy', 'service': 'book-service'})
