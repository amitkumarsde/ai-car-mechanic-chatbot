import logging

from rest_framework import status
from rest_framework.response import Response
from rest_framework.views import exception_handler

logger = logging.getLogger(__name__)


def first_message(details):
    """Find the first readable error text inside DRF error details."""
    if isinstance(details, dict):
        details = next(iter(details.values()), None)
    if isinstance(details, list):
        details = details[0] if details else None
    if isinstance(details, (dict, list)):
        return first_message(details)
    return str(details) if details else None


def api_exception_handler(exc, context):
    """Return every error in one simple shape: {"error": {"message": ..., "details": ...}}."""
    response = exception_handler(exc, context)

    if response is None:
        logger.exception("Unhandled error", exc_info=exc)
        return Response(
            {"error": {"message": "Something went wrong. Please try again."}},
            status=status.HTTP_500_INTERNAL_SERVER_ERROR,
        )

    details = response.data
    if isinstance(details, dict) and "detail" in details:
        message, details = str(details["detail"]), None
    else:
        message = first_message(details) or "Please check the details you entered."
    response.data = {"error": {"message": message, "details": details}}
    return response
