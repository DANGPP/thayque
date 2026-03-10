from rest_framework import serializers
from django.utils.text import slugify
from .models import Category, Author, Publisher, Book, BookImage


class CategorySerializer(serializers.ModelSerializer):
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True)
    
    class Meta:
        model = Category
        fields = '__all__'


class AuthorSerializer(serializers.ModelSerializer):
    class Meta:
        model = Author
        fields = '__all__'


class PublisherSerializer(serializers.ModelSerializer):
    class Meta:
        model = Publisher
        fields = '__all__'


class BookImageSerializer(serializers.ModelSerializer):
    class Meta:
        model = BookImage
        fields = '__all__'


class BookSerializer(serializers.ModelSerializer):
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    publisher_name = serializers.CharField(source='publisher.name', read_only=True)
    images = BookImageSerializer(many=True, read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)
    slug = serializers.SlugField(required=False, allow_blank=True, allow_null=True)

    class Meta:
        model = Book
        fields = '__all__'


class BookListSerializer(serializers.ModelSerializer):
    """Serializer nhẹ cho danh sách"""
    category_name = serializers.CharField(source='category.name', read_only=True)
    author_name = serializers.CharField(source='author.name', read_only=True)
    final_price = serializers.DecimalField(max_digits=10, decimal_places=2, read_only=True)

    class Meta:
        model = Book
        fields = ['id', 'title', 'slug', 'price', 'discount_price', 'final_price',
                  'cover_image', 'avg_rating', 'total_reviews', 'stock',
                  'category_name', 'author_name', 'is_featured']
