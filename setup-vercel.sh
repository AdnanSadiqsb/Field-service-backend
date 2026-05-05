#!/bin/bash
# Setup script for Vercel deployment
# Usage: chmod +x setup-vercel.sh && ./setup-vercel.sh

set -e

echo "🚀 Field Service Backend - Vercel Deployment Setup"
echo "=================================================="
echo ""

# Check prerequisites
echo "📋 Checking prerequisites..."

if ! command -v vercel &> /dev/null; then
    echo "❌ Vercel CLI not found. Installing..."
    npm install -g vercel
fi

if ! command -v python &> /dev/null; then
    echo "❌ Python not found. Please install Python 3.8+"
    exit 1
fi

if ! command -v git &> /dev/null; then
    echo "❌ Git not found. Please install Git"
    exit 1
fi

echo "✅ All prerequisites met"
echo ""

# Generate secret key
echo "🔑 Generating Django secret key..."
SECRET_KEY=$(python -c "from django.core.management.utils import get_random_secret_key; print(get_random_secret_key())")
CRON_SECRET=$(openssl rand -hex 32)

echo ""
echo "📝 Environment Setup"
echo "===================="
echo ""
echo "Generated secrets (save these):"
echo "DJANGO_SECRET_KEY: $SECRET_KEY"
echo "CRON_SECRET: $CRON_SECRET"
echo ""

# Create .env.local if it doesn't exist
if [ ! -f .env.local ]; then
    echo "📄 Creating .env.local from .env.example..."
    cp .env.example .env.local
    
    # Update with generated secrets
    if [[ "$OSTYPE" == "darwin"* ]]; then
        # macOS
        sed -i '' "s/your-secret-key-here-change-this/$SECRET_KEY/" .env.local
        sed -i '' "s/your-random-cron-secret-here/$CRON_SECRET/" .env.local
    else
        # Linux
        sed -i "s/your-secret-key-here-change-this/$SECRET_KEY/" .env.local
        sed -i "s/your-random-cron-secret-here/$CRON_SECRET/" .env.local
    fi
    
    echo "✅ .env.local created"
else
    echo "⏭️  .env.local already exists, skipping..."
fi

echo ""

# Check if Vercel project is linked
echo "🔗 Checking Vercel project..."
if [ ! -d .vercel ]; then
    echo "📌 Linking to Vercel..."
    vercel link
else
    echo "✅ Vercel project already linked"
fi

echo ""
echo "✨ Setup complete!"
echo ""
echo "Next steps:"
echo "==========="
echo "1. Update .env.local with your actual credentials:"
echo "   - Database connection (DB_HOST, DB_NAME, etc.)"
echo "   - Redis URL"
echo "   - AWS S3 credentials"
echo "   - Email service credentials"
echo "   - Sentry DSN (optional)"
echo ""
echo "2. Run migrations locally (if database is accessible):"
echo "   python manage.py migrate --settings=src.config.production"
echo ""
echo "3. Set environment variables in Vercel:"
echo "   vercel env add <VARIABLE_NAME>"
echo ""
echo "   Or use the Vercel dashboard:"
echo "   https://vercel.com/dashboard → Project → Settings → Environment Variables"
echo ""
echo "4. Push to your repository to trigger deployment:"
echo "   git add ."
echo "   git commit -m 'Setup Vercel deployment'"
echo "   git push"
echo ""
echo "5. Monitor deployment:"
echo "   vercel logs --follow"
echo ""
echo "📚 Full guide: See VERCEL_DEPLOYMENT.md"
