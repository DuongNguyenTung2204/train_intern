"""
Internal endpoints called by order_service during checkout.
"""
from django.conf import settings
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem

INTERNAL_TOKEN = getattr(settings, "INTERNAL_SERVICE_TOKEN", "")


def _verify(request):
    if request.headers.get("X-Service-Token", "") != INTERNAL_TOKEN:
        raise PermissionDenied("Invalid service token.")


class InternalCartView(APIView):
    """
    GET /internal/cart/{user_id}/
    Returns cart items as plain dicts for order_service to snapshot.
    """
    authentication_classes = []
    permission_classes     = []

    def get(self, request, user_id):
        _verify(request)
        try:
            cart = Cart.objects.prefetch_related("items").get(user_id=user_id)
        except Cart.DoesNotExist:
            return Response({"items": []})

        items = [
            {"product_id": item.product_id, "quantity": item.quantity}
            for item in cart.items.all()
        ]
        return Response({"cart_id": cart.pk, "user_id": user_id, "items": items})


class InternalCartClearView(APIView):
    """
    DELETE /internal/cart/{user_id}/clear/
    Wipes all cart items after a successful order.
    """
    authentication_classes = []
    permission_classes     = []

    def delete(self, request, user_id):
        _verify(request)
        CartItem.objects.filter(cart__user_id=user_id).delete()
        return Response({"message": "Cart cleared."})
