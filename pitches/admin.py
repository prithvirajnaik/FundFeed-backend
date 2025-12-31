from django.contrib import admin
from .models import Pitch, SavedPitch

@admin.register(Pitch)
class PitchAdmin(admin.ModelAdmin):
    list_display = ("title", "developer", "status", "funding_stage", "views", "created_at")
    list_filter = ("status", "funding_stage", "created_at")
    search_fields = ("title", "tags", "developer__email")
    ordering = ("-created_at",)
    readonly_fields = ("id", "views", "created_at")

    actions = ["approve_pitches", "reject_pitches"]

    def approve_pitches(self, request, queryset):
        queryset.update(status="approved")

    def reject_pitches(self, request, queryset):
        queryset.update(status="rejected")

    approve_pitches.short_description = "Approve selected pitches"
    reject_pitches.short_description = "Reject selected pitches"


@admin.register(SavedPitch)
class SavedPitchAdmin(admin.ModelAdmin):
    list_display = ("investor", "pitch", "saved_at")
    list_filter = ("saved_at",)
    search_fields = ("investor__email", "pitch__title")
    readonly_fields = ("saved_at",)
