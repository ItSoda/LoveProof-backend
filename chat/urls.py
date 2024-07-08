from django.urls import path

from chat.views import ChatListAPIView


app_name = 'chat'

urlpatterns = [
    path('', ChatListAPIView.as_view(), name='list_chat'),
]
