from django.urls import path
from .views import (
    PostCreateView,
    PostListView,
    PostDetailView,
    PostUpdateView,
    PostDeleteView,
    CommentCreateView,
    CommentListView,
    CommentUpdateView,
    CommentDeleteView,
    LikeToggleView,
    LikePostListView,
    ChangePostStatusView,

    PostListAdminView,
    AdminCountView,
)

app_name = 'blog'

urlpatterns = [
    path('posts/', PostListView.as_view(), name='post-list'),  # List all posts
    path('posts/create/', PostCreateView.as_view(), name='post-create'),  # Create a new post
    path('posts/<int:pk>/', PostDetailView.as_view(), name='post-detail'),  # Retrieve a specific post
    path('posts/<int:pk>/update/', PostUpdateView.as_view(), name='post-update'),  # Update a specific post
    path('posts/<int:pk>/delete/', PostDeleteView.as_view(), name='post-delete'),  # Delete a specific post

    path('comments/', CommentListView.as_view(), name='comment-list'),  # List all comments (filter by post using query params)
    path('comments/create/', CommentCreateView.as_view(), name='comment-create'),  # Create a new comment
    path('comments/<int:pk>/update/', CommentUpdateView.as_view(), name='comment-update'),  # Update a specific comment
    path('comments/<int:pk>/delete/', CommentDeleteView.as_view(), name='comment-delete'),  # Delete a specific comment

    path('likes/toggle/', LikeToggleView.as_view(), name='like-toggle'),  # Toggle like for a post
    path('posts/<int:pk>/likes/', LikePostListView.as_view(), name='post-like-list'),  # List all likes for a specific post


    ##admin views
    path('admin/posts/<int:pk>/status/', ChangePostStatusView.as_view(), name='post-status'),  # Change post status
    path('admin/posts/', PostListAdminView.as_view(), name='post-list-admin'),  # List all posts for admin
    path('admin/count/', AdminCountView.as_view(), name='admin-count'),  # Count posts, comments, likes
]
