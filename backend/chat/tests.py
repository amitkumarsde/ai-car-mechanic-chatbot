import shutil
import tempfile
import uuid
from datetime import timedelta
from types import SimpleNamespace
from unittest.mock import patch

from django.core.files.uploadedfile import SimpleUploadedFile
from django.core.cache import cache
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APITestCase

from chat.models import Booking, Conversation, Diagnosis, MediaFile
from chat.services import gemini

PNG_BYTES = b"\x89PNG\r\n\x1a\n" + b"\x00" * 64
TEMP_MEDIA = tempfile.mkdtemp()


@override_settings(MEDIA_ROOT=TEMP_MEDIA, GEMINI_API_KEY="")
class BaseTest(APITestCase):
    def setUp(self):
        cache.clear()
        self.client_id = str(uuid.uuid4())
        self.client.credentials(HTTP_X_CLIENT_ID=self.client_id)

    @classmethod
    def tearDownClass(cls):
        super().tearDownClass()
        shutil.rmtree(TEMP_MEDIA, ignore_errors=True)

    def chat(self, message, conversation_id=None, media_ids=None):
        body = {"message": message, "media_ids": media_ids or []}
        if conversation_id:
            body["conversation_id"] = conversation_id
        return self.client.post("/api/chat/", body, format="json")

    def diagnose_by_rules(self):
        conversation_id = self.chat("My car is not starting")
        conversation_id = conversation_id.data["conversation_id"]
        for answer in ["yes", "yes", "no"]:
            response = self.chat(answer, conversation_id)
        return conversation_id, response


class ChatRuleTests(BaseTest):
    def test_missing_client_id_is_rejected(self):
        self.client.credentials()
        response = self.chat("hello")
        self.assertEqual(response.status_code, 400)
        self.assertIn("error", response.data)

    def test_empty_message_is_rejected(self):
        response = self.chat("")
        self.assertEqual(response.status_code, 400)

    def test_greeting_uses_rules(self):
        for text in ["Hello", "hello there", "Hi, can you help me?"]:
            response = self.chat(text)
            self.assertEqual(response.status_code, 201)
            self.assertIn("virtual car mechanic", response.data["reply"]["text"])

    @patch("chat.services.gemini.ask_mechanic")
    def test_non_car_question_is_rejected_without_ai(self, mock_ai):
        response = self.chat("What is the capital of France?")
        self.assertIn("only help with car", response.data["reply"]["text"])
        mock_ai.assert_not_called()

    @patch("chat.services.gemini.ask_mechanic")
    def test_known_issue_asks_follow_up_then_diagnoses_without_ai(self, mock_ai):
        first = self.chat("My car is not starting")
        self.assertEqual(first.data["state"], "asking")
        self.assertIn("clicking", first.data["reply"]["text"])

        conversation_id, last = self.diagnose_by_rules()
        self.assertEqual(last.data["state"], "diagnosed")
        self.assertEqual(last.data["diagnosis"]["problem"], "Weak or dead battery")
        self.assertEqual(last.data["diagnosis"]["source"], "rule")
        self.assertIn("My diagnosis: Weak or dead battery", last.data["reply"]["text"])
        mock_ai.assert_not_called()

    def test_yes_after_diagnosis_opens_booking_form(self):
        conversation_id, _ = self.diagnose_by_rules()
        response = self.chat("yes please book", conversation_id)
        self.assertEqual(response.data["action"], "show_booking_form")

    def test_new_problem_after_diagnosis_starts_new_questions(self):
        conversation_id, _ = self.diagnose_by_rules()
        response = self.chat("no, but now my brakes are squeaking", conversation_id)
        self.assertEqual(response.data["state"], "asking")
        self.assertIn("brake", response.data["reply"]["text"].lower())

    def test_not_sure_answer_is_not_counted_as_no(self):
        conversation_id = self.chat("My car is not starting").data["conversation_id"]
        self.chat("not sure", conversation_id)
        self.assertIsNone(Conversation.objects.get(id=conversation_id).answers[0]["value"])

    def test_other_user_cannot_use_conversation(self):
        conversation_id = self.chat("Hello").data["conversation_id"]
        self.client.credentials(HTTP_X_CLIENT_ID=str(uuid.uuid4()))
        response = self.chat("hi", conversation_id)
        self.assertEqual(response.status_code, 404)


class ChatAITests(BaseTest):
    @patch("chat.services.gemini.ask_mechanic")
    def test_unknown_car_issue_uses_ai(self, mock_ai):
        mock_ai.return_value = {"is_car_related": True, "reply": "Which car model is it?", "diagnosis": None}
        response = self.chat("My steering wheel feels heavy")
        self.assertEqual(response.data["reply"]["source"], "ai")
        self.assertEqual(response.data["state"], "ai_chat")

    @patch("chat.services.gemini.ask_mechanic")
    def test_ai_diagnosis_is_saved(self, mock_ai):
        mock_ai.return_value = {
            "is_car_related": True,
            "reply": "Thanks for the details.",
            "diagnosis": {
                "problem": "Low power steering fluid", "details": "", "recommendation": "Top up fluid",
                "service": "Power Steering Service", "urgency": "medium", "estimated_cost": "₹500 - ₹2,000",
            },
        }
        response = self.chat("My steering wheel feels heavy")
        self.assertEqual(response.data["diagnosis"]["source"], "ai")
        self.assertEqual(Diagnosis.objects.count(), 1)

    @patch("chat.services.gemini.ask_mechanic", side_effect=gemini.GeminiError("down"))
    def test_ai_failure_returns_friendly_message(self, _):
        response = self.chat("My steering wheel feels heavy")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["reply"]["source"], "rule")
        self.assertIn("could not analyse", response.data["reply"]["text"])

    @override_settings(GEMINI_API_KEY="test-key", GEMINI_MODEL="main-model", GEMINI_FALLBACK_MODEL="backup-model")
    @patch("chat.services.gemini.get_client")
    def test_backup_model_is_used_when_main_model_fails(self, mock_client):
        backup_reply = SimpleNamespace(text='{"is_car_related": true, "reply": "Backup answer", "diagnosis": null}')
        for main_failure in [Exception("503 busy"), SimpleNamespace(text="not json")]:
            generate = mock_client.return_value.models.generate_content
            generate.reset_mock()
            generate.side_effect = [main_failure, backup_reply]
            self.assertEqual(gemini.ask_mechanic([])["reply"], "Backup answer")
            self.assertEqual([call.kwargs["model"] for call in generate.call_args_list], ["main-model", "backup-model"])

    def test_parse_response_rejects_bad_json(self):
        with self.assertRaises(gemini.GeminiError):
            gemini.parse_response("not json")

    def test_parse_response_cleans_urgency(self):
        data = gemini.parse_response('{"reply": "ok", "diagnosis": {"problem": "X", "urgency": "super"}}')
        self.assertEqual(data["diagnosis"]["urgency"], "medium")


class UploadTests(BaseTest):
    def upload(self, name, content, content_type):
        file = SimpleUploadedFile(name, content, content_type=content_type)
        return self.client.post("/api/upload/", {"file": file}, format="multipart")

    def test_valid_image_upload(self):
        response = self.upload("dashboard.png", PNG_BYTES, "image/png")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["kind"], "image")
        self.assertNotIn("dashboard", MediaFile.objects.get().file.name)

    def test_wrong_extension_is_rejected(self):
        response = self.upload("virus.exe", b"MZ" + b"\x00" * 20, "application/octet-stream")
        self.assertEqual(response.status_code, 400)

    def test_fake_image_is_rejected(self):
        response = self.upload("fake.png", b"this is text", "image/png")
        self.assertEqual(response.status_code, 400)
        self.assertIn("does not match", str(response.data))

    @patch("chat.services.gemini.ask_mechanic")
    def test_chat_with_media_uses_ai(self, mock_ai):
        mock_ai.return_value = {"is_car_related": True, "reply": "I see a warning light.", "diagnosis": None}
        media_id = self.upload("light.png", PNG_BYTES, "image/png").data["id"]
        response = self.chat("What is this light?", media_ids=[media_id])
        self.assertEqual(response.data["reply"]["source"], "ai")
        self.assertEqual(len(response.data["user_message"]["media"]), 1)

    def test_media_of_other_user_cannot_be_used(self):
        media_id = self.upload("light.png", PNG_BYTES, "image/png").data["id"]
        self.client.credentials(HTTP_X_CLIENT_ID=str(uuid.uuid4()))
        response = self.chat("check this", media_ids=[media_id])
        self.assertEqual(response.status_code, 400)


class DiagnosisTests(BaseTest):
    def test_diagnose_now_from_partial_answers(self):
        conversation_id = self.chat("brakes are squeaking").data["conversation_id"]
        self.chat("yes", conversation_id)
        response = self.client.post("/api/diagnosis/", {"conversation_id": conversation_id}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["problem"], "Worn brake pads")

    def test_skip_questions_before_any_answer_gives_best_guess(self):
        conversation_id = self.chat("My car is not starting").data["conversation_id"]
        response = self.client.post("/api/diagnosis/", {"conversation_id": conversation_id}, format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["source"], "rule")

    def test_diagnosis_needs_information(self):
        conversation_id = self.chat("hello").data["conversation_id"]
        response = self.client.post("/api/diagnosis/", {"conversation_id": conversation_id}, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("Not enough information", response.data["error"]["message"])

    def test_diagnosis_history_lists_only_my_items(self):
        self.diagnose_by_rules()
        self.assertEqual(len(self.client.get("/api/diagnosis/").data), 1)
        self.client.credentials(HTTP_X_CLIENT_ID=str(uuid.uuid4()))
        self.assertEqual(len(self.client.get("/api/diagnosis/").data), 0)


class BookingTests(BaseTest):
    def booking_body(self, conversation_id, **changes):
        body = {
            "conversation_id": conversation_id,
            "customer_name": "Ravi Kumar",
            "phone": "98765 43210",
            "car_model": "Maruti Swift 2019",
            "address": "MG Road, Bengaluru",
            "preferred_date": str(timezone.localdate() + timedelta(days=1)),
            "time_slot": "morning",
        }
        body.update(changes)
        return body

    def test_create_and_get_booking(self):
        conversation_id, _ = self.diagnose_by_rules()
        response = self.client.post("/api/booking/", self.booking_body(conversation_id), format="json")
        self.assertEqual(response.status_code, 201)
        self.assertEqual(response.data["service"], "Battery Check & Replacement")
        self.assertEqual(response.data["status"], "pending")

        detail = self.client.get(f"/api/booking/{response.data['id']}/")
        self.assertEqual(detail.status_code, 200)
        self.assertEqual(detail.data["phone"], "9876543210")

    def test_same_diagnosis_cannot_be_booked_twice(self):
        conversation_id, _ = self.diagnose_by_rules()
        booking_id = self.client.post("/api/booking/", self.booking_body(conversation_id), format="json").data["id"]

        again = self.client.post("/api/booking/", self.booking_body(conversation_id), format="json")
        self.assertEqual(again.status_code, 400)
        self.assertIn("already booked", again.data["error"]["message"])

        chat_reply = self.chat("yes book it", conversation_id)
        self.assertIsNone(chat_reply.data["action"])
        self.assertIn("already booked", chat_reply.data["reply"]["text"])

        history = self.client.get("/api/diagnosis/").data
        self.assertEqual(str(history[0]["booking_id"]), str(booking_id))

    def test_past_date_and_bad_phone_are_rejected(self):
        conversation_id, _ = self.diagnose_by_rules()
        body = self.booking_body(conversation_id, phone="12ab", preferred_date="2020-01-01")
        response = self.client.post("/api/booking/", body, format="json")
        self.assertEqual(response.status_code, 400)
        self.assertIn("phone", response.data["error"]["details"])
        self.assertIn("preferred_date", response.data["error"]["details"])

    def test_other_user_cannot_see_booking(self):
        conversation_id, _ = self.diagnose_by_rules()
        booking_id = self.client.post("/api/booking/", self.booking_body(conversation_id), format="json").data["id"]
        self.client.credentials(HTTP_X_CLIENT_ID=str(uuid.uuid4()))
        self.assertEqual(self.client.get(f"/api/booking/{booking_id}/").status_code, 404)
        self.assertEqual(Booking.objects.count(), 1)

    def test_conversation_history_contains_messages(self):
        conversation_id, _ = self.diagnose_by_rules()
        response = self.client.get(f"/api/conversations/{conversation_id}/")
        self.assertEqual(response.status_code, 200)
        self.assertEqual(len(response.data["messages"]), 8)
        self.assertEqual(len(self.client.get("/api/conversations/").data), 1)
        self.assertEqual(Conversation.objects.count(), 1)
