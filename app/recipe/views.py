from rest_framework.viewsets import GenericViewSet
from rest_framework.mixins import ListModelMixin, CreateModelMixin
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Tag, Ingredient
from .serializers import TagSerializer, IngredientSerializer


class BaseAttrViewSet(GenericViewSet, ListModelMixin, CreateModelMixin):
    """Base attribute view set. """
    authentication_classes = TokenAuthentication,
    permission_classes = IsAuthenticated,

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user) \
                            .order_by('-name')

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class TagViewSet(BaseAttrViewSet):
    """The ViewSet for Tags."""
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
        

class IngredientViewSet(BaseAttrViewSet):
    """The ViewSet for Ingredients."""
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
