import shutil
import tempfile

from django import forms
from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from yatube.settings import NUMBER_OF_POSTS

from ..models import Follow, Group, Post

User = get_user_model()


class PostPagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.group_2 = Group.objects.create(
            title='Тестовая группа 2',
            slug='test_slug_2',
            description='Тестовое описание 2',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group
        )

    # Проверяем используемые шаблоны
    def test_pages_uses_correct_template(self):
        """URL-адрес использует соответствующий шаблон."""
        # Собираем в словарь пары "reverse(name): имя_html_шаблона"
        slug = self.group.slug
        username = self.user
        post_id = self.post.id
        templates_pages_names = {
            reverse("posts:index"):
                'posts/index.html',
            reverse("posts:group_list", kwargs={"slug": slug}):
                'posts/group_list.html',
            reverse("posts:profile", kwargs={"username": username}):
                'posts/profile.html',
            reverse("posts:post_edit", kwargs={"post_id": post_id}):
                'posts/create_post.html',
            reverse("posts:post_detail", kwargs={"post_id": post_id}):
                'posts/post_detail.html',
            reverse("posts:post_create"):
                'posts/create_post.html',
        }

        # Проверяем, что при обращении к name вызывается соответствующий шаблон
        for reverse_name, template in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertTemplateUsed(response, template)

    def test_index_page_show_correct_context(self):
        """Шаблон index сформирован с правильным контекстом."""
        response = self.authorized_client.get(reverse('posts:index'))
        first_object = response.context['page_obj'][-1]
        post_text = first_object.text
        post_group = first_object.group
        post_author = first_object.author
        self.assertEqual(post_text, self.post.text)
        self.assertEqual(post_group, self.group)
        self.assertEqual(post_author, self.user)

    def test_group_page_show_correct_context(self):
        """Шаблон group_list сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:group_list', kwargs={'slug': self.group.slug})
        )
        post = response.context['page_obj'][-1]
        self.assertEqual(post.group.slug, self.group.slug)

    def test_profile_page_show_correct_context(self):
        """Шаблон profile сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:profile', kwargs={'username': self.user})
        )
        post = response.context['posts_user'][0]
        self.assertEqual(post.author, self.user)

    def test_detail_page_show_correct_context(self):
        """Шаблон post_detail сформирован с правильным контекстом"""
        post_id = self.post.id
        response = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': post_id})
        )
        post_context = response.context['post']
        self.assertEqual(post_context.id, post_id)

    def test_create_page_show_correct_context(self):
        """Шаблон create_post сформирован с правильным контекстом"""
        response = self.authorized_client.get(reverse('posts:post_create'))
        # Словарь ожидаемых типов полей формы:
        # указываем, объектами какого класса должны быть поля формы
        form_fields = {
            'text': forms.fields.CharField,
            'group': forms.models.ModelChoiceField
        }

        # Проверяем типы полей формы в словаре context
        for value, expected in form_fields.items():
            with self.subTest(value=value):
                form_field = response.context.get('form').fields.get(value)
                # Проверяет, что поле формы является экземпляром
                # указанного класса
                self.assertIsInstance(form_field, expected)

    def test_edit_page_show_correct_context(self):
        """Шаблон post_edit сформирован с правильным контекстом"""
        response = self.authorized_client.get(
            reverse('posts:post_edit', kwargs={"post_id": self.post.id})
        )

        form = response.context['form'].initial['text']
        self.assertEqual(form, self.post.text)

    def test_post_with_group_on_pages(self):
        """Проверяет, что если при создании поста указать группу,
            то этот пост появляется: на главной странице сайта,
            на странице выбранной группы, в профайле пользователя."""
        templates_pages_names = {
            reverse("posts:index"):
                'posts/index.html',
            reverse("posts:group_list", kwargs={"slug": self.group.slug}):
                'posts/group_list.html',
            reverse("posts:profile", kwargs={"username": self.user}):
                'posts/profile.html',
        }

        for reverse_name, _ in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertIn(
                    self.post, response.context['page_obj']
                )

    def test_post_did_not_fall_into_another_group(self):
        """Проверяет, что этот пост не попал в группу,
            для которой не был предназначен"""
        template_page = reverse(
            'posts:group_list', kwargs={'slug': self.group_2.slug}
        )
        response = self.authorized_client.get(template_page)
        self.assertNotIn(
            self.post, response.context['page_obj']
        )


class PostPaginationTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.posts = [
            Post(
                id=i,
                author=cls.user,
                text=f'Тестовый пост {i}',
                group=cls.group
            )
            for i in range(1, 14)
        ]

        Post.objects.bulk_create(cls.posts)

    def test_first_page_contains_ten_records(self):
        """Проверка: количество постов на первой странице равно 10"""
        templates_pages_names = {
            reverse("posts:index"):
                'posts/index.html',
            reverse("posts:group_list", kwargs={"slug": self.group.slug}):
                'posts/group_list.html',
            reverse("posts:profile", kwargs={"username": self.user}):
                'posts/profile.html',
        }

        for reverse_name, _ in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    len(response.context['page_obj']), NUMBER_OF_POSTS
                )

    def test_second_page_contains_three_records(self):
        """Проверка: на второй странице должно быть три поста"""
        templates_pages_names = {
            reverse("posts:index"):
                'posts/index.html',
            reverse("posts:group_list", kwargs={"slug": self.group.slug}):
                'posts/group_list.html',
            reverse("posts:profile", kwargs={"username": self.user}):
                'posts/profile.html',
        }

        for reverse_name, _ in templates_pages_names.items():
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name + '?page=2')
                count_posts = Post.objects.count() % NUMBER_OF_POSTS
                self.assertEqual(
                    len(response.context['page_obj']), count_posts
                )


# Создаем временную папку для медиа-файлов;
# на момент теста медиа папка будет переопределена
TEMP_MEDIA_ROOT = tempfile.mkdtemp(dir=settings.BASE_DIR)


@override_settings(MEDIA_ROOT=TEMP_MEDIA_ROOT)
class PostImagesTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        small_gif = (
            b'\x47\x49\x46\x38\x39\x61\x02\x00'
            b'\x01\x00\x80\x00\x00\x00\x00\x00'
            b'\xFF\xFF\xFF\x21\xF9\x04\x00\x00'
            b'\x00\x00\x00\x2C\x00\x00\x00\x00'
            b'\x02\x00\x01\x00\x00\x02\x02\x0C'
            b'\x0A\x00\x3B'
        )
        uploaded = SimpleUploadedFile(
            name='small.gif',
            content=small_gif,
            content_type='image/gif'
        )

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
            image=uploaded
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_post_with_image_on_pages(self):
        """Проверяет, что при выводе поста с картинкой
            изображение передаётся в словаре context."""
        templates_pages_names = [
            reverse("posts:index"),
            reverse("posts:group_list", kwargs={"slug": self.group.slug}),
            reverse("posts:profile", kwargs={"username": self.user})
        ]
        for reverse_name in templates_pages_names:
            with self.subTest(reverse_name=reverse_name):
                response = self.authorized_client.get(reverse_name)
                self.assertEqual(
                    self.post.image, response.context['page_obj'][-1].image
                )

    def test_post_with_image_on_pages_detail(self):
        """Проверяет, что при выводе поста с картинкой
            изображение передаётся в словаре context."""
        template_page = reverse(
            "posts:post_detail", kwargs={"post_id": self.post.id}
        )
        response = self.authorized_client.get(template_page)
        self.assertEqual(
            self.post.image, response.context['post'].image
        )


class FollowTests(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.user_2 = User.objects.create_user(username='Vova')
        cls.authorized_client = Client()
        cls.authorized_client_2 = Client()
        cls.authorized_client.force_login(cls.user)
        cls.authorized_client_2.force_login(cls.user_2)

    def test_authorized_user_can_follow_other_users(self):
        """Авторизованный пользователь может подписываться
            на других пользователей и удалять их из подписок."""
        author = self.user_2
        self.authorized_client.post(
            reverse("posts:profile_follow", kwargs={"username": author})
        )
        follow = Follow.objects.filter(user=self.user)
        self.assertEqual(author, follow[0].author)

    def test_authorized_user_can_delete_subscription(self):
        """Авторизованный пользователь может удалять подписку."""
        author = self.user_2
        self.authorized_client.post(
            reverse("posts:profile_follow", kwargs={"username": author})
        )
        count_follow = Follow.objects.filter(user=self.user).count()
        self.authorized_client.post(
            reverse("posts:profile_unfollow", kwargs={"username": author})
        )
        count_follow_after = Follow.objects.filter(user=self.user).count()
        self.assertEqual(count_follow_after + 1, count_follow)

    def test_new_post_appears_in_feed_those_follow_him(self):
        """Новая запись пользователя появляется в ленте тех,
            кто на него подписан и не появляется в ленте тех,
            кто не подписан."""
        author = self.user_2
        self.authorized_client.post(
            reverse("posts:profile_follow", kwargs={"username": author})
        )
        group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )
        post = Post.objects.create(
            author=self.user_2,
            text='Тестовый пост',
            group=group
        )
        response = self.authorized_client.get(
            reverse("posts:follow_index")
        )
        response_2 = self.authorized_client_2.get(
            reverse("posts:follow_index")
        )
        self.assertIn(post, response.context['page_obj'])
        self.assertNotIn(post, response_2.context['page_obj'])
