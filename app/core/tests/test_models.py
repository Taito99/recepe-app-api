"""
Tests for models
"""
from django.test import TestCase
from django.contrib.auth import get_user_model
from decimal import Decimal
from core.models import Recipe, Tag, Ingredient

def create_user(email="testuser@example,com", password="Passwordsd2323"):
    """Create a test user"""
    return get_user_model().objects.create_user(email, password)

class ModelTests(TestCase):
    """Tests for models"""

    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful"""

        email = "test@example.com"
        password = "Password1234"
        user = get_user_model().objects.create_user(
            email=email,
            password=password
        )

        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized"""

        sample_emails = [
            ['test1@EXAMPLE.com', 'test1@example.com'],
            ['Test2@Example.com', 'Test2@example.com'],
            ['TEST3@EXAMPLE.com', 'TEST3@example.com'],
            ['test4@example.COM', 'test4@example.com'],
            ['test5@example.Com', 'test5@example.com']
        ]

        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email=email, password='password1234')
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(email='', password='password1234')

    def test_create_new_superuser(self):
        """Test creating a new superuser"""
        superuser = get_user_model().objects.create_superuser(
            'test123@example.com',
            'password123'
        )

        self.assertTrue(superuser.is_superuser)
        self.assertTrue(superuser.is_staff)

    def test_create_recipe(self):
        """Test creating a new recipe"""
        user = get_user_model().objects.create_user(
            email="testuser23@example.com",
            password="Passosdos"
        )
        recipe = Recipe.objects.create(
            user=user,
            title="Test Recipe",
            time_minutes=10,
            price=10,
            description="This is a test recipe",
            link="https://example.com"

        )

        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a new tag"""
        user = create_user()
        tag = Tag.objects.create(user=user, name="Vegan")

        self.assertEqual(str(tag), tag.name)

    def test_create_ingredient(self):
        """Test creating a new ingredient"""
        user = create_user()
        ingredient = Ingredient.objects.create(
            user=user,
            name="Ingredient1"
        )
        self.assertEqual(str(ingredient), ingredient.name)