from rest_framework.routers import DefaultRouter
from django.urls import path, include
from . import views

router = DefaultRouter()
router.register('recipes', views.RecipeViewSet)
router.register('tags', views.TagAttrViewSet)
router.register('ingredients', views.IngredientAttrViewSet)

app_name = 'recipe'

urlpatterns = [
    path('', include(router.urls)),
]