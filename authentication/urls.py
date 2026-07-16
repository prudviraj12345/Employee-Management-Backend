from django.urls import path
from .views import change_password, email_check, login, profile, public_stats

urlpatterns = [
    path("login/", login, name="login"),
    path("profile/", profile, name="profile"),
    path("change-password/", change_password, name="change_password"),
    path("public-stats/", public_stats, name="public_stats"),
    path("email-check/", email_check, name="email_check"),
]
