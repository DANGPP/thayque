from django.db import models


class Cart(models.Model):
    """Giỏ hàng của khách hàng"""
    customer_id = models.IntegerField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'carts'

    def __str__(self):
        return f"Cart of customer {self.customer_id}"

    @property
    def total_items(self):
        return sum(item.quantity for item in self.items.all())

    @property
    def total_price(self):
        return sum(item.subtotal for item in self.items.all())


class CartItem(models.Model):
    """Sản phẩm trong giỏ hàng"""
    cart = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name='items')
    book_id = models.IntegerField()
    book_title = models.CharField(max_length=500)  # Cache book info
    book_price = models.DecimalField(max_digits=10, decimal_places=2)
    book_image = models.URLField(blank=True, null=True)
    quantity = models.IntegerField(default=1)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'cart_items'
        unique_together = ['cart', 'book_id']

    def __str__(self):
        return f"{self.book_title} x {self.quantity}"

    @property
    def subtotal(self):
        return self.book_price * self.quantity
