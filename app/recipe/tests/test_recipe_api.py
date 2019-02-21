import os
import tempfile

from PIL import Image

from django.test import TestCase
from django.contrib.auth import get_user_model
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient
from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPES_URL = reverse('recipe:recipe-list')

# Helper functions

def image_upload_url(recipe_id):
    """Return URL for recipe image upload."""
    return reverse('recipe:recipe-upload-image', args=[recipe_id])

def detail_url(id):
    """ Return a url of recipe details."""
    return reverse('recipe:recipe-detail', args=[id])

def sample_tag(user, name='Main course'):
    """ Create and return a sample tag."""
    return Tag.objects.create(user=user, name=name)

def sample_ingredient(user, name='Cinnamon'):
    """ Create and return a sample ingredient."""
    return Ingredient.objects.create(user=user, name=name)

def sample_recipe(user, **params):
    """Create and return a sample recipe."""
    defaults = {
        'title': 'Borscht',
        'time': 5,
        'price': 25,
    }
    defaults.update(params)
    
    return Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """Test unauth'ed recipe API access."""
    
    def setUp(self):
        self.client = APIClient()

    def test_auth_required(self):
        """Test authentication is required."""
        response = self.client.get(RECIPES_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)

    
class PrivateRecipeApiTests(TestCase):
    """Test auth'ed recipe API access."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@google.com',
                                                         password='testpass')
        self.client.force_authenticate(self.user)

    def test_retrieve_recipes(self):
        """Test retrieving a list of recipes."""
        sample_recipe(user=self.user)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.order_by('-id')
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_recipes_limited_to_user(self):
        """Test that recipes received are limited to the auth'ed user."""
        user2 = get_user_model().objects.create_user(email='other@google.com',
                                                   password='testpass')
        sample_recipe(user=user2)
        sample_recipe(user=self.user)

        response = self.client.get(RECIPES_URL)
        recipes = Recipe.objects.filter(user=self.user)
        serializer = RecipeSerializer(recipes, many=True)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_view_recipe_detail(self):
        """Test viewing a recipe detail."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        response = self.client.get(detail_url(recipe.id))
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_create_recipe(self):
        """Test creating recipe."""
        payload = {
            'title': 'Humburger',
            'time': 7,
            'price': 2,
        }
        response = self.client.post(RECIPES_URL, payload)
        recipe = Recipe.objects.get(**payload)
        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        self.assertEqual(response.data, serializer.data)
        for key in payload.keys():
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Test creating recipe with tags."""
        tag1 = sample_tag(user=self.user, name='Vegan')
        tag2 = sample_tag(user=self.user, name='Spicy')
        payload = {
            'title': 'Avocado cheesecake',
            'tags': [tag1.id, tag2.id],
            'time': 10,
            'price': 20,
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        tags = recipe.tags.all()
        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating recipe with ingredients."""
        ingredient1 = sample_ingredient(user=self.user, name='Herring')
        ingredient2 = sample_ingredient(user=self.user, name='Carrot')
        payload = {
            'title': 'Dressed herring',
            'ingredients': [ingredient1.id, ingredient2.id],
            'time': 45,
            'price': 250,
        }
        response = self.client.post(RECIPES_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(id=response.data['id'])
        ingredients = recipe.ingredients.all()
        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
        
    def test_partial_update_recipe(self):
        """Test updating a recipe with patch."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        new_tag = sample_tag(user=self.user, name='Carry')
        payload = {
            'title': 'Chicken tikka',
            'tags': [new_tag.id],
        }

        url = detail_url(recipe.id)
        self.client.patch(url, payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()
    
        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(tags.count(), 1)
        self.assertIn(new_tag, tags)

    def test_full_update_recipe(self):
        """Test updating a recipe with put."""
        recipe = sample_recipe(user=self.user)
        recipe.tags.add(sample_tag(user=self.user))
        payload = {
            'title': 'Julienne',
            'time': 35,
            'price': 10,
        }

        url = detail_url(recipe.id)
        self.client.put(url, payload)
        recipe.refresh_from_db()
        tags = recipe.tags.all()

        self.assertEqual(recipe.title, payload['title'])
        self.assertEqual(recipe.time, payload['time'])
        self.assertEqual(tags.count(), 0)


class RecipeImageUploadTests(TestCase):

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@google.com',
                                                         password='testpass')
        self.client.force_authenticate(self.user)                                                         
        self.recipe = sample_recipe(user=self.user)

    def tearDown(self):
        return self.recipe.image.delete()

    def test_upload_image_to_recipe(self):
        """Test uploading an image to the recipe."""
        url = image_upload_url(self.recipe.id)
        with tempfile.NamedTemporaryFile(suffix='.jpg') as file:
            image = Image.new('RGB', (15, 15))
            image.save(file, format='JPEG')
            file.seek(0)
            response = self.client.post(url, {'image': file}, format='multipart')

        self.recipe.refresh_from_db()
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertIn('image', response.data)
        self.assertTrue(os.path.exists(self.recipe.image.path))

    def test_upload_image_bad_request(self):
        """Test uploading an invalid image."""
        url = image_upload_url(self.recipe.id)
        response = self.client.post(url, {'image': 'NotAnImage'}, format='multipart')

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)
