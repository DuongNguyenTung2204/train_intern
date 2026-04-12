from django.urls import path
from .views import (
    OrderListCreateView, OrderDetailView, OrderCancelView,
    AdminOrderListView, AdminOrderStatusView,
)

urlpatterns = [
    path("",                     OrderListCreateView.as_view(),  name="order-list-create"),
    path("<int:pk>/",            OrderDetailView.as_view(),      name="order-detail"),
    path("<int:pk>/cancel/",     OrderCancelView.as_view(),      name="order-cancel"),
    path("admin/",               AdminOrderListView.as_view(),   name="order-admin-list"),
    path("admin/<int:pk>/status/", AdminOrderStatusView.as_view(), name="order-admin-status"),
]
