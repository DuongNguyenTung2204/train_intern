from django.urls import path
from .internal_views import InternalCartView, InternalCartClearView

urlpatterns = [
    path("cart/<int:user_id>/",       InternalCartView.as_view(),      name="internal-cart"),
    path("cart/<int:user_id>/clear/", InternalCartClearView.as_view(), name="internal-cart-clear"),
]
