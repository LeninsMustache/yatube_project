from django.shortcuts import render, get_object_or_404

from .models import Post, Group


SCREEN_POSTS = 10


def index(request):
    posts = Post.objects.select_related('group', 'author')[:SCREEN_POSTS]
    context = {
        'posts': posts,
    }
    return render(request, 'posts/index.html', context)


def group_posts(request, slug):
    group = get_object_or_404(Group, slug=slug)
    posts = group.group_posts.all()[:SCREEN_POSTS]
    context = {
        'group': group,
        'posts': posts,
    }
    return render(request, 'posts/group_list.html', context)
