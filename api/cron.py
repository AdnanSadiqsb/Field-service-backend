"""
Vercel Cron endpoint for background tasks.
This endpoint is called by Vercel periodically and executes background tasks.

Configure cron schedule in vercel.cron.json
"""

import os
import sys
import json

# Set Django settings module
os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.production')

# Add project root to path
sys.path.insert(0, '/var/task')

import django
django.setup()

from django.http import JsonResponse


def handler(request):
    """
    Handler for Vercel Cron events.
    Executes background tasks (e.g., Celery beat tasks or management commands).
    
    Vercel sends POST requests with authorization header.
    """
    
    # Verify this is POST
    method = request.get('httpMethod', 'GET').upper()
    if method != 'POST':
        return {
            'statusCode': 405,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Method not allowed'}),
        }
    
    # Verify Cron Secret for security
    headers = request.get('headers', {})
    auth_header = headers.get('authorization', '')
    expected_secret = os.getenv('CRON_SECRET', '')
    
    if not expected_secret or auth_header != f'Bearer {expected_secret}':
        return {
            'statusCode': 401,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({'error': 'Unauthorized'}),
        }
    
    try:
        # Execute your background tasks here
        # Examples:
        
        # 1. Run Django management command:
        # from django.core.management import call_command
        # call_command('seed_trades')
        
        # 2. Call Celery task:
        # from src.common.tasks import example_task
        # example_task.delay()
        
        # 3. Multiple tasks:
        # from src.professionals.tasks import update_professional_metrics
        # from src.notifications.tasks import send_pending_notifications
        # update_professional_metrics.delay()
        # send_pending_notifications.delay()
        
        # For now, just return success
        # Replace above with your actual task calls
        print("✅ Cron job executed successfully")
        
        return {
            'statusCode': 200,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'success',
                'message': 'Background tasks executed'
            }),
        }
        
    except Exception as e:
        import traceback
        error_msg = str(e)
        print(f"❌ Cron job error: {error_msg}")
        print(traceback.format_exc())
        
        return {
            'statusCode': 500,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                'status': 'error',
                'message': error_msg
            }),
        }
