from django.contrib import admin
from django.urls import path

from users.views import UserLoginAPIView, UserLogoutAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', UserLoginAPIView.as_view(), name='login'),
    path('api/logout/', UserLogoutAPIView.as_view(), name='logout'),
]
