
from django.db.models import Count
from django.utils.timezone import now


def posts_annotate(posts):
    return posts.select_related(
        'author',
        'category',
        'location'
    ).annotate(comment_count=Count('comments')).order_by('-pub_date')


def posts_filter(posts):
    return posts.filter(
        pub_date__lte=now(),
        is_published=True,
        category__is_published=True
    )
