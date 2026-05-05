"""
Vercel serverless handler for Django application.
This wraps the Django WSGI application for use with Vercel's serverless platform.
"""

import os
import sys
import django

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.production')

# Setup Django
django.setup()

from django.core.wsgi import get_wsgi_application

# Get the WSGI application
application = get_wsgi_application()


def handler(request):
    """
    WSGI handler for Vercel serverless functions.
    Routes all requests through Django's WSGI application.
    """
    return application(request.environ, request.start_response)
