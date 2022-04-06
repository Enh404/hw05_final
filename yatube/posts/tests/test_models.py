from django.test import TestCase

from ..models import Group, Post, User


class PostModelTest(TestCase):
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
            text='Тестовый текст для проверки',
            author=cls.user,
            group=cls.group,
        )

    def test_model_post_have_correct_object_names(self):
        post = PostModelTest.post
        self.assertEqual(post.text[:15], str(post))

    def test_model_group_have_correct_object_names(self):
        group = PostModelTest.group
        self.assertEqual(group.title, str(group))
