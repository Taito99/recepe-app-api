"""Views for the use Api"""
from rest_framework import  generics
from rest_framework_simplejwt.views import TokenObtainPairView
from .serializers import UserSerializer, AuthTokenSerializer

class CreateUserView(generics.CreateAPIView):
    """Create a new user in the system"""
    serializer_class = UserSerializer

class CreateTokenView(TokenObtainPairView):
    """Create a new JWT token for the user"""
    serializer_class = AuthTokenSerializer