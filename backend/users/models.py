from django.contrib.auth.models import AbstractBaseUser, PermissionsMixin
from django.db import models
from django.utils import timezone

from .managers import CustomUserManager


class CustomUser(AbstractBaseUser, PermissionsMixin):
    """
    Describes CustomUser model, which includes
    'first_name', 'last_name' and 'email'
    as required fields.
    """

    email = models.EmailField(
        unique=True,
        verbose_name='Электронная почта'
    )
    username = models.CharField(
        max_length=150,
        verbose_name='Имя пользователя',
        unique=True
    )
    first_name = models.CharField(max_length=150, verbose_name='Имя')
    last_name = models.CharField(max_length=150, verbose_name='Фамилия')
    is_staff = models.BooleanField(
        default=False, verbose_name='Администратор'
    )
    is_active = models.BooleanField(
        default=True, verbose_name='Активен'
    )
    date_joined = models.DateTimeField(
        default=timezone.now, verbose_name='Дата регистрации'
    )
    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['first_name', 'last_name', 'username']

    objects = CustomUserManager()

    class Meta:
        ordering = ('username',)
        verbose_name = 'Пользователь'
        verbose_name_plural = 'Пользователи'

    def __str__(self):
        return self.email

    def is_admin(self):
        return self.is_staff


class Follow(models.Model):
    """
    Describes Follow model. Used in implementation of
    subscribe system.
    """

    user = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='follower',
        verbose_name='Пользователь'
    )
    author = models.ForeignKey(
        CustomUser,
        on_delete=models.CASCADE,
        related_name='following',
        verbose_name='На кого подписан'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        null=True,
        verbose_name='Время создания'
    )

    class Meta:
        ordering = ['-created_at']
        verbose_name = 'Подписка'
        verbose_name_plural = 'Подписки'
        constraints = [
            models.UniqueConstraint(
                fields=['user', 'author'], name='unique_sub'
            )
        ]

    def __str__(self):
        return f'{self.user} following {self.author}'
