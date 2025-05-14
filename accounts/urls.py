# accounts/urls.py

from django.urls import path
from . import views

app_name = "accounts"

urlpatterns = [
    path('set-language/', views.set_language, name='set_language'),
    path('confirm/<str:uidb64>/<str:token>/<int:timestamp>/', views.confirm_email, name='confirm_email'),
    path("login/", views.login_view, name="login"),
    path('logout/', views.logout_view, name='logout'),
    path("profile/", views.profile_view, name="profile"),




]
