from django.urls import path

from . import views
from .views import category_posts, index, post_detail

app_name = 'blog'

urlpatterns = [
    path('', index, name='index'),
    path(
        'profile/<slug:username>/',
        views.ProfileDetailView.as_view(),
        name='profile'
    ),
    path(
        'profile/<slug:username>/edit/',
        views.ProfileEditView.as_view(),
        name='edit_profile'
    ),
    path(
        'posts/create/',
        views.PostsCreateView.as_view(),
        name='create_post'
    ),
    path(
        'posts/<int:post_id>/edit/',
        views.PostsUpdateView.as_view(),
        name='edit_post'
    ),
    path(
        'posts/<int:post_id>/delete/',
        views.PostsDeleteView.as_view(),
        name='delete_post'
    ),
    path(
        'posts/<int:post_id>/create/',
        views.CommentCreateView.as_view(),
        name='add_comment'
    ),
    path(
        'posts/<int:post_id>/edit_comment/<int:com_id>',
        views.CommentUpdateView.as_view(),
        name='edit_comment'
    ),
    path(
        'posts/<int:post_id>/delete_comment/<int:com_id>',
        views.CommentDeleteView.as_view(),
        name='delete_comment'
    ),
    path('posts/<int:post_id>/', post_detail, name='post_detail'),
    path(
        'category/<slug:category_slug>/',
        category_posts,
        name='category_posts'
    ),
]
