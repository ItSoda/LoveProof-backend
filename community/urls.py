from django.urls import path

from community.views import PostListCreateAPIView, PostDetailAPIView


app_name = 'community'

urlpatterns = [
    path('', PostListCreateAPIView.as_view(), name='post_list_create'),
    path('<int:pk>/detail/', PostDetailAPIView.as_view(), name='post_detail'),
]
