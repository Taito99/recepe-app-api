from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from core.models import Recipe # and this works as well
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer # This import works

RECIPES_URL=reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])


def create_user(**params):
    """Create a new user."""
    return get_user_model().objects.create_user(**params)

def create_recipe(user, **params):
    """Create a new recipe"""
    defaults = {
        'title': 'Test Recipe',
        'time_minutes': 10,
        'price': Decimal(10),
        'description': 'Test Recipe',
        'link': 'https://test.com',
    }
    defaults.update(params)
    return Recipe.objects.create(user=user, **defaults)

class PublicRecipeApiTests(TestCase):
    """Test the public recipe API"""

    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that auth is required."""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateRecipeApiTests(TestCase):
    """Test the private recipe API"""
    def setUp(self):
        self.client = APIClient()
        self.user=create_user(email='testop@example.con', password='Passdsdosdo')

        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        create_recipe(self.user)
        create_recipe(self.user)

        response = self.client.get(RECIPES_URL)

        recipes = Recipe.objects.all().order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test retrieving recipes for user"""
        user2 = create_user(email='testopzxc@example.con', password='Lodfdokfdkfodl2')
        create_recipe(user2)
        create_recipe(self.user)
        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_get_recipe_detail(self):
        recipe = create_recipe(self.user)

        url = detail_url(recipe.id)
        response = self.client.get(url)
        serializer = RecipeDetailSerializer(recipe)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating a new recipe."""
        payload = {
            'title': 'Test Recipe',
            'time_minutes': 10,
            'price': Decimal(10),

        }
        response = self.client.post(RECIPES_URL, payload)
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_partial_update_recipe(self):
        """Test updating a recipe with patch."""
        original_link = "https://test.com"
        recipe = create_recipe(self.user,
                               title="Original Name",
                               link=original_link
                               )
        payload = {'title': 'New Title'}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.link, original_link)
        self.assertEqual(recipe.user, self.user)

    def test_full_update_recipe(self):
        """Test updating a recipe with patch."""
        recipe = create_recipe(
            self.user,
            title="Original Name",
            link="https://testoriginal.com",
            price=Decimal(10),
            description="Test Recipe",
            time_minutes=10,
        )
        payload = {
            'title': 'New Title',
            'link': 'https://testnotoriginal.com',
            'price': Decimal(12),
            'description': 'Test Recipe New',
            'time_minutes': 20,
        }
        url = detail_url(recipe.id)
        response = self.client.put(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        for key, value in payload.items():
            self.assertEqual(getattr(recipe, key), value)
        self.assertEqual(recipe.user, self.user)

    def test_update_user_return_error(self):
        bad_user = create_user(email='testbad@example.con', password='Psaoddokddfko')
        recipe = create_recipe(user=self.user)

        payload = {
           'user': bad_user.id,
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload)
        recipe.refresh_from_db()
        self.assertEqual(recipe.user, self.user)

    def test_delete_recipe(self):
        """Test deleting a recipe."""
        recipe = create_recipe(self.user)
        url = detail_url(recipe.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        self.assertFalse(Recipe.objects.filter(id=recipe.id).exists())

    def test_delete_other_users_recipe_error(self):
        """Test deleting a recipe that belong to another user."""
        new_user = create_user(email='testo2p@example.con', password='<PASSWORD>')
        recipe = create_recipe(new_user)
        url = detail_url(recipe.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_404_NOT_FOUND)
        self.assertTrue(Recipe.objects.filter(id=recipe.id).exists())



