from .models import Comment


def comments_count(page_obj):
    for post in page_obj:
        post.comment_count = len(Comment.objects.filter(post_id=post.pk))
