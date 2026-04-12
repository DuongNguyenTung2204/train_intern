"""
Internal product endpoints called by cart_service and order_service.
Protected with X-Service-Token — never exposed via nginx.
"""
from django.conf import settings
from django.db import transaction
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework import status

from .models import Product
from .serializers import ProductSerializer

INTERNAL_TOKEN = getattr(settings, "INTERNAL_SERVICE_TOKEN", "")


def _verify(request):
    if request.headers.get("X-Service-Token", "") != INTERNAL_TOKEN:
        raise PermissionDenied("Invalid service token.")


class InternalProductDetailView(APIView):
    authentication_classes = []
    permission_classes     = []

    def get(self, request, pk):
        _verify(request)
        try:
            product = Product.objects.get(pk=pk, is_active=True)
        except Product.DoesNotExist:
            return Response({"detail": "Not found."}, status=status.HTTP_404_NOT_FOUND)
        return Response(ProductSerializer(product).data)


class InternalDecrementStockView(APIView):
    """
    POST /internal/products/{id}/decrement-stock/
    Body: {"quantity": N}
    Atomically decrements stock. Returns 409 if insufficient.
    """
    authentication_classes = []
    permission_classes     = []

    def post(self, request, pk):
        _verify(request)
        quantity = int(request.data.get("quantity", 0))
        if quantity <= 0:
            return Response({"detail": "quantity must be positive."}, status=400)

        with transaction.atomic():
            try:
                product = Product.objects.select_for_update().get(pk=pk, is_active=True)
            except Product.DoesNotExist:
                return Response({"detail": "Not found."}, status=404)

            if product.stock < quantity:
                return Response(
                    {"detail": f"Insufficient stock. Available: {product.stock}"},
                    status=status.HTTP_409_CONFLICT,
                )
            product.stock -= quantity
            product.save(update_fields=["stock"])

        return Response({"id": product.pk, "stock": product.stock})
