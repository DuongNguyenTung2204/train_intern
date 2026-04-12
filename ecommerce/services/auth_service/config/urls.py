from django.contrib import admin
from django.urls import path, include
from rest_framework_simplejwt.views import TokenRefreshView, TokenBlacklistView
from apps.accounts.views import CustomTokenObtainPairView

urlpatterns = [
    path("admin/", admin.site.urls),
    path("api/v1/auth/", include("apps.accounts.urls")),
    path("api/v1/auth/token/", CustomTokenObtainPairView.as_view(), name="token_obtain"),
    path("api/v1/auth/token/refresh/", TokenRefreshView.as_view(), name="token_refresh"),
    path("api/v1/auth/token/blacklist/", TokenBlacklistView.as_view(), name="token_blacklist"),
    # Internal – service-to-service only (not exposed via nginx)
    path("internal/", include("apps.accounts.internal_urls")),
]
