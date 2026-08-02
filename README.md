# 57R337 $M4R7 NYC — Campaign Operations Center

Street Smart NYC Campaign Operations Center. A campaign management platform for voice, SMS, email, WhatsApp, Telegram, Messenger, and Instagram campaigns.

## Quick Start

```bash
# Create virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt

# Set environment variables
cp .env.example .env
# Edit .env with your settings

# Run the application
python run.py
```

Access the UI at: http://localhost:8080

## Project Structure

```
ssmartnyc-press1-power-campainer/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions
│   ├── static/              # Static assets (CSS, JS, images)
│   │   ├── css/
│   │   ├── js/
│   │   └── img/
│   ├── modules/             # Feature modules (one directory per module)
│   │   ├── auth/            # Authentication
│   │   ├── configengine/    # Configuration engine
│   │   ├── database/        # Database models and migrations
│   │   ├── filemanager/     # File management
│   │   ├── assetlibrary/    # Asset library
│   │   ├── notifications/   # Notification system
│   │   ├── api/             # REST API
│   │   ├── taskqueue/       # Celery task queue
│   │   ├── storage/         # File storage
│   │   ├── logging_module/  # Structured logging
│   │   └── ui/              # UI templates and routes
│   ├── templates/           # HTML templates
│   └── tests/               # Test suite
├── config/                  # Configuration files
├── docs/                    # Documentation
│   ├── campaign-operations-plan.md  # Complete development plan
│   ├── version-1.0-spec.md         # Version 1.0 frozen spec
│   ├── operator/            # Operator guide
│   └── admin/               # Administrator guide
├── uploads/                 # File storage
├── exports/                 # Export files
├── logs/                    # Log files
├── migrations/              # Alembic migration scripts
├── tests/                   # Test suite
├── .env.example             # Environment variables template
├── .gitignore
├── CHANGELOG.md
├── Dockerfile
├── docker-compose.yml
├── README.md
├── requirements.txt
├── requirements-dev.txt
├── run.py
└── VERSION
```

## Development

Run tests:
```bash
pytest
```

Run with coverage:
```bash
pytest --cov=app
```

## Stages

This project follows a dependency-based staging approach:
- Stage 0: Product Definition
- Stage 1: Foundation (current)
- Stage 2: Universal Data Layer
- Stage 3: Upload Center
- Stage 4: Provider Center
- Stage 5: Campaign Engine
- Stage 6: Workflow Builder
- Stage 7: Live Operations Center
- Stage 8: AI Layer
- Stage 9: Enterprise

## Version 1.0

Version 1.0 includes 30 modules across all stages, with 15 additional features identified from user feedback:
- Guided Setup Wizard
- Readiness Score
- Dependency Checker
- System Map
- Queue Visualization
- Campaign Replay
- Provider Failover
- Asset Versioning
- Campaign Simulation
- Contact Journey
- AI Campaign Builder
- Notification Center
- Health Center
- Global Search
- Command Palette
- Workspace Navigation

## Documentation

- **Plan**: `docs/campaign-operations-plan.md` — Complete development plan
- **V1.0 Spec**: `docs/version-1.0-spec.md` — Frozen Version 1.0 specification
- **Operator Guide**: `docs/operator/README.md` — Day-to-day operations
- **Admin Guide**: `docs/admin/README.md` — System administration
- **Changelog**: `CHANGELOG.md` — Version history
