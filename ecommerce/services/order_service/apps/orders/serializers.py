from rest_framework import serializers
from .models import Order, OrderItem


class OrderItemSerializer(serializers.ModelSerializer):
    subtotal = serializers.DecimalField(max_digits=12, decimal_places=2, read_only=True)

    class Meta:
        model  = OrderItem
        fields = ("id", "product_id", "product_name", "product_sku", "unit_price", "quantity", "subtotal")


class OrderSerializer(serializers.ModelSerializer):
    items          = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source="get_status_display", read_only=True)

    class Meta:
        model  = Order
        fields = (
            "id", "user_id", "user_email", "status", "status_display",
            "shipping_name", "shipping_phone", "shipping_address",
            "total_price", "note", "items",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "user_id", "user_email", "total_price", "created_at", "updated_at")


class CheckoutSerializer(serializers.Serializer):
    """Validates checkout input and orchestrates the cross-service checkout flow."""
    shipping_name    = serializers.CharField(max_length=150)
    shipping_phone   = serializers.CharField(max_length=20)
    shipping_address = serializers.CharField()
    note             = serializers.CharField(required=False, allow_blank=True)

    def create(self, validated_data):
        from django.db import transaction
        from utils.service_client import get_user_cart, get_product, decrement_stock, clear_user_cart

        user = self.context["request"].user

        # 1. Fetch cart from cart_service
        cart_data = get_user_cart(user.id)
        items = cart_data.get("items", [])
        if not items:
            raise serializers.ValidationError("Cart is empty.")

        # 2. Resolve products and compute total
        resolved = []
        total = 0
        for item in items:
            product = get_product(item["product_id"])
            if not product:
                raise serializers.ValidationError(
                    f"Product #{item['product_id']} is unavailable."
                )
            if item["quantity"] > product["stock"]:
                raise serializers.ValidationError(
                    f"Insufficient stock for '{product['name']}'. Available: {product['stock']}"
                )
            line_total = float(product["price"]) * item["quantity"]
            total += line_total
            resolved.append({"product": product, "quantity": item["quantity"]})

        # 3. Persist order atomically, then decrement stock + clear cart
        with transaction.atomic():
            order = Order.objects.create(
                user_id          = user.id,
                user_email       = user.email,
                total_price      = round(total, 2),
                **validated_data,
            )
            order_items = [
                OrderItem(
                    order        = order,
                    product_id   = r["product"]["id"],
                    product_name = r["product"]["name"],
                    product_sku  = r["product"].get("sku", ""),
                    unit_price   = r["product"]["price"],
                    quantity     = r["quantity"],
                )
                for r in resolved
            ]
            OrderItem.objects.bulk_create(order_items)

        # 4. Decrement stock via product_service (outside transaction – best effort)
        for r in resolved:
            try:
                decrement_stock(r["product"]["id"], r["quantity"])
            except Exception:
                pass  # log in production; stock inconsistency handled by reconciliation job

        # 5. Clear cart
        clear_user_cart(user.id)

        return order


class UpdateOrderStatusSerializer(serializers.ModelSerializer):
    class Meta:
        model  = Order
        fields = ("status",)
