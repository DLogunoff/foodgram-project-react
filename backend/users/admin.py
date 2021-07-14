from django.contrib import admin

from .models import CustomUser, Follow


class CustomUserAdmin(admin.ModelAdmin):
    list_display = ('id', 'username', 'email',
                    'first_name', 'last_name', 'is_staff'
                    )
    list_filter = ('email', 'username')
    search_fields = ('username',)
    empty_value_display = '---'


class FollowAdmin(admin.ModelAdmin):
    list_display = ('id', 'user', 'author', 'created_at')
    list_filter = ('created_at', )


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Follow, FollowAdmin)
