# Django Rest Framework boilerplate

[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

This is boilerplate for starting fresh new DRF projects. It's built using [cookiecutter-django-rest](https://github.com/agconti/cookiecutter-django-rest).

## Highlights

- Modern Python development with Python 3.8+
- Bleeding edge Django 3.1+
- Fully dockerized, local development via docker-compose.
- PostgreSQL
- Full test coverage, continuous integration, and continuous deployment.
- Celery tasks

### Features built-in

- JSON Web Token authentication using [Simple JWT](https://django-rest-framework-simplejwt.readthedocs.io/en/latest/)
- Social (FB + G+) signup/sigin
- API Throttling enabled
- Password reset endpoints
- User model with profile picture field using Easy Thumbnails
- Files management (thumbnails generated automatically for images)
- Sentry setup
- Swagger API docs out-of-the-box
- Code formatter [black](https://black.readthedocs.io/en/stable/)
- Tests (with mocking and factories) with code-coverage support

## API Docs

API documentation is automatically generated using Swagger. You can view documention by visiting this [link](http://localhost:8000/swagger).

## Prerequisites

If you are familiar with Docker, then you just need [Docker](https://docs.docker.com/docker-for-mac/install/). If you don't want to use Docker, then you just need Python3 and Postgres installed.

## Local Development with Docker

Start the dev server for local development:

```bash
cp .env.dist .env
docker-compose up
```

Run a command inside the docker container:

```bash
docker-compose run --rm web [command]
```

## Local Development without Docker

### Install

```bash
python3 -m venv env && source env/bin/activate                # activate venv
cp .env.dist .env                                             # create .env file and fill-in DB info
pip install -r requirements.txt                               # install py requirements
./manage.py migrate                                           # run migrations
./manage.py collectstatic --noinput                           # collect static files
redis-server                                                  # run redis locally for celery
celery -A src.config worker --beat --loglevel=debug
  --pidfile="./celerybeat.pid"
  --scheduler django_celery_beat.schedulers:DatabaseScheduler # run celery beat and worker
```

### Run dev server

This will run server on [http://localhost:8000](http://localhost:8000)

```bash
./manage.py runserver
```

### Create superuser

If you want, you can create initial super-user with next commad:

```bash
./manage.py createsuperuser
```

### Running Tests

To run all tests with code-coverate report, simple run:

```bash
./manage.py test
```


You're now ready to ROCK! ✨ 💅 🛳

# Field-service-backend

## Vercel Deployment

This project is configured for serverless deployment on Vercel. 

### Quick Start

1. **Prepare for Deployment**
   ```bash
   chmod +x setup-vercel.sh
   ./setup-vercel.sh
   ```

2. **Set up External Services**
   - PostgreSQL database (AWS RDS, Heroku, Railway, etc.)
   - Redis instance (Redis Cloud, AWS ElastiCache, etc.)
   - AWS S3 bucket for media/static files
   - Email service (SendGrid, AWS SES, etc.)

3. **Deploy to Vercel**
   ```bash
   vercel --prod
   ```

### Documentation

- **[VERCEL_DEPLOYMENT.md](VERCEL_DEPLOYMENT.md)** - Complete deployment guide with step-by-step instructions
- **[DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md)** - Pre and post-deployment checklist
- **[VERCEL_QUICK_REFERENCE.md](VERCEL_QUICK_REFERENCE.md)** - Quick commands and troubleshooting

### Project Structure for Vercel

```
api/
  index.py          # Main WSGI handler for all routes
  cron.py           # Background tasks via Vercel Cron
vercel.json         # Vercel configuration
vercel.cron.json    # Cron schedule configuration
.env.example        # Environment variables template
requirements/
  prod.txt          # Production dependencies
  vercel.txt        # Vercel-optimized dependencies
```

### Key Files

- `api/index.py` - Serverless handler that routes all requests through Django
- `api/cron.py` - Scheduled background task handler (runs via Vercel Cron)
- `vercel.json` - Configuration for build, environment, and routing
- `vercel.cron.json` - Cron schedule (e.g., every 6 hours)

### Environment Variables

All environment variables should be set in Vercel dashboard. See `.env.example` for required variables.

Key variables:
- `DJANGO_SECRET_KEY` - Django secret key
- `DB_*` - PostgreSQL credentials
- `REDIS_URL` - Redis connection URL
- `DJANGO_AWS_*` - AWS S3 credentials
- `EMAIL_*` - Email service configuration
- `CRON_SECRET` - Secret token for cron verification

### Database Migrations

Run migrations before or after deployment:

```bash
# Pull .env variables
vercel env pull

# Run migrations
python manage.py migrate --settings=src.config.production

# Create superuser
python manage.py createsuperuser --settings=src.config.production
```

### Static Files & Media

- Static files are served from AWS S3
- Media files are uploaded to AWS S3
- Configure S3 bucket in Django settings

### Background Tasks

- Scheduled tasks configured in `api/cron.py`
- Run on Vercel Cron schedule (configured in `vercel.cron.json`)
- Secure via `CRON_SECRET` token verification

### Troubleshooting

See [VERCEL_QUICK_REFERENCE.md](VERCEL_QUICK_REFERENCE.md) for:
- Common error solutions
- Database connection issues
- Static files problems
- Monitoring and logs
- Rollback procedures

### Support

For issues or questions:
1. Check the troubleshooting section in VERCEL_QUICK_REFERENCE.md
2. Review Vercel logs: `vercel logs --follow`
3. Verify environment variables in Vercel dashboard
4. Check database and Redis connectivity
