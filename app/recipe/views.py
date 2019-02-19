from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient, Recipe
from .serializers import RecipeSerializer, IngredientSerializer, \
                         RecipeDetailSerializer, TagSerializer


class BaseAttrViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    """Base attribute view set. """
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) \
                            .order_by('-name')


class TagViewSet(BaseAttrViewSet):
    """The ViewSet for Tags."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
        

class IngredientViewSet(BaseAttrViewSet):
    """The ViewSet for Ingredients."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer


class RecipeViewSet(ModelViewSet):
    """Manage recipes in the db."""
    serializer_class = RecipeSerializer
    queryset = Recipe.objects.all()
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user)

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'retrieve':
            return RecipeDetailSerializer
        
        return self.serializer_class
