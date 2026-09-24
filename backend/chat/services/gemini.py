import json
import logging

from django.conf import settings
from google import genai
from google.genai import types

logger = logging.getLogger(__name__)

SYSTEM_PROMPT = """You are a senior automobile technician with 20 years of experience helping car owners in India.
Rules:
1. Only answer car or vehicle mechanical questions. If the question is not about cars, set is_car_related to false and politely say you can only help with car problems.
2. Before giving a diagnosis, ask short follow-up questions (one or two at a time) about symptoms, when it happens, car model and age.
3. If the customer shared images, audio or video, study them and mention only what you can clearly see or hear. Never guess or invent details (like smoke, steam or leaks) that are not really there. If the media is unclear, say so and ask questions.
4. Give a diagnosis only when you have enough information. Keep replies short, simple, polite and friendly, in plain English.
5. Never invent exact prices; give a rough cost range in Indian Rupees.
Reply ONLY with JSON in this shape:
{"is_car_related": true, "reply": "text for the customer", "diagnosis": null}
When you are ready to diagnose, diagnosis must be:
{"problem": "...", "details": "...", "recommendation": "...", "service": "...", "urgency": "low|medium|high", "estimated_cost": "₹x - ₹y"}"""

FORCE_DIAGNOSIS_NOTE = "\nYou must give your best diagnosis now in the diagnosis field, even if some information is missing."

_client = None


class GeminiError(Exception):
    pass


def get_client():
    global _client
    if _client is None:
        # Retry only "server busy" errors; 50s per try keeps main + backup model within a normal web request
        retry = types.HttpRetryOptions(attempts=3, http_status_codes=[500, 502, 503, 504])
        _client = genai.Client(api_key=settings.GEMINI_API_KEY, http_options=types.HttpOptions(timeout=50_000, retry_options=retry))
    return _client


def build_transcript(messages):
    lines = []
    for message in messages:
        speaker = "Customer" if message.role == "user" else "Mechanic"
        lines.append(f"{speaker}: {message.text or '[sent media]'}")
    return "\n".join(lines)


def parse_response(raw_text):
    """Turn Gemini JSON text into a safe dict with only the fields we use."""
    try:
        data = json.loads(raw_text)
    except (TypeError, json.JSONDecodeError) as error:
        raise GeminiError("AI returned invalid JSON") from error

    reply = str(data.get("reply", "")).strip()
    if not reply:
        raise GeminiError("AI returned an empty reply")

    diagnosis = data.get("diagnosis")
    if isinstance(diagnosis, dict) and diagnosis.get("problem"):
        urgency = str(diagnosis.get("urgency", "medium")).lower()
        diagnosis = {
            "problem": str(diagnosis["problem"])[:200],
            "details": str(diagnosis.get("details", "")),
            "recommendation": str(diagnosis.get("recommendation", "")) or "Visit a trusted mechanic for a full inspection.",
            "service": str(diagnosis.get("service", "General Inspection"))[:100],
            "urgency": urgency if urgency in {"low", "medium", "high"} else "medium",
            "estimated_cost": str(diagnosis.get("estimated_cost", ""))[:60],
        }
    else:
        diagnosis = None

    return {"is_car_related": bool(data.get("is_car_related", True)), "reply": reply, "diagnosis": diagnosis}


def ask_mechanic(history, media_files=(), force_diagnosis=False):
    """Send chat history and media to Gemini and get a structured mechanic reply."""
    if not settings.GEMINI_API_KEY:
        raise GeminiError("GEMINI_API_KEY is not set")

    prompt = "Conversation so far:\n" + build_transcript(history) + "\n\nReply as the mechanic."
    parts = [types.Part.from_text(text=prompt)]
    for media in media_files:
        with media.file.open("rb") as file:
            parts.append(types.Part.from_bytes(data=file.read(), mime_type=media.content_type))

    config = types.GenerateContentConfig(
        system_instruction=SYSTEM_PROMPT + (FORCE_DIAGNOSIS_NOTE if force_diagnosis else ""),
        response_mime_type="application/json",
        temperature=0.3,
    )

    # Try the backup model when the main one is busy, out of quota or returns a bad reply
    models = [settings.GEMINI_MODEL]
    if settings.GEMINI_FALLBACK_MODEL and settings.GEMINI_FALLBACK_MODEL != settings.GEMINI_MODEL:
        models.append(settings.GEMINI_FALLBACK_MODEL)

    for model in models:
        try:
            response = get_client().models.generate_content(model=model, contents=[types.Content(role="user", parts=parts)], config=config)
            return parse_response(response.text)
        except Exception as error:
            logger.warning("Gemini model %s failed: %s", model, error)

    raise GeminiError("AI service is not available right now")
