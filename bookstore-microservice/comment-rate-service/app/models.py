from django.db import models


class Review(models.Model):
    """Đánh giá sách"""
    book_id = models.IntegerField()
    customer_id = models.IntegerField()
    customer_name = models.CharField(max_length=255)
    
    rating = models.IntegerField(choices=[(i, i) for i in range(1, 6)])  # 1-5 stars
    title = models.CharField(max_length=255, blank=True, null=True)
    comment = models.TextField()
    
    is_verified_purchase = models.BooleanField(default=False)
    is_approved = models.BooleanField(default=True)
    helpful_count = models.IntegerField(default=0)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'reviews'
        ordering = ['-created_at']
        unique_together = ['book_id', 'customer_id']

    def __str__(self):
        return f"Review by {self.customer_name} - {self.rating} stars"


class ReviewReply(models.Model):
    """Phản hồi đánh giá"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='replies')
    staff_id = models.IntegerField(blank=True, null=True)
    staff_name = models.CharField(max_length=255)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_replies'
        ordering = ['created_at']

    def __str__(self):
        return f"Reply to review {self.review.id}"


class ReviewHelpful(models.Model):
    """Đánh giá hữu ích"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    customer_id = models.IntegerField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'review_helpful'
        unique_together = ['review', 'customer_id']
