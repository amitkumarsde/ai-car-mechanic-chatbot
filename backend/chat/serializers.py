from datetime import timedelta

from django.utils import timezone
from rest_framework import serializers

from chat.models import Booking, Conversation, Diagnosis, MediaFile, Message

MAX_BOOKING_DAYS_AHEAD = 60


class MediaFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = MediaFile
        fields = ["id", "kind", "original_name", "size"]


class MessageSerializer(serializers.ModelSerializer):
    media = MediaFileSerializer(many=True, read_only=True)

    class Meta:
        model = Message
        fields = ["id", "role", "source", "text", "media", "created_at"]


class DiagnosisSerializer(serializers.ModelSerializer):
    booking_id = serializers.SerializerMethodField()

    class Meta:
        model = Diagnosis
        fields = [
            "id", "conversation_id", "problem", "details", "recommendation", "service",
            "urgency", "estimated_cost", "source", "booking_id", "created_at",
        ]

    def get_booking_id(self, diagnosis):
        booking = diagnosis.bookings.first()
        return booking.id if booking else None


class ConversationSerializer(serializers.ModelSerializer):
    latest_diagnosis = serializers.SerializerMethodField()

    class Meta:
        model = Conversation
        fields = ["id", "title", "state", "latest_diagnosis", "created_at", "updated_at"]

    def get_latest_diagnosis(self, conversation):
        diagnosis = conversation.diagnoses.first()
        return DiagnosisSerializer(diagnosis).data if diagnosis else None


class ConversationDetailSerializer(ConversationSerializer):
    messages = MessageSerializer(many=True, read_only=True)
    diagnoses = DiagnosisSerializer(many=True, read_only=True)

    class Meta(ConversationSerializer.Meta):
        fields = [*ConversationSerializer.Meta.fields, "messages", "diagnoses"]


class ChatRequestSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField(required=False)
    message = serializers.CharField(max_length=2000, allow_blank=True, required=False, default="", trim_whitespace=True)
    media_ids = serializers.ListField(child=serializers.UUIDField(), max_length=3, required=False, default=list)

    def validate(self, data):
        if not data["message"] and not data["media_ids"]:
            raise serializers.ValidationError("Send a message or attach a file.")
        return data


class UploadSerializer(serializers.Serializer):
    file = serializers.FileField(max_length=255, allow_empty_file=False)


class DiagnosisRequestSerializer(serializers.Serializer):
    conversation_id = serializers.UUIDField()


class BookingSerializer(serializers.ModelSerializer):
    conversation_id = serializers.UUIDField(write_only=True)
    diagnosis_id = serializers.IntegerField(write_only=True, required=False, allow_null=True)
    diagnosis = DiagnosisSerializer(read_only=True)
    service = serializers.CharField(max_length=100, required=False, allow_blank=True)
    phone = serializers.CharField(max_length=20)

    class Meta:
        model = Booking
        fields = [
            "id", "conversation_id", "diagnosis_id", "diagnosis", "customer_name", "phone", "car_model",
            "service", "address", "preferred_date", "time_slot", "notes", "status", "created_at",
        ]
        read_only_fields = ["id", "status", "created_at"]

    def validate_customer_name(self, value):
        value = value.strip()
        if len(value) < 2:
            raise serializers.ValidationError("Name is too short.")
        return value

    def validate_phone(self, value):
        value = value.replace(" ", "").replace("-", "")
        Booking.phone_validator(value)
        return value

    def validate_preferred_date(self, value):
        today = timezone.localdate()
        if value < today:
            raise serializers.ValidationError("Date cannot be in the past.")
        if value > today + timedelta(days=MAX_BOOKING_DAYS_AHEAD):
            raise serializers.ValidationError(f"Date must be within {MAX_BOOKING_DAYS_AHEAD} days.")
        return value

    def validate(self, data):
        client_id = self.context["client_id"]
        conversation = Conversation.objects.filter(id=data.pop("conversation_id"), client_id=client_id).first()
        if conversation is None:
            raise serializers.ValidationError({"conversation_id": "Conversation not found."})

        diagnosis_id = data.pop("diagnosis_id", None)
        diagnosis = conversation.diagnoses.filter(id=diagnosis_id).first() if diagnosis_id else conversation.diagnoses.first()
        if diagnosis_id and diagnosis is None:
            raise serializers.ValidationError({"diagnosis_id": "Diagnosis not found in this conversation."})
        if diagnosis and diagnosis.bookings.exists():
            raise serializers.ValidationError({"diagnosis_id": "A mechanic is already booked for this diagnosis."})

        if not data.get("service"):
            if diagnosis is None:
                raise serializers.ValidationError({"service": "Service is required when there is no diagnosis."})
            data["service"] = diagnosis.service

        data.update(conversation=conversation, diagnosis=diagnosis, client_id=client_id)
        return data
