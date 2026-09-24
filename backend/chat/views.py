import uuid

from django.db import transaction
from django.shortcuts import get_object_or_404
from rest_framework import status
from rest_framework.exceptions import ValidationError
from rest_framework.parsers import MultiPartParser
from rest_framework.response import Response
from rest_framework.views import APIView

from chat.models import Booking, Conversation, Diagnosis, MediaFile, Message
from chat.serializers import (
    BookingSerializer,
    ChatRequestSerializer,
    ConversationDetailSerializer,
    ConversationSerializer,
    DiagnosisRequestSerializer,
    DiagnosisSerializer,
    MediaFileSerializer,
    MessageSerializer,
    UploadSerializer,
)
from chat.services import chatbot
from chat.services.media import MAX_TOTAL_MEDIA_SIZE, validate_upload


def get_client_id(request):
    """Every browser sends a random X-Client-Id so users only see their own data."""
    try:
        return uuid.UUID(request.headers.get("X-Client-Id", ""))
    except ValueError:
        raise ValidationError({"X-Client-Id": "A valid X-Client-Id header (UUID) is required."}) from None


class BaseAPIView(APIView):
    throttle_scope = "default"


class HealthView(BaseAPIView):
    def get(self, request):
        return Response({"status": "ok"})


class ChatView(BaseAPIView):
    throttle_scope = "chat"

    def post(self, request):
        client_id = get_client_id(request)
        serializer = ChatRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        data = serializer.validated_data

        media_files = list(MediaFile.objects.filter(id__in=data["media_ids"], client_id=client_id, message__isnull=True))
        if len(media_files) != len(set(data["media_ids"])):
            raise ValidationError({"media_ids": "Some files were not found or are already used."})
        if sum(media.size for media in media_files) > MAX_TOTAL_MEDIA_SIZE:
            raise ValidationError({"media_ids": "Total file size is too large for one message."})

        if data.get("conversation_id"):
            conversation = get_object_or_404(Conversation, id=data["conversation_id"], client_id=client_id)
        else:
            conversation = Conversation.objects.create(client_id=client_id, title=data["message"][:60] or "Media upload")

        with transaction.atomic():
            user_message = Message.objects.create(conversation=conversation, role=Message.Role.USER, text=data["message"])
            MediaFile.objects.filter(id__in=[media.id for media in media_files]).update(message=user_message)

        reply = chatbot.handle_message(conversation, data["message"], media_files)
        bot_message = Message.objects.create(
            conversation=conversation, role=Message.Role.BOT, source=reply.source, text=reply.text
        )
        conversation.save(update_fields=["updated_at"])

        return Response(
            {
                "conversation_id": conversation.id,
                "state": conversation.state,
                "user_message": MessageSerializer(user_message).data,
                "reply": MessageSerializer(bot_message).data,
                "diagnosis": DiagnosisSerializer(reply.diagnosis).data if reply.diagnosis else None,
                "action": reply.action,
            },
            status=status.HTTP_201_CREATED,
        )


class UploadView(BaseAPIView):
    throttle_scope = "upload"
    parser_classes = [MultiPartParser]

    def post(self, request):
        client_id = get_client_id(request)
        serializer = UploadSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        uploaded_file = serializer.validated_data["file"]

        kind, mime_type, extension = validate_upload(uploaded_file)
        original_name = uploaded_file.name[:255]
        uploaded_file.name = f"{uuid.uuid4().hex}.{extension}"

        media = MediaFile.objects.create(
            client_id=client_id,
            file=uploaded_file,
            original_name=original_name,
            kind=kind,
            content_type=mime_type,
            size=uploaded_file.size,
        )
        return Response(MediaFileSerializer(media).data, status=status.HTTP_201_CREATED)


class DiagnosisView(BaseAPIView):
    def get(self, request):
        client_id = get_client_id(request)
        diagnoses = Diagnosis.objects.filter(conversation__client_id=client_id).prefetch_related("bookings")[:50]
        return Response(DiagnosisSerializer(diagnoses, many=True).data)

    def post(self, request):
        client_id = get_client_id(request)
        serializer = DiagnosisRequestSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        conversation = get_object_or_404(Conversation, id=serializer.validated_data["conversation_id"], client_id=client_id)

        diagnosis = chatbot.diagnose_now(conversation)
        if diagnosis is None:
            raise ValidationError(
                {"conversation_id": "Not enough information yet. Please describe the car problem or answer a question first."}
            )
        return Response(DiagnosisSerializer(diagnosis).data, status=status.HTTP_201_CREATED)


class BookingCreateView(BaseAPIView):
    def post(self, request):
        client_id = get_client_id(request)
        serializer = BookingSerializer(data=request.data, context={"client_id": client_id})
        serializer.is_valid(raise_exception=True)

        with transaction.atomic():
            booking = serializer.save()
            Message.objects.create(
                conversation=booking.conversation,
                role=Message.Role.BOT,
                source=Message.Source.RULE,
                text=(
                    f"Your booking for {booking.service} on {booking.preferred_date:%d %b %Y} "
                    f"({booking.get_time_slot_display()}) is received. Booking ID: {booking.id}. "
                    "Our mechanic will call you to confirm."
                ),
            )
        return Response(BookingSerializer(booking).data, status=status.HTTP_201_CREATED)


class BookingDetailView(BaseAPIView):
    def get(self, request, booking_id):
        client_id = get_client_id(request)
        booking = get_object_or_404(Booking.objects.select_related("diagnosis"), id=booking_id, client_id=client_id)
        return Response(BookingSerializer(booking).data)


class ConversationListView(BaseAPIView):
    def get(self, request):
        client_id = get_client_id(request)
        conversations = Conversation.objects.filter(client_id=client_id).prefetch_related("diagnoses__bookings")[:50]
        return Response(ConversationSerializer(conversations, many=True).data)


class ConversationDetailView(BaseAPIView):
    def get(self, request, conversation_id):
        client_id = get_client_id(request)
        conversation = get_object_or_404(
            Conversation.objects.prefetch_related("messages__media", "diagnoses__bookings"),
            id=conversation_id,
            client_id=client_id,
        )
        return Response(ConversationDetailSerializer(conversation).data)
