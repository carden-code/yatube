from http import HTTPStatus

from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()
        cls.user = User.objects.create_user(username='Slava')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test-slug',
            description='Тестовое описание',
        )
        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовая группа',
        )

    def test_home_page(self):
        """Проверяем что страница работает корректно"""
        response = self.guest_client.get('/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_group_slug(self):
        """Проверяем что страница работает корректно"""
        path = reverse('posts:group_list', kwargs={'slug': self.group.slug})
        response = self.guest_client.get(path=path)
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_create_post_page(self):
        """Проверяем что происходит редирект
            не авторизованного пользователя"""
        path = reverse('posts:post_create')
        response = self.guest_client.get(path=path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_edit_post_page(self):
        """Проверяем что происходит редирект
            не авторизованного пользователя"""
        path = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        response = self.guest_client.get(path=path)
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)

    def test_not_found(self):
        """Проверяем не существующую страницу 404"""
        response = self.guest_client.get('/not_found/')
        self.assertEqual(response.status_code, HTTPStatus.NOT_FOUND.value)
        self.assertTemplateUsed(response, 'core/404.html')

    def test_create_redirect_anonymous(self):
        """Проверяем правильность редиректа, анонимного юзера"""
        path = reverse('posts:post_create')
        response = self.guest_client.get(path=path, follow=True)
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + path)

    def test_post_edit_redirect_anonymous(self):
        """Проверяем правильность редиректа, анонимного юзера"""
        path = reverse('posts:post_edit', kwargs={'post_id': self.post.id})
        response = self.guest_client.get(path=path, follow=True)
        self.assertRedirects(
            response, reverse('users:login') + '?next=' + path
        )

    def test_urls_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/': 'posts/index.html',
            f'/group/{self.group.slug}/': 'posts/group_list.html',
            f'/profile/{self.user}/': 'posts/profile.html',
            f'/posts/{self.post.id}/': 'posts/post_detail.html',
            f'/posts/{self.post.id}/edit/': 'posts/create_post.html',
            '/create/': 'posts/create_post.html'
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.authorized_client.get(address)
                self.assertTemplateUsed(response, template)
