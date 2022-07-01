from django.contrib.auth import get_user_model
from django.test import Client, TestCase
from django.urls import reverse

User = get_user_model()


class UserFormTest(TestCase):
    @classmethod
    def setUpClass(cls):
        super().setUpClass()
        cls.user = User.objects.create_user(username='Slava')
        cls.client = Client()

    def test_new_record_is_created_in_db(self):
        """при заполнении формы 'users:signup'
            создаётся новый пользователь."""
        users_count = User.objects.count()
        form_data = {
            'username': 'Kolya',
            'password1': 'dima2222',
            'password2': 'dima2222'
        }

        self.client.post(
            reverse('users:signup'),
            data=form_data,
            follow=True
        )
        self.assertEqual(users_count + 1, User.objects.count())
