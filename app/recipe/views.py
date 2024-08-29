"""Views for Recipe API."""

from django.shortcuts import render
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer

from rest_framework import viewsets, mixins
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated

from core.models import Recipe, Tag


class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def get_queryset(self):
        """Retrieve Recipe for authenticate user."""
        return self.queryset.filter(user=self.request.user).order_by("-id")
    
    def get_serializer_class(self):
        if self.action == "list":
            return RecipeSerializer
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)
    

class TagViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Manage Tag in the Database."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return self.queryset.filter(user=self.request.user).order_by("-name")


