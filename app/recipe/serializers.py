from rest_framework import serializers

from core.models import Tag, Ingredient


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
