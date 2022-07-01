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
        cache.clear()

    def test_cache(self):
        """Тест для проверки кеширования главной страницы"""
        template_page_name = reverse('posts:index')
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        # 1. Создаём пост.
        post = Post.objects.create(
            author=self.user,
            text='Тестовый пост',
            group=group
        )
        # 2. Смотрим на страницу, сохраняем контент.
        response = self.authorized_client.get(template_page_name)
        content_page = response.content
        # 3. Удаляем пост.
        post.delete()
        # 4. Снова смотрим на страницу и сохраняем контент.
        response_2 = self.authorized_client.get(template_page_name)
        content_2_page = response_2.content
        # 5. Сравниваем контент из пункта 2 и 4, должны совподать.
        self.assertEqual(content_page, content_2_page)
        # 6. Чистим кэш.
        cache.clear()
        # 7. Снова смотрим на страницу и сохраняем контент.
        response_3 = self.authorized_client.get(template_page_name)
        content_3_page = response_3.content
        # 8. Теперь контенты не совпадают
        self.assertNotEqual(content_page, content_3_page)
