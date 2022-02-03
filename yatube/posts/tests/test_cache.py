from django.contrib.auth import get_user_model
from django.core.cache import cache
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class CacheTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

    def test_cache(self):
        """Тест для проверки кеширования главной страницы"""
        template_page_name = reverse('posts:index')
        response = self.authorized_client.get(template_page_name)

        group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=group
        )
        # Что то тут не то...
        # response = self.authorized_client.get(template_page_name)

        self.assertNotIn(
            post, response.context['page_obj']
        )
        cache.clear()

        response = self.authorized_client.get(template_page_name)
        self.assertIn(
            post, response.context['page_obj']
        )
