from django.urls import path
from .views import CartDetailView, CartItemCreateView, CartItemUpdateDeleteView, CartClearView

urlpatterns = [
    path("",            CartDetailView.as_view(),          name="cart-detail"),
    path("items/",      CartItemCreateView.as_view(),       name="cart-item-create"),
    path("items/<int:pk>/", CartItemUpdateDeleteView.as_view(), name="cart-item-detail"),
    path("clear/",      CartClearView.as_view(),            name="cart-clear"),
]
