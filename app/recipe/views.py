from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe

from recipe import serializers


class GenericVIew(viewsets.GenericViewSet,
                  mixins.ListModelMixin,
                  mixins.CreateModelMixin):
    """
    Generic view set for creating and retrieving models
    """

    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        """Return only the tags related to current auth user"""
        return self.queryset.filter(user=self.request.user).order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(GenericVIew):
    """
    Manage tags in a database
    """

    queryset = Tag.objects.all()
    serializer_class = serializers.TagSerializers


class IngredientsViewSet(GenericVIew):
    """
    Manage ingredients in a database
    """

    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Manage the Recipe endpoint
    """

    queryset = Recipe.objects.all()
    permission_classes = (IsAuthenticated,)
    authentication_classes = (TokenAuthentication,)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by('id')

    def get_serializer_class(self):
        """Return the Detail Serializer if the action is retrieve"""

        if self.action == 'retrieve':
            return serializers.RecipeDetailSerializer

        return serializers.RecipeSerializer

    def perform_create(self, serializer):
        """Save a model with user as current auth user"""

        serializer.save(user=self.request.user)
