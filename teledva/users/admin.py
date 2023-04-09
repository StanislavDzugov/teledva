from django.contrib import admin

from .models import Company, CustomUser


class CustomUserAdmin(admin.ModelAdmin):
    exclude = ('password', )

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Company)