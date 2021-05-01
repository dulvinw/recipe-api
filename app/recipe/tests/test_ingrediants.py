from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Ingredient
from recipe.serializers import IngredientSerializer

INGREDIENTS_URL = reverse('recipe:ingredient-list')


class PublicIngredientApiTests(TestCase):
    """
    Test the public apis of Ingredients
    """

    def setUp(self):
        self.client = APIClient()

    def test_unauthorized_access_ingredients(self):
        """Test un auth access to ingredients endpoing"""
        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_401_UNAUTHORIZED)


class PrivateIngredientApiTests(TestCase):
    """
    Test the private APIs of the Ingredient endpoint
    """

    def setUp(self):
        self.client = APIClient()
        self.user = get_user_model().objects.create_user(email='test@test.com',
                                                         password='test123')
        self.client.force_authenticate(self.user)

    def test_get_all_ingredients(self):
        """Test if all the ingredients could be retrieved"""
        Ingredient.objects.create(user=self.user, name='Oil')
        Ingredient.objects.create(user=self.user, name='Cabbage')

        res = self.client.get(INGREDIENTS_URL)
        ingredients = Ingredient.objects.all().order_by('-name')
        serializer = IngredientSerializer(ingredients, many=True)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_ingredients_limited_to_a_user(self):
        """
        Test only the resources related to the authenticated user is
        retrieved
        """
        user = get_user_model().objects.create_user(email='test2@test.com',
                                                    password='test123')
        Ingredient.objects.create(user=user, name='oil')
        ingredient = Ingredient.objects.create(user=self.user, name='cabbage')

        res = self.client.get(INGREDIENTS_URL)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(len(res.data), 1)
        self.assertEqual(res.data[0]['name'], ingredient.name)

    def test_create_ingredient_successful(self):
        """Create an ingredient in the database"""
        payload = {'name': 'Oil'}

        res = self.client.post(INGREDIENTS_URL, payload)
        exists = Ingredient.objects.filter(name=payload['name'],
                                           user=self.user).exists()

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        self.assertTrue(exists)

    def test_create_ingredient_invalid(self):
        """Do not create an ingredient if request is missing values"""
        payload = {'name': ''}

        res = self.client.post(INGREDIENTS_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_400_BAD_REQUEST)
