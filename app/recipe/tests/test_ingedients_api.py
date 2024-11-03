"""Tests for ingredients api"""

from django.contrib.auth import get_user_model
from django.urls import reverse
from django.test import TestCase
from rest_framework import status
from rest_framework.test import APIClient
from core.models import Ingredient, Recipe
from recipe.serializers import IngredientSerializer
from decimal import Decimal

INGREDIENTS_URL = reverse('recipe:ingredient-list')
def create_user(email="testingredient@example.com", password="Password122334"):
    return get_user_model().objects.create_user(email=email, password=password)

def detail_url(ingredient_id):
    return reverse('recipe:ingredient-detail', args=[ingredient_id])


class PublicIngredientsApiTests(TestCase):
    """Test the public ingredients API"""
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test that authentication is required"""
        response = self.client.get(INGREDIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API"""
    def setUp(self):
        self.client = APIClient()
        self.user = create_user()
        self.client.force_authenticate(self.user)

    def test_retrieve_ingredient_list(self):
        """Test retrieving a list of ingredients"""
        Ingredient.objects.create(user=self.user, name='Kale')
        Ingredient.objects.create(user=self.user, name='Salt')
        response = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('name')
        serializer = IngredientSerializer(ingredients, many=True)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredient_limited_to_user(self):
        """Test retrieving ingredients for the authenticated user"""
        user2 = create_user(email="testingredient2@example.com")
        Ingredient.objects.create(user=user2, name='Kale')
        ingredient = Ingredient.objects.create(user=self.user, name='Salt')
        response = self.client.get(INGREDIENTS_URL)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(len(response.data), 1)
        self.assertEqual(response.data[0]['name'], ingredient.name)
        self.assertEqual(response.data[0]['id'], ingredient.id)

    def test_update_ingredient(self):
        """Test updating a ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Kale')
        payload = {'name': 'Salt'}
        url = detail_url(ingredient.id)
        response = self.client.patch(url, payload)
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        ingredient.refresh_from_db()
        self.assertEqual(response.data['name'], payload['name'])

    def test_delete_ingredient(self):
        """Test deleting a ingredient"""
        ingredient = Ingredient.objects.create(user=self.user, name='Peper')
        url = detail_url(ingredient.id)
        response = self.client.delete(url)
        self.assertEqual(response.status_code, status.HTTP_204_NO_CONTENT)
        ingredients = Ingredient.objects.all().filter(id=ingredient.id)
        self.assertFalse(ingredients.exists())

    def test_filter_ingredients_assigned_to_recipes(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Kale')
        ingredient2 = Ingredient.objects.create(user=self.user, name='Salt')
        recipe = Recipe.objects.create(
            title="Kale Salat",
            time_minutes=5,
            price=Decimal('5.5'),
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})
        serializer1 = IngredientSerializer(ingredient1)
        serializer2 = IngredientSerializer(ingredient2)
        self.assertIn(serializer1.data, response.data)
        self.assertNotIn(serializer2.data, response.data)

    def test_filter_ingredients_unique(self):
        """Test filtering ingredients by those assigned to recipes"""
        ingredient1 = Ingredient.objects.create(user=self.user, name='Eggs')
        Ingredient.objects.create(user=self.user, name='Lentils')
        recipe = Recipe.objects.create(
            title="Eggs dinner",
            time_minutes=5,
            price=Decimal('5.3'),
            user=self.user,
        )
        recipe2 = Recipe.objects.create(
            title="Lentils dinner",
            time_minutes=5,
            price=Decimal('5.1'),
            user=self.user,
        )
        recipe.ingredients.add(ingredient1)
        recipe2.ingredients.add(ingredient1)

        response = self.client.get(INGREDIENTS_URL, {'assigned_only': 1})

        self.assertEqual(len(response.data), 1)

