from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from core.models import Recipe
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