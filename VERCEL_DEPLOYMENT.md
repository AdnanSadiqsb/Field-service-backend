# Vercel Deployment Setup for Field Service Backend

This guide prepares your Django application for deployment on Vercel as a serverless application.

## Prerequisites

### Required Services (Managed Externally)
You'll need to set up these services before deploying to Vercel:

1. **Database**: PostgreSQL database (recommended: AWS RDS, Heroku Postgres, or Railway)
2. **Cache/Queue**: Redis instance (recommended: Redis Cloud, AWS ElastiCache, or similar)
3. **Email Service**: SMTP email service (recommended: SendGrid, AWS SES, or similar)
4. **Static Storage**: AWS S3 bucket for media and static files
5. **Monitoring**: Sentry for error tracking (optional but recommended)

### Local Prerequisites
- Python 3.8+
- Vercel CLI: `npm install -g vercel`
- Git account (GitHub, GitLab, or Bitbucket)

## Step 1: Prepare Your Environment

### 1.1 Create `.env.example`
```bash
# Django Settings
DJANGO_SETTINGS_MODULE=src.config.production
DJANGO_SECRET_KEY=your-secret-key-here
DEBUG=False

# Database Configuration
DB_ENGINE=django.db.backends.postgresql
DB_NAME=your-db-name
DB_USER=your-db-user
DB_PASSWORD=your-db-password
DB_HOST=your-db-host.rds.amazonaws.com
DB_PORT=5432

# Redis Configuration
REDIS_URL=redis://default:password@your-redis-host:6379
BROKER_URL=$REDIS_URL
CELERY_RESULT_BACKEND=$REDIS_URL

# AWS S3 Configuration
DJANGO_AWS_ACCESS_KEY_ID=your-access-key
DJANGO_AWS_SECRET_ACCESS_KEY=your-secret-key
DJANGO_AWS_STORAGE_BUCKET_NAME=your-bucket-name
AWS_S3_REGION_NAME=us-east-1

# Email Configuration
EMAIL_BACKEND=django.core.mail.backends.smtp.EmailBackend
EMAIL_HOST=smtp.sendgrid.net
EMAIL_PORT=587
EMAIL_HOST_USER=apikey
EMAIL_HOST_PASSWORD=SG.your-sendgrid-api-key
EMAIL_FROM=noreply@yourdomain.com

# Sentry Configuration
SENTRY_DSN=https://your-sentry-dsn@sentry.io/project

# Vercel Cron Configuration
CRON_SECRET=your-secret-cron-token

# Site Configuration
SITE_URL=https://your-domain.vercel.app
ALLOWED_HOSTS=your-domain.vercel.app,www.your-domain.com

# Social Auth (if applicable)
SOCIAL_AUTH_CALLBACK_DOMAIN=https://your-domain.vercel.app
```

### 1.2 Commit and Push
```bash
git add .
git commit -m "Prepare for Vercel deployment"
git push origin main
```

## Step 2: Set Up External Services

### 2.1 PostgreSQL Database
- Create a PostgreSQL database on your provider of choice
- Get connection credentials (host, port, username, password, database name)
- Ensure it allows connections from Vercel's IP ranges

### 2.2 Redis Instance
- Set up a Redis instance on a managed provider
- Get connection URL (usually in format: `redis://:password@host:port`)

### 2.3 AWS S3 Bucket (for media and static files)
```bash
# Prerequisites: AWS CLI configured with credentials
aws s3 mb s3://your-bucket-name --region us-east-1

# Create IAM user for S3 access with policy:
{
  "Version": "2012-10-17",
  "Statement": [
    {
      "Effect": "Allow",
      "Action": [
        "s3:*"
      ],
      "Resource": [
        "arn:aws:s3:::your-bucket-name",
        "arn:aws:s3:::your-bucket-name/*"
      ]
    }
  ]
}
```

### 2.4 Email Service (SendGrid recommended)
- Sign up for SendGrid
- Get API key from dashboard
- Set EMAIL_HOST_PASSWORD to your API key

### 2.5 Sentry (Optional)
- Create a Sentry project
- Get your DSN from project settings

## Step 3: Deploy to Vercel

### 3.1 Connect Repository
```bash
vercel link
# Follow the prompts to connect your GitHub/GitLab/Bitbucket repository
```

### 3.2 Add Environment Variables
```bash
# Using Vercel CLI
vercel env add DB_NAME
vercel env add DB_USER
vercel env add DB_PASSWORD
vercel env add DB_HOST
vercel env add DB_PORT
vercel env add REDIS_URL
vercel env add BROKER_URL
vercel env add CELERY_RESULT_BACKEND
vercel env add DJANGO_AWS_ACCESS_KEY_ID
vercel env add DJANGO_AWS_SECRET_ACCESS_KEY
vercel env add DJANGO_AWS_STORAGE_BUCKET_NAME
vercel env add EMAIL_HOST_PASSWORD
vercel env add SENTRY_DSN
vercel env add CRON_SECRET
vercel env add SITE_URL
vercel env add DJANGO_SECRET_KEY

# Or use Vercel web dashboard to set all values
```

### 3.3 Run Database Migrations

**First time deployment:**
```bash
# Option 1: Using a one-off Dyno-like service (if available)
# Option 2: Run migrations locally pointing to your Vercel database
export $(cat .env | xargs)
python manage.py migrate --settings=src.config.production

# Option 3: Use a Vercel deployment hook to run migrations
# See step 3.4 below
```

### 3.4 Set Up Migration Deployment Hook (Optional)

Create a migrations endpoint at `/api/migrate.py`:

```python
# api/migrate.py
import os
import django
from django.core.management import call_command

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'src.config.production')
django.setup()

def handler(request):
    if request.method != 'POST':
        return {'status': 'error', 'message': 'Method not allowed'}, 405
    
    # Verify auth header
    token = request.headers.get('authorization', '')
    if token != f'Bearer {os.getenv("DEPLOYMENT_SECRET", "")}':
        return {'status': 'error', 'message': 'Unauthorized'}, 401
    
    try:
        call_command('migrate', verbosity=2)
        call_command('collectstatic', '--noinput', verbosity=1)
        return {'status': 'success', 'message': 'Migrations completed'}
    except Exception as e:
        return {'status': 'error', 'message': str(e)}, 500
```

Then add webhook to your `vercel.json`:
```json
{
  "buildCommand": "curl -X POST https://your-domain.vercel.app/api/migrate -H 'Authorization: Bearer $DEPLOYMENT_SECRET' || true"
}
```

### 3.5 Deploy
```bash
vercel --prod
```

## Step 4: Configure Background Tasks

### 4.1 Vercel Cron
Edit `vercel.cron.json` to schedule your background tasks:

```json
{
  "crons": [
    {
      "path": "/api/cron",
      "schedule": "0 */6 * * *"
    }
  ]
}
```

Schedule meanings:
- `0 */6 * * *` - Every 6 hours
- `0 0 * * *` - Daily at midnight
- `0 9 * * 1` - Every Monday at 9 AM
- See crontab.guru for more formats

### 4.2 Implement Cron Tasks
Edit `api/cron.py` to execute your Celery tasks or management commands:

```python
# Example: Call specific tasks
from src.common.tasks import my_background_task

def handler(request):
    # Verify cron secret
    if request.headers.get('authorization') != f'Bearer {os.getenv("CRON_SECRET")}':
        return JsonResponse({'error': 'Unauthorized'}, status=401)
    
    # Execute your tasks
    my_background_task.delay()
    
    return JsonResponse({'status': 'success'})
```

## Step 5: Verification

### 5.1 Check Deployment
```bash
vercel list              # Show all deployments
vercel env ls            # List environment variables
vercel logs              # View logs
```

### 5.2 Test API Endpoints
```bash
# Test health check
curl https://your-domain.vercel.app/health_check

# Test API
curl https://your-domain.vercel.app/api/endpoint
```

### 5.3 Monitor Logs
```bash
# View real-time logs
vercel logs --follow

# Export logs
vercel logs > logs.txt
```

## Step 6: Post-Deployment

### 6.1 Set Up Custom Domain
1. In Vercel dashboard, go to Project Settings → Domains
2. Add your custom domain
3. Update DNS records according to Vercel's instructions

### 6.2 Enable Auto-Deployments
1. In Vercel dashboard, go to Settings → Git
2. Configure deployment branches

### 6.3 Monitor Performance
- Enable Vercel Analytics
- Set up error tracking in Sentry
- Monitor database and Redis usage

## Troubleshooting

### Cold Starts
- Serverless functions have cold start times (1-5 seconds)
- Consider using Vercel's Reserved Concurrent Executions for critical APIs
- Optimize imports in your handler

### Database Connection Issues
- Check that your database is accessible from Vercel
- Verify database credentials in environment variables
- Check security groups/firewall rules

### Static Files Not Loading
- Run `python manage.py collectstatic --noinput`
- Verify S3 bucket credentials
- Check S3 bucket permissions

### Cron Not Executing
- Verify CRON_SECRET is set correctly
- Check Vercel cron logs
- Ensure endpoint returns 200 status code

### Dependencies Error
- Ensure all dependencies are in `requirements/prod.txt`
- Test requirement installation locally: `pip install -r requirements/prod.txt`

## Performance Optimization Tips

1. **Use connection pooling** for database connections
2. **Enable caching** in Django settings
3. **Optimize static files** (minify CSS/JS)
4. **Use CDN** for static assets (Vercel provides this by default)
5. **Consider database query optimization** and indexing
6. **Set up log monitoring** for performance debugging

## Security Best Practices

1. Never commit `.env` files with real credentials
2. Rotate secrets regularly
3. Use Vercel's secrets management, not environment files
4. Enable 2FA on Vercel account
5. Use HTTPS for all communication (Vercel provides this by default)
6. Keep Django SECRET_KEY strong and unique
7. Update dependencies regularly

## Rollback Procedure

If something goes wrong:

```bash
# List recent deployments
vercel list

# Rollback to a specific deployment
vercel rollback <deployment-id>

# Or redeploy from a known good commit
git checkout <commit-hash>
vercel --prod
```

## Next Steps

1. Monitor your first deployment
2. Set up logging and error tracking
3. Configure auto-deployments from your repository
4. Set up staging environment for testing
5. Document deployment runbooks for your team
