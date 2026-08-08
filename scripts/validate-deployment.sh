#!/bin/bash
set -e

echo "=== Production Deployment Validation ==="

# Source .env
if [ -f /home/ssmartnycbase/ssmartnyc-press1-power-campainer/.env ]; then
    set -a
    source /home/ssmartnycbase/ssmartnyc-press1-power-campainer/.env
    set +a
fi

# Check environment
if [ "$FLASK_ENV" != "production" ]; then
    echo "❌ FLASK_ENV is not set to production"
    exit 1
fi
echo "✓ FLASK_ENV=production"

# Check SECRET_KEY
if [ -z "$FLASK_SECRET_KEY" ] || [ "$FLASK_SECRET_KEY" = "dev-secret-key-change-me" ]; then
    echo "❌ FLASK_SECRET_KEY is not set or is default"
    exit 1
fi
echo "✓ FLASK_SECRET_KEY is set"

# Check database
if [ -z "$DATABASE_URL" ]; then
    echo "❌ DATABASE_URL is not set"
    exit 1
fi
echo "✓ DATABASE_URL is set"

# Check gunicorn
if ! command -v gunicorn &> /dev/null; then
    echo "❌ gunicorn not found"
    exit 1
fi
echo "✓ gunicorn installed"

# Check nginx
if ! command -v nginx &> /dev/null; then
    echo "❌ nginx not found"
    exit 1
fi
echo "✓ nginx installed"

# Check wsgi.py
if [ ! -f "/home/ssmartnycbase/ssmartnyc-press1-power-campainer/wsgi.py" ]; then
    echo "❌ wsgi.py not found"
    exit 1
fi
echo "✓ wsgi.py exists"

echo ""
echo "=== All validation checks passed ==="
