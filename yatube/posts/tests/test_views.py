from time import sleep

from django.test import Client, TestCase
from django.urls import reverse
from django import forms
from django.core.cache import cache

from yatube.settings import POSTS_NUMBER, NUMBER_OF_POSTS_CREATED
from ..models import Post, Group, User, Comment, Follow


class PostViewsTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nobody')
        cls.user_not_author = User.objects.create_user(username='test_user')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый description',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
            description='Тестовый description2',
        )
        cls.post = Post.objects.create(
            text='Тестовый текст',
            author=cls.user,
            group=cls.group,
        )
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user_not_author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_pages_uses_correct_template(self):
        cache.clear()
        templates_pages_names = {
            reverse('posts:index'): 'posts/index.html',
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            ):
            'posts/group_list.html',
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            ):
            'posts/profile.html',
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            ):
            'posts/post_detail.html',
            reverse('posts:post_create'): 'posts/create_post.html',
            reverse(
                'posts:post_edit',
                kwargs={'post_id': self.post.pk},
            ):
            'posts/create_post.html',
            reverse('posts:follow_index'): 'posts/follow.html',
        }
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(template=template):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_post_index_page_show_correct_context(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.user.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
        }
        self.assertIn('page_obj', response.context)
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_posts_groups_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug}))
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.user.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
        }
        self.assertIn('page_obj', response.context)
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_profile_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        first_object = response.context['page_obj'][0]
        context_objects = {
            self.user.id: first_object.author.id,
            self.post.text: first_object.text,
            self.group.slug: first_object.group.slug,
            self.post.id: first_object.id,
        }
        self.assertIn('page_obj', response.context)
        for reverse_name, response_name in context_objects.items():
            with self.subTest(reverse_name=reverse_name):
                self.assertEqual(response_name, reverse_name)

    def test_post_post_detail_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_detail',
                kwargs={'post_id': self.post.pk},
            )
        )
        self.assertEqual(response.context['post'].text, self.post.text)
        self.assertEqual(response.context['post'].author, self.user)
        self.assertEqual(response.context['post'].group, self.group)
        self.assertEqual(response.context['comments'][0], self.comment)

    def test_create_page_show_correct_context(self):
        response = self.authorized_client.get(reverse('posts:post_create'))
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        response = self.authorized_client.get(
            reverse(
                'posts:post_edit',
                kwargs={'post_id': '1'},
            )
        )
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.fields.ChoiceField,
            'image': forms.fields.ImageField,
        }

        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                self.assertIsInstance(form_field, expected)

class PaginatorViewsTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nobody')
        cls.group = Group.objects.create(
            title='Тестовый заголовок',
            slug='test-slug',
            description='Тестовый description',
        )
        cls.group_2 = Group.objects.create(
            title='Тестовый заголовок2',
            slug='test-slug2',
            description='Тестовый description2',
        )
        for i in range(NUMBER_OF_POSTS_CREATED):
            cls.post = Post.objects.create(
                text='Тестовый текст' + str(i),
                author=cls.user,
                group=cls.group,
            )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_index_first_page_contains_ten_records(self):
        cache.clear()
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(len(response.context['page_obj']), POSTS_NUMBER)

    def test_index_second_page_contains_three_records(self):
        response = self.authorized_client.get(
            reverse('posts:index') + '?page=2'
        )
        self.assertEqual(
            len(response.context['page_obj']),
            NUMBER_OF_POSTS_CREATED - POSTS_NUMBER
        )

    def test_group_list_first_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:group_list',
                kwargs={'slug': self.group.slug},
            )
        )
        self.assertEqual(len(response.context['page_obj']), POSTS_NUMBER)

    def test_group_list_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:group_list',
            kwargs={'slug': self.group.slug}) + '?page=2',
        )
        self.assertEqual(
            len(response.context['page_obj']),
            NUMBER_OF_POSTS_CREATED - POSTS_NUMBER
        )

    def test_profile_first_page_contains_ten_records(self):
        response = self.authorized_client.get(
            reverse(
                'posts:profile',
                kwargs={'username': self.user.username},
            )
        )
        self.assertEqual(len(response.context['page_obj']), POSTS_NUMBER)

    def test_profile_second_page_contains_three_records(self):
        response = self.authorized_client.get(reverse(
            'posts:profile',
            kwargs={'username': self.user.username}) + '?page=2',
        )
        self.assertEqual(
            len(response.context['page_obj']),
            NUMBER_OF_POSTS_CREATED - POSTS_NUMBER
        )

class СacheTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nobody')
        cls.user_not_author = User.objects.create_user(username='test_user')
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
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user_not_author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_cache(self):
        response_before = self.authorized_client.get(reverse('posts:index'))
        Post.objects.create(text='Кештекст', author=self.user, group=self.group)
        response_after = self.authorized_client.get(reverse('posts:index'))
        self.assertEqual(response_before.content, response_after.content)

        sleep(21)
        response = self.authorized_client.get(reverse('posts:index'))
        self.assertNotEqual(response_before.content, response.content)

class FollowTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Nobody')
        cls.user_not_author = User.objects.create_user(username='test_user')
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
        cls.comment = Comment.objects.create(
            text='Тестовый комментарий',
            post=cls.post,
            author=cls.user_not_author,
        )

    def setUp(self):
        self.authorized_client = Client()
        self.authorized_client.force_login(self.user)

    def test_auth_follow(self):
        self.authorized_client.get(
            reverse('posts:profile_follow',
            kwargs={'username': self.user_not_author.username}
            )
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=self.user_not_author).exists(),
            True
        )

        self.authorized_client.get(
            reverse('posts:profile_unfollow',
            kwargs={'username': self.user_not_author.username}
            )
        )
        self.assertIs(
            Follow.objects.filter(user=self.user, author=self.user_not_author).exists(),
            False
        )

    def test_new_post(self):
        Follow.objects.create(user=self.user, author=self.user_not_author)
        post = Post.objects.create(
            author=self.user_not_author, 
            text='qwerty',
            group=self.group,
        )
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertIn(post, response.context['page_obj'].object_list)

        self.authorized_client.logout()
        any_user = User.objects.create_user(
            username='user_another'
        )
        self.authorized_client.force_login(any_user)
        response = self.authorized_client.get(reverse('posts:follow_index'))
        self.assertNotIn(post, response.context['page_obj'].object_list)

