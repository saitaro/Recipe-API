from rest_framework.serializers import ModelSerializer
from core.models import Tag, Ingredient


class TagSerializer(ModelSerializer):
    """The serializer for tag objects."""
    
    class Meta:
        model = Tag
        fields = 'id', 'name'
        read_only_fields = 'id',


class IngredientSerializer(ModelSerializer):
    """The serializer for ingredient objects."""
    
    class Meta:
        model = Ingredient
        fields = 'id', 'name'
        read_only_fields = 'id',
        