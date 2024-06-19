from django.contrib import admin
from django.urls import path

from users.views import UserLoginAPIView


urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/login/', UserLoginAPIView.as_view(), name='login'),
]
