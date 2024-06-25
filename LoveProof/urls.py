from django.contrib import admin
from django.urls import path, include

from users.views import UserRegistrationView, UserLoginAPIView, UserLogoutAPIView, VerifyEmailAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/register/', UserRegistrationView.as_view(), name='register'),
    path('api/login/', UserLoginAPIView.as_view(), name='login'),
    path('api/logout/', UserLogoutAPIView.as_view(), name='logout'),
    path('verify-email/', VerifyEmailAPIView.as_view(), name='email_verify'),
    path('api/v1/users/', include('users.urls', namespace='users'))
]
