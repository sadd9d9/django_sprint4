from django.contrib import admin

from .models import Category, Comment, Location, Post


class PostInline(admin.TabularInline):
    model = Post
    extra = 1


@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'title',
        'description',
        'slug',
        'is_published'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('title', 'description')
    list_filter = ('is_published',)


@admin.register(Location)
class LocationAdmin(admin.ModelAdmin):
    inlines = (
        PostInline,
    )
    list_display = (
        'name',
        'is_published'
    )
    list_editable = (
        'is_published',
    )
    search_fields = ('name',)
    list_filter = ('is_published',)


@admin.register(Post)
class PostAdmin(admin.ModelAdmin):
    list_display = (
        'title',
        'author',
        'location',
        'category',
        'pub_date',
        'is_published'
    )
    list_editable = (
        'is_published',
        'category'
    )
    search_fields = ('title',)
    list_filter = ('category', 'is_published')


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ('post', 'author')
