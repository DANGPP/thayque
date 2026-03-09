from django.contrib import admin
from .models import Review, ReviewReply, ReviewHelpful


class ReviewReplyInline(admin.TabularInline):
    model = ReviewReply
    extra = 0


@admin.register(Review)
class ReviewAdmin(admin.ModelAdmin):
    list_display = ['id', 'customer_name', 'book_id', 'rating', 'is_approved', 'helpful_count', 'created_at']
    list_filter = ['rating', 'is_approved', 'is_verified_purchase']
    search_fields = ['customer_name', 'comment']
    list_editable = ['is_approved']
    inlines = [ReviewReplyInline]
