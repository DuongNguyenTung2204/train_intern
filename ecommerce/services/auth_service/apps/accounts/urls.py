from django.urls import path

from .views import ChangePasswordView, ProfileView, RegisterView

urlpatterns = [
    path("register/",        RegisterView.as_view(),        name="auth-register"),
    path("profile/",         ProfileView.as_view(),         name="auth-profile"),
    path("change-password/", ChangePasswordView.as_view(),  name="auth-change-password"),
]
