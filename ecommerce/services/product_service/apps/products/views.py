import django_filters
from rest_framework import viewsets, permissions
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import Category, Product
from .serializers import CategorySerializer, ProductSerializer


class IsAdminOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method in permissions.SAFE_METHODS:
            return True
        return request.user and request.user.is_staff


class ProductFilter(django_filters.FilterSet):
    min_price = django_filters.NumberFilter(field_name="price", lookup_expr="gte")
    max_price = django_filters.NumberFilter(field_name="price", lookup_expr="lte")
    category  = django_filters.CharFilter(field_name="categories__slug")
    in_stock  = django_filters.BooleanFilter(method="filter_in_stock")

    class Meta:
        model  = Product
        fields = ["is_active", "min_price", "max_price", "category", "in_stock"]

    def filter_in_stock(self, qs, name, value):
        return qs.filter(stock__gt=0) if value else qs.filter(stock=0)


class CategoryViewSet(viewsets.ModelViewSet):
    queryset         = Category.objects.filter(parent=None, is_active=True).prefetch_related("children")
    serializer_class = CategorySerializer
    permission_classes = [IsAdminOrReadOnly]
    lookup_field     = "slug"


class ProductViewSet(viewsets.ModelViewSet):
    queryset = Product.objects.filter(is_active=True).prefetch_related("categories")
    serializer_class   = ProductSerializer
    permission_classes = [IsAdminOrReadOnly]
    filterset_class    = ProductFilter
    search_fields      = ["name", "description", "sku"]
    ordering_fields    = ["price", "created_at"]
    lookup_field       = "slug"

    @action(detail=False, methods=["get"], url_path="low-stock")
    def low_stock(self, request):
        if not request.user.is_staff:
            return Response({"detail": "Forbidden."}, status=403)
        threshold = int(request.query_params.get("threshold", 5))
        qs = Product.objects.filter(stock__lte=threshold, is_active=True).order_by("stock")
        return Response(ProductSerializer(qs, many=True).data)
