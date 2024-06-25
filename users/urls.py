from django.urls import path

from users.views import ProfileAPIView, CheckerListAPIView, CheckerDetailAPIView


app_name = 'users'

urlpatterns = [
    path('profile/', ProfileAPIView.as_view(), name='profile'),
    path('users/', CheckerListAPIView.as_view(), name='checker-list'),
    path('users/<str:username>', CheckerDetailAPIView.as_view(), name='checker-detail')
]
