from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.authentication import JWTAuthentication

from .serializers import UserSerializer, CreateUserSerializer


class CreateUserView(generics.CreateAPIView):
    """Users can register"""
    serializer_class = CreateUserSerializer


class ManageUserView(generics.RetrieveUpdateDestroyAPIView):
    """Users can manage their accounts.
    Change their information and delete the account."""
    serializer_class = UserSerializer
    authentication_classes = (JWTAuthentication,)
    permission_classes = (IsAuthenticated,)

    def get_object(self):
        return self.request.user
