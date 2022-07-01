from http import HTTPStatus

from django.test import Client, TestCase
from django.urls.base import reverse


class AboutURLTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.guest_client = Client()

    def test_aboutpage(self):
        """Проверяем что страница работает корректно (200 - OK)"""
        response = self.guest_client.get('/about/author/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_techpage(self):
        """Проверяем что страница работает корректно (200 - OK)"""
        response = self.guest_client.get('/about/tech/')
        self.assertEqual(response.status_code, HTTPStatus.OK.value)

    def test_urls_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        templates_url_names = {
            '/about/author/': 'about/author.html',
            '/about/tech/': 'about/tech.html',
        }

        for address, template in templates_url_names.items():
            with self.subTest(address=address):
                response = self.guest_client.get(address)
                self.assertTemplateUsed(response, template)

    def test_pages_uses_correct_template(self):
        """Namespace использует соответствующий шаблон."""
        templates_pages_names = {
            f'{reverse("about:author")}': 'about/author.html',
            f'{reverse("about:tech")}': 'about/tech.html'
        }

        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.guest_client.get(reverse_name)
                self.assertTemplateUsed(response, template)
