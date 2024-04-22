from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse, reverse_lazy

User = get_user_model()


class LoginLogoutRegisterTests(TestCase):
    def setUp(self) -> None:
        self.user = User.objects.create_user(username="ssava", email="ssava@gmail.com", password="example_pass32523")

    def test_login(self):
        url = reverse('login')
        data = {'username': 'ssava', 'password': 'example_pass32523'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url == '/')

    def test_logout(self):
        self.client.force_login(user=self.user)
        url = reverse('logout')
        response = self.client.get(url)
        self.assertEqual(response.status_code, 302)
        self.assertTrue(response.url == '/')
        response_after_logout = self.client.get(reverse('orders'))
        self.assertEqual(response_after_logout.status_code, 302)
        self.assertTrue(response_after_logout.url.startswith('/login/'))

    def test_register(self):
        url = reverse('register')
        data = {
            'username': 'ssava2',
            "email": "ssava2@gmail.com",
            'password1': 'example423gw2',
            'password2': 'example423gw2'
        }
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 302)
        self.assertRedirects(response, reverse_lazy('login'))
        self.assertEqual(User.objects.count(), 2)
        self.assertTrue(User.objects.filter(username=data['username']).exists())

    def test_register_with_existing_username(self):
        url = reverse('register')
        data = {'username': self.user.username, 'password1': 'example423gw2', 'password2': 'example423gw2'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(response.context['form'].has_error('username'))

    def test_register_with_existing_email(self):
        url = reverse('register')
        data = {'username': "test", "email": self.user.email, 'password1': 'example423gw2', 'password2': 'example423gw2'}
        response = self.client.post(url, data)
        self.assertEqual(response.status_code, 200)
        self.assertEqual(User.objects.count(), 1)
        self.assertTrue(response.context['form'].has_error('email'))

