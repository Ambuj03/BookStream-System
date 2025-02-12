from django.db import models
from bm_app.models import Distributor, Books

class CartItem(models.Model):
    cart_item_id = models.AutoField(primary_key=True)
    distributor = models.ForeignKey(Distributor, on_delete=models.CASCADE)
    book = models.ForeignKey(Books, on_delete=models.CASCADE, null=True, blank=True)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)
    product_name = models.CharField(max_length=255)

    def __str__(self):
        return f"{self.product_name} ({self.quantity})"

    class Meta:
        db_table = "cart_item"

    def get_subtotal(self):
        return self.book.book_price * self.quantity

    def __str__(self):
        return f"{self.product_name} ({self.quantity})" 