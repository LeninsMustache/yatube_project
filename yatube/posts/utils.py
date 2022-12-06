from django.core.paginator import Paginator

SCREEN_POSTS = 10


def show_paginator(request, post_list,):
    paginator = Paginator(post_list, SCREEN_POSTS)
    page_number = request.GET.get('page')
    page_obj = paginator.get_page(page_number)
    return page_obj
