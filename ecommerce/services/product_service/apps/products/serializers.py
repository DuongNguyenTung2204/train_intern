from rest_framework import serializers
from .models import Category, Product


class CategorySerializer(serializers.ModelSerializer):
    children = serializers.SerializerMethodField()

    class Meta:
        model  = Category
        fields = ("id", "name", "slug", "parent", "is_active", "children")

    def get_children(self, obj):
        qs = obj.children.filter(is_active=True)
        return CategorySerializer(qs, many=True).data


class ProductSerializer(serializers.ModelSerializer):
    categories    = CategorySerializer(many=True, read_only=True)
    category_ids  = serializers.PrimaryKeyRelatedField(
        many=True, write_only=True,
        queryset=Category.objects.filter(is_active=True),
        source="categories",
    )
    is_in_stock   = serializers.BooleanField(read_only=True)

    class Meta:
        model  = Product
        fields = (
            "id", "name", "slug", "description",
            "price", "compare_price",
            "categories", "category_ids",
            "image", "stock", "sku",
            "is_in_stock", "is_active",
            "created_at", "updated_at",
        )
        read_only_fields = ("id", "slug", "created_at", "updated_at")
