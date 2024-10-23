from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .forms import CustomUserChangeForm, CustomUserCreationForm
from .models import Admin, CustomUser, Expert, Labeler


# Custom UserAdmin for the Django admin
class CustomUserAdmin(UserAdmin):
    add_form = CustomUserCreationForm
    form = CustomUserChangeForm
    model = CustomUser
    list_display = ["email", "role", "is_staff"]
    ordering = ["email"]
    fieldsets = UserAdmin.fieldsets + ((None, {"fields": ("role",)}),)


admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(Labeler)
admin.site.register(Expert)
admin.site.register(Admin)
