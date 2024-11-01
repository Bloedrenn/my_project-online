from django.urls import path, reverse_lazy

from .views import register, log_in, log_out

# Импорт служебных функций для работы с пользователями. django.contrib.auth - это встроенное приложение Django, которое предоставляет функционал для работы с пользователями.
from django.contrib.auth.views import PasswordResetView, PasswordResetDoneView, PasswordResetConfirmView, PasswordResetCompleteView

urlpatterns = [
    path('register/', register, name='register'),
    path('login/', log_in, name='log_in'),
    path('logout/', log_out, name='log_out'),

    # Маршруты связанные со сбросом пароля
    ## Маршрут для сброса пароля
    path("password-reset/", PasswordResetView.as_view(
            template_name="users/password_reset_form.html",
            email_template_name="users/password_reset_email.html",
            success_url=reverse_lazy("password_reset_done"),
        ), name="password_reset",
    ),
    ## Маршрут для подтверждения сброса пароля
    path("password-reset/done/", PasswordResetDoneView.as_view(
            template_name="users/password_reset_done.html"
        ), name="password_reset_done",
    ),
    ## Маршрут для ввода нового пароля
    path("reset/<uidb64>/<token>/", PasswordResetConfirmView.as_view(
            template_name="users/password_reset_confirm.html",
            success_url=reverse_lazy("password_reset_complete"),
        ), name="password_reset_confirm",
    ),
    ## Маршрут для завершения сброса пароля
    path("reset/done/", PasswordResetCompleteView.as_view(
            template_name="users/password_reset_complete.html"
        ), name="password_reset_complete",
    ),
]