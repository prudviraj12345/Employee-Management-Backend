from django.urls import path
from .views import change_password, login, profile

urlpatterns = [
    path("login/", login, name="login"),
    path("profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
]
