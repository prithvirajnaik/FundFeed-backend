# from django.contrib import admin
# from .models import User
# from django.contrib.auth.admin import UserAdmin

# class CustomUserAdmin(UserAdmin):
#     model = User
#     list_display = ("email", "username", "role", "is_staff", "is_active")
#     list_filter = ("role", "is_staff", "is_active")
#     fieldsets = (
#         (None, {"fields": ("email", "password")}),
#         ("Personal info", {"fields": ("username", "avatar_url", "location")}),
#         ("Permissions", {"fields": ("is_staff", "is_active", "groups", "user_permissions")}),
#     )
#     add_fieldsets = (
#         (None, {
#             "classes": ("wide",),
#             "fields": ("email", "username", "password1", "password2", "role", "is_staff", "is_active")
#         }),
#     )
#     search_fields = ("email", "username")
#     ordering = ("email",)

# admin.site.register(User, CustomUserAdmin)

from django.contrib import admin
from .models import User, DeveloperProfile, InvestorProfile

@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "username", "role", "status", "is_active")
    list_filter = ("role", "status", "is_active")
    search_fields = ("email", "username")
    ordering = ("email",)
    readonly_fields = ("id",)

    actions = ["approve_users", "reject_users"]

    def approve_users(self, request, queryset):
        queryset.update(status="approved", is_active=True)

    def reject_users(self, request, queryset):
        queryset.update(status="rejected", is_active=False)

    approve_users.short_description = "Approve selected users"
    reject_users.short_description = "Reject selected users"

@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "title")
    search_fields = ("user__email", "title", "skills")
    list_filter = ("title",)

@admin.register(InvestorProfile)
class InvestorProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "firm", "investor_type")
    search_fields = ("user__email", "firm", "investor_type")
    list_filter = ("investor_type",)
