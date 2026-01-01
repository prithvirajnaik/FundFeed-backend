from django.contrib import admin
from .models import Pitch, SavedPitch
from django.db import models
@admin.register(Pitch)
class PitchAdmin(admin.ModelAdmin):
    list_display = ("title", "developer", "status", "funding_stage", "views", "created_at")
    list_filter = ("status", "funding_stage", "created_at")
    search_fields = ("title", "tags", "developer__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "views", "created_at")

    # approve_pitches.short_description = "Approve selected pitches"
    # reject_pitches.short_description = "Reject selected pitches"

    def changelist_view(self, request, extra_context=None):
        extra_context = extra_context or {}
        extra_context['summary_stats'] = {
            'total_pitches': Pitch.objects.count(),
            'total_views': Pitch.objects.aggregate(models.Sum('views'))['views__sum'] or 0,
            'approved_count': Pitch.objects.filter(status='approved').count(),
        }
        return super().changelist_view(request, extra_context=extra_context)


@admin.register(SavedPitch)
class SavedPitchAdmin(admin.ModelAdmin):
    list_display = ("investor", "pitch", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("investor__email", "pitch__title")
    readonly_fields = ("saved_at",)
