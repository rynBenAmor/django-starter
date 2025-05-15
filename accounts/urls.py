# accounts/urls.py
from django.urls import path, reverse_lazy
from . import views
from django.contrib.auth.views import (
        PasswordResetView,
        PasswordResetDoneView,
        PasswordResetConfirmView,
        PasswordResetCompleteView
    )



app_name = "accounts"

urlpatterns = [
    path('set-language/', views.set_language, name='set_language'),

    path('verify_email/<str:uidb64>/<str:token>/<str:signed_ts>/', views.verify_email, name='verify_email'),
    path('login/', views.login_view, name='login'),
    path('logout/', views.logout_view, name='logout'),
    path('profile/', views.profile_view, name="profile"),

    path("reset_password/", PasswordResetView.as_view(
            email_template_name="registration/password_reset_email.txt", #plain txt
            html_email_template_name="registration/password_reset_email.html", #html
            subject_template_name="registration/password_reset_subject.txt",
            success_url=reverse_lazy("accounts:password_reset_done"),
        ),
        name="reset_password",
    ),

    path('password_reset_confirm/<uidb64>/<token>/', PasswordResetConfirmView.as_view(
            success_url=reverse_lazy("accounts:password_reset_complete"),
        ), 
        name='password_reset_confirm'
    ),

    path('password_reset_done/', PasswordResetDoneView.as_view(), name='password_reset_done'),

    path('password_reset_complete/', PasswordResetCompleteView.as_view(), name='password_reset_complete'),

]
