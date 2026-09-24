from pathlib import Path

from rest_framework.exceptions import ValidationError

MB = 1024 * 1024

ALLOWED_MEDIA = {
    "image": {"extensions": {"jpg", "jpeg", "png", "webp"}, "max_size": 5 * MB},
    "audio": {"extensions": {"mp3", "wav", "m4a", "ogg", "webm"}, "max_size": 10 * MB},
    "video": {"extensions": {"mp4", "mov", "webm"}, "max_size": 15 * MB},
}

# Media is sent to Gemini inside one request, so all files in one message must stay within 15 MB
MAX_TOTAL_MEDIA_SIZE = 15 * MB

MIME_TYPES = {
    "jpg": "image/jpeg", "jpeg": "image/jpeg", "png": "image/png", "webp": "image/webp",
    "mp3": "audio/mpeg", "wav": "audio/wav", "m4a": "audio/mp4", "ogg": "audio/ogg",
    "mp4": "video/mp4", "mov": "video/quicktime",
}


def has_valid_signature(extension, head):
    """Check the first bytes of the file so a renamed file cannot pass as media."""
    if extension in {"jpg", "jpeg"}:
        return head.startswith(b"\xff\xd8\xff")
    if extension == "png":
        return head.startswith(b"\x89PNG\r\n\x1a\n")
    if extension == "webp":
        return head[:4] == b"RIFF" and head[8:12] == b"WEBP"
    if extension == "wav":
        return head[:4] == b"RIFF" and head[8:12] == b"WAVE"
    if extension == "mp3":
        return head.startswith(b"ID3") or (len(head) > 1 and head[0] == 0xFF and head[1] & 0xE0 == 0xE0)
    if extension in {"mp4", "m4a", "mov"}:
        return head[4:8] == b"ftyp"
    if extension == "ogg":
        return head.startswith(b"OggS")
    if extension == "webm":
        return head.startswith(b"\x1a\x45\xdf\xa3")
    return False


def validate_upload(uploaded_file):
    """Return (kind, mime_type, extension) or raise ValidationError."""
    extension = Path(uploaded_file.name).suffix.lower().lstrip(".")
    kinds = [kind for kind, rule in ALLOWED_MEDIA.items() if extension in rule["extensions"]]
    if not kinds:
        allowed = sorted({ext for rule in ALLOWED_MEDIA.values() for ext in rule["extensions"]})
        raise ValidationError({"file": f"File type not allowed. Allowed types: {', '.join(allowed)}."})

    # A .webm file can be audio or video, so the browser's content type decides
    declared_kind = (uploaded_file.content_type or "").split("/")[0]
    kind = declared_kind if declared_kind in kinds else kinds[0]

    max_size = ALLOWED_MEDIA[kind]["max_size"]
    if uploaded_file.size == 0:
        raise ValidationError({"file": "File is empty."})
    if uploaded_file.size > max_size:
        raise ValidationError({"file": f"{kind.title()} must be smaller than {max_size // MB} MB."})

    head = uploaded_file.read(16)
    uploaded_file.seek(0)
    if not has_valid_signature(extension, head):
        raise ValidationError({"file": "File content does not match its extension."})

    mime_type = MIME_TYPES.get(extension, f"{kind}/{extension}")
    return kind, mime_type, extension
