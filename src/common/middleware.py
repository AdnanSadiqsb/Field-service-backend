import json
import logging

logger = logging.getLogger(__name__)

# URL prefixes this middleware applies to — only wrap API responses
API_PREFIX = '/api/'


class APIResponseMiddleware:
    """
    Intercepts all API JSON responses and wraps them in the standard format:

    Success:  { "status": true,  "message": "...", "data": {...} }
    Error:    { "status": false, "error_message": "...", "errors": {...} }

    Skips:
    - Non-API URLs (admin, swagger, health, etc.)
    - Responses already in the standard format (e.g. from exception handler)
    - Non-JSON responses (file downloads, redirects, etc.)
    """

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        response = self.get_response(request)

        # Only process API routes
        if not request.path.startswith(API_PREFIX):
            return response

        # Only process JSON responses
        content_type = response.get('Content-Type', '')
        if 'application/json' not in content_type:
            return response

        try:
            # DRF responses: data is already a dict, no need to decode
            if hasattr(response, 'data'):
                body = response.data
            else:
                body = json.loads(response.content.decode('utf-8'))
        except (ValueError, AttributeError):
            return response

        # Skip if already in our standard format
        if isinstance(body, dict) and 'status' in body and isinstance(body['status'], bool):
            return response

        # Wrap based on HTTP status code
        if response.status_code >= 400:
            wrapped = _wrap_error(body, response.status_code)
        else:
            wrapped = _wrap_success(body)

        # Re-encode and return
        response.content = json.dumps(wrapped)
        response['Content-Length'] = len(response.content)
        return response


def _wrap_success(body):
    return {
        "status": True,
        "message": "Success",
        "data": body if isinstance(body, (dict, list)) else {},
    }


def _wrap_error(body, status_code):
    error_message, errors = _extract_error(body, status_code)
    return {
        "status": False,
        "error_message": error_message,
        "errors": errors,
    }


def _extract_error(body, status_code):
    """Extract a readable error_message and errors dict from any DRF error body."""
    if not isinstance(body, dict):
        return _default_message(status_code), {}

    # Already partially structured
    if 'detail' in body:
        return str(body['detail']), {}

    errors = {}
    first_message = None

    for field, value in body.items():
        if field == 'non_field_errors':
            msg = _extract_message(value)
            if first_message is None:
                first_message = msg
            # non_field_errors go into error_message, not errors dict
        else:
            msg = _extract_message(value)
            errors[field] = msg
            if first_message is None:
                first_message = msg

    return first_message or _default_message(status_code), errors


def _extract_message(value):
    if isinstance(value, list) and value:
        return str(value[0])
    if isinstance(value, str):
        return value
    return str(value)


def _default_message(status_code):
    defaults = {
        400: "Bad request.",
        401: "Authentication credentials were not provided.",
        403: "You do not have permission to perform this action.",
        404: "Resource not found.",
        405: "Method not allowed.",
        429: "Too many requests.",
        500: "An unexpected error occurred. Please try again later.",
    }
    return defaults.get(status_code, "An error occurred.")
