from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse
from django import forms

from ..models import Group, Post
from ..tests import test_paginator_view

NUMBER_OF_TEST_POSTS = 13


User = get_user_model()


class ViewsPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug'
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый текст поста',
            group=cls.group,
        )

    def setUp(self):
        self.user = User.objects.create_user(username='Mikhail')
        self.second_user = User.objects.create_user(username='Julia')
        self.guest_client = Client()
        self.authorized_client = Client()
        self.another_authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.another_authorized_client.force_login(self.second_user)
        Post.objects.create(
            author=self.second_user,
            text='Тестовый пост',
            group=Group.objects.create(
                title='--empty--',
                description='--empty--',
                slug='test-slug-2',
            )
        )
        context = []
        for i in range(NUMBER_OF_TEST_POSTS):
            context.append(Post.objects.create(
                author=self.user,
                text='Тестовый текст поста',
                group=self.group,
            ))

    def test_pages_uses_correct_template(self):
        templates_pages_names = {
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse('posts:index'): 'posts/index.html',
            reverse('posts:group_list', kwargs={
                'slug': 'test-slug'
            }): 'posts/group_list.html',
            reverse('posts:profile', kwargs={
                'username': 'author'
            }): 'posts/profile.html',
            reverse('posts:post_detail', kwargs={
                'post_id': '5'
            }): 'posts/post_detail.html',
            reverse('posts:post_edit', kwargs={
                'post_id': '5'
            }): 'posts/create_post.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_paginator_view(self):
        test_paginator_view.PaginatorViewTests()

    def test_index_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:index'))
        page_objects = response.context['page_obj']
        self.assertEqual(len(page_objects), 10)

    def test_group_list_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': 'test-slug'}))
        page_objects = response.context['page_obj']
        for obj in page_objects:
            self.assertEqual(obj.group, self.group)

    def test_profile_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user.username}))
        page_objects = response.context['page_obj']
        for obj in page_objects:
            self.assertEqual(obj.author.username, self.user.username)

    def test_post_detail_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': '1'}))
        first_object = response.context['post']
        post_author_0 = first_object.author.username
        post_text_0 = first_object.text
        post_group_0 = first_object.group.title
        self.assertEqual(post_author_0, 'author')
        self.assertEqual(post_text_0, 'Тестовый текст поста')
        self.assertEqual(post_group_0, 'Тестовый заголовок')

    def test_create_post_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField,
        }
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
            self.assertIsInstance(form_field, expected)

    def test_created_post_is_shown(self):
        new_post = Post.objects.create(
            author=self.second_user,
            text='Тестовый пост',
            group=Group.objects.create(
                title='new_group',
                description='--empty--',
                slug='test-slug-3',
            )
        )
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertContains(response, new_post)
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': new_post.group.slug}))
        self.assertContains(response, new_post)
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={
                'username': new_post.author.username,
            }))
        self.assertContains(response, new_post)
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        self.assertNotContains(response, new_post)
