from django.contrib.auth import get_user_model
from django.db import models

User = get_user_model()


class Tag(models.Model):
    """Describe Tag model."""
    BLUE = '#0000FF'
    RED = '#FF0000'
    GREEN = '#008000'
    LIGHT_GREEN = '#6FFF00'
    PURPLE = '#800080'
    TURQUOISE = '#40E0D0'
    YELLOW = '#FFFF00'
    BROWN = '#A52A2A'

    COLOR_CHOICES = [
        (BLUE, 'Синий'),
        (RED, 'Красный'),
        (GREEN, 'Зелёный'),
        (LIGHT_GREEN, 'Светло-зелёный'),
        (PURPLE, 'Фиолетовый'),
        (TURQUOISE, 'Бирюзовый'),
        (YELLOW, 'Жёлтый'),
        (BROWN, 'Коричневый')
    ]

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название тега',
    )
    color = models.CharField(
        max_length=7,
        choices=COLOR_CHOICES,
        unique=True,
        verbose_name='Цвет',
    )
    slug = models.SlugField(
        max_length=200,
        unique=True,
        verbose_name='Слаг'
    )

    class Meta:
        ordering = ['id']
        verbose_name = 'Тег'
        verbose_name_plural = 'Теги'

    def __str__(self):
        return self.name


class Ingredient(models.Model):
    """Describes Ingredient model"""

    name = models.CharField(
        max_length=200,
        unique=True,
        verbose_name='Название ингредиента'
    )
    measurement_unit = models.CharField(
        max_length=20, verbose_name='Единица измерения'
    )

    class Meta:
        ordering = ['name']
        verbose_name = 'Ингредиент'
        verbose_name_plural = 'Ингредиенты'

    def __str__(self):
        return self.name


class Recipe(models.Model):
    MAX_COOKING_TIME = 1000

    author = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='recipes',
        verbose_name='Автор'
    )
    tags = models.ManyToManyField(
        Tag,
        through='TagsInRecipe'
    )
    name = models.CharField(max_length=200, verbose_name='Название')
    text = models.TextField(verbose_name='Описание')
    cooking_time = models.PositiveSmallIntegerField(
        verbose_name='Время приготовления'
    )
    ingredients = models.ManyToManyField(
        Ingredient,
        through='IngredientInRecipe',
        related_name='recipes',
        blank=True,
    )
    pub_date = models.DateTimeField(
        auto_now_add=True,
        verbose_name='Время публикации'
    )
    image = models.ImageField(
        upload_to='recipes/images/',
        verbose_name='Изображение',
    )

    class Meta:
        ordering = ['-pub_date']
        verbose_name = 'Рецепт'
        verbose_name_plural = 'Рецепты'

    def __str__(self):
        return self.name


class TagsInRecipe(models.Model):
    """
    Describes Tag-Recipe model, which will be used
    by Recipe model.
    This model is created by hand to set correct display in
    admin panel
    """

    tag = models.ForeignKey(
        Tag,
        verbose_name='Тег в рецепте',
        on_delete=models.CASCADE
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
    )

    class Meta:
        verbose_name = 'Теги в рецепте'
        verbose_name_plural = verbose_name


class IngredientInRecipe(models.Model):
    """
    Describes Ingredient-Recipe model, which will be used
    by Recipe model
    """

    ingredient = models.ForeignKey(
        Ingredient,
        on_delete=models.CASCADE,
        verbose_name='Ингредиент в рецепте'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        verbose_name='Рецепт'
    )
    amount = models.PositiveSmallIntegerField(
        null=True, blank=True,
        verbose_name='Количество ингредиента',
    )

    class Meta:
        verbose_name = 'Количество ингредиента в рецепте'
        verbose_name_plural = verbose_name

    def __str__(self):
        return f'{self.ingredient} in {self.recipe}'


class Favorite(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='favorites',
        verbose_name='Рецепт'
    )
    when_added = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления'
    )

    class Meta:
        ordering = ['-when_added', ]
        verbose_name = 'Избранное'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_favorite'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe}'


class ShoppingCart(models.Model):
    user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Пользователь'
    )
    recipe = models.ForeignKey(
        Recipe,
        on_delete=models.CASCADE,
        related_name='shopping_cart',
        verbose_name='Рецепт'
    )
    when_added = models.DateTimeField(
        auto_now_add=True, verbose_name='Дата добавления'
    )

    class Meta:
        verbose_name = 'Корзина'
        verbose_name_plural = verbose_name
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'recipe'], name='unique_shopping_cart'
            )
        ]

    def __str__(self):
        return f'{self.user} added {self.recipe}'
