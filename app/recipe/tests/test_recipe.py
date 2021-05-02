from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe

from recipe.serializers import RecipeSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_recipe(user, **params):
    """Create and return a sample recipe"""

    defaults = {
        'title': 'Default Title',
        'price': '5.0',
        'time_minutes': '5'
    }

    defaults.update(params)

    Recipe.objects.create(user=user, **defaults)


class PublicRecipeApiTests(TestCase):
    """
    Test the public apis of recipe endpoint
    """

    def setUp(self):
        self.client = APIClient()

    def test_no_unauth_access(self):
        """Test an un auth user can't access the endpoint"""
        res = self.client.get(RECIPE_URL)
        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateRecipeApiTest(TestCase):
    """
    Test the private APIs of the Recipe endpoint
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(
            email='test@test.com',
            password='test123'
        )
        self.client.force_authenticate(self.user)

    def test_get_all_recipes(self):
        """Test getting all the recipes from DB"""

        sample_recipe(self.user)
        sample_recipe(self.user)

        recipes = Recipe.objects.all().order_by('id')
        serializer = RecipeSerializer(recipes, many=True)

        res = self.client.get(RECIPE_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_get_recipes_related_to_user(self):
        """
        Test that we are only recieving the recipes for the current
        logged in user
        """

        user = get_user_model().objects.create_user(
            email='test2@test.com',
            password='test123'
        )

        sample_recipe(user=user)
        sample_recipe(user=self.user)

        res = self.client.get(RECIPE_URL)

        recipies = Recipe.objects.all().filter(user=self.user).order_by('id')
        serializer = RecipeSerializer(recipies, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data, serializer.data)
