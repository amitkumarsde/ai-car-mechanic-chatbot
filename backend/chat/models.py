import uuid

from django.core.validators import RegexValidator
from django.db import models


class Conversation(models.Model):
    class State(models.TextChoices):
        NEW = "new"
        ASKING = "asking"
        AI_CHAT = "ai_chat"
        DIAGNOSED = "diagnosed"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(db_index=True)
    title = models.CharField(max_length=120, blank=True)
    state = models.CharField(max_length=20, choices=State.choices, default=State.NEW)
    current_issue = models.CharField(max_length=50, blank=True)
    question_index = models.PositiveSmallIntegerField(default=0)
    answers = models.JSONField(default=list, blank=True)
    ai_turns = models.PositiveSmallIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ["-updated_at"]

    def __str__(self):
        return self.title or str(self.id)


class Message(models.Model):
    class Role(models.TextChoices):
        USER = "user"
        BOT = "bot"

    class Source(models.TextChoices):
        USER = "user"
        RULE = "rule"
        AI = "ai"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="messages")
    role = models.CharField(max_length=10, choices=Role.choices)
    source = models.CharField(max_length=10, choices=Source.choices, default=Source.USER)
    text = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["created_at", "id"]


class MediaFile(models.Model):
    class Kind(models.TextChoices):
        IMAGE = "image"
        AUDIO = "audio"
        VIDEO = "video"

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(db_index=True)
    message = models.ForeignKey(Message, on_delete=models.SET_NULL, null=True, blank=True, related_name="media")
    file = models.FileField(upload_to="uploads/%Y/%m/")
    original_name = models.CharField(max_length=255)
    kind = models.CharField(max_length=10, choices=Kind.choices)
    content_type = models.CharField(max_length=100)
    size = models.PositiveIntegerField()
    created_at = models.DateTimeField(auto_now_add=True)


class Diagnosis(models.Model):
    class Urgency(models.TextChoices):
        LOW = "low"
        MEDIUM = "medium"
        HIGH = "high"

    class Source(models.TextChoices):
        RULE = "rule"
        AI = "ai"

    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="diagnoses")
    problem = models.CharField(max_length=200)
    details = models.TextField(blank=True)
    recommendation = models.TextField()
    service = models.CharField(max_length=100)
    urgency = models.CharField(max_length=10, choices=Urgency.choices, default=Urgency.MEDIUM)
    estimated_cost = models.CharField(max_length=60, blank=True)
    source = models.CharField(max_length=10, choices=Source.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
        verbose_name_plural = "diagnoses"


class Booking(models.Model):
    class Status(models.TextChoices):
        PENDING = "pending"
        CONFIRMED = "confirmed"
        CANCELLED = "cancelled"

    class TimeSlot(models.TextChoices):
        MORNING = "morning", "Morning (9 AM - 12 PM)"
        AFTERNOON = "afternoon", "Afternoon (12 PM - 4 PM)"
        EVENING = "evening", "Evening (4 PM - 7 PM)"

    phone_validator = RegexValidator(r"^\+?[0-9]{10,13}$", "Enter a valid phone number (10 to 13 digits).")

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    client_id = models.UUIDField(db_index=True)
    conversation = models.ForeignKey(Conversation, on_delete=models.CASCADE, related_name="bookings")
    diagnosis = models.ForeignKey(Diagnosis, on_delete=models.SET_NULL, null=True, blank=True, related_name="bookings")
    customer_name = models.CharField(max_length=100)
    phone = models.CharField(max_length=15, validators=[phone_validator])
    car_model = models.CharField(max_length=100)
    service = models.CharField(max_length=100)
    address = models.CharField(max_length=255)
    preferred_date = models.DateField()
    time_slot = models.CharField(max_length=10, choices=TimeSlot.choices)
    notes = models.TextField(blank=True, max_length=500)
    status = models.CharField(max_length=10, choices=Status.choices, default=Status.PENDING)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ["-created_at"]
