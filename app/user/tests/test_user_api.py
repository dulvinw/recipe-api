from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
ME = reverse('user:me')


def create_user(**params):
    return get_user_model().objects.create_user(**params)


class PublicUserApiTest(TestCase):
    """Test the users API (Public)"""

    def setup(self):
        self.client = APIClient()

    def test_create_valid_user_success(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'test@test.com',
            'password': 'testPass',
            'name': 'TestName'
        }
        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(**res.data)
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', res.data)

    def test_user_exist(self):
        """Test creating a user that already exists"""
        payload = {
            'email': 'test@test.com',
            'password': 'testPass',
            'name': 'TestUser'
        }
        create_user(**payload)

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short(self):
        """Password should be atleas 5 characters long"""
        payload = {
            'email': 'test@test.com',
            'password': 'pwd',
            'name': 'TestUser'
        }

        res = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(
            email=payload['email']
        ).exists()
        self.assertFalse(user_exists)

    def test_create_token_user(self):
        """Test creating token for user"""
        payload = {
            'email': 'test@test.com',
            'password': 'pwd123',
            'name': 'TestUser'
        }

        create_user(**payload)
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertIn('token', res.data)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created for invalid credentials"""
        payload = {
            'email': 'test@test.com',
            'password': 'pwd123',
            'name': 'TestUser'
        }

        create_user(email='test@test.com', password='test123')
        res = self.client.post(TOKEN_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('token', res.data)

    def test_create_token_user_not_in(self):
        """Test that token is not created when user is not found"""
        create_user(email='test@test.com', password='test123')

        payload = {
            'email': 'test@gmail.com',
            'password': 'test123',
            'name': 'TestUser'
        }
        res = self.client.post(TOKEN_URL, payload)

        self.assertNotIn('token', res.data)
        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)

    def test_unauthorized_access(self):
        """Test unauthorized access for user endpoint"""
        res = self.client.get(ME)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTests(TestCase):
    """
    Test private user apis
    """

    def setUp(self):
        self.user = create_user(
            name='TestUser',
            email='test@test.com',
            password='password'
        )
        self.client = APIClient()
        self.client.force_authenticate(self.user)

    def test_profile_for_already_logged_in_user(self):
        """Test retrieve current logged in user"""
        res = self.client.get(ME)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, {
            'name': 'TestUser',
            'email': 'test@test.com'
        })

    def test_post_not_allowed(self):
        """Test that post is not allowed on ME urs"""
        res = self.client.post(ME, {})

        self.assertEqual(res.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating the user profile"""
        payload = {
            'name': 'New Name',
            'email': 'new@new.com',
            'password': 'newPassword'
        }

        self.client.put(ME, payload)

        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(self.user.email, payload['email'])
        self.assertTrue(self.user.check_password(payload['password']))
