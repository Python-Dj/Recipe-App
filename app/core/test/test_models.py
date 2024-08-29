"""
Tests for Models.
"""

from decimal import Decimal
from core import models

from django.test import TestCase
from django.contrib.auth import get_user_model

from core.models import Tag


def create_user(email="test@exmaple.com", password="testpass"):
    """Create and return new User"""
    user =  get_user_model().objects.create_user(email, password)
    return user


class ModelTests(TestCase):
    """Test Models"""

    def test_create_user_with_email_success(self):
        """Test creating a user with email successful."""
        email = "test@example.com"
        password = "testpass123"
        user = get_user_model().objects.create_user(
            email=email,
            password=password,
        )
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test email is normalized for new users."""
        sample_emails = [
            ["test1@EXAmple.com", "test1@example.com"],
            ["Test2@Example.com", "Test2@example.com"],
            ["TEST3@EXAMPLE.COM", "TEST3@example.com"],
            ["test4@example.COM", "test4@example.com"],
        ]
        for email, expected in sample_emails:
            user = get_user_model().objects.create_user(email, "sample123")
            self.assertEqual(user.email, expected)

    def test_new_user_without_email_raises_error(self):
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user("", "sample123")

    def test_create_superuser(self):
        user = get_user_model().objects.create_superuser(
            "test@example.com",
            "test123"
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_create_recipe(self):
        """Test creating a recipe successful."""
        user = get_user_model().objects.create_user(
            email="test@example.com",
            password="user@123",
        )
        recipe = models.Recipe.objects.create(
            user=user,
            title="Sample recipe name",
            time_minutes=5,
            price=Decimal(5.21),
            description="Sample recipe description."
        )
        self.assertEqual(str(recipe), recipe.title)

    def test_create_tag(self):
        """Test creating a Tag is successful."""
        user = create_user()
        tag = Tag.objects.create(user=user, name="Tag-1")

        self.assertEqual(str(tag), tag.name)