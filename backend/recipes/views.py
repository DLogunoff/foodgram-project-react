from django.http import HttpResponse
from django.shortcuts import get_object_or_404
from django_filters.rest_framework import DjangoFilterBackend
from reportlab.pdfbase import pdfmetrics
from reportlab.pdfbase.ttfonts import TTFont
from reportlab.pdfgen import canvas
from rest_framework import filters, status, viewsets
from rest_framework.decorators import api_view
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.response import Response
from rest_framework.views import APIView

from .filters import RecipeFilter
from .models import (Favorite, Ingredient, IngredientInRecipe, Recipe,
                     ShoppingCart, Tag)
from .permissions import AdminOrAuthorOrReadOnly
from .serializers import (CreateRecipeSerializer, FavoriteSerializer,
                          IngredientSerializer, ShoppingCartSerializer,
                          ShowRecipeSerializer, TagSerializer)


class TagViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Describes Tag viewset, which allows only GET-method.
    With router works as /api/tags/ to get the list of all tags
    and /api/tags/<id> to get tag by id
    permissions: All users can use this url.
    """
    queryset = Tag.objects.all()
    serializer_class = TagSerializer
    permission_classes = [AllowAny, ]


class IngredientViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Describes Tag viewset, which allows only GET-method.
    With router works as /api/ingredients/ to get the list of all ingredients
    and /api/ingredients/<id> to get ingredient by id
    permissions: All users can use this url.
    """
    queryset = Ingredient.objects.all()
    serializer_class = IngredientSerializer
    permission_classes = [AllowAny, ]
    filter_backends = [filters.SearchFilter]
    search_fields = ('name', )


class RecipeViewSet(viewsets.ModelViewSet):
    """
    Describes ViewSet, which provides get/post/delete/patch methods
    to work with recipes
    """

    queryset = Recipe.objects.all()
    permission_classes = [AdminOrAuthorOrReadOnly, ]
    filter_backends = [DjangoFilterBackend, ]
    filterset_class = RecipeFilter

    def get_serializer_class(self):
        if self.request.method == 'GET':
            return ShowRecipeSerializer
        return CreateRecipeSerializer

    def get_serializer_context(self):
        context = super(RecipeViewSet, self).get_serializer_context()
        context.update({'request': self.request})
        return context


class FavoriteViewSet(APIView):
    """
    Describes ViewSet to add and delete Favorite recipes
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get_or_create(user=user, recipe=recipe)
        serializer = FavoriteSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        Favorite.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class ShoppingCartViewSet(APIView):
    """
    Describes ViewSet to add and delete recipes to/from shopping cart
    """

    permission_classes = [IsAuthenticated, ]

    def post(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if Favorite.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get_or_create(user=user, recipe=recipe)
        serializer = ShoppingCartSerializer(recipe)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    def delete(self, request, recipe_id):
        user = self.request.user
        recipe = get_object_or_404(Recipe, id=recipe_id)
        if not ShoppingCart.objects.filter(user=user, recipe=recipe).exists():
            return Response(status=status.HTTP_400_BAD_REQUEST)
        ShoppingCart.objects.get(user=user, recipe=recipe).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
def DownloadShoppingCart(request):
    """
    Describes View-function, which allows to download a PDF file
    listing the ingredients that are present in the recipes that
    are added to shopping cart
    with name, measurement units and
    summarized amount of those ingredients.
    """

    user = request.user
    shopping_cart = user.shopping_cart.all()
    buying_list = {}
    for i in range(len(shopping_cart)):
        recipe = shopping_cart[i].recipe
        ingredients = IngredientInRecipe.objects.filter(recipe=recipe)
        for j in range(len(ingredients)):
            amount = ingredients[j].amount
            name = ingredients[j].ingredient.name
            measurement_unit = ingredients[j].ingredient.measurement_unit
            if name not in buying_list.keys():
                buying_list[name] = {
                    'measurement_unit': measurement_unit,
                    'amount': amount
                }
            else:
                buying_list[name]['amount'] = (buying_list[name]['amount']
                                               + amount)
    file_name = 'buying_list'
    pdfmetrics.registerFont(TTFont('DejaVuSerif', 'DejaVuSerif.ttf'))
    response = HttpResponse(content_type='application/pdf')
    response['Content-Disposition'] = f'attachment; filename="{file_name}.pdf"'
    p = canvas.Canvas(response)
    p.setFont('DejaVuSerif', 15)
    height = 800
    for name, data in buying_list.items():
        p.drawString(
            50,
            height,
            f"{name} ({data['measurement_unit']}) - {data['amount']}"
        )
        height -= 25
    p.showPage()
    p.save()
    return response
