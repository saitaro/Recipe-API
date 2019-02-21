from unittest.mock import patch

from django.test import TestCase
from django.contrib.auth import get_user_model

from core import models


def sample_user(email='test@google.com', password='testpass'):
    """Create sample user."""
    return get_user_model().objects.create_user(email=email, password=password)


class ModelTests(TestCase):
    def test_create_user_with_email_successful(self):
        """Test creating a new user with an email is successful."""
        email = 'nort87@mail.ru'
        password = 'sugarbooger123'
        user = get_user_model().objects.create_user(email=email,
                                                    password=password)
        self.assertEqual(user.email, email)
        self.assertTrue(user.check_password(password))

    def test_new_user_email_normalized(self):
        """Test the email for a new user is normalized."""
        email = 'petrovich@IBM.COM'
        user = get_user_model().objects.create_user(email, 'testpass123')

        self.assertEqual(user.email, email.lower())

    def test_new_user_invalid_email(self):
        """Test creating user with no email raises error."""
        with self.assertRaises(ValueError):
            get_user_model().objects.create_user(None, 'test123')

    def test_create_new_superuser(self):
        """Test creating a new superuser."""
        user = get_user_model().objects.create_superuser(
            'test@allthegoodies.com', 'test343434'
        )
        self.assertTrue(user.is_superuser)
        self.assertTrue(user.is_staff)

    def test_tag_str(self):
        """Test the tag string representation."""
        tag = models.Tag.objects.create(user=sample_user(), 
                                        name='Vegan')
        self.assertEqual(str(tag), tag.name)
        
    def test_ingredient_str(self):
        """Test the ingredient string representation."""
        ingredient = models.Ingredient.objects.create(user=sample_user(),
                                                      name='Chocolate')
        self.assertEqual(ingredient.name, str(ingredient))

    def test_recipe_str(self):
        """Test the recipe string representation."""
        recipe = models.Recipe.objects.create(user=sample_user(),
                                              title='Borscht',
                                              time=15,
                                              price=4.50)
        self.assertEqual(recipe.title, str(recipe))

    @patch('uuid.uuid4')
    def test_recipe_file_name_uuid(self, mock_uuid):
        """Test that image is saved in the corrent location."""
        uuid = 'test-id'
        mock_uuid.return_value = uuid
        file_path = models.recipe_image_file_path(None, 'img.jpg')

        expected_path = f'uploads/recipe/{uuid}.jpg'
        self.assertEqual(file_path, expected_path)
