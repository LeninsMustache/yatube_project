from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug',
            description='test_description',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.user = User.objects.create_user(username='admin')
        self.user_for_test_edit = User.objects.create_user(username='NoName')
        self.authorized_client_for_edit = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)
        self.authorized_client_for_edit.force_login(self.user_for_test_edit)
        self.group = Group.objects.create(
            title='test',
            description='test',
            slug='test-slug'
        )
        self.post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=self.group
        )

    def test_urls_templates(self):
        template_url_name = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user.username}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
        }
        for adress, template in template_url_name.items():
            with self.subTest(adress=adress):
                response = self.authorized_client.get(adress)
                self.assertTemplateUsed(response, template)

    def test_404_url(self):
        response_url = {
            self.guest_client: '/page-not-found/',
            self.authorized_client: '/and-not-found-too/',
        }
        for client, url in response_url.items():
            with self.subTest(client=client):
                response = self.client.get(url)
                self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_home_url_exists_at_desired_location(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list_exists_at_desired_location(self):
        response = self.guest_client.get(f'/group/{self.group.slug}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile_exists_at_desired_location(self):
        response = self.guest_client.get(f'/profile/{self.user.username}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail_exists_at_desired_location(self):
        response = self.guest_client.get(f'/posts/{self.post.pk}/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_access_right(self):
        response = self.guest_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.authorized_client.get(f'/posts/{self.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
        response = self.authorized_client_for_edit.get(
            f'/posts/{PostURLTests.post.pk}/edit/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_create_post_access_right(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)
