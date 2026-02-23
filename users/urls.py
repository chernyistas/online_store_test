from django.contrib.auth.views import LoginView, LogoutView
from django.urls import path

from users.views import UserCreateView, UserUpdateView

app_name = "users"

urlpatterns = [
    path("login/", LoginView.as_view(template_name="users/login.html"), name="login"),
    path("logout/", LogoutView.as_view(), name="logout"),
    path("register/", UserCreateView.as_view(template_name="users/register.html"), name="register"),
    path("profile/", UserUpdateView.as_view(), name="profile"),
]
