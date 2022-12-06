from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post
from ..forms import PostForm

NUMBER_OF_TEST_POSTS = 13


User = get_user_model()


class PostFormTests(TestCase):
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
        cls.form = PostForm()

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        Post.objects.create(
            author=self.user,
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

    def test_create_post(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый пос',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True,
        )
        self.assertRedirects(response, reverse(
            'posts:profile', kwargs={
                'username': self.post.author.username,
            }))
        self.assertEqual(Post.objects.count(), post_count + 1)
        self.assertTrue(
            Post.objects.filter(
                text=form_data['text'],
                group=form_data['group'],
                author=self.post.author
            ).exists()
        )

    def test_post_edit(self):
        post_count = Post.objects.count()
        form_data = {
            'text': 'Тестовый тек',
            'group': self.group.pk,
        }
        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.pk}),
            data=form_data,
            follow=True)
        self.assertRedirects(response, reverse(
            'posts:post_detail', kwargs={
                'post_id': self.post.pk
            }))
        self.assertEqual(Post.objects.count(), post_count)
        self.assertTrue(Post.objects.filter(
            text=form_data['text'],
            group=form_data['group'],
            author=self.post.author
        ).exists())
