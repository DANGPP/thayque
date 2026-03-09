from django.contrib import admin
from .models import Category, Author, Publisher, Book, BookImage


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'parent', 'is_active', 'created_at']
    list_filter = ['is_active', 'parent']
    search_fields = ['name', 'slug']
    prepopulated_fields = {'slug': ('name',)}


@admin.register(Author)
class AuthorAdmin(admin.ModelAdmin):
    list_display = ['name', 'nationality', 'birth_date', 'created_at']
    search_fields = ['name', 'nationality']


@admin.register(Publisher)
class PublisherAdmin(admin.ModelAdmin):
    list_display = ['name', 'phone', 'email', 'created_at']
    search_fields = ['name', 'email']


class BookImageInline(admin.TabularInline):
    model = BookImage
    extra = 1


@admin.register(Book)
class BookAdmin(admin.ModelAdmin):
    list_display = ['title', 'author', 'category', 'price', 'stock', 'avg_rating', 'is_active', 'is_featured']
    list_filter = ['is_active', 'is_featured', 'category', 'author']
    search_fields = ['title', 'isbn', 'author__name']
    prepopulated_fields = {'slug': ('title',)}
    inlines = [BookImageInline]
    list_editable = ['is_active', 'is_featured', 'stock']
