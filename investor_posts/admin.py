from django.contrib import admin
from .models import InvestorPost, SavedInvestorPost

@admin.register(InvestorPost)
class InvestorPostAdmin(admin.ModelAdmin):
    list_display = ("title", "investor", "amount_range", "location", "views", "created_at")
    list_filter = ("location", "created_at")
    search_fields = ("title", "tags", "investor__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "views", "saved_count", "created_at")

@admin.register(SavedInvestorPost)
class SavedInvestorPostAdmin(admin.ModelAdmin):
    list_display = ("developer", "post", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("developer__email", "post__title")
    readonly_fields = ("saved_at",)
