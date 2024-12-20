from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Tag, Recipe
from recipe.serializers import TagSerializer
from decimal import Decimal


TAGS_URL = reverse('recipe:tag-list')

def create_user(email="testuser@example.com", password="Passwodoefdof"):
    return get_user_model().objects.create_user(email, password)

def detail_url(tag_id):
    """Return tag detail url"""
    return reverse('recipe:tag-detail', args=[tag_id])

class PublicTagsAPITests(TestCase):
    """Test the public tags API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required."""
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateTagsAPITests(TestCase):
    """Test the private tags API"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_tags(self):
        """Test retrieving tags."""
        Tag.objects.create(user=self.user, name='Vegan')
        Tag.objects.create(user=self.user, name='Desert')

        res = self.client.get(TAGS_URL)
        tags = Tag.objects.all().order_by('name')
        serializer = TagSerializer(tags, many=True)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_tags_limited_to_user(self):
        """Test retrieving tags for authenticated user."""
        user2 = create_user(email="testuser2@example.com")
        Tag.objects.create(user=user2, name='Meat')
        tag = Tag.objects.create(user=self.user, name='FastFood')
        res = self.client.get(TAGS_URL)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], tag.name)
        self.assertEqual(res.data[0]['id'], tag.id)

    def test_update_tag(self):
        """Test updating tag"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        payload = {'name': 'Diner'}
        url = detail_url(tag.id)
        res = self.client.patch(url, payload)
        self.assertEqual(res.status_code, status.HTTP_200_OK)
        tag.refresh_from_db()
        self.assertEqual(tag.name, payload['name'])

    def test_delete_tag(self):
        """Test deleting tag"""
        tag = Tag.objects.create(user=self.user, name='Pie')
        url = detail_url(tag.id)
        res = self.client.delete(url)
        self.assertEqual(res.status_code, status.HTTP_204_NO_CONTENT)
        tags = Tag.objects.filter(user=self.user)
        self.assertFalse(tags.exists())

    def test_filter_tags_assigned_to_recipe(self):
        """Test filtering tags by assigned value"""
        tag1 = Tag.objects.create(user=self.user, name='Breakfast')
        tag2 = Tag.objects.create(user=self.user, name='Pineapple')
        recipe = Recipe.objects.create(
            title='Green eggs on tost',
            time_minutes=10,
            price=Decimal('10'),
            user=self.user
        )
        recipe.tags.add(tag1)

        res = self.client.get(TAGS_URL, {'assigned_only': 1})

        serializer1 = TagSerializer(tag1)
        serializer2 = TagSerializer(tag2)
        self.assertIn(serializer1.data, res.data)
        self.assertNotIn(serializer2.data, res.data)

    def test_filter_tags_unique(self):
        """Test filtering tags by unique value"""
        tag = Tag.objects.create(user=self.user, name='Breakfast')
        Tag.objects.create(user=self.user, name='Pineapple')
        recipe = Recipe.objects.create(
            title='Green eggs on tost',
            time_minutes=10,
            price=Decimal('10'),
            user=self.user
        )
        recipe2 = Recipe.objects.create(
            title='Black eggs on tost',
            time_minutes=10,
            price=Decimal('10'),
            user=self.user
        )
        recipe.tags.add(tag)
        recipe2.tags.add(tag)
        res = self.client.get(TAGS_URL, {'assigned_only': 1})
        self.assertEqual(len(res.data), 1)
