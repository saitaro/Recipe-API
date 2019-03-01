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
        """Create a new object."""
        serializer.save(user=self.request.user)

    def get_queryset(self):
        """Return objects for the authenticated user."""
        assigned_only = bool(self.request.query_params.get('assigned_only'))
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)
        return queryset.filter(user=self.request.user) \
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

    def _params_to_ints(self, qs):
        """ List of str -> list of int."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated used."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        if tags:
            tag_ids = self._params_to_ints(tags)
            self.queryset = self.queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            self.queryset = self.queryset.filter(ingredients__id__in=ingredient_ids)
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


