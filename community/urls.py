from django.urls import path

from community.views import PostListCreateAPIView, PostDetailAPIView, CommentListCreateAPIView


app_name = 'community'

urlpatterns = [
    path('', PostListCreateAPIView.as_view(), name='post_list_create'),
    path('<int:pk>/detail/', PostDetailAPIView.as_view(), name='post_detail'),
    path('posts/<int:post_pk>/comments/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
]
