from rest_framework import viewsets, mixins, status
from rest_framework.response import Response
from rest_framework.decorators import action
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication
from drf_spectacular.utils import extend_schema, extend_schema_view, OpenApiParameter, OpenApiTypes
from core.models import Recipe, Tag, Ingredient
from . import serializers

# Recipe ViewSet
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'tags',
                type=OpenApiTypes.STR,
                description='Comma separated list of tag IDs to filter by.',
            ),
            OpenApiParameter(
                'ingredients',
                type=OpenApiTypes.STR,
                description='Comma separated list of ingredient IDs to filter by.',
            )
        ],
        tags=['recipes']
    ),
    retrieve=extend_schema(tags=['recipes']),
    create=extend_schema(tags=['recipes']),
    update=extend_schema(tags=['recipes']),
    partial_update=extend_schema(tags=['recipes']),
    destroy=extend_schema(tags=['recipes'])
)
class RecipeViewSet(viewsets.ModelViewSet):
    """ViewSet for viewing and editing recipes."""
    serializer_class = serializers.RecipeDetailSerializer
    queryset = Recipe.objects.all()
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def _params_to_ints(self, qs):
        """Convert a list of comma-separated strings to a list of integers."""
        return [int(str_id) for str_id in qs.split(',')]

    def get_queryset(self):
        """Retrieve recipes for the authenticated user, optionally filtered by tags or ingredients."""
        tags = self.request.query_params.get('tags')
        ingredients = self.request.query_params.get('ingredients')
        queryset = self.queryset.filter(user=self.request.user)

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.order_by('-id').distinct()

    def get_serializer_class(self):
        """Return appropriate serializer class based on action."""
        if self.action == 'list':
            return serializers.RecipeSerializer
        elif self.action == 'upload_image':
            return serializers.RecipeImageSerializer
        return self.serializer_class

    def perform_create(self, serializer):
        """Create a new recipe for the authenticated user."""
        serializer.save(user=self.request.user)

    @action(methods=['POST'], detail=True, url_path='upload-image')
    def upload_image(self, request, pk=None):
        """Upload an image to a specific recipe."""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

# Base ViewSet for Recipe Attributes (Tags and Ingredients)
@extend_schema_view(
    list=extend_schema(
        parameters=[
            OpenApiParameter(
                'assigned_only',
                type=OpenApiTypes.INT,
                enum=[0, 1],
                description='Return only attributes assigned to recipes.',
            )
        ]
    )
)
class BaseRecipeAttrViewSet(mixins.UpdateModelMixin, mixins.DestroyModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Base viewset for recipe attributes such as tags and ingredients."""
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        """Retrieve attributes for the authenticated user, optionally filtering by assigned status."""
        assigned_only = bool(int(self.request.query_params.get('assigned_only', 0)))
        queryset = self.queryset.filter(user=self.request.user)

        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.order_by('name').distinct()

# Tag ViewSet
@extend_schema_view(
    list=extend_schema(tags=['tags']),
    retrieve=extend_schema(tags=['tags']),
    create=extend_schema(tags=['tags']),
    update=extend_schema(tags=['tags']),
    partial_update=extend_schema(tags=['tags']),
    destroy=extend_schema(tags=['tags'])
)
class TagAttrViewSet(BaseRecipeAttrViewSet):
    """ViewSet for viewing and editing tags."""
    serializer_class = serializers.TagSerializer
    queryset = Tag.objects.all()

# Ingredient ViewSet
@extend_schema_view(
    list=extend_schema(tags=['ingredients']),
    retrieve=extend_schema(tags=['ingredients']),
    create=extend_schema(tags=['ingredients']),
    update=extend_schema(tags=['ingredients']),
    partial_update=extend_schema(tags=['ingredients']),
    destroy=extend_schema(tags=['ingredients'])
)
class IngredientAttrViewSet(BaseRecipeAttrViewSet):
    """ViewSet for viewing and editing ingredients."""
    serializer_class = serializers.IngredientSerializer
    queryset = Ingredient.objects.all()
