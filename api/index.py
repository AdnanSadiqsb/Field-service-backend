"""
Vercel serverless handler for Django application.
This wraps the Django WSGI application for use with Vercel's serverless platform.
"""

import os
import sys

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.production')

# Add project root to path
sys.path.insert(0, '/var/task')

import django
django.setup()

from django.core.wsgi import get_wsgi_application

# Create WSGI application
app = get_wsgi_application()


def handler(request):
    """
    Vercel serverless handler wrapper.
    Converts Vercel request format to WSGI environ.
    """
    # Build environ dict from Vercel request
    environ = {
        'REQUEST_METHOD': request['httpMethod'],
        'SCRIPT_NAME': '',
        'PATH_INFO': request.get('path', '/'),
        'QUERY_STRING': request.get('queryStringParameters', '') or '',
        'CONTENT_TYPE': request.get('headers', {}).get('content-type', ''),
        'CONTENT_LENGTH': request.get('headers', {}).get('content-length', '') or '0',
        'SERVER_NAME': request.get('headers', {}).get('host', 'localhost').split(':')[0],
        'SERVER_PORT': '443',
        'SERVER_PROTOCOL': 'HTTP/1.1',
        'wsgi.version': (1, 0),
        'wsgi.url_scheme': 'https',
        'wsgi.input': None,
        'wsgi.errors': sys.stderr,
        'wsgi.multithread': True,
        'wsgi.multiprocess': False,
        'wsgi.run_once': False,
    }
    
    # Add HTTP headers
    for header, value in request.get('headers', {}).items():
        header_key = f'HTTP_{header.upper().replace("-", "_")}'
        if header_key not in ['HTTP_CONTENT_TYPE', 'HTTP_CONTENT_LENGTH']:
            environ[header_key] = value
    
    # Collect response
    response_started = [False]
    response_status = [None]
    response_headers = [None]
    
    def start_response(status, response_headers_list):
        response_started[0] = True
        response_status[0] = int(status.split()[0])
        response_headers[0] = dict(response_headers_list)
    
    try:
        # Handle body
        body = request.get('body', '')
        from io import BytesIO
        if isinstance(body, str):
            body = body.encode('utf-8')
        environ['wsgi.input'] = BytesIO(body)
        
        # Call WSGI app
        response_data = app(environ, start_response)
        
        # Collect response body
        body_parts = []
        for data in response_data:
            if data:
                if isinstance(data, bytes):
                    body_parts.append(data.decode('utf-8'))
                else:
                    body_parts.append(data)
        
        if hasattr(response_data, 'close'):
            response_data.close()
        
        response_body = ''.join(body_parts)
        
        return {
            'statusCode': response_status[0] or 500,
            'headers': response_headers[0] or {'Content-Type': 'text/html'},
            'body': response_body,
        }
    except Exception as e:
        import traceback
        print(traceback.format_exc())
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': f'{{"error": "{str(e)}"}}',
        }
