import shutil
import tempfile
from http import HTTPStatus

from django.conf import settings
from django.contrib.auth import get_user_model
from django.core.files.uploadedfile import SimpleUploadedFile
from django.test import Client, TestCase, override_settings
from django.urls import reverse

from ..models import Group, Post

User = get_user_model()


class PostFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='test_group',
            slug='test_slug'
        )

        cls.post = Post.objects.create(
            text='Тестовый текст',
            group=cls.group,
            author=cls.user
        )

    def test_new_record_is_created_in_db(self):
        """При отправке валидной формы со страницы создания поста
            создаётся новая запись в базе данных"""
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'author': self.user
        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        first_post = Post.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertEqual(form_data['text'], first_post.text)
        self.assertEqual(self.user, first_post.author)
        self.assertEqual(self.post.group, first_post.group)

    def test_when_submitting_form_post_change(self):
        """При отправке валидной формы со страницы редактирования поста
            происходит изменение поста с post_id в базе данных."""
        form_data = {
            'text': self.post.text + 'Текст из формы',
            'group': self.post.group.id,
            'author': self.post.author
        }

        response = self.authorized_client.post(
            reverse('posts:post_edit', kwargs={'post_id': self.post.id}),
            data=form_data,
        )

        first_post = Post.objects.get(id=self.post.id)
        self.assertEqual(response.status_code, HTTPStatus.FOUND.value)
        self.assertEqual(form_data['text'], first_post.text)
        self.assertEqual(self.post.author, first_post.author)
        self.assertEqual(self.post.group, first_post.group)

    def test_guest_user_cannot_post(self):
        """При отправки формы со страницы
            создания поста не авторизованным пользователем,
            пост не создаётся в БД и происходит редирект."""

        count_posts = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id
        }

        response = self.client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        self.assertEqual(
            count_posts, Post.objects.count()
        )
        self.assertRedirects(
            response, reverse('users:login') + '?next='
            + reverse('posts:post_create')
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

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA_ROOT, ignore_errors=True)

    def test_new_record_is_created_in_db_image(self):
        """При отправке валидной формы со страницы создания поста
            с картинкой создаётся новая запись в базе данных"""
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
        posts_count = Post.objects.count()
        form_data = {
            'text': 'Текст из формы',
            'group': self.group.id,
            'author': self.user,
            'image': uploaded

        }

        response = self.authorized_client.post(
            reverse('posts:post_create'),
            data=form_data,
            follow=True
        )

        first_post = Post.objects.first()
        self.assertEqual(response.status_code, HTTPStatus.OK.value)
        self.assertEqual(posts_count + 1, Post.objects.count())
        self.assertEqual(form_data['text'], first_post.text)
        self.assertEqual(self.user, first_post.author)
        self.assertEqual(self.post.group, first_post.group)
        self.assertEqual(
            'posts/' + form_data['image'].name, first_post.image
        )


class CommentFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.client = Client()
        cls.authorized_client = Client()
        cls.authorized_client.force_login(cls.user)

        cls.group = Group.objects.create(
            title='Тестовая группа',
            slug='test_slug',
            description='Тестовое описание',
        )

        cls.post = Post.objects.create(
            author=cls.user,
            text='Тестовый пост',
            group=cls.group,
        )

    def test_only_authorized_user_can_comment_posts(self):
        """Проверяет, что комментировать посты может
            только авторизованный пользователь"""
        count_comment = self.user.comments.count()
        form_data = {
            'text': 'Текст из формы',
        }
        self.client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        self.assertEqual(count_comment, self.user.comments.count())

    def test_the_comment_appears_on_the_post_page(self):
        """Проверяет, что после успешной отправки
            комментарий появляется на странице поста"""
        count_comment = self.user.comments.count()
        form_data = {
            'text': 'Текст из формы',
        }
        response = self.authorized_client.post(
            reverse('posts:add_comment', kwargs={'post_id': self.post.id}),
            data=form_data,
            follow=True
        )
        resp = self.authorized_client.get(
            reverse('posts:post_detail', kwargs={'post_id': self.post.id}),
        )
        self.assertEqual(count_comment + 1, self.user.comments.count())
        self.assertRedirects(
            response,
            reverse('posts:post_detail', kwargs={'post_id': self.post.id})
        )
        self.assertEqual(
            form_data['text'], resp.context['comments'].first().text
        )
