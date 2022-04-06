from django.test import TestCase, Client
from http import HTTPStatus
from django.core.cache import cache

from ..models import Post, Group, User


class StaticURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nobody')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый description',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )

    def setUp(self):
        self.guest_client = Client()
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index(self):
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_group_list(self):
        response = self.guest_client.get(
            f'/group/{StaticURLTests.group.slug}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_profile(self):
        response = self.guest_client.get(
            f'/profile/{StaticURLTests.user.username}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_detail(self):
        response = self.guest_client.get(
            f'/posts/{StaticURLTests.post.pk}/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_authorized_client(self):
        response = self.authorized_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_create_guest_client(self):
        response = self.guest_client.get('/create/')
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_post_edit_authorized_client(self):
        response = self.authorized_client.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.OK)

    def test_post_edit_guest_client(self):
        response = self.guest_client.get(
            f'/posts/{StaticURLTests.post.pk}/edit/'
        )
        self.assertEqual(response.status_code, HTTPStatus.FOUND)

    def test_unexisting_page(self):
        response = self.guest_client.get('/unexisting_page/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND)

    def test_urls_uses_correct_template(self):
        cache.clear()
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{StaticURLTests.group.slug}/': 'posts/group_list.html',
            f'/profile/{StaticURLTests.user.username}/': 'posts/profile.html',
            f'/posts/{StaticURLTests.post.pk}/': 'posts/post_detail.html',
            '/create/': 'posts/create_post.html',
            f'/posts/{StaticURLTests.post.pk}/edit/': 'posts/create_post.html',
            '/unexisting_page/': 'core/404.html',
            '/follow/': 'posts/follow.html',
        }
        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
