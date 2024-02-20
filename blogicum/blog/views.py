from django.contrib.auth import get_user_model
from django.contrib.auth.mixins import LoginRequiredMixin, UserPassesTestMixin
from django.core.paginator import Paginator
from django.http.response import HttpResponseRedirect
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.utils.timezone import now
from django.views.generic import (
    CreateView, DeleteView, DetailView, UpdateView
)

from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .models import Category, Comment, Post
from .utils import comments_count


def posts_filter(posts):
    return posts.select_related(
        'author',
        'category',
        'location'
    ).filter(
        pub_date__lte=now(),
        is_published=True,
        category__is_published=True
    )


def index(request):
    post_list = posts_filter(
        Post.objects
    )

    context = {
        'page_obj': Paginator(
            post_list,
            POSTS_PER_PAGE
        ).get_page(request.GET.get('page'))
    }

    comments_count(context['page_obj'])

    return render(
        request,
        'blog/index.html',
        context
    )


def post_detail(request, post_id):

    if request.user == get_object_or_404(Post, pk=post_id).author:
        post_detail_filter = Post.objects.select_related(
            'author',
            'category',
            'location'
        )
    else:
        post_detail_filter = posts_filter(Post.objects)

    post = get_object_or_404(
        post_detail_filter,
        pk=post_id
    )

    comments = Comment.objects.prefetch_related(
        'author'
    ).filter(
        post_id=post.pk
    )

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': comments
    }

    return render(
        request,
        'blog/detail.html',
        context
    )


def category_posts(request, category_slug):
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = posts_filter(category.posts)

    context = {
        'category': category,
        'page_obj': Paginator(
            post_list,
            POSTS_PER_PAGE
        ).get_page(request.GET.get('page'))
    }

    comments_count(context['page_obj'])

    return render(
        request,
        'blog/category.html',
        context
    )


class PermissionMixin(UserPassesTestMixin):

    def test_func(self):
        object = self.get_object()
        return object.author == self.request.user


class PostsCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostsUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'
    pk_url_kwarg = 'post_id'

    def get_object(self):
        return get_object_or_404(Post, pk=self.kwargs['post_id'])

    def handle_no_permission(self):
        return HttpResponseRedirect(
            reverse('blog:post_detail', kwargs={
                'post_id': self.get_object().pk})
        )

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            self.request.POST or None,
            instance=self.get_object()
        )
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': self.get_object().pk}
        )


class PostsDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'
    success_url = reverse_lazy('blog:index')
    pk_url_kwarg = 'post_id'

    def form_valid(self, form):
        get_object_or_404(Post, pk=self.kwargs['post_id']).delete()
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = PostForm(
            instance=get_object_or_404(Post, pk=self.kwargs['post_id'])
        )
        return context


class CommentCreateView(LoginRequiredMixin, CreateView):
    model = Comment
    form_class = CommentForm

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': Post.objects.get(pk=self.kwargs['post_id']).pk}
        )


class CommentUpdateView(PermissionMixin, LoginRequiredMixin, UpdateView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'com_id'

    def form_valid(self, form):
        form.instance.author = self.request.user
        return super().form_valid(form)

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['form'] = CommentForm(
            self.request.POST or None, instance=Comment.objects.get(
                pk=self.kwargs['com_id']
            )
        )
        return context

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': Post.objects.get(pk=self.kwargs['post_id']).pk}
        )


class CommentDeleteView(PermissionMixin, LoginRequiredMixin, DeleteView):
    model = Comment
    form_class = CommentForm
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'com_id'

    def form_valid(self, form):
        self.Comment.objects.get(
            pk=self.kwargs['com_id']
        ).delete()
        return super().form_valid(form)

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'post_id': Post.objects.get(pk=self.kwargs['post_id']).pk}
        )


class ProfileDetailView(DetailView):
    model = get_user_model()
    template_name = 'blog/profile.html'

    def get_object(self):
        return get_object_or_404(
            get_user_model(),
            username=self.kwargs.get('username')
        )

    def get_context_data(self, **kwargs):

        context = {
            'profile': self.get_object(),
            'page_obj': Paginator(Post.objects.filter(
                author__username=self.get_object().username
            ), POSTS_PER_PAGE).get_page(self.request.GET.get('page'))
        }

        comments_count(context['page_obj'])

        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = get_user_model()
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email')
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        return get_user_model().objects.get(
            username=self.kwargs.get('username')
        )
