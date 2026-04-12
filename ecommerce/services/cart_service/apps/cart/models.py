"""
Cart models – user identity comes from JWT; no FK to a User table.
product_id is a soft reference; the actual product lives in product_service.
"""
from django.db import models


class Cart(models.Model):
    # owner identified by the user_id from JWT payload
    user_id    = models.IntegerField(unique=True, db_index=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f"Cart[user={self.user_id}]"


class CartItem(models.Model):
    cart       = models.ForeignKey(Cart, on_delete=models.CASCADE, related_name="items")
    product_id = models.IntegerField()      # soft FK to product_service
    quantity   = models.PositiveIntegerField(default=1)
    added_at   = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ("cart", "product_id")

    def __str__(self):
        return f"{self.quantity}x product#{self.product_id}"
