"""Views for Recipe API."""

from django.shortcuts import render
from .serializers import RecipeSerializer, RecipeDetailSerializer, TagSerializer, IngredientSerializer, RecipeImageSerializer

from rest_framework import viewsets, mixins, status
from rest_framework.authentication import TokenAuthentication
from rest_framework.permissions import IsAuthenticated
from rest_framework.decorators import action
from rest_framework.response import Response

from core.models import Recipe, Tag, Ingredient

from drf_spectacular.utils import extend_schema_view, extend_schema, OpenApiParameter, OpenApiTypes # type: ignore



@extend_schema_view(
    list = extend_schema(
        parameters=[
            OpenApiParameter(
                "tags",
                OpenApiTypes.STR,
                description="comma seperated list of Tags ID's to filter",
            ),
            OpenApiParameter(
                "ingredients",
                OpenApiTypes.STR,
                description="comma seperated list of Ingredients ID's to filter",
            )
        ]
    )
)
class RecipeViewSet(viewsets.ModelViewSet):
    """View for manage recipe API."""
    queryset = Recipe.objects.all()
    serializer_class = RecipeDetailSerializer
    authentication_classes = [TokenAuthentication,]
    permission_classes = [IsAuthenticated,]

    def _params_to_ints(self, qs):
        """Converting a list of string to integer"""
        return [int(str_id) for str_id in qs.split(",")]

    def get_queryset(self):
        """Retrieve Recipe for authenticate user."""
        tags = self.request.query_params.get("tags")
        ingredients = self.request.query_params.get("ingredients")
        queryset = self.queryset

        if tags:
            tag_ids = self._params_to_ints(tags)
            queryset = queryset.filter(tags__id__in=tag_ids)
        if ingredients:
            ingredient_ids = self._params_to_ints(ingredients)
            queryset = queryset.filter(ingredients__id__in=ingredient_ids)

        return queryset.filter(
            user=self.request.user
        ).order_by("-id").distinct()

    
    def get_serializer_class(self):
        if self.action == "list":
            return RecipeSerializer
        elif self.action == "upload_image":
            return RecipeImageSerializer
        
        return self.serializer_class
    
    def perform_create(self, serializer):
        """Create a new recipe"""
        serializer.save(user=self.request.user)

    @action(methods=["POST"], detail=True, url_path="upload-image")
    def upload_image(self, request, pk=None):
        """Upload image to a Recipe"""
        recipe = self.get_object()
        serializer = self.get_serializer(recipe, data=request.data)

        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)


@extend_schema_view(
    list=extend_schema(
        parameters = [
            OpenApiParameter(
                "assigned_only",
                OpenApiTypes.INT, enum=[0, 1],
                description="filter by items assign to recipe."
            )
        ]
        
    )
)
class BasicRecipeAttrViewSet(mixins.DestroyModelMixin, mixins.UpdateModelMixin, mixins.ListModelMixin, viewsets.GenericViewSet):
    """Basic viewset for Recipe attributes."""
    authentication_classes = [TokenAuthentication]
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assigned_only=bool(
            int(self.request.query_params.get("assigned_only", 0))
        )
        queryset = self.queryset
        if assigned_only:
            queryset = queryset.filter(recipe__isnull=False)

        return queryset.filter(user=self.request.user).order_by("-name").distinct()
    

class TagViewSet(BasicRecipeAttrViewSet):
    """Manage Tag in the Database."""
    serializer_class = TagSerializer
    queryset = Tag.objects.all()
    

class IngredientViewSet(BasicRecipeAttrViewSet):
    """Manage Ingredient in database."""
    serializer_class = IngredientSerializer
    queryset = Ingredient.objects.all()



