"""
Order models – user identity comes from JWT; no FK to auth_service DB.
Product snapshot stored at order time – immune to future price changes.
"""
from django.db import models


class Order(models.Model):
    class Status(models.TextChoices):
        PENDING    = "pending",    "Pending"
        CONFIRMED  = "confirmed",  "Confirmed"
        PROCESSING = "processing", "Processing"
        SHIPPED    = "shipped",    "Shipped"
        DELIVERED  = "delivered",  "Delivered"
        CANCELLED  = "cancelled",  "Cancelled"

    user_id          = models.IntegerField(db_index=True)   # from JWT
    user_email       = models.EmailField()                   # snapshot
    status           = models.CharField(max_length=20, choices=Status.choices, default=Status.PENDING)
    shipping_name    = models.CharField(max_length=150)
    shipping_phone   = models.CharField(max_length=20)
    shipping_address = models.TextField()
    total_price      = models.DecimalField(max_digits=14, decimal_places=2)
    note             = models.TextField(blank=True)
    created_at       = models.DateTimeField(auto_now_add=True)
    updated_at       = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-created_at"]

    def __str__(self):
        return f"Order #{self.pk} [{self.status}] user={self.user_id}"


class OrderItem(models.Model):
    order        = models.ForeignKey(Order, on_delete=models.CASCADE, related_name="items")
    product_id   = models.IntegerField()
    product_name = models.CharField(max_length=255)
    product_sku  = models.CharField(max_length=100, blank=True)
    unit_price   = models.DecimalField(max_digits=12, decimal_places=2)
    quantity     = models.PositiveIntegerField()

    @property
    def subtotal(self):
        return self.unit_price * self.quantity

    def __str__(self):
        return f"{self.quantity}x {self.product_name}"
