import logging

from django.http import Http404
from django.core.exceptions import PermissionDenied as DjangoPermissionDenied

from rest_framework import status
from rest_framework.exceptions import (
    ValidationError,
    AuthenticationFailed,
    NotAuthenticated,
    PermissionDenied,
    MethodNotAllowed,
    APIException,
)
from rest_framework.views import exception_handler as drf_exception_handler

logger = logging.getLogger(__name__)


def _flatten_errors(detail):
    """
    Recursively extract the first readable string from DRF error detail.
    Returns (error_message: str, errors: dict).
    """
    if isinstance(detail, list):
        # e.g. non_field_errors or top-level list
        messages = [_flatten_errors(item)[0] for item in detail]
        return " ".join(messages), {}

    if isinstance(detail, dict):
        errors = {}
        first_message = None
        for field, value in detail.items():
            msg, _ = _flatten_errors(value)
            errors[field] = msg
            if first_message is None:
                first_message = msg
        return first_message or "Validation error.", errors

    # ErrorDetail or plain string
    return str(detail), {}


def custom_exception_handler(exc, context):
    # Let DRF build the initial response first
    response = drf_exception_handler(exc, context)

    # --- Django native exceptions not handled by DRF ---
    if isinstance(exc, Http404):
        return _build_error("Resource not found.", {}, status.HTTP_404_NOT_FOUND)

    if isinstance(exc, DjangoPermissionDenied):
        return _build_error("You do not have permission to perform this action.", {}, status.HTTP_403_FORBIDDEN)

    # --- DRF exceptions ---
    if isinstance(exc, ValidationError):
        error_message, errors = _flatten_errors(exc.detail)
        return _build_error(error_message, errors, exc.status_code)

    if isinstance(exc, AuthenticationFailed):
        return _build_error(str(exc.detail), {}, exc.status_code)

    if isinstance(exc, NotAuthenticated):
        return _build_error("Authentication credentials were not provided.", {}, exc.status_code)

    if isinstance(exc, PermissionDenied):
        return _build_error("You do not have permission to perform this action.", {}, exc.status_code)

    if isinstance(exc, MethodNotAllowed):
        return _build_error(f"Method '{exc.args[0] if exc.args else ''}' not allowed.", {}, exc.status_code)

    if isinstance(exc, APIException):
        error_message, errors = _flatten_errors(exc.detail)
        return _build_error(error_message, errors, exc.status_code)

    # --- Unhandled server exceptions ---
    if response is None:
        logger.exception("Unhandled server exception", exc_info=exc)
        return _build_error("An unexpected error occurred. Please try again later.", {}, status.HTTP_500_INTERNAL_SERVER_ERROR)

    return response


def _build_error(error_message, errors, status_code):
    from rest_framework.response import Response
    return Response(
        {"status": False, "error_message": error_message, "errors": errors},
        status=status_code,
    )
