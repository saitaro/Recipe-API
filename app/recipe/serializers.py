from rest_framework.serializers import ModelSerializer, PrimaryKeyRelatedField
from core.models import Tag, Ingredient, Recipe


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


class RecipeSerializer(ModelSerializer):
    """The serializer for recipe objects."""
    ingredients = PrimaryKeyRelatedField(
        many=True,
        queryset=Ingredient.objects.all()
    )
    tags = PrimaryKeyRelatedField(
        many=True,
        queryset=Tag.objects.all()
    )
    
    class Meta:
        model = Recipe
        fields = 'id', 'title', 'ingredients',  \
                 'tags', 'time', 'price', 'link'
        read_only_fields = 'id',


class RecipeDetailSerializer(RecipeSerializer):
    """Serialize a recipe detail."""
    ingredients = IngredientSerializer(many=True, read_only=True)
    tags = TagSerializer(many=True, read_only=True)


class RecipeImageSerializer(ModelSerializer):
    """Serializer for uploading images to recipes."""

    class Meta:
        model = Recipe
        fields = 'id', 'image'
        read_only_fields = 'id',

