from rest_framework import serializers

from core.models import Tag, Ingredient, Recipe


class TagSerializers(serializers.ModelSerializer):
    """
    Tags serializers
    """

    class Meta:
        model = Tag
        fields = ('id', 'name')
        read_only_fields = ('id',)


class IngredientSerializer(serializers.ModelSerializer):
    """
    Ingredient Serializer
    """

    class Meta:
        model = Ingredient
        fields = ('id', 'name',)
        read_only_field = ('id',)


class RecipeSerializer(serializers.ModelSerializer):
    """
    Recipe Serializer
    """

    ingredients = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = serializers.PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )

    class Meta:
        model = Recipe
        fields = ('id', 'title', 'time_minutes', 'price', 'link',
                  'ingredients', 'tags',)
        read_only_field = ('id',)


class RecipeDetailSerializer(RecipeSerializer):
    """
    Serializer for Recipe Detail
    """

    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializers(many=True, read_only=True)


class RecipeImageSerializer(serializers.ModelSerializer):
    """
    Serialize a recipe image
    """

    class Meta:
        model = Recipe
        fields = ('id', 'image',)
        read_only_fields = ('id',)
