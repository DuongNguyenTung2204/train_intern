"""
Internal endpoints — only reachable within the Docker network (nginx blocks /internal/).
"""
from django.urls import path

from .internal_views import InternalUserDetailView

urlpatterns = [
    path("users/<int:pk>/", InternalUserDetailView.as_view(), name="internal-user-detail"),
]
