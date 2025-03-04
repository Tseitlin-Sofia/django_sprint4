import logging

from django.contrib.auth.decorators import login_required
from django.contrib.auth.forms import PasswordResetForm, UserChangeForm
from django.contrib.auth.mixins import LoginRequiredMixin
from django.db.models import Count
from django.http import Http404
from django.shortcuts import get_object_or_404, redirect, render
from django.urls import reverse
from django.utils import timezone
from django.views.generic import (CreateView, DeleteView, DetailView, ListView,
                                  UpdateView)

from .forms import CommentForm, PostForm
from .mixins import OnlyAuthorMixin
from .models import Category, Comment, Post, User
from .utils import paginated_pages, send_email_to_admin

logger = logging.getLogger(__name__)


def password_reset(request):
    template = 'registration/registartion_form.html'
    if request.method == "POST":
        form = PasswordResetForm(request.POST)
        if form.is_valid():
            form.save(request=request)
            return redirect('password_reset_done')
    else:
        form = PasswordResetForm
    context = {'form': form}
    return render(request, template, context)


class PostListView(ListView):
    model = Post
    template_name = 'blog/index.html'

    def get_queryset(self):
        return Post.objects.select_related(
            'category',
            'location',
            'author',
        ).prefetch_related(
            'comments'
        ).filter(
            is_published=True,
            category__is_published=True,
            pub_date__lte=timezone.now()
        ).annotate(
            comment_count=Count('comments')
        ).order_by(
            '-pub_date'
        )

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        post_list = self.get_queryset()
        page_obj = paginated_pages(post_list, self.request)
        context['page_obj'] = page_obj
        return context


class PostCreateView(LoginRequiredMixin, CreateView):
    model = Post
    form_class = PostForm
    template_name = 'blog/create.html'

    def get_login_url(self):
        return reverse('login')

    def form_valid(self, form):
        form.instance.author = self.request.user
        new_post = super().form_valid(form)
        send_email_to_admin(form.instance, self.request.user)
        return new_post

    def get_success_url(self):
        return reverse(
            'blog:profile',
            kwargs={'username': self.request.user.username}
        )


class PostDetailView(DetailView):
    model = Post
    template_name = 'blog/detail.html'

    def get_context_data(self, **kwargs):
        post = self.object
        current_time = timezone.now()

        if post.author != self.request.user:
            if not post.is_published or not post.category.is_published:
                raise Http404("Этот пост доступен только автору публикации.")

            if post.pub_date > current_time:
                raise Http404("Этот пост доступен только автору публикации.")

        context = super().get_context_data(**kwargs)
        comments = self.object.comments.all()
        context['form'] = CommentForm()
        context['comments'] = comments.order_by('created_at')
        context['comment_count'] = comments.count()
        return context


def category_posts(request, category_slug):
    template = 'blog/category.html'
    category = get_object_or_404(
        Category,
        slug=category_slug,
        is_published=True
    )
    post_list = Post.objects.filter(
        category=category,
        is_published=True,
    ).annotate(comment_count=Count('comments'))
    post_list = PostListView().get_queryset().filter(category=category)
    page_obj = paginated_pages(post_list, request)
    context = {'page_obj': page_obj, 'category': category}
    return render(request, template, context)


def profile(request, username):
    user = get_object_or_404(User, username=username)
    posts = Post.objects.filter(
        author=user).annotate(
        comment_count=Count('comments')).order_by('-pub_date')
    page_obj = paginated_pages(posts, request)
    template = 'blog/profile.html'
    context = {
        'page_obj': page_obj,
        'profile': user
    }
    return render(request, template, context)


@login_required
def edit_profile(request):
    template = 'blog/edit_profile.html'
    user = request.user
    if request.method == 'POST':
        form = UserChangeForm(request.POST, instance=request.user)
        if form.is_valid():
            form.save()
            return redirect('blog:profile', username=request.user.username)
    else:
        form = UserChangeForm(instance=request.user)
    context = {
        'form': form,
        'user': user
    }
    return render(request, template, context)


class PostUpdateView(OnlyAuthorMixin, UpdateView):
    model = Post
    fields = ['title', 'text', 'category', 'location', 'image', 'pub_date']
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse(
            'blog:post_detail',
            kwargs={'pk': self.object.pk}
        )

    def dispatch(self, request, *args, **kwargs):
        if (
            not request.user.is_authenticated
                or self.get_object().author != request.user
        ):
            return redirect('blog:post_detail', pk=self.get_object().pk)
        return super().dispatch(request, *args, **kwargs)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, pk=post_id)
    form = CommentForm(request.POST)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('blog:post_detail', pk=post_id)


class CommentUpdateView(OnlyAuthorMixin, UpdateView):
    model = Comment
    fields = '__all__'
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})


class PostDeleteView(OnlyAuthorMixin, DeleteView):
    model = Post
    template_name = 'blog/create.html'

    def get_success_url(self):
        return reverse('blog:list')


class CommentDeleteView(OnlyAuthorMixin, DeleteView):
    model = Comment
    template_name = 'blog/comment.html'

    def get_success_url(self):
        return reverse('blog:post_detail', kwargs={'pk': self.object.post.pk})

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context.pop('form', None)
        return context
