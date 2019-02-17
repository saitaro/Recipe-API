from django.contrib.auth import get_user_model
from django.test import TestCase
from django.urls import reverse

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient

from recipe.serializers import IngredientSerializer


INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientsApiTest(TestCase):
    """Test the publicly available ingredients API."""

    def setUp(self):
        self.client = APIClient()

    def test_login_required(self):
        """Test the login is required to access the endpoint."""
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientsApiTests(TestCase):
    """Test the private ingredients API."""

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user('test@google.com',
                                                         'testpass')
        self.client.force_authenticate(self.user)

    def test_retreive_ingredients_list(self):
        """Test retrieving a list of ingredients."""
        Ingredient.objects.create(user=self.user, name='Salt')
        Ingredient.objects.create(user=self.user, name='Pepper')        
        
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        response = self.client.get(INGREDIENTS_URL)

        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)

    def test_ingredients_limited_to_user(self):
        """Test that only the ingredient of the auth'd user are returned."""
        user2 = get_user_model().objects.create_user('another@google.com',
                                                     'anotherpass')
        Ingredient.objects.create(user=user2, name='Salt')
        Ingredient.objects.create(user=self.user, name='Pepper')                                           
        Ingredient.objects.create(user=self.user, name='Milk')                                           

        ingredients = Ingredient.objects.all()                  \
                                        .filter(user=self.user) \
                                        .order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)
        response = self.client.get(INGREDIENTS_URL)
    
        self.assertEqual(response.status_code, status.HTTP_200_OK)
        self.assertEqual(response.data, serializer.data)
        
    def test_create_ingredient_successful(self):
        """Test creating a new ingredient."""
        payload = {'name': 'Tomato'}
        self.client.post(INGREDIENTS_URL, payload)

        ingredient = Ingredient.objects.filter(user=self.user,
                                               name=payload['name'])
        self.assertTrue(ingredient.exists())

    def test_create_invalid_ingredient(self):
        """Test creating invalid ingredient fails."""
        payload = {'name': ''}
        response = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(response.status_code, status.HTTP_400_BAD_REQUEST)

