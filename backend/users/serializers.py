from django.contrib.auth import authenticate, get_user_model
from django.utils.translation import gettext_lazy
from djoser.serializers import UserSerializer as BaseUserSerializer
from rest_framework import serializers

from foodgram.settings import RECIPES_LIMIT
from recipes.models import Recipe

from .models import Follow

User = get_user_model()


class UserSerializerModified(BaseUserSerializer):
    """
    Describes modified UserSerializer, which includes
    'is_subscribed' field
    """

    is_subscribed = serializers.SerializerMethodField()

    class Meta(BaseUserSerializer.Meta):
        fields = ('email', 'id', 'username',
                  'first_name', 'last_name', 'is_subscribed')

    def get_is_subscribed(self, obj):
        user = self.context.get('request', None).user
        if user.is_anonymous:
            return False
        return Follow.objects.filter(user=user, author=obj).exists()


class MyAuthTokenSerializer(serializers.Serializer):
    """
    Describes Auth serializer, which will use email-password
    combination to generate token.
    """
    email = serializers.EmailField(label=gettext_lazy("Email"))
    password = serializers.CharField(
        label=gettext_lazy("Password",),
        style={'input_type': 'password'},
        trim_whitespace=False
    )

    def validate(self, attrs):
        email = attrs.get('email')
        password = attrs.get('password')

        if email and password:
            user = authenticate(request=self.context.get('request'),
                                email=email, password=password)
            if not user:
                msg = gettext_lazy('Неверные данные для входа.')
                raise serializers.ValidationError(msg, code='authorization')
        else:
            msg = gettext_lazy('Авторизация производится по email и паролю.')
            raise serializers.ValidationError(msg, code='authorization')

        attrs['user'] = user
        return attrs


class FollowRecipeSerializer(serializers.ModelSerializer):
    """
    Describes Recipe Serializer, which used in FollowSerializer
    """

    class Meta:
        model = Recipe
        fields = ('id', 'name', 'image', 'cooking_time')


class FollowSerializer(serializers.ModelSerializer):
    is_subscribed = serializers.SerializerMethodField()
    recipes = serializers.SerializerMethodField()
    recipes_count = serializers.SerializerMethodField()

    class Meta:
        model = User
        fields = ('email', 'id', 'username', 'first_name', 'last_name',
                  'is_subscribed', 'recipes', 'recipes_count')

    def get_is_subscribed(self, obj):
        user = self.context.get('request', None).user
        return obj.follower.filter(user=obj, author=user).exists()

    def get_recipes(self, obj):
        recipes = obj.recipe_author.all()[:RECIPES_LIMIT]
        return FollowRecipeSerializer(recipes, many=True).data

    def get_recipes_count(self, obj):
        return obj.recipe_author.count()
