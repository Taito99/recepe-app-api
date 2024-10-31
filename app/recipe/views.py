from rest_framework import viewsets, mixins
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe, Tag, Ingredient
from . import serializers
from rest_framework_simplejwt.authentication import JWTAuthentication

class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing recipes."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the recipes for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('-id')

    def get_serializer_class(self):
        """Return appropriate serializer class."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe."""
        serializer.save(user=self.request.user)

class TagViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """ViewSet for viewing and editing tags."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the tags for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('name')

class IngredientViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve the ingredients for the authenticated user."""
        return self.queryset.filter(user=self.request.user).order_by('name')
