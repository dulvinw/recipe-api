from django.test import TestCase
from django.urls import reverse
from django.contrib.auth import get_user_model

from rest_framework import status
from rest_framework.test import APIClient

from core.models import Recipe, Tag, Ingredient

from recipe.serializers import RecipeSerializer, RecipeDetailSerializer

RECIPE_URL = reverse('recipe:recipe-list')


def sample_tag(user, name='Sample Tag'):
    """Create and return a sample tag"""

    return Tag.objects.create(user=user, name=name)


def sample_ingredient(user, name='Sample Ingredient'):
    """Create and return a sample ingredient"""

    return Ingredient.objects.create(user=user, name=name)


def detail_url(id):
    """return the detail url for recipe"""

    return reverse('recipe:recipe-detail', args=[id])


def sample_recipe(user, **params):
    """Create and return a sample recipe"""

    defaults = {
        'title': 'Default Title',
        'price': '5.0',
        'time_minutes': '5'
    }

    defaults.update(params)

    return Recipe.objects.create(user=user, **defaults)


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

    def test_get_recipe_detail(self):
        """Test the detail endpoint for recipe"""

        recipe = sample_recipe(self.user)
        recipe.tags.add(sample_tag(user=self.user))
        recipe.ingredients.add(sample_ingredient(user=self.user))

        res = self.client.get(detail_url(recipe.id))

        serializer = RecipeDetailSerializer(recipe)

        self.assertEqual(res.status_code, status.HTTP_200_OK)
        self.assertEqual(res.data, serializer.data)

    def test_create_recipe(self):
        """Test that we can create a recipe using endpoint"""
        payload = {
            'title': 'Test Recipe',
            'price': 5.00,
            'time_minutes': 5
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)
        recipe = Recipe.objects.get(pk=res.data['id'])

        for key in payload:
            self.assertEqual(payload[key], getattr(recipe, key))

    def test_create_recipe_with_tags(self):
        """Create a recipe with tags"""

        tag1 = sample_tag(user=self.user)
        tag2 = sample_tag(user=self.user)

        payload = {
            'title': 'Test Recipe',
            'price': 5.00,
            'time_minutes': 5,
            'tags': [tag1.id, tag2.id]
        }

        res = self.client.post(RECIPE_URL, payload)

        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(pk=res.data['id'])
        tags = recipe.tags.all()

        self.assertEqual(tags.count(), 2)
        self.assertIn(tag1, tags)
        self.assertIn(tag2, tags)

    def test_create_recipe_with_ingredients(self):
        """Test creating a recipe with ingredients"""

        ingredient1 = sample_ingredient(user=self.user)
        ingredient2 = sample_ingredient(user=self.user)

        payload = {
            'title': 'Test Recipe',
            'price': 5.0,
            'time_minutes': 5,
            'ingredients': [ingredient1.id, ingredient2.id],
        }

        res = self.client.post(RECIPE_URL, payload)
        self.assertEqual(res.status_code, status.HTTP_201_CREATED)

        recipe = Recipe.objects.get(pk=res.data['id'])
        ingredients = recipe.ingredients.all()

        self.assertEqual(ingredients.count(), 2)
        self.assertIn(ingredient1, ingredients)
        self.assertIn(ingredient2, ingredients)
