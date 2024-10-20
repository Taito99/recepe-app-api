"""Tests for the use Api"""

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework.test import APIClient
from rest_framework import status

CREATE_USER_URL = reverse('user:create')
TOKEN_URL = reverse('user:token')
REFRESH_TOKEN_URL = reverse('user:token_refresh')
ME_URL = reverse('user:me')

def create_user(**user_data):
    """Create a new user"""
    return get_user_model().objects.create_user(**user_data)

class PublicUserApiTest(TestCase):
    """Test the Public user Api"""
    def setUp(self):
        self.client = APIClient()

    def test_create_user_successful(self):
        """Test creating user with valid payload is successful"""
        payload = {
            'email': 'testuserapi@example.com',
            'password': 'PAssword1233',
            'name': 'testuserapi1',
        }
        response = self.client.post(CREATE_USER_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        user = get_user_model().objects.get(email=payload['email'])
        self.assertTrue(user.check_password(payload['password']))
        self.assertNotIn('password', response.data)

    def test_create_user_with_email_already_exists(self):
        """Test creating user with email is already exists"""
        payload = {
            'email': 'testuserapi@example.com',
            'password': 'LOKO4322',
            'name': 'testuserapi12',
        }
        create_user(**payload)
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

    def test_password_too_short_error(self):
        """Test that password is too short (min 8 chars)"""
        payload = {
            'email': 'testuserapi56@example.com',
            'password': 'lol1',
            'name': 'testuserapi122',
        }
        response = self.client.post(CREATE_USER_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        user_exists = get_user_model().objects.filter(email=payload['email']).exists()
        self.assertFalse(user_exists)

    def test_create_token_for_user(self):
        """Test that a token is created for the user"""
        user_detail = {
            'email': 'testuserapi33@example.com',
            'password': 'Mucikia',
            'name': 'Maciek',
        }
        create_user(**user_detail)
        payload = {
            'email': user_detail['email'],
            'password': user_detail['password'],
        }
        response = self.client.post(TOKEN_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('access', response.data)
        self.assertIn('refresh', response.data)

    def test_create_token_invalid_credentials(self):
        """Test that token is not created if invalid credentials are given"""
        user_detail = {
            'email': 'testuserapi35@example.com',
            'password': 'Haslo1234',
            'name': 'Tomasz',
        }
        create_user(**user_detail)
        payload = {
            'email': 'testuserapi3577@example.com',
            'password': 'Haslo123445',
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_create_token_blank_password(self):
        """Test that token is not created if password is blank"""
        payload = {
            'email': 'testuserapi351@example.com',
            'password': '',
            'name': 'Janusz',
        }

        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
        self.assertNotIn('access', response.data)
        self.assertNotIn('refresh', response.data)

    def test_token_refresh(self):
        user_detail = {
            'email': 'testuserapi35222@example.com',
            'password': 'Password1234!',
            'name': 'Piotr',
        }
        create_user(**user_detail)
        payload = {
            'email': user_detail['email'],
            'password': user_detail['password'],
        }
        response = self.client.post(TOKEN_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('refresh', response.data)
        refresh_payload = {
            'refresh': response.data['refresh'],
        }
        refresh_response = self.client.post(REFRESH_TOKEN_URL, refresh_payload)
        self.assertEqual(refresh_response.status_code, status.HTTP_200_OK)
        self.assertIn('access', refresh_response.data)

    def test_retrieve_user_unauthorized(self):
        """Test that authentication is required for users"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateUserApiTest(TestCase):
    """Test Api request that require authentication"""
    def setUp(self):
        self.user = create_user(
            email='test179@example.com',
            password='Password222',
            name='Jhon',
        )
        self.client = APIClient()
        self.client.force_authenticate(user=self.user)

    def test_retrieve_profile_success(self):
        """Test retrieving profile for logged in user"""
        response = self.client.get(ME_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, {
            'email': self.user.email,
            'name': self.user.name,
        })

    def test_post_me_not_allowed(self):
        """Test that post is not allowed for me endpoint"""
        response = self.client.post(ME_URL, {})
        self.assertEqual(response.status_code, status.HTTP_405_METHOD_NOT_ALLOWED)

    def test_update_user_profile(self):
        """Test updating user profile for authenticated user"""
        payload = {
            'name': 'Tom',
        }
        response = self.client.patch(ME_URL, payload)
        self.user.refresh_from_db()
        self.assertEqual(self.user.name, payload['name'])
        self.assertEqual(response.status_code, status.HTTP_200_OK)



