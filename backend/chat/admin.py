from django.contrib import admin

from chat.models import Booking, Conversation, Diagnosis, MediaFile, Message


class MessageInline(admin.TabularInline):
    model = Message
    extra = 0
    readonly_fields = ["role", "source", "text", "created_at"]


@admin.register(Conversation)
class ConversationAdmin(admin.ModelAdmin):
    list_display = ["title", "state", "current_issue", "ai_turns", "updated_at"]
    list_filter = ["state"]
    inlines = [MessageInline]


@admin.register(Diagnosis)
class DiagnosisAdmin(admin.ModelAdmin):
    list_display = ["problem", "service", "urgency", "source", "created_at"]
    list_filter = ["source", "urgency"]


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ["customer_name", "phone", "service", "preferred_date", "time_slot", "status"]
    list_filter = ["status", "preferred_date"]
    list_editable = ["status"]


@admin.register(MediaFile)
class MediaFileAdmin(admin.ModelAdmin):
    list_display = ["original_name", "kind", "size", "created_at"]
