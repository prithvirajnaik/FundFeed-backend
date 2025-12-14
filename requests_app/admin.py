from django.contrib import admin
from .models import ContactRequest, MeetingSummary

@admin.register(ContactRequest)
class ContactRequestAdmin(admin.ModelAdmin):
    list_display = ("developer", "investor", "preference", "viewed", "meeting_status", "created_at")
    list_filter = ("preference", "viewed", "meeting_status", "meeting_platform", "created_at")
    search_fields = ("developer__email", "investor__email", "message")
    readonly_fields = ("id", "created_at")

@admin.register(MeetingSummary)
class MeetingSummaryAdmin(admin.ModelAdmin):
    list_display = ("contact_request", "needs_followup", "created_at", "updated_at")
    list_filter = ("needs_followup", "created_at")
    search_fields = ("contact_request__id", "next_steps")
    readonly_fields = ("id", "created_at", "updated_at")

