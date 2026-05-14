from django.contrib import admin
from django.urls import path, include, re_path
from django.contrib.auth import views as auth_view

from api import views
from api.views import *


urlpatterns = [
    path('ping/', ping, name='ping'),
    path('admin/', admin.site.urls),
    path('api/v1/drf-auth/', include('rest_framework.urls')),
    path('api/v1/auth/', include('djoser.urls')),
    re_path(r'^auth/', include('djoser.urls.authtoken')),
    path('', UserHome, name='home'),
    path('login/', LoginUser.as_view(), name='login'),
    path('login./', FakeLoginUser.as_view(), name='fake_login'),
    path('logout/', logout_user, name='logout'),
    path('register/', register, name='register'),
    path('about/', about, name='about'),
    path('contact/', contact, name='contact'),
    path('parse/', ParseUser, name='parse'),
    path('profile/<username>', views.profile, name='profile'),
    path('email/', email),
    path('activate/<uidb64>/<token>', views.activate, name='activate'),
    path('password_change/', views.password_change, name="password_change"),
    path('password_reset/', views.password_reset_request, name="password_reset"),
    path('reset/<uidb64>/<token>', views.passwordResetConfirm, name='password_reset_confirm'),
    path('orders/', My_orders, name="my_orders"),
    path('orders/<int:order_id>/download/<str:file_type>/', views.download_result, name='download_result'),
]
