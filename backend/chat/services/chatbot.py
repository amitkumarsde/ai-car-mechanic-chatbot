import re
from dataclasses import dataclass

from chat.models import Conversation, Diagnosis, Message
from chat.services import gemini
from chat.services.knowledge import BOOK_WORDS, CAR_KEYWORDS, GREETINGS, ISSUES, NO_WORDS, YES_WORDS

MAX_AI_TURNS = 4
HISTORY_LIMIT = 12

GREETING_REPLY = (
    "Hello! I am your virtual car mechanic. Tell me what problem your car has, "
    "for example: 'my car is not starting' or 'engine is overheating'. You can also upload a photo, audio or video."
)
REJECT_REPLY = (
    "Sorry, I can only help with car and mechanical problems. "
    "Please tell me about an issue with your car, like a noise, warning light, starting or braking problem."
)
AI_DOWN_REPLY = (
    "Sorry, I could not analyse this right now. Please try again in a minute, or describe the problem in simple words, "
    "for example: 'car not starting', 'brake squeaking', 'AC not cooling' or 'check engine light is on'."
)
BOOKING_PROMPT = "Would you like me to book a mechanic for this? Reply 'yes' or tap the Book Mechanic button."


@dataclass
class BotReply:
    text: str
    source: str
    diagnosis: Diagnosis | None = None
    action: str | None = None


def normalize(text):
    cleaned = re.sub(r"[^a-z0-9/'\s]", " ", (text or "").lower())
    return " " + " ".join(cleaned.split()) + " "


def contains_any(text, words):
    return any(word in text for word in words)


def first_word(text):
    words = text.split()
    return words[0] if words else ""


def is_greeting(text):
    return text.strip() in GREETINGS or first_word(text) in GREETINGS


def is_car_related(text):
    return contains_any(text, CAR_KEYWORDS)


def find_issue(text):
    """Return the issue key with the most matching keywords, or None."""
    scores = {key: sum(word in text for word in issue["keywords"]) for key, issue in ISSUES.items()}
    best = max(scores, key=scores.get)
    return best if scores[best] > 0 else None


def parse_yes_no(text):
    word = first_word(text)
    if word in YES_WORDS:
        return True
    if word in NO_WORDS:
        return False
    return None


def wants_booking(text):
    return contains_any(text, BOOK_WORDS) or parse_yes_no(text) is True


def diagnosis_summary(diagnosis):
    """Short chat text; the full details are shown in the diagnosis card."""
    return f"My diagnosis: {diagnosis.problem}. Recommended service: {diagnosis.service}.\n\n{BOOKING_PROMPT}"


def save_diagnosis(conversation, data, source):
    conversation.state = Conversation.State.DIAGNOSED
    conversation.save(update_fields=["state", "updated_at"])
    return Diagnosis.objects.create(conversation=conversation, source=source, **data)


def rule_diagnosis(conversation):
    """Pick the cause with the most yes/no points from the answers."""
    issue = ISSUES[conversation.current_issue]
    scores = {cause: 0 for cause in issue["causes"]}
    for answer in conversation.answers:
        question = issue["questions"][answer["question_index"]]
        if answer["value"] is True:
            scores[question["yes"]] += 1
        elif answer["value"] is False:
            scores[question["no"]] += 1
    best_cause = max(scores, key=scores.get)
    return save_diagnosis(conversation, issue["causes"][best_cause], Diagnosis.Source.RULE)


def start_rule_flow(conversation, issue_key):
    issue = ISSUES[issue_key]
    conversation.state = Conversation.State.ASKING
    conversation.current_issue = issue_key
    conversation.question_index = 0
    conversation.answers = []
    conversation.save()
    first_question = issue["questions"][0]["text"]
    return BotReply(
        f"It sounds like a {issue['title'].lower()} issue. Let me ask a few quick questions.\n\n{first_question}",
        Message.Source.RULE,
    )


def continue_rule_flow(conversation, text):
    issue = ISSUES[conversation.current_issue]
    conversation.answers = [
        *conversation.answers,
        {"question_index": conversation.question_index, "answer": text.strip(), "value": parse_yes_no(text)},
    ]
    conversation.question_index += 1

    if conversation.question_index < len(issue["questions"]):
        conversation.save()
        return BotReply(issue["questions"][conversation.question_index]["text"], Message.Source.RULE)

    conversation.save()
    diagnosis = rule_diagnosis(conversation)
    return BotReply(diagnosis_summary(diagnosis), Message.Source.RULE, diagnosis)


def recent_history(conversation):
    messages = list(conversation.messages.order_by("-created_at", "-id")[:HISTORY_LIMIT])
    return list(reversed(messages))


def ask_ai(conversation, media_files=(), force_diagnosis=False):
    force = force_diagnosis or conversation.ai_turns >= MAX_AI_TURNS
    try:
        result = gemini.ask_mechanic(recent_history(conversation), media_files, force_diagnosis=force)
    except gemini.GeminiError:
        return BotReply(AI_DOWN_REPLY, Message.Source.RULE)

    if not result["is_car_related"]:
        return BotReply(result["reply"], Message.Source.AI)

    conversation.ai_turns += 1
    conversation.state = Conversation.State.AI_CHAT
    conversation.save(update_fields=["ai_turns", "state", "updated_at"])

    if result["diagnosis"]:
        diagnosis = save_diagnosis(conversation, result["diagnosis"], Diagnosis.Source.AI)
        return BotReply(f"{result['reply']}\n\n{diagnosis_summary(diagnosis)}", Message.Source.AI, diagnosis)
    return BotReply(result["reply"], Message.Source.AI)


def booking_reply(conversation):
    booking = conversation.diagnoses.first().bookings.first()
    if booking:
        return BotReply(f"A mechanic is already booked for this problem. Booking ID: {booking.id}.", Message.Source.RULE)
    return BotReply(
        "Great! Please fill in your details in the booking form and I will book a mechanic for you.",
        Message.Source.RULE,
        action="show_booking_form",
    )


def reset(conversation):
    conversation.state = Conversation.State.NEW
    conversation.current_issue = ""
    conversation.question_index = 0
    conversation.answers = []
    conversation.ai_turns = 0
    conversation.save()


def handle_message(conversation, raw_text, media_files=()):
    """Decide the reply: rules first, Gemini only when rules cannot help."""
    text = normalize(raw_text)

    if media_files:
        return ask_ai(conversation, media_files)

    if conversation.state == Conversation.State.DIAGNOSED:
        if wants_booking(text):
            return booking_reply(conversation)
        if parse_yes_no(text) is False and not find_issue(text):
            return BotReply("No problem. Tell me if you notice any other issue with your car.", Message.Source.RULE)
        reset(conversation)

    if conversation.state == Conversation.State.ASKING:
        return continue_rule_flow(conversation, raw_text)

    issue_key = find_issue(text)
    if issue_key:
        return start_rule_flow(conversation, issue_key)

    if conversation.state == Conversation.State.AI_CHAT:
        return ask_ai(conversation)

    if is_greeting(text):
        return BotReply(GREETING_REPLY, Message.Source.RULE)

    if is_car_related(text):
        return ask_ai(conversation)

    return BotReply(REJECT_REPLY, Message.Source.RULE)


def diagnose_now(conversation):
    """Give a diagnosis on request using what we already know."""
    latest = conversation.diagnoses.first()
    if conversation.state == Conversation.State.DIAGNOSED and latest:
        return latest

    reply = None
    if conversation.state == Conversation.State.ASKING:
        diagnosis = rule_diagnosis(conversation)
        reply = BotReply(diagnosis_summary(diagnosis), Message.Source.RULE, diagnosis)
    elif conversation.state == Conversation.State.AI_CHAT:
        reply = ask_ai(conversation, force_diagnosis=True)

    if reply is None or reply.diagnosis is None:
        return None
    Message.objects.create(conversation=conversation, role=Message.Role.BOT, source=reply.source, text=reply.text)
    return reply.diagnosis
