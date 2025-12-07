from django.contrib import admin
from .models import ContactRequest

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("developer", "investor", "preference", "viewed", "created_at")
    list_filter = ("preference", "viewed", "created_at")
    search_fields = ("developer__email", "investor__email", "message")
    readonly_fields = ("id", "created_at")
