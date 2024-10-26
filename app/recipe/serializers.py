from rest_framework import serializers

from core.models import Recipe

class RecipeSerializer(serializers.ModelSerializer):
    class Meta:
        model = Recipe
        fields = ['id', 'title', 'time_minutes', 'price', 'link']
        read_only_fields = ['id']

class RecipeDetailSerializer(serializers.ModelSerializer):
    """Serializer for recipes detail"""
    class Meta(RecipeSerializer.Meta):
        model = Recipe

        fields = RecipeSerializer.Meta.fields + ['description']