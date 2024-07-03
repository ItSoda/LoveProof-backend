from django.urls import path

from community.views import (
    PostListCreateAPIView, PostDetailAPIView,
    CommentListCreateAPIView, CommentDetailView,
    LikePostAPIView, LikeCommentAPIView,
    ReportListAPIView
)


app_name = 'community'

urlpatterns = [
    path('', PostListCreateAPIView.as_view(), name='post_list_create'),
    path('<int:pk>/detail/', PostDetailAPIView.as_view(), name='post_detail'),
    path('posts/<int:post_pk>/comments/', CommentListCreateAPIView.as_view(), name='comment_list_create'),
    path('comments/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
    path('posts/<int:post_pk>/like/', LikePostAPIView.as_view(), name='like_post'),
    path('comments/<int:comment_pk>/like/', LikeCommentAPIView.as_view(), name='like_comment'),
    path('reports/', ReportListAPIView.as_view(), name='report_list'),
]
