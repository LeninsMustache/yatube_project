from django.test import Client, TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from ..models import Post, Group

FIRST_PAGE_SCREEN_POSTS = 10
NUMBER_OF_TEST_POSTS = 15
SECOND_PAGE_SCREEN_POSTS = 5


User = get_user_model()


class PaginatorViewTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='author')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            description='Тестовое описание',
            slug='test-slug')
        context = []
        for i in range(NUMBER_OF_TEST_POSTS):
            context.append(Post(
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group,
            ))
            cls.post = Post.objects.create(
                author=cls.user,
                text='Тестовый текст поста',
                group=cls.group,
            )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_page_contains_ten_records(self):
        first_page = {
            reverse('posts:index'): FIRST_PAGE_SCREEN_POSTS,
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }): FIRST_PAGE_SCREEN_POSTS,
            reverse('posts:profile', kwargs={
                'username': self.user
            }): FIRST_PAGE_SCREEN_POSTS,
            reverse('posts:index') + '?page=2': SECOND_PAGE_SCREEN_POSTS,
            reverse('posts:group_list', kwargs={
                'slug': self.group.slug
            }) + '?page=2': SECOND_PAGE_SCREEN_POSTS,
            reverse('posts:profile', kwargs={
                'username': self.user
            }) + '?page=2': SECOND_PAGE_SCREEN_POSTS,
        }
        for value, expected in first_page.items():
            with self.subTest(value=value):
                response = self.authorized_client.get(value)
                self.assertEqual(
                    len(response.context['page_obj']), expected)
