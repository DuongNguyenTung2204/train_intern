from django.urls import path
from .internal_views import InternalProductDetailView, InternalDecrementStockView

urlpatterns = [
    path("products/<int:pk>/",               InternalProductDetailView.as_view(),  name="internal-product-detail"),
    path("products/<int:pk>/decrement-stock/", InternalDecrementStockView.as_view(), name="internal-decrement-stock"),
]
