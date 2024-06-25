from django.urls import path

from users.views import ProfileAPIView


app_name = 'users'

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile'),
]
