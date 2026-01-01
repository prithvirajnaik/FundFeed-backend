from django.contrib import admin
from .models import InvestorPost, SavedInvestorPost

from django.db import models

@admin.register(InvestorPost)
class InvestorPostAdmin(admin.ModelAdmin):
    list_display = ("title", "investor", "status", "location", "views", "created_at")
    list_filter = ("status", "location", "created_at")
    search_fields = ("title", "tags", "investor__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "views", "saved_count", "created_at")

    actions = ["approve_posts", "reject_posts"]

    def approve_posts(self, request, queryset):
        queryset.update(status="approved")

    def reject_posts(self, request, queryset):
        queryset.update(status="rejected")

    approve_posts.short_description = "Approve selected investor posts"
    reject_posts.short_description = "Reject selected investor posts"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['summary_stats'] = {
            'Total Posts': InvestorPost.objects.count(),
            'Total Views': InvestorPost.objects.aggregate(models.Sum('views'))['views__sum'] or 0,
            'Approved': InvestorPost.objects.filter(status='approved').count(),
        }
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(SavedInvestorPost)
class SavedInvestorPostAdmin(admin.ModelAdmin):
    list_display = ("developer", "post", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("developer__email", "post__title")
    readonly_fields = ("saved_at",)
