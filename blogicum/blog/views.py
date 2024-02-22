from django.contrib.auth.forms import UserCreationForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.core.paginator import Paginator
from django.http import Http404
from django.shortcuts import get_object_or_404, render
from django.urls import reverse, reverse_lazy
from django.views.generic import CreateView, DeleteView, ListView, UpdateView

from .constants import POSTS_PER_PAGE
from .forms import CommentForm, PostForm
from .mixins import CommentMixin, OnlyAuthorMixin, PostMixin
from .models import Category, Post, User
from .services import posts_annotate, posts_filter


def index(request):
    post_list = posts_filter(posts_annotate(Post.objects))

    context = {
        'page_obj': Paginator(
            post_list,
            POSTS_PER_PAGE
        ).get_page(request.GET.get('page'))
    }

    return render(
        request,
        'blog/index.html',
        context
    )


def post_detail(request, post_id):
    post = get_object_or_404(Post, pk=post_id)

    if request.user != post.author:
        post = get_object_or_404(
            posts_filter(Post.objects),
            pk=post_id
        )

    context = {
        'post': post,
        'form': CommentForm(),
        'comments': post.comments.select_related('author')
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
    post_list = posts_filter(posts_annotate(category.posts))

    context = {
        'category': category,
        'page_obj': Paginator(
            post_list,
            POSTS_PER_PAGE
        ).get_page(request.GET.get('page'))
    }

    return render(
        request,
        'blog/category.html',
        context
    )


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


class PostsUpdateView(PostMixin, UpdateView):

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={self.pk_url_kwarg: self.get_object().pk}
        )


class PostsDeleteView(PostMixin, DeleteView):
    pass


class CommentCreateView(CommentMixin, CreateView):

    def form_valid(self, form):
        form.instance.author = self.request.user
        form.instance.post = get_object_or_404(
            Post,
            pk=self.kwargs['post_id']
        )
        return super().form_valid(form)


class CommentUpdateView(CommentMixin, OnlyAuthorMixin, UpdateView):
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'com_id'


class CommentDeleteView(CommentMixin, OnlyAuthorMixin, DeleteView):
    template_name = 'blog/comment.html'
    pk_url_kwarg = 'com_id'


class ProfileListView(ListView):
    model = User
    template_name = 'blog/profile.html'
    paginate_by = POSTS_PER_PAGE

    def get_profile(self):
        return get_object_or_404(
            User,
            username=self.kwargs.get('username')
        )

    def get_queryset(self):
        posts = posts_annotate(self.get_profile().posts)
        if self.request.user != self.get_profile():
            posts = posts_filter(posts)
        return posts

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['profile'] = self.get_profile()
        return context


class ProfileEditView(LoginRequiredMixin, UpdateView):
    model = User
    template_name = 'blog/user.html'
    fields = ('first_name', 'last_name', 'username', 'email')
    success_url = reverse_lazy('blog:index')

    def get_object(self):
        if self.kwargs.get('username') != self.request.user.username:
            raise Http404
        return self.request.user


class UserCreateView(CreateView):
    form_class = UserCreationForm
    template_name = 'registration/registration_form.html'
    success_url = reverse_lazy('blog:index')
