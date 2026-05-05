# Vercel Deployment Checklist

Use this checklist to ensure your application is properly configured for Vercel deployment.

## Pre-Deployment Phase

### [ ] Code Preparation
- [ ] All changes committed to git
- [ ] Repository pushed to GitHub/GitLab/Bitbucket
- [ ] No uncommitted changes locally (`git status` shows clean working directory)
- [ ] Verified code passes linting/tests locally

### [ ] Environment Variables
- [ ] Created `.env.example` with all required variables
- [ ] Generated strong Django SECRET_KEY
- [ ] Generated random CRON_SECRET token
- [ ] All sensitive values are NOT committed to git

### [ ] External Services Setup

#### Database (PostgreSQL)
- [ ] PostgreSQL database created on managed provider (AWS RDS, Heroku, Railway, etc.)
- [ ] Database name, username, password obtained
- [ ] Database host/endpoint obtained
- [ ] Database port confirmed (typically 5432)
- [ ] Security group/firewall allows connections from Vercel IPs
- [ ] Test connection from local machine works

#### Redis Instance
- [ ] Redis instance created on managed provider (Redis Cloud, AWS ElastiCache, etc.)
- [ ] Redis connection URL obtained (format: `redis://:password@host:port`)
- [ ] Test connection works locally

#### AWS S3 Bucket
- [ ] S3 bucket created for media/static files
- [ ] IAM user created with S3 access policy
- [ ] AWS Access Key ID obtained
- [ ] AWS Secret Access Key obtained
- [ ] CORS policy configured if needed
- [ ] Bucket name documented

#### Email Service (SendGrid recommended)
- [ ] Account created and verified
- [ ] API key generated
- [ ] Domain verified (if using custom domain)
- [ ] Test email sent successfully

#### Sentry (Optional)
- [ ] Sentry project created
- [ ] DSN obtained
- [ ] Project settings configured

### [ ] Local Testing
- [ ] Installed requirements: `pip install -r requirements/prod.txt`
- [ ] Created `.env.local` with test database
- [ ] Ran migrations: `python manage.py migrate --settings=src.config.production`
- [ ] Created superuser: `python manage.py createsuperuser --settings=src.config.production`
- [ ] Tested API endpoints locally
- [ ] Static files collected: `python manage.py collectstatic --settings=src.config.production`
- [ ] Health check endpoint works: `GET /health_check/`

### [ ] Configuration Files
- [ ] `vercel.json` configured correctly
- [ ] `vercel.cron.json` configured with schedule
- [ ] `api/index.py` handler configured
- [ ] `api/cron.py` cron tasks configured
- [ ] `.env.example` is up-to-date

## Vercel Deployment Phase

### [ ] Vercel Project Setup
- [ ] Vercel account created
- [ ] Project repository connected to Vercel
- [ ] `vercel link` executed successfully
- [ ] Build command verified (should be: `pip install -r requirements/prod.txt`)

### [ ] Environment Variables in Vercel
Set these in Vercel Dashboard (Settings → Environment Variables):

**Core Django:**
- [ ] `DJANGO_SETTINGS_MODULE` = `src.config.production`
- [ ] `DJANGO_SECRET_KEY` = (generated strong key)
- [ ] `DEBUG` = `False`

**Database:**
- [ ] `DB_ENGINE` = `django.db.backends.postgresql`
- [ ] `DB_NAME` = (your database name)
- [ ] `DB_USER` = (your database user)
- [ ] `DB_PASSWORD` = (your database password)
- [ ] `DB_HOST` = (your database host)
- [ ] `DB_PORT` = `5432`

**Redis/Celery:**
- [ ] `REDIS_URL` = (your redis connection URL)
- [ ] `BROKER_URL` = (same as REDIS_URL)
- [ ] `CELERY_RESULT_BACKEND` = (same as REDIS_URL)

**AWS S3:**
- [ ] `DJANGO_AWS_ACCESS_KEY_ID` = (your AWS access key)
- [ ] `DJANGO_AWS_SECRET_ACCESS_KEY` = (your AWS secret key)
- [ ] `DJANGO_AWS_STORAGE_BUCKET_NAME` = (your bucket name)
- [ ] `AWS_S3_REGION_NAME` = (e.g., `us-east-1`)

**Email:**
- [ ] `EMAIL_BACKEND` = `django.core.mail.backends.smtp.EmailBackend`
- [ ] `EMAIL_HOST` = (e.g., `smtp.sendgrid.net`)
- [ ] `EMAIL_PORT` = `587`
- [ ] `EMAIL_HOST_USER` = `apikey`
- [ ] `EMAIL_HOST_PASSWORD` = (your API key)
- [ ] `EMAIL_FROM` = (your email address)

**Site Configuration:**
- [ ] `SITE_URL` = (your Vercel domain or custom domain)
- [ ] `ALLOWED_HOSTS` = (comma-separated list of domains)
- [ ] `CRON_SECRET` = (generated random token)

**Optional:**
- [ ] `SENTRY_DSN` = (if using Sentry)

### [ ] Deploy to Vercel
```bash
vercel --prod
```
- [ ] Build completed successfully
- [ ] No error messages in build logs
- [ ] Deployment URL obtained

## Post-Deployment Phase

### [ ] Initial Testing
- [ ] Access deployment URL in browser
- [ ] Health check endpoint responds: `https://your-domain.vercel.app/health_check/`
- [ ] API endpoints return expected responses
- [ ] No error logs in Vercel console
- [ ] Database migrations are current

### [ ] Database Setup
- [ ] Run migrations on production database:
  ```bash
  # Option 1: Using Vercel CLI
  vercel env pull
  python manage.py migrate --settings=src.config.production
  
  # Option 2: Via migration endpoint (if implemented)
  curl -X POST https://your-domain.vercel.app/api/migrate \
    -H "Authorization: Bearer $DEPLOYMENT_SECRET"
  ```
- [ ] Create admin user if needed
- [ ] Verify data integrity

### [ ] Admin Panel Access
- [ ] Django admin accessible: `https://your-domain.vercel.app/admin/`
- [ ] Login works with superuser credentials
- [ ] All models visible

### [ ] Static Files & Media
- [ ] CSS/JS files served correctly
- [ ] Media uploads work
- [ ] S3 bucket contains uploaded files
- [ ] Images display correctly

### [ ] Background Tasks
- [ ] Cron job configured in `vercel.cron.json`
- [ ] CRON_SECRET properly set
- [ ] Test cron endpoint manually:
  ```bash
  curl -X POST https://your-domain.vercel.app/api/cron \
    -H "Authorization: Bearer $CRON_SECRET" \
    -H "Content-Type: application/json"
  ```
- [ ] Logs show successful execution

### [ ] Error Tracking
- [ ] Sentry errors showing (if enabled)
- [ ] Error details captured correctly
- [ ] Alerts configured

### [ ] Domain Configuration
- [ ] Custom domain configured (if using one)
- [ ] SSL certificate auto-generated (Vercel does this)
- [ ] HTTPS working properly
- [ ] HTTP redirects to HTTPS

### [ ] Monitoring & Logging
- [ ] Enable Vercel Analytics
- [ ] Configure error notifications
- [ ] Monitor database usage
- [ ] Monitor Redis usage
- [ ] Monitor S3 storage
- [ ] Check cold start times

### [ ] Security Review
- [ ] Django DEBUG mode is False
- [ ] ALLOWED_HOSTS properly configured
- [ ] CORS properly configured
- [ ] Secret keys are strong and unique
- [ ] Database credentials not in logs
- [ ] No sensitive data in git history

### [ ] Documentation
- [ ] Setup instructions documented for team
- [ ] Environment variables documented
- [ ] Deployment runbook created
- [ ] Emergency contact/escalation path documented

## Rollback Plan

### [ ] If Deployment Fails
- [ ] Identify error in build logs
- [ ] Check all environment variables are set
- [ ] Verify database/Redis connectivity
- [ ] Check for missing dependencies in `requirements/prod.txt`
- [ ] Rollback to previous version:
  ```bash
  vercel rollback <deployment-id>
  ```

### [ ] Common Issues
- [ ] **Cold start timeouts**: Increase maxDuration in vercel.json
- [ ] **Static files missing**: Run collectstatic, check S3 bucket
- [ ] **Database connection fails**: Verify DATABASE_URL and whitelist Vercel IPs
- [ ] **Tasks not running**: Check CRON_SECRET, verify schedule
- [ ] **Email not sending**: Check provider settings and API credentials

## Maintenance Checklist (Regular)

- [ ] Update dependencies monthly
- [ ] Review error tracking
- [ ] Check database performance
- [ ] Rotate secrets quarterly
- [ ] Review access logs
- [ ] Test disaster recovery procedures
- [ ] Update documentation

## Sign-Off

- [ ] Deployment tested by developer: ________________ Date: _______
- [ ] Reviewed by lead/manager: ________________ Date: _______
- [ ] Production environment verified: ________________ Date: _______

---

**For issues, see:** VERCEL_DEPLOYMENT.md or README.md
