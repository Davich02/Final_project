from rest_framework.test import APITestCase
from rest_framework import status
from apps.users.models import User


class RegisterTests(APITestCase):
    def test_weak_password_rejected(self):
        response = self.client.post('/api/users/register/', {
            'email': 'weak@test.com',
            'password': '12345678',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_strong_password_creates_user(self):
        response = self.client.post('/api/users/register/', {
            'email': 'strong@test.com',
            'password': 'MyStr0ngP@ssword',
            'first_name': 'Test',
            'last_name': 'User',
        })
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertTrue(User.objects.filter(email='strong@test.com').exists())