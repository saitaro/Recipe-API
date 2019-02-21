from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.viewsets import GenericViewSet, ModelViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework import status

from core.models import Tag, Ingredient, Recipe
from .serializers import RecipeSerializer, IngredientSerializer, TagSerializer, \
                         RecipeDetailSerializer, RecipeImageSerializer


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
        elif self.action == 'upload_image':
            return RecipeImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(
            recipe,
            data=request.data
        )
        if serializer.is_valid():
            serializer.save()
            return Response(
                serializer.data,
                status=status.HTTP_200_OK,
            )
        return Response(
            serializer.errors,
            status=status.HTTP_400_BAD_REQUEST
        )


