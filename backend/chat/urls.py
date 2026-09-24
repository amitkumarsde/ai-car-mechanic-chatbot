from django.urls import path

from chat import views

urlpatterns = [
    path("health/", views.HealthView.as_view(), name="health"),
    path("chat/", views.ChatView.as_view(), name="chat"),
    path("upload/", views.UploadView.as_view(), name="upload"),
    path("diagnosis/", views.DiagnosisView.as_view(), name="diagnosis"),
    path("booking/", views.BookingCreateView.as_view(), name="booking-create"),
    path("booking/<uuid:booking_id>/", views.BookingDetailView.as_view(), name="booking-detail"),
    path("conversations/", views.ConversationListView.as_view(), name="conversation-list"),
    path("conversations/<uuid:conversation_id>/", views.ConversationDetailView.as_view(), name="conversation-detail"),
]
