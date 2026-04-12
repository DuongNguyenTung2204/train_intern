from rest_framework import generics, status, permissions
from rest_framework.response import Response
from rest_framework.views import APIView

from .models import Cart, CartItem
from .serializers import CartSerializer, CartItemSerializer


class CartDetailView(generics.RetrieveAPIView):
    """GET /api/v1/cart/"""
    serializer_class   = CartSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_object(self):
        cart, _ = Cart.objects.prefetch_related("items").get_or_create(
            user_id=self.request.user.id
        )
        return cart


class CartItemCreateView(generics.CreateAPIView):
    """POST /api/v1/cart/items/"""
    serializer_class   = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def create(self, request, *args, **kwargs):
        cart, _ = Cart.objects.get_or_create(user_id=request.user.id)
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        product_id = serializer.validated_data["product_id"]
        quantity   = serializer.validated_data.get("quantity", 1)

        item, created = CartItem.objects.get_or_create(
            cart=cart, product_id=product_id,
            defaults={"quantity": quantity},
        )
        if not created:
            item.quantity += quantity
            item.save()

        return Response(
            CartItemSerializer(item).data,
            status=status.HTTP_201_CREATED if created else status.HTTP_200_OK,
        )


class CartItemUpdateDeleteView(generics.RetrieveUpdateDestroyAPIView):
    """GET/PATCH/DELETE /api/v1/cart/items/{id}/"""
    serializer_class   = CartItemSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return CartItem.objects.filter(cart__user_id=self.request.user.id)


class CartClearView(APIView):
    """DELETE /api/v1/cart/clear/"""
    permission_classes = [permissions.IsAuthenticated]

    def delete(self, request):
        Cart.objects.filter(user_id=request.user.id).first() and \
            CartItem.objects.filter(cart__user_id=request.user.id).delete()
        return Response({"message": "Cart cleared."}, status=status.HTTP_204_NO_CONTENT)
