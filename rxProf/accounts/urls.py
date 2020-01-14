from django.contrib.auth import views
from .views import redirectRegister, redirectLogin, Register, customLogout, Settings
from django.urls import path
app_name="accounts"
urlpatterns = [
    path('redirect_l/', redirectLogin, name='redirect_l'),
	path('login/', views.LoginView.as_view(), name='login'),
    path('logout/', customLogout, name='logout'),
    path('password-reset/', views.PasswordResetView.as_view(), name='password_reset_form'),
    path('password-reset/done/', views.PasswordResetDoneView.as_view(), name='password_reset_done'),
    path('reset/<uidb64>/<token>/', views.PasswordResetConfirmView.as_view(), name='password_reset_confirm'),
    path('reset/done/', views.PasswordResetCompleteView.as_view(), name='password_reset_complete'),
	path('redirect_r/', redirectRegister, name='redirect_r'),
	path('register/', Register.as_view(), name='register'),
	path('settings/', Settings.as_view(), name='settings'),
]
