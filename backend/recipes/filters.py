from django_filters import rest_framework as filters

from .models import Recipe, Ingredient


class RecipeFilter(filters.FilterSet):
    tags = filters.AllValuesMultipleFilter(
        field_name='tagsinrecipe__tag__slug'
    )
    is_favorited = filters.BooleanFilter(method='get_favorite')
    is_in_shopping_cart = filters.BooleanFilter(
        method='get_is_in_shopping_cart'
    )

    class Meta:
        model = Recipe
        fields = ('is_favorited', 'is_in_shopping_cart', 'author', 'tags')

    def get_favorite(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(favorites__user=user)
        return Recipe.objects.all()

    def get_is_in_shopping_cart(self, queryset, name, value):
        user = self.request.user
        if value:
            return Recipe.objects.filter(shopping_cart__user=user)
        return Recipe.objects.all()


class IngredientFilter(filters.FilterSet):
    name = filters.CharFilter(field_name='name', lookup_expr='icontains')

    class Meta:
        model = Ingredient
        fields = ('name', )
