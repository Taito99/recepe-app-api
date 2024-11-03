from django.contrib.auth import get_user_model
from django.template.defaultfilters import title
from django.test import TestCase
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient
from decimal import Decimal
from core.models import Recipe, Tag, Ingredient # and this works as well
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer # This import works'
import tempfile
import os

from PIL import Image

RECIPES_URL=reverse('recipe:recipe-list')

def detail_url(recipe_id):
    """Return recipe detail URL."""
    return reverse('recipe:recipe-detail', args=[recipe_id])

def image_upload_url(recipe_id):
    """Return image upload URL."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])


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

    def test_create_recipe_with_new_tag(self):
        """Test creating a recipe with a new tag."""
        payload = {
            'title': "Thai Prawn",
            'time_minutes': 10,
            'price': Decimal('10.50'),
            "tags": [{'name': 'Thai'}, {'name': 'Dinner'}]
        }
        response = self.client.post(RECIPES_URL, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        for tag in payload['tags']:
            exists = Tag.objects.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_tag(self):
        """Test creating a recipe with an existing tag."""
        tag_indian = Tag.objects.create(name='Indian', user=self.user)
        payload = {
            'title': "Thai Prawn",
            'time_minutes': 10,
            'price': Decimal('12.50'),
            "tags": [{'name': 'Indian'}, {'name': 'Dinner'}]
        }
        response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.tags.count(), 2)
        self.assertIn(tag_indian, recipe.tags.all())
        for tag in payload['tags']:
            exists = Tag.objects.filter(name=tag['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_tag_on_update(self):
        """Test creating a tag on a recipe."""
        recipe = create_recipe(self.user)

        payload = {
            'tags': [{'name': 'Lunch'}]
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertTrue(recipe.tags.filter(name='Lunch').exists())

    def test_update_recipe_assign_tag(self):
        """Test updating a recipe with an existing tag."""
        tag_breakfast = Tag.objects.create(name='Breakfast', user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag_breakfast)

        tag_lunch = Tag.objects.create(name='Lunch', user=self.user)
        payload = {
            'tags': [{'name': 'Lunch'}],
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertIn(tag_lunch, recipe.tags.all())
        self.assertNotIn(tag_breakfast, recipe.tags.all())

    def test_clear_recipe_tags(self):
        """Test clearing a recipe tags."""
        tag = Tag.objects.create(name='Breakfast', user=self.user)
        recipe = create_recipe(self.user)
        recipe.tags.add(tag)
        payload = {
            'tags': [],
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        recipe.refresh_from_db()
        self.assertEqual(recipe.tags.count(), 0)

    def test_create_recipe_with_new_ingredients(self):
        """Test creating a recipe with a new ingredient."""
        payload = {
            'title': "Cauliflower Tacos",
            'time_minutes': 10,
            'price': Decimal('12.50'),
            "ingredients": [{'name': 'Cauliflower'}, {'name': 'Salt'}]
        }
        response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        for ingredient in payload['ingredients']:
            exists = Ingredient.objects.filter(name=ingredient['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_recipe_with_existing_ingredients(self):
        """Test creating a recipe with an existing ingredient."""
        ingredient = Ingredient.objects.create(name='Lemon', user=self.user)
        payload = {
            'title': "Lemonade",
            'time_minutes': 5,
            'price': Decimal('10.50'),
            "ingredients": [{'name': 'Lemon'}, {'name': 'Water'}]
        }
        response = self.client.post(RECIPES_URL, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipes = Recipe.objects.filter(user=self.user)
        self.assertEqual(recipes.count(), 1)
        recipe = recipes[0]
        self.assertEqual(recipe.ingredients.count(), 2)
        self.assertIn(ingredient, recipe.ingredients.all())
        for ingredient in payload['ingredients']:
            exists = Ingredient.objects.filter(name=ingredient['name'], user=self.user).exists()
            self.assertTrue(exists)

    def test_create_ingredient_on_update(self):
        """Test creating an ingredient on a recipe."""
        recipe = create_recipe(self.user)
        payload = {'ingredients': [{'name': 'Limes'}]}
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)

        recipe.refresh_from_db()
        self.assertTrue(
            recipe.ingredients.filter(name='Limes').exists())

    def test_update_recipe_assign_ingredient(self):
        """Test updating a recipe with an existing ingredient."""
        ingredient1 = Ingredient.objects.create(name='Peper', user=self.user)
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient1)

        ingredient2 = Ingredient.objects.create(name='Salt', user=self.user)
        payload = {
            'ingredients': [{'name': 'Salt'}],
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn(ingredient2, recipe.ingredients.all())
        self.assertNotIn(ingredient1, recipe.ingredients.all())

    def test_clear_recipe_ingredients(self):
        """Test clearing a recipe ingredients."""
        ingredient = Ingredient.objects.create(name="Olives", user=self.user)
        recipe = create_recipe(self.user)
        recipe.ingredients.add(ingredient)
        payload = {
            'ingredients': [],
        }
        url = detail_url(recipe.id)
        response = self.client.patch(url, payload, format='json')
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(recipe.ingredients.count(), 0)

    def test_filter_by_tags(self):
        """Test filtering by tags."""
        r1 = create_recipe(self.user, title='Thai Vegetable Curry')
        r2 = create_recipe(self.user, title='Turtle Curry')
        tag1 = Tag.objects.create(name='Vegan', user=self.user)
        tag2 = Tag.objects.create(name='Meat', user=self.user)
        r1.tags.add(tag1)
        r2.tags.add(tag2)
        create_recipe(self.user, title="Fish")  # Recipe without any tags

        params = {'tags': f'{tag1.id},{tag2.id}'}
        response = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)

        self.assertIn(s1.data, response.data)
        self.assertIn(s2.data, response.data)
        self.assertEqual(len(response.data), 2)

    def test_filter_by_ingredients(self):
        """Test filtering by ingredients."""
        r1 = create_recipe(self.user, title='Thai Vegetable Curry')
        r2 = create_recipe(self.user, title='Turtle Curry')
        in1 = Ingredient.objects.create(name="Olives", user=self.user)
        in2 = Ingredient.objects.create(name="Salt", user=self.user)
        r1.ingredients.add(in1)
        r2.ingredients.add(in2)
        create_recipe(self.user, title="Fish Fishy")  # Recipe without any ingredients

        params = {'ingredients': f'{in1.id},{in2.id}'}
        response = self.client.get(RECIPES_URL, params)

        s1 = RecipeSerializer(r1)
        s2 = RecipeSerializer(r2)

        self.assertIn(s1.data, response.data)
        self.assertIn(s2.data, response.data)
        self.assertEqual(len(response.data), 2)


class ImageUploadTest(TestCase):
    """Tests image upload endpoint."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='testimage@example.com',
            password='Passododfdof34',
        )
        self.client.force_authenticate(user=self.user)
        self.recipe = create_recipe(self.user)

    def tearDown(self):
        self.recipe.image.delete()

    def test_upload_image(self):
        """Test uploading an image."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as image_file:
            img = Image.new('RGB', (10, 10))
            img.save(image_file, format='JPEG')
            image_file.seek(0)
            payload = {
                'image': image_file
            }
            response = self.client.post(url, payload, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_with_bad_request(self):
        """Test uploading an image with bad request."""
        url = image_upload_url(self.recipe.id)
        payload = {
            "image": "notanimage"
        }
        response = self.client.post(url, payload, format='multipart')
        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

