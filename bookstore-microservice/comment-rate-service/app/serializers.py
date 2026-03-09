from rest_framework import serializers
from .models import Review, ReviewReply, ReviewHelpful


class ReviewReplySerializer(serializers.ModelSerializer):
    class Meta:
        model = ReviewReply
        fields = '__all__'
        read_only_fields = ['created_at']


class ReviewSerializer(serializers.ModelSerializer):
    replies = ReviewReplySerializer(many=True, read_only=True)

    class Meta:
        model = Review
        fields = '__all__'
        read_only_fields = ['helpful_count', 'created_at', 'updated_at']


class CreateReviewSerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    customer_id = serializers.IntegerField()
    customer_name = serializers.CharField()
    rating = serializers.IntegerField(min_value=1, max_value=5)
    title = serializers.CharField(required=False, allow_blank=True)
    comment = serializers.CharField()


class BookRatingSummarySerializer(serializers.Serializer):
    book_id = serializers.IntegerField()
    avg_rating = serializers.DecimalField(max_digits=3, decimal_places=2)
    total_reviews = serializers.IntegerField()
    rating_distribution = serializers.DictField()
