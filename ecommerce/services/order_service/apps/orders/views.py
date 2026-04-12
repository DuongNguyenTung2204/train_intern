from rest_framework import generics, permissions, status
from rest_framework.response import Response

from .models import Order
from .serializers import OrderSerializer, CheckoutSerializer, UpdateOrderStatusSerializer


class IsAdminUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user and request.user.is_staff


class OrderListCreateView(generics.ListCreateAPIView):
    """
    GET  /api/v1/orders/  – my orders
    POST /api/v1/orders/  – checkout
    """
    permission_classes = [permissions.IsAuthenticated]

    def get_serializer_class(self):
        return CheckoutSerializer if self.request.method == "POST" else OrderSerializer

    def get_queryset(self):
        return (
            Order.objects
            .filter(user_id=self.request.user.id)
            .prefetch_related("items")
        )

    def create(self, request, *args, **kwargs):
        s = CheckoutSerializer(data=request.data, context={"request": request})
        s.is_valid(raise_exception=True)
        order = s.save()
        return Response(OrderSerializer(order).data, status=status.HTTP_201_CREATED)


class OrderDetailView(generics.RetrieveAPIView):
    """GET /api/v1/orders/{id}/"""
    serializer_class   = OrderSerializer
    permission_classes = [permissions.IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user_id=self.request.user.id).prefetch_related("items")


class OrderCancelView(generics.UpdateAPIView):
    """PATCH /api/v1/orders/{id}/cancel/"""
    permission_classes = [permissions.IsAuthenticated]
    http_method_names  = ["patch"]

    def get_queryset(self):
        return Order.objects.filter(user_id=self.request.user.id)

    def patch(self, request, *args, **kwargs):
        order = self.get_object()
        if order.status not in (Order.Status.PENDING, Order.Status.CONFIRMED):
            return Response({"detail": "Cannot cancel at this stage."}, status=400)
        order.status = Order.Status.CANCELLED
        order.save()
        return Response(OrderSerializer(order).data)


class AdminOrderListView(generics.ListAPIView):
    """GET /api/v1/orders/admin/ — staff only"""
    serializer_class   = OrderSerializer
    permission_classes = [IsAdminUser]
    filterset_fields   = ["status", "user_id"]

    def get_queryset(self):
        return Order.objects.all().prefetch_related("items")


class AdminOrderStatusView(generics.UpdateAPIView):
    """PATCH /api/v1/orders/admin/{id}/status/ — staff only"""
    serializer_class   = UpdateOrderStatusSerializer
    permission_classes = [IsAdminUser]
    queryset           = Order.objects.all()
