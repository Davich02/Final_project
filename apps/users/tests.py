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


class UserProfileTests(APITestCase):
    def setUp(self):
        self.user = User.objects.create_user(email='user@test.com', password='TestPass123!')
        self.client.force_authenticate(user=self.user)

    def test_new_user_is_tenant(self):
        response = self.client.get('/api/users/me/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data['roles'], ['Tenants'])

    def test_update_profile(self):
        response = self.client.patch('/api/users/me/', {'first_name': 'Anna'})
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.user.refresh_from_db()
        self.assertEqual(self.user.first_name, 'Anna')

    def test_become_landlord(self):
        response = self.client.post('/api/users/become-landlord/')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertCountEqual(response.data['roles'], ['Tenants', 'Landlords'])

        response = self.client.post('/api/users/become-landlord/')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_anonymous_cant_become_landlord(self):
        self.client.force_authenticate(user=None)
        response = self.client.post('/api/users/become-landlord/')
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)
