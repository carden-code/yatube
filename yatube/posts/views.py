from django.contrib.auth import get_user_model
from django.contrib.auth.decorators import login_required
from django.core.paginator import Paginator
from django.shortcuts import get_object_or_404, redirect, render

from yatube.settings import NUMBER_OF_POSTS

from .forms import CommentForm, PostForm
from .models import Comment, Follow, Group, Post

User = get_user_model()


def pagination_process(req, obj, number) -> Paginator:
    paginator = Paginator(obj, number)
    page_number = req.GET.get('page')
    return paginator.get_page(page_number)


def index(request):
    """Обработчик главной страницы"""
    posts = Post.objects.all()
    page_obj = pagination_process(request, posts, NUMBER_OF_POSTS)
    template = 'posts/index.html'
    context = {
        'page_obj': page_obj
    }
    return render(request=request, template_name=template, context=context)


def group_posts(request, slug):
    """Обработчик груп постов"""
    group = get_object_or_404(Group, slug=slug)
    posts = group.posts.all()
    page_obj = pagination_process(request, posts, NUMBER_OF_POSTS)
    template = 'posts/group_list.html'
    context = {
        'group': group,
        'page_obj': page_obj
    }
    return render(request=request, template_name=template, context=context)


def profile(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    posts = author.posts.all()
    following = False
    if user.is_authenticated:
        followers_user = Follow.objects.filter(user=user)
        if followers_user:
            for object in followers_user:
                if object.author == author:
                    following = True
    page_obj = pagination_process(request, posts, NUMBER_OF_POSTS)
    template = 'posts/profile.html'
    context = {
        'posts_user': posts,
        'username': author,
        'page_obj': page_obj,
        'following': following
    }
    return render(request, template_name=template, context=context)


def post_detail(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form_comment = CommentForm()
    comments_post = Comment.objects.filter(post=post_id)
    user = post.author
    count_posts = user.posts.count()
    template = 'posts/post_detail.html'
    context = {
        'post': post,
        'count_posts': count_posts,
        'form': form_comment,
        'comments': comments_post
    }
    return render(request, template_name=template, context=context)


@login_required
def post_create(request):
    template = 'posts/create_post.html'
    form = PostForm(
        request.POST or None,
        files=request.FILES or None
    )

    if form.is_valid():
        post = form.save(commit=False)
        post.author = request.user
        post.save()
        return redirect('posts:profile', post.author)

    context = {
        'form': form
    }
    return render(request, template_name=template, context=context)


@login_required
def post_edit(request, post_id):
    post = get_object_or_404(Post, id=post_id)

    form = PostForm(
        request.POST or None,
        files=request.FILES or None,
        instance=post
    )
    if form.is_valid() and post.author == request.user:
        form.save()
        return redirect('posts:post_detail', post.id)

    template = 'posts/create_post.html'
    context = {
        'form': form,
    }
    return render(request, template_name=template, context=context)


@login_required
def add_comment(request, post_id):
    post = get_object_or_404(Post, id=post_id)
    form = CommentForm(request.POST or None)
    if form.is_valid():
        comment = form.save(commit=False)
        comment.author = request.user
        comment.post = post
        comment.save()
    return redirect('posts:post_detail', post_id=post_id)


@login_required
def follow_index(request):
    """Обработчик страницы подписок"""
    user = get_object_or_404(User, username=request.user)
    posts = Post.objects.filter(author__following__user=user)
    page_obj = pagination_process(request, posts, NUMBER_OF_POSTS)
    template = 'posts/follow.html'
    context = {
        'page_obj': page_obj
    }
    return render(request=request, template_name=template, context=context)


@login_required
def profile_follow(request, username):
    # Подписаться на автора
    author = get_object_or_404(User, username=username)
    user = request.user
    if author != user:
        follow_user = Follow.objects.filter(user=user)
        following = False

        if follow_user:
            for object in follow_user:
                if object.author == author:
                    following = True

        if not following:
            follow = Follow.objects.create(
                user=user,
                author=author
            )
            follow.save()
    return redirect('posts:profile', username=username)


@login_required
def profile_unfollow(request, username):
    author = get_object_or_404(User, username=username)
    user = request.user
    follow_user = Follow.objects.filter(user=user)
    if follow_user:
        for object in follow_user:
            if object.author == author:
                object.delete()
    return redirect('posts:profile', username=username)
