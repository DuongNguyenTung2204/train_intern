from rest_framework import serializers
from .models import Cart, CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_detail = serializers.SerializerMethodField()

    class Meta:
        model  = CartItem
        fields = ("id", "product_id", "quantity", "added_at", "product_detail")
        read_only_fields = ("id", "added_at")

    def get_product_detail(self, obj):
        """Fetch live product info from product_service (best-effort)."""
        from utils.service_client import get_product
        return get_product(obj.product_id)

    def validate_product_id(self, value):
        from utils.service_client import get_product
        product = get_product(value)
        if product is None:
            raise serializers.ValidationError("Product not found or inactive.")
        if not product.get("is_in_stock", False):
            raise serializers.ValidationError("Product is out of stock.")
        return value

    def validate(self, attrs):
        from utils.service_client import get_product
        product  = get_product(attrs["product_id"])
        quantity = attrs.get("quantity", 1)
        if product and quantity > product.get("stock", 0):
            raise serializers.ValidationError(
                {"quantity": f"Only {product['stock']} units available."}
            )
        return attrs


class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model  = Cart
        fields = ("id", "user_id", "items", "updated_at")
