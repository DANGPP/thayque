from django.db import models
from django.utils.text import slugify


class Category(models.Model):
    """Danh mục sách"""
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True, blank=True)
    description = models.TextField(blank=True, null=True)
    image = models.URLField(blank=True, null=True)
    parent = models.ForeignKey('self', on_delete=models.SET_NULL, null=True, blank=True, related_name='children')
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'categories'
        verbose_name_plural = 'Categories'
        ordering = ['name']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.name)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.name


class Author(models.Model):
    """Thông tin tác giả"""
    name = models.CharField(max_length=255)
    bio = models.TextField(blank=True, null=True)
    avatar = models.URLField(blank=True, null=True)
    birth_date = models.DateField(blank=True, null=True)
    nationality = models.CharField(max_length=100, blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'authors'
        ordering = ['name']

    def __str__(self):
        return self.name


class Publisher(models.Model):
    """Nhà xuất bản"""
    name = models.CharField(max_length=255)
    address = models.TextField(blank=True, null=True)
    phone = models.CharField(max_length=20, blank=True, null=True)
    email = models.EmailField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'publishers'
        ordering = ['name']

    def __str__(self):
        return self.name


class Book(models.Model):
    """Sách"""
    title = models.CharField(max_length=500)
    slug = models.SlugField(unique=True, max_length=500, blank=True)
    isbn = models.CharField(max_length=20, unique=True, blank=True, null=True)
    description = models.TextField(blank=True, null=True)
    price = models.DecimalField(max_digits=10, decimal_places=2)
    discount_price = models.DecimalField(max_digits=10, decimal_places=2, blank=True, null=True)
    stock = models.IntegerField(default=0)
    pages = models.IntegerField(blank=True, null=True)
    language = models.CharField(max_length=50, default='Vietnamese')
    cover_image = models.URLField(blank=True, null=True)
    published_date = models.DateField(blank=True, null=True)
    
    # Relations
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='books')
    author = models.ForeignKey(Author, on_delete=models.SET_NULL, null=True, related_name='books')
    publisher = models.ForeignKey(Publisher, on_delete=models.SET_NULL, null=True, related_name='books')
    
    # Stats
    avg_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0)
    total_reviews = models.IntegerField(default=0)
    total_sold = models.IntegerField(default=0)
    
    is_active = models.BooleanField(default=True)
    is_featured = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'books'
        ordering = ['-created_at']

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title)
        super().save(*args, **kwargs)

    def __str__(self):
        return self.title

    @property
    def final_price(self):
        return self.discount_price if self.discount_price else self.price


class BookImage(models.Model):
    """Hình ảnh sách"""
    book = models.ForeignKey(Book, on_delete=models.CASCADE, related_name='images')
    image_url = models.URLField()
    is_primary = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'book_images'

    def __str__(self):
        return f"Image for {self.book.title}"
