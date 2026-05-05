#!/bin/bash
# Run Django migrations for Vercel deployment
# Usage: chmod +x run-migrations.sh && ./run-migrations.sh

set -e

# Load .env file if it exists
if [ -f .env.local ]; then
    export $(cat .env.local | xargs)
fi

echo "🗄️  Running Django Migrations"
echo "=============================="
echo ""
echo "Database: $DB_HOST"
echo "Database Name: $DB_NAME"
echo ""

# Check if database is accessible
echo "🔍 Checking database connectivity..."
python -c "
import psycopg2
import os

try:
    conn = psycopg2.connect(
        host=os.getenv('DB_HOST'),
        port=os.getenv('DB_PORT', '5432'),
        database=os.getenv('DB_NAME'),
        user=os.getenv('DB_USER'),
        password=os.getenv('DB_PASSWORD')
    )
    conn.close()
    print('✅ Database connection successful')
except Exception as e:
    print(f'❌ Database connection failed: {e}')
    exit(1)
"

echo ""
echo "🔄 Running migrations..."
python manage.py migrate --settings=src.config.production --verbosity=2

echo ""
echo "📊 Collecting static files..."
python manage.py collectstatic --settings=src.config.production --noinput

echo ""
echo "✅ Migrations completed successfully!"
