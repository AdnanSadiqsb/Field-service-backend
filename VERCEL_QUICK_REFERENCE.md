# Vercel Deployment - Quick Reference

Quick commands and solutions for common Vercel deployment tasks.

## Initial Setup

```bash
# Install Vercel CLI
npm install -g vercel

# Link to your Vercel project
vercel link

# Set up environment (runs setup-vercel.sh)
chmod +x setup-vercel.sh
./setup-vercel.sh

# Add environment variables
vercel env add DJANGO_SECRET_KEY
vercel env add DB_NAME
vercel env add DB_USER
# ... etc for all variables

# Or pull and edit locally
vercel env pull
```

## Deployment

```bash
# Deploy to staging
vercel

# Deploy to production
vercel --prod

# With specific comment/message
vercel --prod --message "Deploy: Fix authentication bug"

# Force rebuild without caching
vercel --prod --force
```

## Monitoring & Logs

```bash
# View deployment logs (real-time)
vercel logs --follow

# View logs from specific deployment
vercel logs <deployment-id>

# List all deployments
vercel list

# Get deployment details
vercel inspect <deployment-id>

# View live logs
vercel logs --follow --output raw
```

## Rollback

```bash
# List deployments and pick one to rollback to
vercel list

# Rollback to a specific deployment
vercel rollback <deployment-id>

# Rollback to previous production
vercel rollback --prod
```

## Environment Variables

```bash
# Pull variables to .env.local
vercel env pull

# List all environment variables
vercel env ls

# Add new variable
vercel env add VARIABLE_NAME

# Remove variable
vercel env rm VARIABLE_NAME

# View specific environment (staging/production)
vercel env ls production
vercel env ls development
```

## Database Migrations

```bash
# Run migrations manually
export $(cat .env.local | xargs)
python manage.py migrate --settings=src.config.production

# Using the helper script
chmod +x run-migrations.sh
./run-migrations.sh

# Test migration connection
python manage.py check --settings=src.config.production
python manage.py showmigrations --settings=src.config.production
```

## Testing Endpoints

```bash
# Health check
curl https://your-domain.vercel.app/health_check/

# API endpoint
curl -H "Authorization: Bearer YOUR_TOKEN" \
  https://your-domain.vercel.app/api/endpoint

# Admin panel
https://your-domain.vercel.app/admin/

# Cron endpoint (test)
curl -X POST https://your-domain.vercel.app/api/cron \
  -H "Authorization: Bearer $CRON_SECRET" \
  -H "Content-Type: application/json"
```

## Troubleshooting

### Function Timeout (Error 504)
```bash
# Check timeout in vercel.json
# Max duration: 30 seconds for serverless

# Increase in vercel.json:
{
  "functions": {
    "api/**/*.py": {
      "maxDuration": 60
    }
  }
}

# Optimize code to reduce execution time
```

### Database Connection Fails
```bash
# Test connection locally first
python -m psycopg2 -H $DB_HOST -U $DB_USER -d $DB_NAME -c "SELECT 1"

# Check environment variables
vercel env ls

# Verify database allows Vercel IPs
# Check security groups, IP whitelist, etc.

# View specific logs
vercel logs --follow | grep "database\|connection\|error"
```

### Static Files Missing
```bash
# Collect static files locally
python manage.py collectstatic \
  --settings=src.config.production --noinput

# Verify in S3
aws s3 ls s3://your-bucket-name/static/

# Check S3 credentials
vercel env ls | grep AWS
```

### Cron Not Running
```bash
# Verify cron configuration
cat vercel.cron.json

# Check CRON_SECRET is set
vercel env ls | grep CRON

# Check cron logs
vercel logs --follow | grep "cron\|api/cron"

# Test cron manually
curl -X POST https://your-domain.vercel.app/api/cron \
  -H "Authorization: Bearer $CRON_SECRET" \
  -v
```

### Memory Issues
```bash
# Check memory usage in vercel.json
# Default: 1024MB, Max: 3008MB

# Increase memory:
{
  "functions": {
    "api/**/*.py": {
      "memory": 2048
    }
  }
}

# Monitor actual usage in logs
vercel logs --follow | grep "memory\|usage"
```

### Cold Starts Taking Too Long
```bash
# Cold start is normal for serverless (1-5 seconds first request)
# Recommendations:
# 1. Enable Vercel's Reserved Concurrent Executions
# 2. Keep dependencies slim in requirements/prod.txt
# 3. Use a cron job to keep function warm
# 4. Optimize imports (move heavy imports inside function)
```

### Deploy Fails - Build Error
```bash
# Check build logs
vercel logs

# Common issues:
# 1. Missing dependency in requirements/prod.txt
# 2. Python version mismatch
# 3. Import errors
# 4. Syntax errors in code

# Test build locally
pip install -r requirements/prod.txt
python -c "import src"  # test imports

# Push fix and redeploy
git add .
git commit -m "Fix build error"
git push
vercel --prod
```

## Performance Tips

```bash
# Optimize requirements file
# - Remove dev dependencies
# - Use binary packages (psycopg2-binary instead of psycopg2)
# - Pin versions in requirements

# Monitor function execution
vercel analytics (if enabled)

# Enable caching headers
# Set in Django settings for static files
Cache-Control: public, max-age=86400, immutable
```

## Security

```bash
# Never commit secrets
git commit --allow-empty -m "Check .gitignore"
git rm --cached .env .env.local
git add .gitignore
git commit -m "Properly ignore environment files"

# Rotate secrets periodically
# 1. Generate new secrets
# 2. Update in Vercel dashboard
# 3. Redeploy
# 4. Verify working
# 5. Document change

# Check what's exposed
git log --diff-filter=D --summary | grep delete | grep -E '\.(env|txt|key)' 

# List sensitive files that might be committed
git ls-files | grep -E '(\.env|secret|credentials|password)'
```

## Project Management

```bash
# Add team member to Vercel
vercel teams members add <email>

# Configure domains
# Dashboard → Project → Settings → Domains

# Set up custom domain with DNS
# Dashboard → Project → Domains → Add
# Follow DNS configuration steps

# Enable auto-deployment
# Dashboard → Git Configuration
# Select branches to auto-deploy

# Set up notifications
# Dashboard → Project → Settings → Notifications
```

## Useful Links

- Vercel Dashboard: https://vercel.com/dashboard
- Project Settings: https://vercel.com/dashboard/[project]/settings
- Environment Variables: https://vercel.com/dashboard/[project]/settings/environment-variables
- Deployments: https://vercel.com/dashboard/[project]/deployments
- Documentation: https://vercel.com/docs

## Common Commands Summary

| Task | Command |
|------|---------|
| Deploy to production | `vercel --prod` |
| View logs | `vercel logs --follow` |
| List deployments | `vercel list` |
| Rollback | `vercel rollback <id>` |
| Set env var | `vercel env add VAR_NAME` |
| Pull env vars | `vercel env pull` |
| Run migrations | `python manage.py migrate --settings=src.config.production` |
| Check health | `curl https://domain.vercel.app/health_check/` |

---

For detailed information, see:
- [VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md) - Complete deployment guide
- [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) - Pre-deployment checklist
- [Official Vercel Docs](https://vercel.com/docs) - Vercel documentation
