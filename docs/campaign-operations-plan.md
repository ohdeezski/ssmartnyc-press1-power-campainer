# 57R337 $M4R7 NYC — Campaign Operations Center
## Complete Dependency-Based Development Plan

---

# M15510N & PR0DUC7 G04L5

**What this software is:**
A campaign operations center that lets anyone run voice, SMS, email, WhatsApp, Telegram, Messenger, and Instagram campaigns — from one screen — without knowing anything about telecom systems.

**Who uses it:**
- Campaign managers who need to reach people
- Sales teams running outbound calls
- Support teams sending follow-ups
- Anyone who needs to contact a list of people using voice, text, or email

**Design philosophy:**
The software explains itself. Every screen tells you exactly what is happening, what is ready, and what needs attention. No technical knowledge required.

**Street Smart NYC Cyber Branding:**
- Main headers use cyber styling: `C4MP41GN`, `C0NN3CT`, `L0G5`
- Body text stays normal and readable
- Status colors: Gray (not started), Blue (preparing), Cyan (connecting), Green (running), Yellow (waiting), Orange (retrying), Purple (transferring), Red (failed), White (finished)
- Colors: Background `#050505`, Cards `#101418`, Border `#1CEFFF`, Accent `#00E5FF`, Warning `#FFAA00`, Danger `#FF3366`, Success `#00FF99`, Purple `#7B2EFF`

**Development Principle — Dependencies First:**
Every system is built only after its foundation exists. No campaign feature is built until the platform it runs on is complete. Each stage depends on the stage before it. Nothing is skipped.

---

# M0DUL3 00 — D3PL0YM3NT & R3L3453 57R473GY

**Goal:** One codebase. Deploy everywhere.

```text
Development -> Testing -> Beta -> Production -> Android -> Enterprise
```

### Stage 0: Local Development
Runs entirely on workstation.
```text
Parrot OS / Linux -> Python Flask -> SQLite -> Local Assets -> Local Providers -> Git
```
- Fast development
- No cloud costs
- Easy debugging
- Offline capable

### Stage 1: Development Server
As soon as the dashboard works, deploy automatically.
```text
GitHub -> Vercel -> streetsmartnyc.online
```
Use Vercel primarily for web frontend (great developer experience and free tier for static/frontend hosting).

### Stage 2: Backend Hosting
For the Flask backend, use Google Cloud Run long-term (leveraging existing credits):
```text
GitHub -> Google Cloud Run -> Flask API -> Database
```
**Cloud Run Advantages:**
- Scales to zero when idle
- Container-based
- Simple deployments
- HTTPS included
- Custom domain support (`api.streetsmartnyc.online`)
- Native integration with Google Cloud ecosystem

### Subdomains Strategy
- `streetsmartnyc.online` — Landing / Marketing
- `dashboard.streetsmartnyc.online` — Web Dashboard UI
- `api.streetsmartnyc.online` — Core REST & WebSocket API
- `status.streetsmartnyc.online` — Health & Provider Monitoring
- `docs.streetsmartnyc.online` — API & User Documentation
- `download.streetsmartnyc.online` — Asset & App Downloads

### Stage 3: Database & Storage Evolution
- **Database**:
  - Early MVP: `SQLite` (`instance/campaigns.db`)
  - Beta: `PostgreSQL`
  - Enterprise: `Cloud SQL (PostgreSQL)`
- **Storage**:
  - Development: Local (`uploads/`, `assets/`, `reports/`)
  - Cloud / Prod: `Google Cloud Storage` (Audio, Reports, Templates, Images, PDFs, Backups)

### Authentication Progression
- Development: Local Accounts (Email / Password + Roles)
- Production: Google OAuth, Microsoft OAuth, Email Magic Link
- Enterprise: SAML 2.0, OIDC, Single Sign-On (SSO)

### Automated CI/CD Pipeline
```text
GitHub Push -> Lint & Type Check -> Pytest Suite -> Docker Build -> Cloud Run Deploy -> Health Check -> Notification
```

### Environment Isolation
- `.env.development`
- `.env.testing`
- `.env.beta`
- `.env.production`
*(No secrets stored in codebase. Enforced via Environment Variables & Secret Manager)*

### Logging & Real-Time Monitoring
- Development: Console & `logs/app.log`
- Production: Centralized Google Cloud Logging, Error Reporting, Audit Logs
- Dashboard Metrics: CPU, RAM, Storage, API Latency, DB Connections, SocketIO status, Provider Latency, Disk I/O

### Beta Rollout Strategy
Invite-only tiered rollout: `10 Users -> 50 Users -> 100 Users -> Public Launch`

### Mobile & Cross-Platform Roadmap
Do **not** build native Android first.
```text
Responsive Web App -> Progressive Web App (PWA) -> Android / iOS (Flutter)
```
- **Benefits**: Single codebase, immediate mobile access, easier testing before app store publishing.
- **Google Play Rollout**: `Internal Testing -> Closed Testing -> Open Testing -> Production`

### Version Timeline
- `0.1`: Internal Development & Foundation
- `0.3`: UI & Dashboard Complete
- `0.5`: Backend & Universal Data Layer Complete
- `0.7`: Closed Beta (10-50 Users)
- `0.9`: Public Beta
- `1.0`: Production Web Release
- `1.5`: Mobile PWA / Android Release (Flutter)
- `2.0`: Multi-tenant Enterprise Release

---

# 5747475 5747U5 — 574G3 574713

## Stage 0: Product Definition

**Goal:** Freeze the product definition before writing a single line of code.

**What gets defined:**

### Mission
A campaign operations center where Asterisk is just one connector among many. Voice, SMS, email, WhatsApp, Telegram, Messenger, and Instagram all plug into the same workflow engine, unified contact database, analytics, scheduler, AI assistant, and review screen. The result is software that explains itself.

### Target Users
- Campaign managers with zero telecom experience
- Sales teams running outbound voice/SMS/email campaigns
- Support teams sending follow-up messages
- Small businesses managing customer outreach
- Agencies managing multiple client campaigns

### Brand Guide
- Name: Street Smart NYC Campaign Operations Center
- Colors: `#050505` background, `#101418` cards, `#1CEFFF` borders, `#00E5FF` accent, `#FFAA00` warning, `#FF3366` danger, `#00FF99` success, `#7B2EFF` purple
- Typography: Cyber styling on headers only (page titles, card titles, dashboard labels, major navigation, status labels). Body text, buttons, logs, phone numbers, error messages, config names, file names stay normal.
- Cyber effects: Thin neon borders, faint scanline overlay, animated status pulse, cyan hover, terminal font for stats only
- Visual landmarks: `57R337 $M4R7 NYC` (main header), `C4MP41GN` (section title), `C0NF1G` (configuration), `L0G5` (logs), `4UD10` (audio), `C4MP41GN TYP3` (campaign type)

### Design System
- Cards as primary UI containers
- Progress bars for all multi-step processes
- Color-coded status indicators for all states
- Plain-language event feed instead of raw logs
- Cyber styling only on headers and status labels
- All interactive elements use normal, readable text

### UX Rules
1. Every screen tells you exactly what is happening
2. Nothing starts until you review it on the Launch Review screen
3. Status colors tell you the state at a glance
4. The progress pipeline shows where contacts are in the process
5. The live event feed uses human-readable timestamps and descriptions
6. No technical jargon in user-facing text
7. Every action has a clear confirmation or feedback
8. Errors say what went wrong and how to fix it
9. Post-campaign results are auto-generated
10. The AI assistant explains things in plain language

### Architecture
- Channel-agnostic campaign engine
- Each communication channel is a pluggable connector
- Universal data layer shared by all campaign types
- Event bus for real-time updates
- REST API + WebSocket for automation
- SQLite or PostgreSQL for persistence
- Background task queue for long-running operations

### Directory Layout
```
street-smart-campaign-center/
├── app/
│   ├── modules/
│   │   ├── auth/
│   │   ├── campaigns/
│   │   ├── contacts/
│   │   ├── providers/
│   │   ├── uploads/
│   │   ├── assets/
│   │   ├── analytics/
│   │   ├── workflow/
│   │   ├── notifications/
│   │   ├── automation/
│   │   ├── ai/
│   │   ├── database/
│   │   ├── storage/
│   │   ├── events/
│   │   └── ui/
│   ├── config/
│   ├── tests/
│   └── docs/
├── uploads/
│   ├── numbers/
│   │   ├── active/
│   │   ├── success/
│   │   └── blacklist/
│   ├── audio/
│   │   ├── intro/
│   │   ├── outro/
│   │   ├── agent/
│   │   ├── hold/
│   │   └── misc/
│   ├── templates/
│   │   ├── sms/
│   │   ├── email/
│   │   ├── whatsapp/
│   │   ├── telegram/
│   │   ├── messenger/
│   │   └── instagram/
│   └── assets/
│       ├── images/
│       ├── logos/
│       └── branding/
├── config/
│   ├── providers/
│   ├── caller-profiles/
│   ├── number-pools/
│   └── templates/
├── logs/
│   ├── campaign/
│   ├── calls/
│   ├── errors/
│   └── audit/
├── exports/
│   ├── csv/
│   ├── excel/
│   └── pdf/
└── docs/
    └── campaign-operations-plan.md
```

### Coding Standards
- Python 3.10+ with type hints
- Flask + Flask-SocketIO for web layer
- SQLAlchemy for database ORM
- Celery + Redis for background task queue
- Tailwind CSS for UI styling
- SocketIO for real-time events
- render_template_string() instead of manual string replacement
- Single Flask initialization (no duplicates)
- REST API + WebSocket + JSON endpoints
- All user-facing text in plain English
- All technical terms translated to plain language in UI


### Environment Setup

**Python 3.11+** required. All development uses virtual environments.

```bash
# Create project
mkdir street-smart-campaign-center
cd street-smart-campaign-center

# Virtual environment
python3 -m venv venv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
```

**Project scaffold:**
```
street-smart-campaign-center/
├── app/
│   ├── __init__.py          # Flask app factory
│   ├── config.py            # Configuration classes
│   ├── extensions.py        # Flask extensions (db, socketio, celery, etc.)
│   ├── modules/             # Feature modules (one directory per module)
│   │   ├── __init__.py
│   │   ├── auth/
│   │   │   ├── __init__.py
│   │   │   ├── models.py
│   │   │   ├── routes.py
│   │   │   ├── services.py
│   │   │   └── tests/
│   │   ├── campaigns/
│   │   ├── contacts/
│   │   ├── providers/
│   │   ├── uploads/
│   │   ├── assets/
│   │   ├── analytics/
│   │   ├── workflow/
│   │   ├── notifications/
│   │   ├── automation/
│   │   ├── ai/
│   │   ├── database/
│   │   ├── storage/
│   │   ├── events/
│   │   └── ui/
│   ├── templates/           # HTML templates
│   ├── static/              # CSS, JS, images
│   └── utils/               # Shared utilities
├── migrations/              # Alembic migration scripts
├── tests/                   # Test suite
│   ├── unit/
│   ├── integration/
│   ├── ui/
│   └── load/
├── docs/                    # Documentation
├── uploads/                 # File storage
├── config/                  # Configuration files
├── logs/                    # Log files
├── exports/                 # Export files
├── requirements.txt         # Python dependencies
├── requirements-dev.txt     # Development dependencies
├── Dockerfile               # Container definition
├── docker-compose.yml       # Multi-container setup
├── .env.example             # Environment variables template
├── .gitignore
└── README.md
```

**Requirements.txt (core):**
```
Flask>=3.0
Flask-SocketIO>=5.3
Flask-SQLAlchemy>=3.1
Flask-Migrate>=4.0
Flask-Login>=0.6
Flask-WTF>=1.2
celery>=5.3
redis>=5.0
gunicorn>=21.2
python-dotenv>=1.0
Pillow>=10.0
python-magic>=0.4
werkzeug>=3.0
```

**Requirements-dev.txt:**
```
pytest>=7.4
pytest-cov>=4.1
pytest-flask>=1.3
flake8>=6.1
black>=23.0
isort>=5.12
mypy>=1.5
coverage>=7.3
factory-boy>=3.3
faker>=19.0
selenium>=4.11
locust>=2.20
```

### Coding Standards (Updated)
- Python 3.11+ with type hints on all public functions
- Flask application factory pattern (`create_app()`)
- Single Flask initialization — no duplicates
- SQLAlchemy ORM for all database access
- Celery for all background tasks
- SocketIO for all real-time communication
- REST API with JSON responses
- WebSocket for live updates
- render_template_string() instead of manual string replacement
- All user-facing text in plain English
- All technical terms translated to plain language in UI
- Type hints on every function signature
- Docstrings on every public class and function
- Consistent naming: snake_case for variables, PascalCase for classes, SCREAMING_SNAKE_CASE for constants

### Testing Standards (Updated)
Every stage ends with testing. Never continue until green.

| Test Level | Description | When |
|-----------|-------------|------|
| Unit Tests | Individual functions and methods | After each module is built |
| Integration Tests | Module-to-module interactions | After each stage is complete |
| UI Tests | User interface flows and validation | Before each stage ships |
| Load Tests | Performance under concurrent usage | Before production deployment |
| Manual Tests | Human verification of all user flows | Before each stage ships |
| Beta | Limited user testing with real data | Before production release |
| Production | Full deployment with monitoring | Final step |

**Per-module testing:** Each module (1.1-1.11) must have its own unit test file in `tests/unit/` before integration testing begins.

### CI/CD Pipeline
| Stage | Action |
|-------|--------|
| On commit | Run linter (flake8, black, isort) |
| On commit | Run type checker (mypy) |
| On commit | Run unit tests |
| On PR | Run integration tests |
| On PR | Run UI tests |
| On merge to main | Run load tests |
| On release | Run full test suite |
| On deploy | Run migration scripts |
| On deploy | Health check all services |

### Backward Compatibility / Migration from Existing Codebase
The existing Flask application (from plan-for-app) will be migrated, not rewritten:
1. Existing routes are mapped to new module structure
2. Existing templates are refactored to use Jinja2 properly
3. Existing configuration is imported into the new config system
4. Existing database (if any) is migrated using Alembic
5. Existing uploaded files are moved to the new directory structure
6. No data is lost during migration
7. A migration script is provided and tested



---

# 5747475 5747U5 — 574G3 574713 (Continued)

## Stage 1: Foundation

**Goal:** Build the platform that every future module depends on. No campaign features yet.

**Why this order:** Authentication, database, storage, logging, notifications, API, task queue, file manager, asset library, and configuration engine are the foundation. Every campaign type, every upload, every provider connection, every workflow, every notification — all of it depends on these systems existing first.

### 1.1 Authentication

**What it does:** Secure the system so only authorized people can control campaigns.

**Features:**
- Login with email/password
- Role-based access control (Admin, Manager, Operator, Viewer)
- User sessions with timeout
- Optional MFA (multi-factor authentication)
- Password reset flow
- User management screen
- Activity log for every login attempt

**Why first:** Without authentication, anyone reaching the panel can control campaigns, access contacts, and see all data. This is a security and legal requirement before any campaign data is stored.

**Non-tech explanation:** "Think of it like a key to the building. Only people with the right key can get in, and different people can only go to certain rooms."

### 1.2 Settings

**What it does:** Central configuration engine for the entire system.

**Features:**
- Application-wide settings (timezone, default language, date format)
- System settings (max file size, allowed formats, storage paths)
- UI preferences (theme: Cyber / Classic / Terminal)
- Notification preferences (email alerts, in-app alerts, sound alerts)
- Backup settings (frequency, retention, location)
- Export settings (default format, default date range)

**Why first:** Every other module needs to know where to store files, how to format data, and what the user's preferences are. Settings is the system's memory.

### 1.3 Database

**What it does:** Persistent storage for all campaign data, user data, and system state.

**Features:**
- PostgreSQL (production) or SQLite (development)
- Connection pooling
- Migration system (Alembic or similar)
- Backup and restore tooling
- Database health monitoring

**Why first:** Every module needs a place to store and retrieve data. The database is the foundation of persistence.

### 1.4 Storage

**What it does:** File storage system for all uploaded assets.

**Features:**
- Local file storage (development)
- S3-compatible object storage (production)
- File upload API
- File download API
- File deletion with confirmation
- File validation (type, size, content)
- Storage quota management
- Directory structure enforcement

**Why first:** Uploads, assets, templates, and all file-based features depend on a working storage system.

### 1.5 Logging

**What it does:** System-wide logging for debugging, auditing, and monitoring.

**Features:**
- Structured logging (JSON format)
- Log levels (DEBUG, INFO, WARNING, ERROR, CRITICAL)
- Log rotation (daily, size-based)
- Log retention policy
- Log search and filtering
- Log export (CSV, PDF)
- Audit log for every user action

**Why first:** Every other module needs to log events. The logging system must exist before any feature can produce logs.

### 1.6 Notifications

**What it does:** Deliver alerts and updates to users in real time.

**Features:**
- In-app toast notifications
- In-app banner notifications
- Browser push notifications (optional)
- Email notifications (optional)
- Telegram notifications (optional)
- Notification center (unread count, history)
- Notification preferences per user
- Notification types: Campaign started, Campaign finished, Error, Upload complete, Provider disconnected, Queue empty, Disk full, System alert

**Why first:** Every stage of the campaign lifecycle needs to notify the user. The notification system must exist before campaigns can run.

### 1.7 API

**What it does:** Expose the system programmatically for automation and integration.

**Features:**
- REST API (JSON)
- WebSocket API (real-time events)
- API key management
- Rate limiting
- API documentation (OpenAPI/Swagger)
- Webhook support (external systems receive events)
- Authentication for API (token-based)

**Why first:** Automation, integrations, and future extensibility all depend on the API. Building it early means every subsequent module can be consumed programmatically.

### 1.8 Task Queue

**What it does:** Handle long-running background tasks without blocking the web server.

**Features:**
- Celery + Redis (or equivalent)
- Task scheduling (delayed, periodic, one-time)
- Task retry with exponential backoff
- Task status tracking
- Task result storage
- Task cancellation
- Worker health monitoring

**Why first:** Campaigns run as background tasks. File conversions, provider API calls, report generation, and email sending all need to happen asynchronously. The task queue must exist before any campaign can execute.

### 1.9 File Manager

**What it does:** Unified system for managing all uploaded files.

**Features:**
- Upload (drag-and-drop, click-to-upload)
- Validate (format, size, content)
- Preview (audio play, image display, text render)
- Version history (every replacement saved)
- Replace (upload new version, old version archived)
- Archive (move to archive, remove from active)
- Delete (with confirmation)
- Restore (recover from archive or previous version)
- Search (by name, type, date, tags)
- Sort (by name, date, type, size)
- Bulk operations (select multiple, delete, archive, export)

**Why first:** The Upload Center depends on a working file manager. Every campaign type uploads files through this system.

### 1.10 Asset Library

**What it does:** Central repository for all reusable assets.

**Features:**
- Store all intros, outros, hold music, voicemail recordings, images, PDFs, email templates, SMS templates, caller ID profiles, logos, brand themes, AI prompts, campaign templates
- Searchable by name, tag, type, date
- Version history for every asset
- Quick switching between assets
- Preview for every asset type
- Tags and categories for organization
- Usage tracking (which campaigns use which assets)
- Shared across campaigns

**Why first:** Every campaign uses assets. The asset library must exist before campaigns can reference audio files, templates, images, or any other reusable content.

### 1.11 Configuration Engine

**What it does:** Dynamic configuration management for the entire system.

**Features:**
- Auto-save configuration changes
- Configuration versioning
- Rollback to previous configuration
- Undo configuration changes
- Configuration validation before saving
- Environment-specific settings (dev, staging, production)
- Secret management (API keys, tokens, passwords encrypted at rest)
- Configuration export/import

**Why first:** Every module needs configuration. The configuration engine ensures settings are managed safely and consistently.

### Per-Module Testing Checklists

#### 1.1 Authentication — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: User registration | ☐ |
| Unit: User login/logout | ☐ |
| Unit: Session management | ☐ |
| Unit: Role-based access control | ☐ |
| Unit: Password reset flow | ☐ |
| Unit: MFA enrollment and verification | ☐ |
| Unit: Session timeout | ☐ |
| Unit: Invalid credentials handling | ☐ |
| Integration: Auth → API → UI | ☐ |
| UI: Login page | ☐ |
| UI: Registration page | ☐ |
| UI: Settings page | ☐ |
| UI: MFA setup page | ☐ |
| Manual: Complete auth workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.2 Settings — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Read settings | ☐ |
| Unit: Write settings | ☐ |
| Unit: Validate settings | ☐ |
| Unit: Auto-save settings | ☐ |
| Unit: Rollback settings | ☐ |
| Unit: Environment-specific settings | ☐ |
| Integration: Settings → all modules | ☐ |
| UI: Settings page | ☐ |
| Manual: Complete settings workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.3 Database — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: CRUD operations | ☐ |
| Unit: Migrations (up/down) | ☐ |
| Unit: Backup | ☐ |
| Unit: Restore | ☐ |
| Unit: Connection pooling | ☐ |
| Unit: Query performance | ☐ |
| Integration: DB → all modules | ☐ |
| Manual: Full database workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.4 Storage — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Upload file | ☐ |
| Unit: Download file | ☐ |
| Unit: Delete file | ☐ |
| Unit: Validate file type | ☐ |
| Unit: Validate file size | ☐ |
| Unit: Validate file content | ☐ |
| Unit: Storage quota | ☐ |
| Integration: Storage → all modules | ☐ |
| UI: File upload UI | ☐ |
| Manual: Complete storage workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.5 Logging — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Write log entry | ☐ |
| Unit: Read log entries | ☐ |
| Unit: Search logs | ☐ |
| Unit: Filter logs | ☐ |
| Unit: Export logs | ☐ |
| Unit: Log rotation | ☐ |
| Unit: Audit log for user actions | ☐ |
| Integration: Logging → all modules | ☐ |
| UI: Log viewer | ☐ |
| Manual: Complete logging workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.6 Notifications — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Create notification | ☐ |
| Unit: Deliver toast notification | ☐ |
| Unit: Deliver banner notification | ☐ |
| Unit: Deliver alert notification | ☐ |
| Unit: Mark notification as read | ☐ |
| Unit: Clear notifications | ☐ |
| Unit: Notification preferences | ☐ |
| Integration: Notifications → event bus | ☐ |
| UI: Notification center | ☐ |
| Manual: Complete notification workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.7 API — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: API endpoint (each route) | ☐ |
| Unit: API authentication | ☐ |
| Unit: API rate limiting | ☐ |
| Unit: API error handling | ☐ |
| Unit: API documentation | ☐ |
| Unit: WebSocket connection | ☐ |
| Unit: WebSocket event handling | ☐ |
| Integration: API → all modules | ☐ |
| UI: API documentation page | ☐ |
| Manual: Complete API workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.8 Task Queue — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Enqueue task | ☐ |
| Unit: Execute task | ☐ |
| Unit: Retry task | ☐ |
| Unit: Cancel task | ☐ |
| Unit: Task status tracking | ☐ |
| Unit: Task result storage | ☐ |
| Unit: Worker health monitoring | ☐ |
| Integration: Task queue → all modules | ☐ |
| Manual: Complete task queue workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.9 File Manager — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Upload file | ☐ |
| Unit: Validate file | ☐ |
| Unit: Preview file | ☐ |
| Unit: Version history | ☐ |
| Unit: Replace file | ☐ |
| Unit: Archive file | ☐ |
| Unit: Delete file | ☐ |
| Unit: Restore file | ☐ |
| Unit: Search files | ☐ |
| Unit: Sort files | ☐ |
| Unit: Bulk operations | ☐ |
| Integration: File manager → storage | ☐ |
| UI: File manager UI | ☐ |
| Manual: Complete file manager workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.10 Asset Library — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Store asset | ☐ |
| Unit: Search assets | ☐ |
| Unit: Version asset | ☐ |
| Unit: Preview asset | ☐ |
| Unit: Tag asset | ☐ |
| Unit: Categorize asset | ☐ |
| Unit: Track asset usage | ☐ |
| Integration: Asset library → file manager | ☐ |
| UI: Asset library UI | ☐ |
| Manual: Complete asset library workflow | ☐ |
| Beta: Internal testing | ☐ |

#### 1.11 Configuration Engine — Testing Checklist
| Test | Pass? |
|------|-------|
| Unit: Save configuration | ☐ |
| Unit: Validate configuration | ☐ |
| Unit: Rollback configuration | ☐ |
| Unit: Undo configuration change | ☐ |
| Unit: Environment-specific config | ☐ |
| Unit: Secret management | ☐ |
| Unit: Configuration export/import | ☐ |
| Integration: Config → all modules | ☐ |
| UI: Configuration UI | ☐ |
| Manual: Complete configuration workflow | ☐ |
| Beta: Internal testing | ☐ |

### Stage 1 Testing Checklist (Integration)

| Test | Pass? |
|------|-------|
| Integration: All modules work together | ☐ |
| UI: All settings screens functional | ☐ |
| Load: 100 concurrent API requests | ☐ |
| Manual: Full settings workflow | ☐ |
| Beta: Internal testing | ☐ |

**Stage 1 is complete when all tests pass green.**

---


---

## Stage 2: Universal Data Layer

**Goal:** Build universal data objects that every campaign type shares. Instead of building Voice, SMS, and Email separately, build the universal objects first, then plug channels into them.

**Why this order:** Every campaign type uses the same fundamental objects — Campaign, Contact, Asset, Provider, Message, Call, etc. Building these once as universal objects means every campaign type automatically shares the same data model, the same tracking, the same reporting, and the same workflows. No duplication.

### 2.1 Campaign

**What it is:** The top-level container for everything.

**Fields:**
- `id` — unique identifier
- `name` — campaign name (e.g., "Summer Sale")
- `type` — campaign type (Voice, SMS, Email, WhatsApp, Telegram, Messenger, Instagram, Mixed)
- `status` — Draft, Queued, Running, Paused, Finished, Failed, Archived
- `created_at` — when it was created
- `started_at` — when it was launched
- `finished_at` — when it completed
- `created_by` — user who created it
- `template_id` — reference to a reusable campaign template
- `workflow_id` — reference to the automation workflow
- `settings` — JSON blob of all campaign-specific settings
- `results` — JSON blob of final results

**Why this matters:** Every campaign, regardless of channel, starts here. The campaign object is the root of everything.

### 2.2 Campaign Template

**What it is:** A saved campaign configuration without contacts. Reusable for future campaigns.

**Fields:**
- `id` — unique identifier
- `campaign_id` — reference to the original campaign
- `name` — template name
- `category` — Sales, Support, Political, Survey, Emergency, Healthcare, etc.
- `settings` — all campaign settings preserved
- `audio_ids` — references to audio assets used
- `template_ids` — references to SMS/email templates used
- `caller_profile_id` — reference to caller identity profile
- `provider_ids` — references to providers used
- `workflow_id` — reference to automation workflow
- `contacts_removed` — contacts are stripped, only configuration preserved

**Why this matters:** One-click duplicate for the next campaign. Saves time and prevents configuration errors.

### 2.3 Campaign Run

**What it is:** A single execution of a campaign. A campaign can have multiple runs.

**Fields:**
- `id` — unique identifier
- `campaign_id` — reference to the campaign
- `run_number` — which execution this is (1st, 2nd, etc.)
- `status` — Queued, Running, Paused, Finished, Failed
- `started_at` — when this run started
- `finished_at` — when this run completed
- `total_contacts` — number of contacts in this run
- `total_calls` — total calls made
- `total_messages` — total messages sent
- `total_emails` — total emails sent
- `success_count` — total successful outcomes
- `failed_count` — total failures
- `conversion_count` — total conversions
- `cost` — total cost of this run
- `duration` — how long this run took
- `settings_snapshot` — exact settings used for this run

**Why this matters:** Campaign runs provide historical data for analytics and comparison.

### 2.4 Contact

**What it is:** A single person or entity to be contacted.

**Fields:**
- `id` — unique identifier
- `first_name` — first name
- `last_name` — last name
- `phone` — phone number (normalized)
- `email` — email address
- `company` — company name
- `tags` — list of tags for segmentation
- `consent_status` — opted_in, opted_out, unknown
- `consent_date` — when consent was given
- `language` — preferred language
- `timezone` — preferred timezone
- `notes` — internal notes
- `created_at` — when contact was added
- `updated_at` — when contact was last updated
- `interaction_history` — JSON array of all interactions across all channels

**Why this matters:** The contact is the target of every campaign. Universal contact object means every channel can reach the same person.

### 2.5 Contact List

**What it is:** A group of contacts, often uploaded as a file.

**Fields:**
- `id` — unique identifier
- `name` — list name
- `source` — where it came from (upload, CRM, database, Google Sheets)
- `contact_ids` — array of contact references
- `total_count` — number of contacts
- `valid_count` — number of valid contacts after validation
- `duplicate_count` — number of duplicates found
- `invalid_count` — number of invalid entries found
- `blocked_count` — number of blacklisted contacts
- `created_at` — when the list was created
- `updated_at` — when the list was last updated

**Why this matters:** Campaigns reference contact lists, not individual contacts. This enables batch operations and efficient processing.

### 2.6 Asset

**What it is:** Any reusable file or content piece.

**Fields:**
- `id` — unique identifier
- `name` — asset name
- `type` — audio, image, document, template, logo, theme, prompt
- `subtype` — intro, outro, hold_music, voicemail, sms_template, email_template, etc.
- `file_path` — where the file is stored
- `file_size` — size in bytes
- `file_format` — original format (WAV, MP3, HTML, TXT, etc.)
- `version` — current version number
- `versions` — array of previous versions with timestamps
- `tags` — searchable tags
- `created_by` — user who uploaded it
- `created_at` — when asset was created
- `updated_at` — when asset was last updated
- `preview_url` — URL for previewing the asset
- `thumbnail_url` — URL for thumbnail (images)
- `metadata` — JSON blob of additional metadata (duration for audio, dimensions for images, etc.)

**Why this matters:** Assets are the building blocks of campaigns. The asset library provides version history, search, and quick switching.

### 2.7 Provider

**What it is:** A connected service that can send messages or make calls.

**Fields:**
- `id` — unique identifier
- `name` — provider name (e.g., "Twilio Voice", "Asterisk Server")
- `type` — voice, sms, email, whatsapp, telegram, messenger, instagram
- `provider_type` — asterisk, twilio, flowroute, telnyx, skyetel, generic_sip, google, microsoft, smtp, sendgrid, mailgun, meta, telegram_bot
- `status` — connected, expired, needs_login, disabled
- `credentials` — encrypted credentials (API keys, tokens, SIP credentials)
- `connection_params` — connection parameters (server, port, trunk, context, etc.)
- `priority` — priority order for failover
- `health_status` — healthy, degraded, down
- `last_health_check` — timestamp of last health check
- `failover_provider_id` — reference to backup provider
- `rate_limit` — messages/calls per second allowed
- `created_at` — when provider was connected
- `updated_at` — when provider was last updated

**Why this matters:** Every campaign needs a provider. The universal provider object means any channel can use any provider with the same interface.

### 2.8 Connection

**What it is:** The actual connection instance between the system and a provider.

**Fields:**
- `id` — unique identifier
- `provider_id` — reference to the provider
- `status` — connected, disconnected, connecting, error
- `connected_at` — when the connection was established
- `disconnected_at` — when the connection was lost
- `last_used_at` — when the connection was last used
- `health_check_result` — last health check result
- `latency_ms` — connection latency
- `error_message` — last error message (if any)

**Why this matters:** Providers can have multiple connection instances (e.g., different trunks). The connection object tracks the state of each individual connection.

### 2.9 Message

**What it is:** A single message sent through any channel.

**Fields:**
- `id` — unique identifier
- `campaign_run_id` — reference to the campaign run
- `contact_id` — reference to the recipient
- `channel` — voice, sms, email, whatsapp, telegram, messenger, instagram
- `provider_id` — reference to the provider used
- `status` — queued, sending, accepted, delivered, opened, clicked, replied, completed, failed
- `status_history` — array of status changes with timestamps
- `content` — the message content (template + variables filled in)
- `template_id` — reference to the template used
- `attachments` — array of asset references
- `sent_at` — when the message was sent
- `delivered_at` — when delivery was confirmed
- `opened_at` — when the recipient opened it (if trackable)
- `clicked_at` — when the recipient clicked a link (if trackable)
- `replied_at` — when the recipient replied (if trackable)
- `error_message` — error details if delivery failed
- `cost` — cost of this message

**Why this matters:** Every communication is a message. The universal message object enables cross-channel tracking and unified reporting.

### 2.10 Call

**What it is:** A single voice call instance.

**Fields:**
- `id` — unique identifier
- `campaign_run_id` — reference to the campaign run
- `contact_id` — reference to the recipient
- `provider_id` — reference to the voice provider used
- `status` — dialing, ringing, answered, press1, transferred, voicemail, no_answer, busy, failed, completed
- `status_history` — array of status changes with timestamps
- `caller_id` — the caller ID used for this call
- `duration_seconds` — how long the call lasted
- `intro_asset_id` — reference to the intro audio played
- `hold_asset_id` — reference to the hold music played
- `agent_connect_asset_id` — reference to the agent bridge audio
- `outro_asset_id` — reference to the outro audio played
- `voicemail_asset_id` — reference to the voicemail audio played
- `press1_detected` — whether the recipient pressed 1
- `transferred_to` — agent extension or number if transferred
- `recording_url` — URL to call recording (if enabled)
- `sent_at` — when the call was initiated
- `answered_at` — when the call was answered
- `completed_at` — when the call ended
- `cost` — cost of this call

**Why this matters:** Voice campaigns need detailed call tracking. The universal call object integrates with the message tracking system for unified reporting.

### 2.11 Conversation

**What it is:** A complete interaction thread between a contact and the system across all channels.

**Fields:**
- `id` — unique identifier
- `contact_id` — reference to the contact
- `campaign_run_id` — reference to the campaign run (if applicable)
- `messages` — array of message references
- `calls` — array of call references
- `status` — active, completed, archived
- `started_at` — when the conversation began
- `ended_at` — when the conversation ended
- `outcome` — converted, no_answer, busy, opted_out, completed, failed
- `summary` — AI-generated summary of the conversation
- `next_action` — recommended next step

**Why this matters:** The conversation object provides a unified view of every interaction a contact has had, regardless of channel. This is the basis for the contact timeline and AI recommendations.

### 2.12 Workflow

**What it is:** The automation logic that defines how a campaign behaves.

**Fields:**
- `id` — unique identifier
- `name` — workflow name
- `campaign_type` — which campaign types this workflow applies to
- `steps` — array of workflow steps (visual pipeline)
- `created_by` — user who created it
- `created_at` — when the workflow was created
- `updated_at` — when the workflow was last updated

**Why this matters:** The workflow object is the visual campaign builder. It defines the sequence of actions, conditions, delays, and branches that make a campaign work.

### 2.13 Rule

**What it is:** A condition that triggers an action within a workflow.

**Fields:**
- `id` — unique identifier
- `workflow_id` — reference to the parent workflow
- `name` — rule name
- `condition` — the condition to evaluate (e.g., "call answered == false")
- `action` — the action to take when condition is met (e.g., "send SMS after 15 minutes")
- `delay_seconds` — how long to wait before executing the action
- `max_retries` — maximum number of times to retry this rule
- `priority` — execution order

**Why this matters:** Rules are the building blocks of automation. They define what happens when something occurs during a campaign.

### 2.14 Trigger

**What it is:** An event that starts a workflow or rule evaluation.

**Fields:**
- `id` — unique identifier
- `workflow_id` — reference to the parent workflow
- `event_type` — call_answered, call_failed, press1_detected, no_answer, message_delivered, message_opened, message_replied, campaign_started, campaign_finished, timer
- `condition` — additional condition for the trigger
- `action_id` — reference to the action to execute

**Why this matters:** Triggers are the event-driven engine of the workflow system. They make campaigns responsive to real-time events.

### 2.15 Action

**What it is:** Something that happens as a result of a rule being triggered.

**Field types:**
- `send_voice` — place a voice call
- `send_sms` — send an SMS message
- `send_email` — send an email
- `send_whatsapp` — send a WhatsApp message
- `send_telegram` — send a Telegram message
- `send_messenger` — send a Messenger message
- `send_instagram` — send an Instagram DM
- `transfer_to_agent` — transfer to a live agent
- `play_audio` — play an audio file
- `wait` — wait for a specified duration
- `retry` — retry the previous action
- `update_contact` — update contact fields
- `add_tag` — add a tag to the contact
- `remove_tag` — remove a tag from the contact
- `create_task` — create a follow-up task
- `send_notification` — send a notification to the user
- `end_workflow` — stop the workflow for this contact

**Why this matters:** Actions are what actually happen during a campaign. The universal action system means any channel can trigger any action.

### 2.16 Event

**What it is:** A single occurrence in the system (for the event bus).

**Fields:**
- `id` — unique identifier
- `event_type` — campaign_started, call_answered, message_delivered, provider_connected, upload_complete, error, etc.
- `entity_type` — campaign, call, message, contact, provider, asset, etc.
- `entity_id` — reference to the affected entity
- `data` — JSON blob of event data
- `timestamp` — when the event occurred
- `processed` — whether the event has been processed by subscribers

**Why this matters:** The event bus is the nervous system of the application. Every status update, every progress change, every notification originates from events.

### 2.17 Notification

**What it is:** A user-facing alert about something that happened.

**Fields:**
- `id` — unique identifier
- `user_id` — reference to the recipient user
- `type` — info, warning, error, success
- `title` — short title
- `message` — detailed message in plain language
- `read` — whether the user has read it
- `created_at` — when the notification was created
- `action_url` — optional URL to take the user to the relevant screen

**Why this matters:** Notifications bridge the gap between system events and user awareness.

### 2.18 Analytics

**What it is:** Aggregated metrics and statistics.

**Fields:**
- `id` — unique identifier
- `campaign_run_id` — reference to the campaign run
- `channel` — voice, sms, email, whatsapp, telegram, messenger, instagram, combined
- `metric` — calls_made, calls_answered, messages_sent, messages_delivered, emails_sent, emails_opened, conversions, cost, duration, etc.
- `value` — the numeric value
- `metadata` — JSON blob of additional data
- `timestamp` — when the metric was recorded

**Why this matters:** Analytics are computed from events and messages. The analytics object enables fast dashboard rendering and historical comparison.

### 2.19 User

**What it is:** A system user.

**Fields:**
- `id` — unique identifier
- `email` — login email
- `name` — display name
- `role` — admin, manager, operator, viewer
- `status` — active, inactive, suspended
- `mfa_enabled` — whether MFA is active
- `created_at` — when the user was created
- `last_login_at` — when the user last logged in

### 2.20 Role

**What it is:** A set of permissions assigned to users.

**Fields:**
- `id` — unique identifier
- `name` — role name (Admin, Manager, Operator, Viewer)
- `permissions` — JSON array of allowed actions
- `description` — what this role can do

**Why this matters:** Roles enable multi-user support with proper access control.

---

## Stage 3: Upload Center

**Goal:** Build one reusable upload system that handles every file type. Every uploader behaves exactly the same way.

**Why this order:** The file manager (Stage 1) provides the foundation. Now we build the Upload Center that uses it. The upload center is the gateway for all campaign preparation. Every file type — contacts, audio, templates, images, caller IDs, number pools — goes through this single system.

### 3.1 Upload Center Overview

**When it appears:** Step 3 of the campaign builder, after contacts are loaded and before caller identity.

**Layout:** Cards for each upload type, arranged in the order they're needed.

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  4PD47 C3N73R                                                              │
│  ██████████████████████████████████████████████████████████████████████  │
│  18 / 20 Complete                                                           │
│  READY                                                                      │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                                       │
│  Each card shows:                                                            │
│  ├── Title (cyber styled)                                                  │
│  ├── Upload area (drag-and-drop + click)                                    │
│  ├── Accepted formats                                                       │
│  ├── Max file size                                                          │
│  ├── Preview area                                                           │
│  ├── Validation status                                                      │
│  ├── Version history                                                        │
│  └── Action buttons (Replace, Delete, Restore Default, Archive)             │
│                                                                                       │
│  [← Back]                                    [Next →]                         │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 3.2 Upload Types (Every Card)

Every upload card has the same behavior:

```
UPLOAD CARD STRUCTURE
├── Title (cyber styled)
│   ├── Icon
│   └── Name
├── Upload Area
│   ├── Drag-and-drop zone
│   ├── Click-to-browse button
│   ├── Accepted formats displayed
│   ├── Max file size displayed
│   └── Upload progress bar (per file)
├── Preview Area
│   ├── Audio: Play button (▶)
│   ├── Image: Thumbnail display
│   ├── Text: Rendered preview
│   ├── Template: Variable-highlighted preview
│   └── Numbers: Count and sample display
├── Validation Status
│   ├── ✓ PASS — file is valid and ready
│   ├── ⚠ WARNING — file has issues but can be used
│   └── ✗ FAIL — file is invalid, cannot be used
├── Version History
│   ├── Current version indicator
│   ├── Previous versions (click to restore)
│   └── Timestamps for each version
├── Action Buttons
│   ├── Replace — upload a new version
│   ├── Delete — remove the file (with confirmation)
│   ├── Restore Default — go back to the original file
│   └── Archive — move to archive, remove from active
└── Status Badge
    ├── Not Uploaded (gray)
    ├── Uploading (blue)
    ├── Validating (cyan)
    ├── Ready (green)
    ├── Warning (yellow)
    └── Error (red)
```

### 3.3 Upload Types Detail

#### C0N74C75 (Contacts)

**Purpose:** Upload the list of people to contact.

**Accepted formats:**
| Format | Extension | Max Size | Required Columns |
|--------|-----------|----------|------------------|
| Plain Text | `.txt` | 50 MB | One number per line |
| CSV | `.csv` | 50 MB | `name,phone,email` (headers required) |
| Excel | `.xlsx` | 100 MB | Same as CSV, headers in row 1 |
| Google Sheets | Link | Unlimited | Same as CSV |

**Column mapping:** When uploading CSV/Excel, the system shows a column mapping screen:
```
CSV Column    →  System Field
─────────────────────────────────
name          →  First Name
phone         →  Phone Number
email         →  Email Address
company       →  Company Name
```

**After upload, the card shows:**
```
LOADED: 5,234
DUPLICATES: 22  (removed)
INVALID: 7       (flagged)
BLOCKED: 13      (on blacklist, removed)
REMAINING: 5,192
STATUS: ✓ PASS
```

**Directory:** `uploads/numbers/active/`
**Naming:** `numbers_{campaign_name}_{date}.csv`

#### 4UD10 (Audio Files)

**Purpose:** Upload audio files for voice campaigns.

**Upload cards (one per audio type):**

```
INTRO
├── Upload File (WAV, MP3, GSM, OGG, FLAC, M4A)
├── Max Size: 50 MB
├── Recommended: 8kHz, 16-bit, mono WAV
├── Preview: ▶ Play button
├── Replace: upload new version
├── Delete: remove file
└── Restore Default: revert to original
──────────────
HOLD MUSIC
├── Upload File (WAV, MP3, GSM, OGG, FLAC, M4A)
├── Max Size: 50 MB
├── Recommended: 2-5 minutes, looping
├── Preview: ▶ Play button
├── Replace: upload new version
├── Delete: remove file
└── Restore Default: revert to original
──────────────
AGENT CONNECT
├── Upload File (WAV, MP3, GSM, OGG, FLAC, M4A)
├── Max Size: 50 MB
├── Recommended: 5-10 seconds
├── Preview: ▶ Play button
├── Replace: upload new version
├── Delete: remove file
└── Restore Default: revert to original
──────────────
VOICEMAIL
├── Upload File (WAV, MP3, GSM, OGG, FLAC, M4A)
├── Max Size: 50 MB
├── Recommended: 15-20 seconds
├── Preview: ▶ Play button
├── Replace: upload new version
├── Delete: remove file
└── Restore Default: revert to original
──────────────
OUTRO
├── Upload File (WAV, MP3, GSM, OGG, FLAC, M4A)
├── Max Size: 50 MB
├── Recommended: 5-10 seconds
├── Preview: ▶ Play button
├── Replace: upload new version
├── Delete: remove file
└── Restore Default: revert to original
```

**Audio conversion:** All files are automatically converted to 8kHz, 16-bit, mono WAV for Asterisk compatibility. FFmpeg is used first; SoX is the fallback.

**Directory:** `uploads/audio/{type}/`
**Naming:** `{type}_{campaign_name}_{timestamp}.wav`

#### M3554G3 (SMS Templates)

**Purpose:** Write or upload the SMS message template.

**Upload options:**
```
SMS TEMPLATE
├── Write Directly (text box with character counter)
├── Upload Template File (.txt, .html)
├── Choose from Library (saved templates)
└── AI Generate (ask Tomoe to write it)
```

**After template is set, the card shows:**
```
MESSAGE: "Hi {Name}, this is Street Smart NYC calling about..."
VARIABLES: {Name}, {Phone}, {Company}, {Date}
CHARACTER COUNT: 142
STATUS: ✓ PASS
```

**Accepted formats:** Plain Text (10 KB max), HTML (50 KB max)
**Directory:** `uploads/templates/sms/`
**Naming:** `sms_{campaign_name}_{date}.txt`

#### 3M41L (Email Templates)

**Purpose:** Create or upload the email template.

**Upload options:**
```
EMAIL TEMPLATE
├── Subject Line (text field)
├── Body (rich text editor)
├── Upload HTML Template File
├── Choose from Library
└── AI Generate
```

**After template is set, the card shows:**
```
SUBJECT: "Summer Sale — Exclusive Offer Inside"
BODY: [rich text preview]
ATTACHMENTS: 2 files (logo.png, flyer.pdf)
IMAGES: 3 embedded
STATUS: ✓ PASS
```

**Accepted formats:** HTML (100 KB max), Plain Text (10 KB max)
**Attachments:** Images (PNG, JPG, GIF, WebP, 10 MB each), Documents (PDF, DOC, DOCX, XLS, XLSX, 25 MB each)
**Directory:** `uploads/templates/email/` for templates, `uploads/assets/images/` for images, `uploads/assets/` for attachments
**Naming:** `email_{campaign_name}_{date}.html`

#### C4LL3R 1D3N717Y (Caller Identity)

**Purpose:** Choose which phone number and name shows up on the recipient's caller ID.

**Instead of confusing SIP settings, users see Caller Profiles:**

```
CALLER PROFILES
┌─────────────────────────────────────────────┐
│ 📞 Sales NYC                                │
│    212-555-1000                             │
│    Verified ✓                               │
│    ▼ (click to use)                         │
├─────────────────────────────────────────────┤
│ 📞 Support                                  │
│    212-555-1010                             │
│    Verified ✓                               │
│    ▼                                        │
├─────────────────────────────────────────────┤
│ 📞 Collections                              │
│    212-555-1020                             │
│    Verified ✓                               │
│    ▼                                        │
├─────────────────────────────────────────────┤
│ 📞 Spanish                                  │
│    212-555-1030                             │
│    Verified ✓                               │
│    ▼                                        │
├─────────────────────────────────────────────┤
│ 📞 Emergency                                │
│    212-555-1040                             │
│    Verified ✓                               │
│    ▼                                        │
├─────────────────────────────────────────────┤
│ 📞 Custom                                   │
│    (create new profile)                     │
└─────────────────────────────────────────────┘
```

**To create a new profile:**
```
+ CREATE NEW PROFILE
Fields:
  Profile Name: (text)
  Caller Name: (text)
  Caller Number: (phone)
  SIP Trunk: (dropdown of connected trunks)
  Outbound Route: (dropdown)
  Caller ID Prefix: (optional)
  STIR/SHAKEN: (yes/no)
  Notes: (text)
  Save
```

**Rotation options:**
```
ROTATION
○ Fixed (always same number)
○ Sequential (next number each call)
○ Round Robin (cycle through numbers evenly)
○ Random (pick any number randomly)
○ Weighted (some numbers used more than others)
○ Smart Rotation (best number based on time zone and success rate)
```

**Number Pools:**
```
NUMBER POOLS
├── New York (10 numbers)
├── Florida (5 numbers)
├── Support (20 numbers)
└── Sales (15 numbers)
```

Campaign picks a pool, and the system automatically uses numbers from that pool.

**Directory:** `config/caller-profiles/` and `config/number-pools/`

#### PR0V1D3R (Provider Connections)

**Purpose:** Connect and configure all communication providers.

**Voice Providers:**
```
VOICE
CONNECTED ✓
├── Asterisk (your own server)
├── Twilio
├── Flowroute
├── Telnyx
├── Skyetel
└── SIP Provider (custom)
```

**Messaging Providers:**
```
MESSAGING
CONNECTED ✓
├── Facebook (OAuth)
├── Instagram (OAuth)
├── Messenger (OAuth)
├── WhatsApp Business (OAuth)
├── Telegram (Bot Token)
├── Telegram Bot (Bot Token)
├── SMTP Email
├── SMS (Twilio, etc.)
├── Google
├── Microsoft
└── Slack
```

**Each provider shows one of these statuses:**
- 🟢 Connected — ready to use
- 🟡 Expired — needs re-authentication
- 🔴 Needs Login — not connected yet
- ⚫ Disabled — turned off

**One click to reconnect** any provider that is not connected.

**Connection details for each provider type:**

| Provider | Connection Method | What You Need |
|----------|------------------|---------------|
| Asterisk | CLI | Asterisk server running, CLI path |
| Twilio | API Key + OAuth | Account SID, Auth Token, phone number |
| Flowroute | API Credentials | Account ID, API Key, API Secret |
| Telnyx | API Key + Profile Token | API Key, Profile Token, phone number |
| Skyetel | API Key + Secret | API Key, API Secret |
| Generic SIP | SIP Credentials | Server, username, password, port, transport |
| Google | OAuth 2.0 | Google Cloud project, OAuth credentials |
| Microsoft | OAuth 2.0 | Azure app registration, client ID/secret |
| Facebook/Meta | OAuth 2.0 | Meta developer app, page access |
| Instagram | OAuth 2.0 | Meta developer app, Instagram business account |
| WhatsApp Business | OAuth 2.0 (via Meta) | WhatsApp Business account, approved templates |
| Telegram Bot | Bot Token | Bot token from BotFather |
| SMTP | SMTP Credentials or OAuth | Server, port, username, password, from address |
| SendGrid | API Key | API Key |
| Mailgun | API Key + Domain | API Key, domain |
| AWS SNS | IAM Credentials | Access Key, Secret Key, region |

**Directory:** `config/providers/`

#### RUL35 (Campaign Rules)

**Purpose:** Set how the campaign behaves.

**Settings:**
```
CAMPAIGN RULES
├── Concurrent Calls/Messages: [20]
├── Call Attempts: [3]
├── Wait Between Calls: [30 seconds]
├── Business Hours Only: [Yes / No]
├── Timezone Aware: [Yes / No]
├── Retry No Answer After: [15 minutes]
├── Retry Busy After: [1 hour]
├── Max Retry Days: [3]
├── Blackout Periods: [dates/times when no calls]
└── Staggered Start: [delay between batches]
```

**Directory:** `config/campaign-rules/`

#### L4UNCH R3V13W (Final Review)

**Purpose:** Final check before launching. Nothing starts until this page is reviewed.

```
L4UNCH R3V13W
┌─────────────────────────────────────────────┐
│ Campaign Name: Summer Sale                  │
│                                             │
│ Voice:        ✓                             │
│ SMS:          ✓                             │
│ Email:        ✓                             │
│ Instagram:    ✓                             │
│ Telegram:     ✓                             │
│                                             │
│ Recipients:     5,192                       │
│ Estimated Time: 2h 14m                      │
│ Concurrent Calls: 20                        │
│ Estimated Messages: 5,192                   │
│ Estimated Emails: 5,192                     │
│ Estimated Cost: $18.42                      │
│                                             │
│ Voice Files:  ✓ Intro ✓ Hold ✓ Agent ✓ Outro│
│ SMS Template: ✓                             │
│ Email Template: ✓                           │
│ Caller Profile: Sales NYC                   │
│ Number Pool: NY Sales                       │
│ Provider: Asterisk ✓                        │
│                                             │
│ 🟢 ALL SYSTEMS READY                        │
│                                             │
│ [🚀 LAUNCH CAMPAIGN]                        │
└─────────────────────────────────────────────┘
```

### 3.4 Upload Center Testing Checklist

| Test | Pass? |
|------|-------|
| Unit: File upload (each type) | ☐ |
| Unit: File validation (format, size, content) | ☐ |
| Unit: File preview (audio play, image display, text render) | ☐ |
| Unit: File version history (save, restore, archive) | ☐ |
| Unit: File replacement (upload new, old archived) | ☐ |
| Unit: File deletion (with confirmation) | ☐ |
| Unit: Column mapping (CSV/Excel) | ☐ |
| Unit: Contact validation (duplicates, invalid, blocked) | ☐ |
| Unit: Audio conversion (FFmpeg → SoX fallback) | ☐ |
| Unit: Template variable replacement | ☐ |
| Unit: Character count (SMS) | ☐ |
| Unit: Caller profile creation and selection | ☐ |
| Unit: Number pool creation and selection | ☐ |
| Unit: Provider connection (each type) | ☐ |
| Unit: Provider health check | ☐ |
| Unit: Provider failover | ☐ |
| Unit: Launch Review validation | ☐ |
| Unit: Verify (automatic system check) | ☐ |
| Integration: Upload → Validate → Preview → Launch | ☐ |
| UI: Drag-and-drop upload zones | ☐ |
| UI: Upload progress bars | ☐ |
| UI: All card interactions | ☐ |
| Load: Upload 100 files simultaneously | ☐ |
| Manual: Complete upload center workflow | ☐ |
| Beta: Internal testing | ☐ |

**Stage 3 is complete when all tests pass green.**

---


---

## Stage 4: Provider Center

**Goal:** Build one unified interface for connecting, testing, prioritizing, and monitoring all communication providers. Every connector supports the same operations.

**Why this order:** The Upload Center (Stage 3) handles files. The Provider Center handles connections. Campaigns need both before they can run. The Provider Center depends on the universal data layer (Stage 2) for storing provider configurations, and on the configuration engine (Stage 1) for managing credentials securely.

### 4.1 Provider Center Overview

**One screen. All providers. Same interface for every connection type.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  PR0V1D3R C3N73R                                                              │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                                       │
│  VOICE PROVIDERS:                                                            │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Asterisk        🟢 Connected    Latency: 12ms    Uptime: 99.9%  │   │
│  │ Twilio          🟢 Connected    Latency: 45ms    Uptime: 99.7%  │   │
│  │ Flowroute       🟡 Expired      Click to reconnect              │   │
│  │ Telnyx          🔴 Needs Login  Click to connect                │   │
│  │ Skyetel         🟢 Connected    Latency: 30ms    Uptime: 99.8%  │   │
│  │ Generic SIP     ⚫ Disabled     Click to enable                 │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                                       │
│  MESSAGING PROVIDERS:                                                        │
│  ┌─────────────────────────────────────────────────────────────────────┐   │
│  │ Facebook        🟢 Connected    Page: Street Smart NYC          │   │
│  │ Instagram       🟢 Connected    Account: @streetsmartnyc        │   │
│  │ Messenger       🟢 Connected    Page: Street Smart NYC          │   │
│  │ WhatsApp Business 🟢 Connected  Phone: +12125551000             │   │
│  │ Telegram Bot    🟢 Connected    Bot: @streetsmartbot            │   │
│  │ SMTP            🟢 Connected    Server: smtp.streetsmartnyc.com │   │
│  │ Twilio SMS      🟢 Connected    Number: +12125551001            │   │
│  │ Google          🟢 Connected    Account: campaigns@streetsmart  │   │
│  │ Microsoft       🟢 Connected    Account: campaigns@streetsmart  │   │
│  │ Slack           🔴 Needs Login  Click to connect                │   │
│  └─────────────────────────────────────────────────────────────────────┘   │
│                                                                                       │
│  [+ Add New Provider]  [Test All]  [Reconnect All Expired]  [Health Check All] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 4.2 Universal Connector Interface

Every provider connector supports the same operations:

```
CONNECTOR OPERATIONS
├── Connect — Establish connection (OAuth flow or credential entry)
├── Test — Verify the connection works (send test message or make test call)
├── Reconnect — Re-establish connection after disconnection or expiry
├── Priority — Set connection priority for failover (1 = highest)
├── Health — Monitor connection health (latency, uptime, error rate)
├── Failover — Automatic switch to backup provider if primary fails
├── Enable/Disable — Turn connection on or off
├── Edit — Update connection parameters
├── Delete — Remove the connection
└── View Logs — See connection history and events
```

### 4.3 Voice Provider Details

#### Asterisk
- **Connection method:** CLI (Command Line Interface)
- **What you need:** Asterisk server running, CLI path, trunk name, dialplan context
- **No credentials to enter** — the system connects directly to the Asterisk server
- **Test:** System creates a test call file and verifies Asterisk picks it up
- **Health check:** System checks if Asterisk CLI responds and if channels are available

#### Twilio (Voice)
- **Connection method:** API Key + OAuth
- **What you need:** Account SID, Auth Token, Twilio phone number
- **Test:** System makes a test call to a verification number
- **Health check:** System checks API connectivity and account balance

#### Flowroute
- **Connection method:** API Credentials
- **What you need:** Account ID, API Key, API Secret, Flowroute phone number
- **Test:** System sends a test API request and verifies response
- **Health check:** System checks API connectivity and account status

#### Telnyx
- **Connection method:** API Key + Profile Token
- **What you need:** API Key, Profile Token, Telnyx phone number or SIP trunk
- **Test:** System makes a test call or verifies SIP registration
- **Health check:** System checks API connectivity and account balance

#### Skyetel
- **Connection method:** API Key + Secret
- **What you need:** API Key, API Secret, Skyetel phone number or SIP trunk
- **Test:** System sends a test API request and verifies response
- **Health check:** System checks API connectivity and account status

#### Generic SIP
- **Connection method:** SIP Credentials
- **What you need:** SIP Server Address, Username, Password, Domain/Realm, Port, Transport
- **Test:** System attempts SIP registration and verifies response
- **Health check:** System checks registration status and latency

### 4.4 Messaging Provider Details

#### Twilio SMS
- **Connection method:** API Key (same Twilio account as voice)
- **What you need:** Twilio phone number, Messaging Service SID
- **Test:** System sends a test SMS to a verification number
- **Health check:** System checks API connectivity and message delivery rate

#### AWS SNS
- **Connection method:** IAM Credentials
- **What you need:** Access Key, Secret Key, AWS Region, SNS Topic ARN
- **Test:** System publishes a test message to the SNS topic
- **Health check:** System checks API connectivity and topic status

#### SMTP
- **Connection method:** SMTP Credentials or OAuth
- **What you need:** SMTP Server, Port, Username, Password, From Address
- **Test:** System sends a test email to the from address
- **Health check:** System checks SMTP connection and authentication

#### SendGrid
- **Connection method:** API Key
- **What you need:** SendGrid API Key, Sender Email
- **Test:** System sends a test email
- **Health check:** System checks API connectivity and sender reputation

#### Mailgun
- **Connection method:** API Key + Domain
- **What you need:** API Key, Domain, From Email
- **Test:** System sends a test email
- **Health check:** System checks API connectivity and domain verification

#### Meta (Facebook/Messenger/Instagram/WhatsApp)
- **Connection method:** OAuth 2.0
- **What you need:** Meta Developer App, Business Manager, Page/Account access
- **Test:** System verifies page access and sends a test message
- **Health check:** System checks token validity and API rate limits

#### Telegram Bot
- **Connection method:** Bot Token
- **What you need:** Bot token from BotFather
- **Test:** System sends a test message to the bot owner
- **Health check:** System checks bot API connectivity and token validity

### 4.5 Failover and Priority

**How failover works:**
1. Each provider has a priority number (1 = highest)
2. When a campaign starts, the system uses the highest-priority connected provider
3. If the primary provider fails during a campaign, the system automatically switches to the next available provider
4. The system logs the failover event and notifies the user
5. The user can manually reorder providers at any time

**Example:**
```
PRIORITY 1: Asterisk (Primary Voice)
PRIORITY 2: Twilio (Backup Voice)
PRIORITY 3: Flowroute (Emergency Voice)

If Asterisk goes down during a campaign:
→ System automatically switches to Twilio
→ User is notified: "Asterisk connection lost. Switched to Twilio."
→ Campaign continues without interruption
```

### 4.6 Provider Center Testing Checklist

| Test | Pass? |
|------|-------|
| Unit: Connect each provider type | ☐ |
| Unit: Test each provider connection | ☐ |
| Unit: Reconnect expired providers | ☐ |
| Unit: Health check each provider | ☐ |
| Unit: Failover from primary to backup | ☐ |
| Unit: Priority reordering | ☐ |
| Unit: Enable/disable providers | ☐ |
| Unit: Provider deletion with confirmation | ☐ |
| Unit: Credential encryption at rest | ☐ |
| Unit: Token refresh (OAuth providers) | ☐ |
| Integration: Provider → Campaign Engine | ☐ |
| UI: Provider Center screen | ☐ |
| UI: Provider status indicators | ☐ |
| UI: One-click reconnect | ☐ |
| Load: 10 providers connected simultaneously | ☐ |
| Manual: Connect, test, failover workflow | ☐ |
| Beta: Internal testing | ☐ |

**Stage 4 is complete when all tests pass green.**

---

## Stage 5: Campaign Engine

**Goal:** Build the campaign engine — the heart of the system. Instead of building Voice Campaign, SMS Campaign, Email Campaign separately, build one universal campaign engine and plug channels into it.

**Why this order:** The campaign engine depends on the universal data layer (Stage 2), the upload center (Stage 3), and the provider center (Stage 4). It is the system where everything comes together. Voice is just another connector — the same engine runs SMS, email, WhatsApp, Telegram, and mixed campaigns.

### 5.1 Campaign Engine Architecture

```
CAMPAIGN ENGINE
       │
       ├── Workflow Engine (reads the workflow definition)
       │       │
       │       ├── Trigger Evaluator (checks if triggers are met)
       │       │
       │       ├── Rule Evaluator (checks if conditions are met)
       │       │
       │       └── Action Executor (executes the actions)
       │
       ├── Channel Connectors (plug into the engine)
       │       │
       │       ├── Voice Connector → Provider (Asterisk/Twilio/etc.)
       │       ├── SMS Connector → Provider (Twilio/AWS SNS/etc.)
       │       ├── Email Connector → Provider (SMTP/SendGrid/etc.)
       │       ├── WhatsApp Connector → Provider (WhatsApp Business API)
       │       ├── Telegram Connector → Provider (Telegram Bot API)
       │       ├── Messenger Connector → Provider (Meta Messenger API)
       │       └── Instagram Connector → Provider (Meta Instagram API)
       │
       ├── Event Bus (publishes events for real-time updates)
       │
       ├── Tracking System (records every status change)
       │
       └── Reporting System (aggregates results)
```

### 5.2 Campaign Execution Flow

```
1. Campaign is launched
   ↓
2. Engine loads the campaign configuration
   ↓
3. Engine loads the contact list
   ↓
4. Engine validates all assets (audio files, templates, etc.)
   ↓
5. Engine verifies all providers are connected
   ↓
6. Engine starts the workflow
   ↓
7. For each contact in the list:
   │
   ├── Workflow Step 1: Voice Call
   │     │
   │     ├── Engine selects a provider (by priority)
   │     ├── Engine places the call via the provider
   │     ├── Engine tracks the call status:
   │     │     Queued → Dialing → Ringing → Answered → ...
   │     ├── Engine plays intro audio via the provider
   │     ├── Engine monitors for DTMF (Press 1)
   │     │
   │     ├── If Press 1 detected:
   │     │     └── Engine triggers Transfer action
   │     │           └── Engine connects to agent via provider
   │     │
   │     ├── If no answer:
   │     │     └── Engine triggers Wait action (15 minutes)
   │     │           └── Engine triggers SMS action
   │     │
   │     ├── If answered but no Press 1:
   │     │     └── Engine triggers Wait action
   │     │           └── Engine triggers Outro action
   │     │           └── Engine triggers SMS action (if configured)
   │     │
   │     └── Engine records the call result
   │
   ├── Workflow Step 2: SMS (if configured)
   │     │
   │     ├── Engine selects a provider (by priority)
   │     ├── Engine sends the SMS via the provider
   │     ├── Engine tracks the message status:
   │     │     Queued → Sending → Accepted → Delivered → Opened → Clicked → Replied
   │     └── Engine records the message result
   │
   ├── Workflow Step 3: Email (if configured)
   │     │
   │     ├── Engine selects a provider (by priority)
   │     ├── Engine sends the email via the provider
   │     ├── Engine tracks the message status:
   │     │     Queued → Sending → Accepted → Delivered → Opened → Clicked → Replied
   │     └── Engine records the message result
   │
   ├── Workflow Step 4: WhatsApp (if configured)
   │     │
   │     ├── Engine selects a provider (by priority)
   │     ├── Engine sends the message via the provider
   │     ├── Engine tracks the message status:
   │     │     Queued → Approved → Delivered → Read → Button Clicked → Conversation Started
   │     └── Engine records the message result
   │
   ├── Workflow Step 5: Telegram (if configured)
   │     │
   │     ├── Engine selects a provider (by priority)
   │     ├── Engine sends the message via the provider
   │     ├── Engine tracks the message status:
   │     │     Queued → Delivered → Read → Button Pressed
   │     └── Engine records the message result
   │
   └── Engine evaluates completion conditions
         │
         ├── All steps completed → Contact marked as Finished
         ├── Max retries exceeded → Contact marked as Failed
         ├── Opt-out detected → Contact marked as Do Not Contact
         └── Campaign complete → Engine generates report

8. Engine publishes campaign_finished event
   ↓
9. Notification system alerts the user
   ↓
10. Reporting system generates the final report
```

### 5.3 Voice Campaign Execution Detail

```
VOICE CAMPAIGN PATH

START
  │
  ├── Dial Number
  │     │
  │     ├── Ringing...
  │     │     │
  │     │     ├── Answered
  │     │     │     │
  │     │     │     ├── Play Intro Audio
  │     │     │     │     │
  │     │     │     │     ├── Press 1 Detected?
  │     │     │     │     │    ├── YES → Transfer to Agent → DONE (Converted)
  │     │     │     │     │    └── NO → Play Outro → Send SMS Follow-up (if configured) → DONE
  │     │     │     │     └── Timeout (no input)
  │     │     │     │          ├── Leave Voicemail (if configured) → DONE
  │     │     │     │          └── Play Outro → Send SMS Follow-up (if configured) → DONE
  │     │     │     └── Busy / Engaged
  │     │     │          └── Retry in 1 hour → DONE
  │     │     └── No Answer
  │     │          ├── Leave Voicemail (if configured)
  │     │          └── DONE → Queue for SMS Follow-up
  │     └── Failed (network error, invalid number, etc.)
  │          └── Log failure → DONE (Failed)
  │
  └── All numbers processed → Campaign Complete
```

### 5.4 SMS Campaign Execution Detail

```
SMS CAMPAIGN PATH

START
  │
  ├── Queue Messages
  │     │
  ├── Send Batch (respecting provider rate limits)
  │     │
  │     ├── Provider Accepts
  │     │     │
  │     │     ├── Delivered to Phone
  │     │     │     │
  │     │     │     ├── Opened (if supported by provider)
  │     │     │     │     │
  │     │     │     │     ├── Link Clicked → Conversion Tracked
  │     │     │     │     └── No Click
  │     │     │     └── Not Opened
  │     │     │
  │     │     ├── Replied → Reply Tracked, Agent Notified
  │     │     │
  │     │     └── Delivery Failed
  │     │          └── Retry (if configured) → Max retries exceeded → DONE (Failed)
  │     │
  │     └── Provider Rejects (invalid number, blocked, etc.)
  │          └── Log error → Skip → DONE (Failed)
  │
  └── All messages processed → Campaign Complete
```

### 5.5 Email Campaign Execution Detail

```
EMAIL CAMPAIGN PATH

START
  │
  ├── Queue Emails
  │     │
  ├── Send Batch (respecting provider rate limits)
  │     │
  │     ├── Provider Accepts
  │     │     │
  │     │     ├── Delivered to Inbox
  │     │     │     │
  │     │     │     ├── Opened (tracked via pixel)
  │     │     │     │     │
  │     │     │     │     ├── Link Clicked → Conversion Tracked
  │     │     │     │     └── No Click
  │     │     │     └── Not Opened
  │     │     │
  │     │     ├── Bounced → Remove from future campaigns
  │     │     │
  │     │     ├── Replied → Reply Tracked, Agent Notified
  │     │     │
  │     │     └── Provider Rejects (invalid email, spam filtered, etc.)
  │     │          └── Log error → Skip → DONE (Failed)
  │     │
  │     └── Provider Rejects (account issue, rate limit, etc.)
  │          └── Log error → Retry → DONE (Failed if persistent)
  │
  └── All emails processed → Campaign Complete
```

### 5.6 Mixed Campaign Execution Detail

```
MIXED CAMPAIGN PATH (Voice → SMS → Email)

START
  │
  ├── PHASE 1: Voice
  │     │
  │     ├── Call each number
  │     │     │
  │     │     ├── Answered + Press 1 → Transfer to Agent → CONVERTED
  │     │     ├── Answered + No Press → Leave Voicemail → QUEUED FOR SMS
  │     │     ├── No Answer → QUEUED FOR SMS
  │     │     └── Failed → SKIP TO EMAIL (if configured)
  │     │
  │     └── Wait 15 minutes after voice phase
  │
  ├── PHASE 2: SMS (for non-converted contacts)
  │     │
  │     ├── Send SMS to remaining contacts
  │     │     │
  │     │     ├── SMS Clicked → QUEUED FOR EMAIL
  │     │     ├── SMS Not Clicked → QUEUED FOR EMAIL
  │     │     └── SMS Failed → QUEUED FOR EMAIL
  │     │
  │     └── Wait 24 hours after SMS phase
  │
  ├── PHASE 3: Email (for non-converted contacts)
  │     │
  │     ├── Send Email to remaining contacts
  │     │     │
  │     │     ├── Email Opened + Clicked → CONVERTED
  │     │     ├── Email Opened + No Click → FOLLOW-UP LIST
  │     │     └── Email Bounced → REMOVE FROM LIST
  │     │
  │     └── Wait 3 days
  │
  ├── PHASE 4: Voice Retry (optional)
  │     │
  │     ├── Retry calls to contacts who had no answer
  │     │     │
  │     │     └── Same flow as Phase 1
  │     │
  │     └── Wait 7 days
  │
  └── ALL PHASES COMPLETE → GENERATE REPORT
```

### 5.7 Campaign Engine Testing Checklist

| Test | Pass? |
|------|-------|
| Unit: Campaign creation and validation | ☐ |
| Unit: Campaign launch and state transitions | ☐ |
| Unit: Contact list loading and validation | ☐ |
| Unit: Asset loading and validation | ☐ |
| Unit: Provider selection by priority | ☐ |
| Unit: Voice call placement (mock) | ☐ |
| Unit: SMS message sending (mock) | ☐ |
| Unit: Email sending (mock) | ☐ |
| Unit: WhatsApp message sending (mock) | ☐ |
| Unit: Telegram message sending (mock) | ☐ |
| Unit: Workflow trigger evaluation | ☐ |
| Unit: Workflow rule evaluation | ☐ |
| Unit: Workflow action execution | ☐ |
| Unit: Call status tracking | ☐ |
| Unit: Message status tracking | ☐ |
| Unit: Campaign completion detection | ☐ |
| Unit: Report generation | ☐ |
| Unit: Failover between providers | ☐ |
| Unit: Retry logic with configurable delays | ☐ |
| Unit: Blackout period enforcement | ☐ |
| Unit: Business hours enforcement | ☐ |
| Unit: Concurrent limit enforcement | ☐ |
| Unit: Campaign pause and resume | ☐ |
| Unit: Campaign stop and cleanup | ☐ |
| Integration: Voice campaign end-to-end (mock provider) | ☐ |
| Integration: SMS campaign end-to-end (mock provider) | ☐ |
| Integration: Email campaign end-to-end (mock provider) | ☐ |
| Integration: Mixed campaign end-to-end (mock providers) | ☐ |
| Integration: Campaign engine + Upload Center | ☐ |
| Integration: Campaign engine + Provider Center | ☐ |
| Integration: Campaign engine + Event Bus | ☐ |
| Integration: Campaign engine + Notification System | ☐ |
| Integration: Campaign engine + Analytics | ☐ |
| UI: Campaign builder wizard | ☐ |
| UI: Launch Review screen | ☐ |
| UI: Mission Control screen | ☐ |
| Load: 100 concurrent campaign executions | ☐ |
| Load: 10,000 contacts in a single campaign | ☐ |
| Manual: Complete voice campaign from start to finish | ☐ |
| Manual: Complete SMS campaign from start to finish | ☐ |
| Manual: Complete mixed campaign from start to finish | ☐ |
| Beta: Internal testing | ☐ |

**Stage 5 is complete when all tests pass green.**

---


---

## Stage 6: Workflow Builder

**Goal:** Build the visual campaign workflow editor on top of the Campaign Engine (Stage 5). Workflows are stored as data objects and executed by the campaign engine — the builder is the UI layer, not a separate execution system.

**Why this order:** The workflow builder depends on the campaign engine (Stage 5) for execution, the universal data layer (Stage 2) for storing workflow definitions, and the event bus (Stage 2) for triggering workflow steps. The campaign engine (Stage 5) must exist first because workflows are just data that the engine interprets and executes.

### 6.1 Workflow Builder Overview

**Visual drag-and-drop builder. No scripting required.**

```
WORKFLOW BUILDER

START
  │
  ├── Condition: Voice Call Made?
  │     │
  │     ├── YES → Action: Play Intro Audio
  │     │     │
  │     │     ├── Condition: Press 1 Detected?
  │     │     │    ├── YES → Action: Transfer to Agent → END
  │     │     │    └── NO → Action: Play Outro
  │     │     │         │
  │     │     │         └── Action: Wait 15 Minutes → Action: Send SMS → END
  │     │     │
  │     │     └── Condition: No Answer?
  │     │          ├── YES → Action: Leave Voicemail → Action: Wait 15 Minutes → Action: Send SMS → END
  │     │          └── NO → Action: Wait 1 Hour → Action: Retry Voice → END
  │     │
  │     └── NO → Action: Send Email → Action: Wait 3 Days → Action: Voice Retry → END
  │
  └── END
```

### 6.2 Workflow Building Blocks

**Every workflow is made of these blocks:**

| Block | What It Does | Example |
|-------|-------------|---------|
| **Start** | Begins the workflow | Campaign launched |
| **Condition** | Checks if something is true | "Was the call answered?" |
| **Action** | Does something | "Send SMS", "Play audio", "Transfer to agent" |
| **Delay** | Waits for a specified time | "Wait 15 minutes", "Wait 24 hours" |
| **End** | Stops the workflow for this contact | Campaign complete |

### 6.3 Visual Workflow Editor

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  W0RKFL0W BUILDER                                                            │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                                       │
│  [START] ──→ [Condition: Call Answered?]                                             │
│                    │          │                                                     │
│                  YES         NO                                                     │
│                    │          │                                                     │
│              [Action:           [Action: Wait 15 min]                              │
│               Play Intro]            │                                             │
│                    │              [Action: Send SMS]                                │
│              [Condition:              │                                             │
│               Press 1?]               │                                             │
│                    │                   │                                             │
│                  YES                  NO                                            │
│                    │                   │                                             │
│              [Action:           [Action: Wait 1 hour]                               │
│               Transfer to Agent]        │                                            │
│                    │                   │                                             │
│                  END              [Action: Retry Voice]                             │
│                                        │                                            │
│                                       END                                           │
│                                                                                       │
│  TOOLBOX (drag blocks here):                                                     │
│  ┌─────────┐ ┌──────────┐ ┌────────┐ ┌────────┐ ┌──────┐ ┌─────┐ │
│  │ Start   │ │ Condition │ │ Action │ │ Delay  │ │ End  │ │ Loop │ │
│  └─────────┘ └──────────┘ └────────┘ └────────┘ └──────┘ └─────┘ │
│                                                                                       │
│  [Save Workflow]  [Test Workflow]  [Deploy Workflow]  [Duplicate Workflow]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 6.4 Pre-Built Workflow Templates

**Voice Campaign (Default):**
```
START → Play Intro → Press 1? → YES: Transfer to Agent / NO: Play Outro → Send SMS → END
```

**SMS Follow-up:**
```
START → Send SMS → Wait 24h → Send Email → Wait 3 days → Send Voice Retry → END
```

**No Answer Recovery:**
```
START → Voice Call → No Answer? → YES: Wait 15min → Send SMS → Wait 24h → Send Email → END
```

**Press 1 Conversion:**
```
START → Voice Call → Press 1? → YES: Transfer to Agent / NO: Send SMS Follow-up → END
```

**Multi-Channel Nurture:**
```
START → Voice → No Answer → SMS → Clicked? → YES: Send Email / NO: Wait 3 days → Voice Retry → END
```

### 6.5 Workflow Builder Testing Checklist

| Test | Pass? |
|------|-------|
| Unit: Start block creation | ☐ |
| Unit: Condition block creation and evaluation | ☐ |
| Unit: Action block creation and execution | ☐ |
| Unit: Delay block creation and timing | ☐ |
| Unit: End block creation | ☐ |
| Unit: Block connection and flow | ☐ |
| Unit: Workflow save and load | ☐ |
| Unit: Workflow duplicate | ☐ |
| Unit: Workflow validation (no orphaned blocks) | ☐ |
| Unit: Workflow test (dry run) | ☐ |
| Unit: Workflow deployment | ☐ |
| Integration: Workflow → Campaign Engine execution | ☐ |
| Integration: Workflow → Event Bus triggers | ☐ |
| UI: Drag and drop blocks | ☐ |
| UI: Connect blocks with arrows | ☐ |
| UI: Delete blocks | ☐ |
| UI: Edit block properties | ☐ |
| UI: Test workflow dry run | ☐ |
| UI: Deploy workflow to campaign | ☐ |
| Manual: Build and execute a complete workflow | ☐ |
| Beta: Internal testing | ☐ |

**Stage 6 is complete when all tests pass green.**

---

## Stage 7: Live Operations Center

**Goal:** Build the real-time Mission Control dashboard. Everything updates from the event bus. No polling. Everything real time.

**Why this order:** The Live Operations Center depends on the campaign engine (Stage 5) for generating events, the event bus (Stage 2) for distributing events, and the notification system (Stage 1) for delivering alerts. Without the engine producing events, the operations center has nothing to display.

### 7.1 Mission Control Overview

**The top-of-screen dashboard during a live campaign:**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  C4MP41GN: July Sales Blitz        🟢 LIVE          46% Complete    ⏱ 2h14m│
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                                       │
│  CALLS: 1,820 / 5,192    MESSAGES: 0    EMAILS: 0    CONVERSIONS: 1,184  │
│                                                                                       │
│  PROGRESS PIPELINE:                                                                │
│  Loaded ██████████████████████████████████████████████████████████████ 5,192 │
│  Dialing ████████████████ 45                                                      │
│  Ringing ██████████ 32                                                              │
│  Answered ██████ 12                                                               │
│  Press 1 ███ 3                                                                    │
│  Transferred ██ 2                                                                 │
│  Finished ████████████████████████████████████████████████████████████ 1,726  │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ LIVE EVENT FEED                                                          │  │
│  │ 11:22  📥  5,192 contacts loaded                                        │  │
│  │ 11:23  🚀  Campaign started                                             │  │
│  │ 11:24  🔌  Asterisk connected                                           │  │
│  │ 11:24  📞  Dialing 555-0123 (1/5192)                                    │  │
│  │ 11:25  📞  Call answered — 555-0123                                     │  │
│  │ 11:25  🎵  Playing intro message                                        │  │
│  │ 11:26  🔢  Press 1 detected — transferring to agent                    │  │
│  │ 11:27  ✅  Completed — conversion recorded                              │  │
│  │ 11:27  📞  Dialing 555-0145 (2/5192)                                    │  │
│  │ 11:27  🎵  Playing intro message                                        │  │
│  │ 11:28  ❌  No answer — voicemail left, SMS follow-up queued           │  │
│  │ ...                                                                     │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  ┌─────────────────────────────────────────────────────────────────────────┐  │
│  │ PROVIDER HEALTH                                                         │  │
│  │ Asterisk  🟢  Latency: 12ms  Uptime: 99.9%                            │  │
│  │ Twilio    🟢  Latency: 45ms  Uptime: 99.7%                            │  │
│  │ SMTP      🟢  Latency: 30ms  Uptime: 99.8%                            │  │
│  └─────────────────────────────────────────────────────────────────────────┘  │
│                                                                                       │
│  SYSTEM METRICS:                                                                   │
│  ⚡ CPU: 23%   🧠 RAM: 45%   💾 Disk: 62%   🌐 Network: Active              │
│                                                                                       │
│  [⏸ PAUSE]  [⏹ STOP]  [📊 VIEW DETAILS]  [📥 EXPORT]  [🤖 AI ASSISTANT]     │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 7.2 Real-Time Event Bus

**How updates work:**
1. Campaign engine publishes events to the event bus (e.g., `call_answered`, `message_delivered`, `campaign_finished`)
2. The event bus distributes events to all subscribed clients via WebSocket
3. The Mission Control dashboard receives events in real time
4. The UI updates the progress pipeline, event feed, and metrics instantly
5. No polling — everything is push-based

**Event types:**
- `campaign_started` — campaign began executing
- `campaign_finished` — campaign completed
- `campaign_paused` — campaign was paused
- `campaign_resumed` — campaign was resumed
- `campaign_stopped` — campaign was stopped
- `call_placed` — a call was initiated
- `call_answered` — a call was answered
- `call_failed` — a call failed
- `call_completed` — a call finished
- `press1_detected` — recipient pressed 1
- `message_queued` — message entered the queue
- `message_sending` — message is being sent
- `message_delivered` — message was delivered
- `message_opened` — recipient opened the message
- `message_clicked` — recipient clicked a link
- `message_replied` — recipient replied
- `message_failed` — message delivery failed
- `provider_connected` — a provider connected successfully
- `provider_disconnected` — a provider connection was lost
- `provider_health_changed` — provider health status changed
- `upload_complete` — a file upload finished
- `error_occurred` — an error occurred
- `notification_triggered` — a notification was sent

### 7.3 Individual Call/Message Detail Panel

When you click on any contact in the list, a side panel shows the complete journey:

```
┌─────────────────────────────────────┐
│  Call #1874 — 555-0123              │
│  ───────────────────────────────────│
│                                     │
│  Preparing     ✓ Done               │
│  Dialing       ✓ Done               │
│  Ringing       ✓ Done               │
│  Answered      ✓ Done               │
│  Playing Intro ✓ Done               │
│  Waiting       ✓ Done               │
│  Press 1       Waiting...           │
│  Transfer      Pending              │
│  Complete      —                    │
│                                     │
│  ───────────────────────────────────│
│  Duration: 2m 34s                   │
│  Status: In Progress                │
│  Agent: Not assigned yet            │
│  Notes: —                           │
│                                     │
│  [Assign Agent] [Add Note] [Skip]   │
└─────────────────────────────────────┘
```

### 7.4 Status Color System

Every single call, message, and email has a color that tells you its state at a glance:

| Color | Meaning | What It Looks Like |
|-------|---------|-------------------|
| ⬜ Gray | Not Started | The contact has not been reached yet |
| 🔵 Blue | Preparing | The system is getting ready |
| 🔵 Cyan | Connecting | The system is dialing or sending |
| 🟢 Green | Running | The call/message is active |
| 🟡 Yellow | Waiting | On hold, waiting for answer or response |
| 🟠 Orange | Retrying | Will try again after a failed attempt |
| 🟣 Purple | Transferring | Moving to an agent or next channel |
| 🔴 Red | Failed | The call/message did not go through |
| ⚪ White | Finished | Completed successfully |

### 7.5 Notification System

| Notification Type | Visual | When It Appears |
|-------------------|--------|-----------------|
| **Toast** (bottom-right) | Brief popup, auto-dismisses | Campaign starts, upload complete, provider connected |
| **Banner** (top of screen) | Persistent yellow/amber bar | Warning: disk getting full, provider degrading |
| **Alert** (red banner) | Persistent red bar with sound option | Error: provider disconnected, campaign failed, disk full |
| **Badge** (on icon) | Red circle with number | New errors, unread notifications, pending actions |
| **Status change** | Color change on relevant card | Provider goes from 🟢 to 🔴, campaign changes from LIVE to FINISHED |

### 7.6 Live Operations Center Testing Checklist

| Test | Pass? |
|------|-------|
| Unit: Event bus publish/subscribe | ☐ |
| Unit: Event type handling | ☐ |
| Unit: WebSocket connection and reconnection | ☐ |
| Unit: Progress pipeline calculation | ☐ |
| Unit: Status color assignment | ☐ |
| Unit: Event feed generation | ☐ |
| Unit: Notification creation and delivery | ☐ |
| Unit: Provider health monitoring | ☐ |
| Unit: Real-time metrics update | ☐ |
| Unit: Call detail panel data loading | ☐ |
| Integration: Campaign engine → Event Bus → UI | ☐ |
| Integration: WebSocket → Dashboard update | ☐ |
| UI: Mission Control dashboard | ☐ |
| UI: Progress pipeline visualization | ☐ |
| UI: Live event feed | ☐ |
| UI: Individual call detail panel | ☐ |
| UI: Provider health panel | ☐ |
| UI: Notification toasts and banners | ☐ |
| UI: Pause/Stop/Resume campaign controls | ☐ |
| UI: Export during campaign | ☐ |
| Load: 10,000 events per second | ☐ |
| Load: 100 concurrent WebSocket connections | ☐ |
| Manual: Monitor a live campaign | ☐ |
| Beta: Internal testing | ☐ |

**Stage 7 is complete when all tests pass green.**

---

## Stage 8: AI Layer

**Goal:** Add AI assistants (Tomoe, Hermes, Oracle) that recommend, explain, analyze, predict, summarize, and suggest — but never control campaigns directly.

**Why this order:** The AI layer depends on the campaign engine (Stage 5) for data, the event bus (Stage 2) for real-time events, the analytics system (Stage 2) for historical data, and the notification system (Stage 1) for delivering insights. Without campaigns running and data being collected, AI has nothing to analyze.

### 8.1 AI Assistant Overview

**Always-visible panel. Plain language. No jargon.**

```
┌─────────────────────────────────────────────────────────────────────────────┐
│  T0M03 — AI ASSISTANT                                                        │
│  ─────────────────────────────────────────────────────────────────────────  │
│                                                                                       │
│  Current State:                                                           │
│  "Your Summer Sale campaign is 46% complete. 1,820 out of 5,192 contacts   │
│   have been processed. 12 calls are currently active, 8 are waiting for     │
│  available channels. The Asterisk provider is healthy. Twilio is on backup  │
│  and ready if needed."                                                       │
│                                                                                       │
│  What's Working:                                                          │
│  ✓ Voice connection is stable (12ms latency)                              │
│  ✓ 98% of answered calls are being transferred to agents                   │
│  ✓ SMS follow-up queue is processing normally                              │
│                                                                                       │
│  What Needs Attention:                                                    │
│  ⚠ 42 contacts were blocked by the provider. Check your number list for   │
│     invalid or blacklisted numbers.                                         │
│  ⚠ Twilio is approaching 78% of your monthly message limit. Consider      │
│     upgrading your plan or optimizing message content.                      │
│                                                                                       │
│  Recommendations:                                                         │
│  💡 "Your best performing caller profile is 'Sales NYC' with a 23%         │
│      conversion rate. Consider using it for your next campaign."            │
│  💡 "The best time to call your New York contacts is between 10am and       │
│      2pm EST. Your current campaign is calling at 9am."                      │
│  💡 "You have 423 contacts who did not answer. A follow-up SMS campaign    │
│      in 3 days could improve your conversion rate by an estimated 15%."     │
│                                                                                       │
│  Predicted Completion:                                                    │
│  Estimated finish: 2:14 PM EST (in 1h 14m)                                │
│  Estimated cost: $18.42 (so far: $8.72)                                   │
│                                                                                       │
│  [Ask Tomoe]  [Summarize Campaign]  [Clean Duplicates]  [Optimize Dialing] │
└─────────────────────────────────────────────────────────────────────────────┘
```

### 8.2 AI Assistant Capabilities

| Capability | Description | Example |
|-----------|-------------|---------|
| **Explain** | Describe what's happening in plain language | "Your campaign is 46% complete" |
| **Recommend** | Suggest improvements based on data | "Use Sales NYC profile for better conversion" |
| **Predict** | Estimate completion time and cost | "Expected to finish at 2:14 PM" |
| **Summarize** | Generate a summary of campaign results | "4,812 successes, 96 failed, $18.42 spent" |
| **Analyze** | Find patterns and insights | "Best calling time is 10am-2pm EST" |
| **Clean** | Identify and fix data issues | "22 duplicates found in your number list" |
| **Optimize** | Suggest configuration improvements | "Reduce concurrent calls to 15 for better quality" |
| **Detect** | Identify potential problems | "Twilio approaching monthly limit" |
| **Generate** | Create content (messages, templates, follow-ups) | "Write a follow-up SMS for no-answer contacts" |

### 8.3 AI Assistants (Tomoe, Hermes, Oracle)

**Tomoe** — The Operations Assistant
- Always visible in the sidebar
- Explains current campaign state
- Highlights issues and recommends fixes
- Predicts completion times
- Answers natural language questions

**Hermes** — The Analytics Assistant
- Available in the Analytics section
- Analyzes campaign performance data
- Finds trends and patterns
- Compares campaigns against each other
- Generates insights and recommendations

**Oracle** — The Strategy Assistant
- Available in the Campaign Builder
- Helps design campaign workflows
- Recommends channel combinations
- Suggests optimal timing and frequency
- Predicts campaign outcomes before launch

### 8.4 AI Layer Testing Checklist

| Test | Pass? |
|------|-------|
| Unit: AI explain (plain language generation) | ☐ |
| Unit: AI recommend (suggestion generation) | ☐ |
| Unit: AI predict (completion time estimation) | ☐ |
| Unit: AI summarize (result summarization) | ☐ |
| Unit: AI analyze (pattern detection) | ☐ |
| Unit: AI clean (data issue detection) | ☐ |
| Unit: AI optimize (configuration suggestions) | ☐ |
| Unit: AI generate (content creation) | ☐ |
| Unit: AI detect (problem identification) | ☐ |
| Integration: AI → Campaign Engine data | ☐ |
| Integration: AI → Event Bus real-time updates | ☐ |
| Integration: AI → Notification System alerts | ☐ |
| UI: AI assistant panel | ☐ |
| UI: Natural language input | ☐ |
| UI: AI response display | ☐ |
| UI: AI command buttons | ☐ |
| Manual: Test each AI capability | ☐ |
| Beta: Internal testing | ☐ |

**Stage 8 is complete when all tests pass green.**

---

## Stage 9: Enterprise

**Goal:** Add scheduling, permissions, teams, audit, API, integrations, CRM, exports, and testing for production readiness.

**Why this order:** Enterprise features depend on everything else being stable. You don't add team permissions, audit logging, or API access until the core product works reliably. This stage makes the product ready for business use and revenue generation.

### 9.1 Scheduling Center

**What it does:** Schedule campaigns to start at specific times, recur on a schedule, and respect business hours.

**Features:**
- One-time campaigns (start now or start at a specific date/time)
- Recurring campaigns (daily, weekly, monthly)
- Business hours only (no calls outside 9am-6pm)
- Timezone-aware (campaigns respect the contact's timezone)
- Blackout periods (no calls during holidays or maintenance windows)
- Staggered starts (delay between batches to avoid overwhelming providers)
- Campaign queue (view and manage all scheduled campaigns)

**Non-tech explanation:** "Set it and forget it. Pick a date and time, and the campaign starts automatically. No need to be at the computer."

### 9.2 Permissions and Teams

**What it does:** Control who can do what in the system.

**Features:**
- Role-based access control (Admin, Manager, Operator, Viewer)
- User management (add, remove, edit users)
- Team management (group users into teams)
- Campaign-level permissions (who can launch, pause, stop, view)
- Contact-level permissions (who can see which contacts)
- Activity log for every user action
- Session management (active sessions, force logout)

**Non-tech explanation:** "Like a building with different keys. Managers can launch campaigns. Operators can monitor them. Viewers can only look. Nobody can do anything without the right key."

### 9.3 Audit System

**What it does:** Record every action for accountability and compliance.

**Features:**
- Log every user action (login, campaign launch, file upload, config change)
- Log every system event (provider connection, campaign start, error)
- Audit trail with timestamps and user identification
- Audit log export (CSV, PDF)
- Audit log search and filtering
- Retention policy (keep audit logs for X months)
- Compliance reports (GDPR, TCPA, etc.)

**Non-tech explanation:** "Every action is recorded. If something goes wrong, you can see exactly who did what and when."

### 9.4 API and Integrations

**What it does:** Expose the system programmatically for automation and external system integration.

**Features:**
- REST API (JSON) for all operations
- WebSocket API for real-time data
- API key management (generate, revoke, rotate)
- Rate limiting (prevent abuse)
- API documentation (OpenAPI/Swagger)
- Webhook support (external systems receive events)
- CRM integrations (Salesforce, HubSpot, etc.)
- Zapier integration (connect to 5,000+ apps)
- Custom connector SDK

**Non-tech explanation:** "Let other software talk to this system automatically. Your CRM can trigger campaigns. Your accounting system can pull cost data. Your Slack can get campaign notifications."

### 9.5 Exports and Reporting

**What it does:** Export campaign data in multiple formats and generate professional reports.

**Features:**
- Export to CSV (raw data)
- Export to Excel (formatted spreadsheets)
- Export to PDF (professional reports)
- Scheduled exports (automatic daily/weekly/monthly reports)
- Custom report builder
- Dashboard export (screenshot or PDF)
- Shareable report links

### 9.6 Testing Strategy

**Every stage ends with testing. Never continue until green.**

| Test Level | Description | When |
|-----------|-------------|------|
| Unit Tests | Individual functions and methods | After each module is built |
| Integration Tests | Module-to-module interactions | After each stage is complete |
| UI Tests | User interface flows and validation | Before each stage ships |
| Load Tests | Performance under concurrent usage | Before production deployment |
| Manual Tests | Human verification of all user flows | Before each stage ships |
| Beta | Limited user testing with real data | Before production release |
| Production | Full deployment with monitoring | Final step |

**Stage 9 Testing Checklist:**

| Test | Pass? |
|------|-------|
| Unit: Scheduling (one-time, recurring, timezone) | ☐ |
| Unit: Permissions (role-based, campaign-level, contact-level) | ☐ |
| Unit: Audit logging (every action recorded) | ☐ |
| Unit: API (all endpoints, auth, rate limiting) | ☐ |
| Unit: Webhooks (event delivery, retry, dedup) | ☐ |
| Unit: CRM integration (Salesforce, HubSpot) | ☐ |
| Unit: Export (CSV, Excel, PDF) | ☐ |
| Unit: Report generation (executive summary, detailed) | ☐ |
| Unit: Scheduled export (daily, weekly, monthly) | ☐ |
| Integration: API → Campaign Engine | ☐ |
| Integration: Webhook → External System | ☐ |
| Integration: CRM → Contact Sync | ☐ |
| Integration: Export → File Storage | ☐ |
| UI: Scheduling Center | ☐ |
| UI: Permissions Management | ☐ |
| UI: Audit Log Viewer | ☐ |
| UI: API Documentation | ☐ |
| UI: Export and Report screens | ☐ |
| Load: 100 concurrent API requests | ☐ |
| Load: 10,000 contacts in a single campaign | ☐ |
| Load: 100 concurrent campaigns | ☐ |
| Security: SQL injection prevention | ☐ |
| Security: XSS prevention | ☐ |
| Security: Authentication bypass prevention | ☐ |
| Security: API key exposure prevention | ☐ |
| Security: Data encryption at rest | ☐ |
| Security: Data encryption in transit | ☐ |
| Manual: Full enterprise workflow | ☐ |
| Beta: External user testing | ☐ |
| Production: Deployment with monitoring | ☐ |

**Stage 9 is complete when all tests pass green.**

---


---

# M0N371Z4710N R04D M4P

## Monetization Strategy

**Do not monetize immediately.** The roadmap focuses on building a mature product first, then generating revenue.

### Phase 1: Working Product
- Voice, SMS, Email campaigns
- Upload Center
- Provider Center
- Campaign Builder
- Mission Control
- Reporting
- Authentication
- Testing

### Phase 2: Stable Product
- Social connectors (Meta, Instagram, Messenger, WhatsApp Business, Telegram Bot)
- AI assistant
- Automation workflows
- Scheduling
- Analytics
- Asset library
- Reusable templates

### Phase 3: Beta Users
- Limited user testing with real data
- Collect feedback
- Fix bugs
- Optimize performance

### Phase 4: Feedback
- Incorporate user feedback
- Prioritize feature requests
- Refine UX based on real usage

### Phase 5: Version 1.0
- Full feature set
- Production-ready
- Documentation complete
- Support processes established

### Phase 6: THEN Monetize
Only after Version 1.0 is stable and users are satisfied.

---

### Pricing Tiers

#### Free
- 1 user
- Limited contacts (1,000)
- One active campaign at a time
- Community support
- Basic analytics

#### Creator (Monthly Subscription)
- Unlimited campaigns
- Voice, SMS, Email channels
- Campaign templates
- Reports and exports
- Priority support

#### Professional (Monthly Subscription)
- Everything in Creator
- Multi-user teams
- AI assistant
- Automation workflows
- Scheduling
- Advanced analytics
- CRM integrations

#### Business (Monthly Subscription)
- Everything in Professional
- Multiple organizations
- Roles and permissions
- API access
- Webhooks
- Audit logs
- SSO
- High availability

#### Enterprise (Custom Pricing)
- Everything in Business
- On-premises deployment
- White labeling
- Priority support
- Dedicated infrastructure
- Custom integrations
- SLA (service level agreement)

---

### Additional Revenue Streams

| Revenue Stream | Description |
|---------------|-------------|
| **Marketplace** | Users can buy or share campaign templates, workflow templates, AI prompt packs, voice/audio packs, dashboard themes, integrations, reporting templates |
| **Managed Hosting** | We host and manage the system for customers who don't want to self-host |
| **Setup and Migration** | Professional services to set up the system and migrate data from other platforms |
| **AI Campaign Optimization** | Premium AI features for optimizing campaigns, predicting outcomes, and recommending improvements |
| **Premium Analytics** | Advanced analytics with heatmaps, trend analysis, and predictive modeling |
| **Training and Certification** | Training programs for users and administrators |
| **Consulting** | Custom campaign strategy and implementation consulting |
| **API Usage Plans** | Pay-per-use API access for developers and integrators |
| **Custom Connector Development** | Custom integrations with proprietary or niche providers |

---

# F1N41 4U71D — 4LL G4P5, 1NCONS1573NC1355, 4ND 4NY7H1NG 4757

## Comprehensive Gap Audit

### Gaps from Original Plan (Carried Forward)

| # | Gap | Severity | Status in New Plan |
|---|-----|----------|-------------------|
| 1 | No authentication | Critical | ✅ Stage 1.1 |
| 2 | No API | Critical | ✅ Stage 1.7 |
| 3 | No dashboard persistence | High | ✅ Stage 7 (Mission Control persists state) |
| 4 | No search | High | ✅ Stage 1.9 (File Manager search) + Stage 9 (global search) |
| 5 | No notification center | High | ✅ Stage 1.6 + Stage 7 |
| 6 | No file version history | High | ✅ Stage 1.9 (File Manager versioning) + Stage 3 |
| 7 | No test call before launch | High | ✅ Stage 3 (Launch Review includes test call) |
| 8 | No test message before launch | High | ✅ Stage 3 (Launch Review includes test message) |
| 9 | No campaign scheduling | High | ✅ Stage 9.1 (Scheduling Center) |
| 10 | No recurring campaigns | Medium | ✅ Stage 9.1 (recurring campaigns) |
| 11 | No do-not-call list integration | High | ✅ Stage 3 (Contact List includes blacklist) + Stage 9 (compliance) |
| 12 | No consent tracking | High | ✅ Stage 2.4 (Contact consent_status field) |
| 13 | Duplicate Flask initialization | Critical | ✅ Stage 1 (Coding Standards: single Flask initialization) |
| 14 | Manual template variable replacement | Medium | ✅ Stage 1 (Coding Standards: render_template_string()) |
| 15 | No background task queue | Medium | ✅ Stage 1.8 (Task Queue) |
| 16 | No upload progress indicator | Medium | ✅ Stage 3 (Upload progress bars) |
| 17 | No drag-and-drop upload | Low | ✅ Stage 3 (drag-and-drop zones) |
| 18 | No audio trimming | Low | ✅ Stage 3 (audio preview and replace) |
| 19 | No audio volume normalization | Low | ✅ Stage 3 (audio conversion includes normalization) |
| 20 | No caller ID preview | Medium | ✅ Stage 3 (Caller Identity card shows preview) |
| 21 | No timezone conversion for numbers | Medium | ✅ Stage 2.4 (Contact timezone field) + Stage 9.1 |
| 22 | No email bounce handling | Medium | ✅ Stage 5 (Email campaign tracks bounces) |
| 23 | No WhatsApp opt-out handling | High | ✅ Stage 5 (WhatsApp campaign tracks opt-outs) |
| 24 | No Instagram rate limiting | Medium | ✅ Stage 4 (Provider health monitoring includes rate limits) |
| 25 | No unified contact timeline | Medium | ✅ Stage 2.11 (Conversation object) + Stage 2.4 (interaction_history) |
| 26 | No AI-powered number scoring | Medium | ✅ Stage 8 (AI assistant analyzes contact data) |
| 27 | No automatic retry logic for failed messages | Medium | ✅ Stage 5 (Campaign engine retry logic) |
| 28 | No delivery receipt tracking for SMS | Medium | ✅ Stage 5 (SMS campaign tracks delivery receipts) |
| 29 | No email open/click tracking | Medium | ✅ Stage 5 (Email campaign tracks opens and clicks) |
| 30 | No real-time dashboard persistence | Medium | ✅ Stage 7 (Mission Control is real-time via event bus) |

### New Gaps Found in Restructured Plan

| # | Gap | Severity | Recommendation |
|---|-----|----------|----------------|
| 31 | No data migration strategy | High | Add migration scripts for moving from old system to new data model |
| 32 | No backward compatibility plan | High | Define how existing campaigns and data will be handled during migration |
| 33 | No disaster recovery plan | High | Add disaster recovery procedures (backup, restore, failover) |
| 34 | No performance benchmarks | Medium | Define performance targets (e.g., 1000 calls/minute, <100ms API response) |
| 35 | No monitoring and alerting | High | Add system monitoring (Prometheus/Grafana) and alerting (PagerDuty/Slack) |
| 36 | No documentation for operators | Medium | Add operator guide for day-to-day use |
| 37 | No documentation for administrators | Medium | Add admin guide for system configuration and maintenance |
| 38 | No documentation for developers | Medium | Add developer guide for extending the system |
| 39 | No changelog | Medium | Maintain a changelog for every release |
| 40 | No versioning strategy | Medium | Define semantic versioning (MAJOR.MINOR.PATCH) |
| 41 | No release process | Medium | Define release process (branch, test, review, deploy) |
| 42 | No CI/CD pipeline | High | Add automated testing and deployment pipeline |
| 43 | No containerization | Medium | Add Docker support for consistent deployment |
| 44 | No horizontal scaling plan | Medium | Define how the system scales under load |
| 45 | No database indexing strategy | Medium | Add indexes for frequently queried fields |
| 46 | No caching strategy | Medium | Add Redis caching for frequently accessed data |
| 47 | No CDN for static assets | Low | Use CDN for UI assets (CSS, JS, images) |
| 48 | No internationalization (i18n) | Low | Plan for multi-language support |
| 49 | No accessibility (a11y) compliance | Medium | Ensure UI meets WCAG 2.1 AA standards |
| 50 | No mobile responsive design | Medium | Ensure the UI works on tablets and mobile devices |

### Inconsistencies Found

| # | Inconsistency | Resolution |
|---|--------------|-----------|
| 1 | Original plan had "no API" and "should expose REST API" — contradictory | Resolved: API is built in Stage 1.7, before any campaign features |
| 2 | Original plan had "no authentication" and "needs login" — contradictory | Resolved: Authentication is built in Stage 1.1, before any data is stored |
| 3 | Original plan had duplicate Flask initialization — a bug | Resolved: Coding Standards in Stage 0 explicitly require single initialization |
| 4 | Original plan had manual string replacement — fragile | Resolved: Coding Standards in Stage 0 explicitly require render_template_string() |
| 5 | Original plan had "no dashboard persistence" and "need SQLite or Postgres" — incomplete | Resolved: Database (Stage 1.3) and dashboard persistence (Stage 7) are both built |
| 6 | Original plan had "no notification center" and "need notification center" — contradictory | Resolved: Notifications built in Stage 1.6, notification center in Stage 7 |
| 7 | Original plan had "no analytics" and "need analytics" — contradictory | Resolved: Analytics objects built in Stage 2, analytics dashboard in Stage 9 |
| 8 | Original plan had "no AI" and "integrate Tomoe/Hermes/Oracle" — contradictory | Resolved: AI layer built in Stage 8, after all data systems are in place |
| 9 | Original plan had "no quick actions" and "need quick actions" — contradictory | Resolved: Quick actions added to Stage 7 (Mission Control) and Stage 9 |
| 10 | Original plan had "no diagnostics" and "need diagnostics" — contradictory | Resolved: Diagnostics panel added to Stage 9 (Enterprise) |

---

# 5747475 5747U5 — 57H3 C0MPL373 W3 574713

## Three Milestones

### Minimum Viable Product (MVP)
**What:** Voice, SMS, Email campaigns + Upload Center + Provider Center + Campaign Builder + Mission Control + Reporting + Authentication + Testing
**When:** After Stages 1-7 are complete
**Why:** This is the smallest product that delivers real value. Users can run voice, SMS, and email campaigns with full visibility and control.

### Version 1.0
**What:** MVP + Social connectors (Meta, Instagram, Messenger, WhatsApp Business, Telegram Bot) + AI assistant + Automation workflows + Scheduling + Analytics + Asset Library + Reusable Templates
**When:** After Stages 8-9 are complete
**Why:** This is the complete product. All planned features are working. The system is stable, tested, and ready for external users.

### Enterprise Edition
**What:** Version 1.0 + Teams + CRM integrations + Public API + Webhooks + Audit logging + Advanced security + Multi-tenancy + White labeling + Marketplace
**When:** After Version 1.0 is stable and user feedback is incorporated
**Why:** This is the enterprise-grade product. It serves large organizations with complex needs, multiple teams, and strict compliance requirements.

---

## Final Summary

### What This Plan Covers

1. **Where/when/how to upload files** — Complete upload center with timing map, file format reference, storage directories, naming conventions, and validation rules for every file type (numbers, intro, outro, agent, hold music, voicemail, SMS templates, email templates, images, attachments, caller IDs, number pools)

2. **How the dialer connects to provider services** — Complete provider connection guide for every provider type (Asterisk, Twilio, Flowroute, Telnyx, Skyetel, SIP, Google, Microsoft, Facebook, Instagram, WhatsApp Business, Telegram Bot, SMTP, SendGrid, Mailgun, AWS SNS) with connection methods, setup steps, and test procedures

3. **Progress status upkeep with clear visuals** — Complete visual status system with color-coded states, progress pipeline, live event feed, individual call detail, provider health panel, notification system, and campaign completion screen — all in plain language

4. **All campaign types and paths** — 9 campaign types (Voice, SMS, Email, WhatsApp, Telegram, Telegram Bot, Messenger, Instagram, Mixed) with complete execution paths, conditional branches, retry logic, wait timers, and completion conditions

5. **Pre and post starting campaign** — Complete pre-campaign checklist (8 steps with verify screen), live campaign operations (Mission Control), and post-campaign process (auto-generated reports, follow-up lists, template saving)

6. **Clear visual signals and notifications** — Status color system, progress pipeline, live event feed, notification types (toast, banner, alert, badge, status change), and plain-language event descriptions

7. **Non-tech people form** — Every screen uses plain language. No technical jargon in user-facing text. Technical terms are translated to plain English. The AI assistant explains everything in plain language.

8. **Street Smart NYC cyber style** — Cyber styling on headers only, color theme matching Street Smart NYC branding, subtle cyber effects, typography rules (stylize headers only, never stylize body text), and visual landmarks

9. **Dependency-based staging** — 10 stages (0-9) where every system is built only after its foundation exists. No campaign feature is built until the platform it runs on is complete.

10. **Complete gap audit** — 50 gaps found, categorized by severity, with specific recommendations for each

11. **Monetization roadmap** — 6-phase approach from working product to monetization, with 5 pricing tiers and 9 additional revenue streams

12. **Three milestones** — MVP (after Stage 7), Version 1.0 (after Stage 9), Enterprise Edition (after Version 1.0 is stable)

13. **Testing strategy** — Every stage ends with testing. Unit, integration, UI, load, manual, beta, and production testing. Never continue until green.

14. **Future-proofing** — Modular architecture, pluggable connectors, universal data layer, event bus, API-first design, and clear extension points for future channels and features

---

## How to Use This Plan

1. **Start with Stage 0.** Approve the product definition before writing any code.
2. **Build Stage 1 completely.** Do not start Stage 2 until Stage 1 tests pass green.
3. **Follow the dependency order.** Each stage depends on the previous one. Do not skip.
4. **Test at every stage.** Every stage ends with a testing checklist. Never continue until green.
5. **Review the gap audit.** Address critical and high-severity gaps before moving to the next stage.
6. **Use the monetization roadmap.** Do not monetize until Version 1.0 is stable.
7. **Target the three milestones.** MVP, Version 1.0, and Enterprise Edition are the key checkpoints.

---

# 5747475 5747U5 — 15 M1551NG F157UR35

## The 15 Missing Features (From User Feedback)

These features were identified as missing from the original plan and must be incorporated into Version 1.0:

| # | Feature | Description | Priority | Stage |
|---|---------|-------------|----------|-------|
| 1 | **Guided Setup Wizard** | Step-by-step onboarding wizard that walks new users through connecting providers, uploading contacts, creating first campaign, and launching. Shows progress, explains each step in plain language, and provides a readiness check before proceeding. | Critical | Stage 1 |
| 2 | **Readiness Score** | A percentage score (0-100%) that shows how ready the system is to run a campaign. Checks: providers connected, assets uploaded, contacts loaded, templates configured, rules set, and launch review completed. | Critical | Stage 3 |
| 3 | **Dependency Checker** | Validates that all dependencies for a campaign are met before launch. Checks: provider connectivity, asset availability, contact list validity, template completeness, and configuration correctness. | Critical | Stage 3 |
| 4 | **System Map** | Visual diagram showing all connected providers, their status, and how they relate to campaigns. Shows data flow from upload → campaign → provider → contact. | High | Stage 4 |
| 5 | **Queue Visualization** | Real-time visual representation of the task queue showing pending, running, completed, and failed tasks. Includes queue depth, processing rate, and estimated time to completion. | High | Stage 5 |
| 6 | **Campaign Replay** | Ability to replay a completed campaign with the same configuration but different contacts or updated assets. Useful for recurring campaigns and A/B testing. | High | Stage 6 |
| 7 | **Provider Failover** | Automatic failover when a primary provider goes down. System switches to the next available provider in the priority list and notifies the user. | High | Stage 4 |
| 8 | **Asset Versioning** | Every asset upload creates a new version. Previous versions are archived and can be restored. Full version history with timestamps and change notes. | High | Stage 1 |
| 9 | **Campaign Simulation** | Dry-run mode that simulates a campaign without actually sending messages or making calls. Shows estimated reach, cost, and potential issues before going live. | High | Stage 5 |
| 10 | **Contact Journey** | Visual timeline showing every interaction a contact has had across all channels. Shows calls made, messages sent, emails delivered, and outcomes. | High | Stage 7 |
| 11 | **AI Campaign Builder** | AI-assisted campaign creation. Describe what you want in plain language and the AI generates the campaign configuration, workflow, and templates. | Medium | Stage 8 |
| 12 | **Notification Center** | Centralized notification hub showing all notifications (read and unread), with filtering by type, campaign, and time period. Supports mark-all-read and notification preferences. | High | Stage 1 |
| 13 | **Health Center** | System health dashboard showing CPU, memory, disk, network, provider connectivity, queue depth, and error rates. Alerts when thresholds are exceeded. | High | Stage 7 |
| 14 | **Global Search** | Search across all entities: campaigns, contacts, assets, providers, templates, and logs. Supports filters, sorting, and saved searches. | Medium | Stage 9 |
| 15 | **Command Palette** | Keyboard-accessible command palette (Ctrl+K) for quick navigation, actions, and searches. Similar to VS Code's command palette. | Medium | Stage 7 |
| 16 | **Workspace Navigation** | Sidebar navigation with collapsible sections, recent items, favorites, and quick links. Persistent across all pages. | Medium | Stage 1 |

---

# 30-M0D3L V3RS10N 1.0 F34TUR3 M4TR1X

## Complete Module Matrix for Version 1.0

| # | Module | Stage | Dependencies | Description | Status |
|---|--------|-------|-------------|-------------|--------|
| 1 | **Auth** | 1 | None | User authentication, roles, sessions, MFA | ✅ Built |
| 2 | **Settings** | 1 | None | System-wide configuration engine | ✅ Built |
| 3 | **Database** | 1 | None | PostgreSQL/SQLite, migrations, health monitoring | ✅ Built |
| 4 | **Storage** | 1 | None | File storage, upload/download, validation | ✅ Built |
| 5 | **Logging** | 1 | None | Structured logging, audit trail, log rotation | ✅ Built |
| 6 | **Notifications** | 1 | None | Toast, banner, alert, badge notifications | ✅ Built |
| 7 | **API** | 1 | None | REST API, WebSocket, API keys, rate limiting | ✅ Built |
| 8 | **Task Queue** | 1 | None | Celery + Redis, scheduling, retry, monitoring | ✅ Built |
| 9 | **File Manager** | 1 | Storage, Logging | Upload, validate, preview, version, replace, archive | ✅ Built |
| 10 | **Asset Library** | 1 | File Manager, Storage | Central asset repository, versioning, search | ✅ Built |
| 11 | **Config Engine** | 1 | None | Dynamic configuration, versioning, rollback, secrets | ✅ Built |
| 12 | **Campaigns** | 5 | Database, Contacts, Assets, Providers | Campaign CRUD, state machine, execution engine | 🔲 Stub |
| 13 | **Contacts** | 2 | Database, File Manager | Contact CRUD, lists, validation, segmentation | 🔲 Stub |
| 14 | **Providers** | 4 | Database, Config Engine | Provider connections, health checks, failover | 🔲 Stub |
| 15 | **Upload Center** | 3 | File Manager, Asset Library, Contacts | Multi-file upload with validation and preview | 🔲 Stub |
| 16 | **Workflow Builder** | 6 | Campaigns, Event Bus | Visual drag-and-drop workflow editor | 🔲 Stub |
| 17 | **Live Operations** | 7 | Campaigns, Event Bus, Notifications | Mission Control dashboard, real-time updates | 🔲 Stub |
| 18 | **AI Layer** | 8 | Campaigns, Analytics, Event Bus | Tomoe, Hermes, Oracle AI assistants | 🔲 Stub |
| 19 | **Scheduling** | 9 | Campaigns, Task Queue | One-time and recurring campaign scheduling | 🔲 Stub |
| 20 | **Permissions & Teams** | 9 | Auth | RBAC, team management, campaign-level permissions | 🔲 Stub |
| 21 | **Audit System** | 9 | Auth, Logging | Audit trail, compliance reports, retention | 🔲 Stub |
| 22 | **Exports & Reporting** | 9 | Campaigns, Analytics | CSV, Excel, PDF exports, scheduled reports | 🔲 Stub |
| 23 | **Guided Setup Wizard** | 1 | Auth, Settings | Step-by-step onboarding wizard | 🔲 New |
| 24 | **Readiness Score** | 3 | Upload Center, Providers | Campaign readiness percentage score | 🔲 New |
| 25 | **Dependency Checker** | 3 | Upload Center, Providers | Pre-launch dependency validation | 🔲 New |
| 26 | **System Map** | 4 | Providers | Visual provider/campaign data flow diagram | 🔲 New |
| 27 | **Queue Visualization** | 5 | Task Queue, Campaigns | Real-time queue monitoring dashboard | 🔲 New |
| 28 | **Campaign Replay** | 6 | Campaigns | Replay completed campaigns with new data | 🔲 New |
| 29 | **Contact Journey** | 7 | Contacts, Campaigns | Visual contact interaction timeline | 🔲 New |
| 30 | **Health Center** | 7 | Task Queue, Providers | System health monitoring and alerting | 🔲 New |

### Additional Modules (Planned for V1.1+)

| # | Module | Planned For | Description |
|---|--------|-------------|-------------|
| 31 | **Global Search** | V1.1 | Cross-entity search with filters and saved searches |
| 32 | **Command Palette** | V1.1 | Keyboard-accessible command palette (Ctrl+K) |
| 33 | **Workspace Navigation** | V1.1 | Sidebar navigation with recent items and favorites |
| 34 | **AI Campaign Builder** | V1.1 | AI-assisted campaign creation from natural language |
| 35 | **Notification Center** | V1.1 | Centralized notification hub with filtering |

---

## Version 1.0 Frozen Spec

### UI/UX Design Bible

**Design Tokens:**
- Background: `#050505`
- Card: `#101418`
- Border: `#1CEFFF`
- Accent: `#00E5FF`
- Warning: `#FFAA00`
- Danger: `#FF3366`
- Success: `#00FF99`
- Purple: `#7B2EFF`

**Typography Rules:**
- Headers: Cyber styling (neon, terminal font)
- Body text: Normal, readable sans-serif
- Buttons: Normal text, cyber border on hover
- Status labels: Cyber styling with color coding
- Logs, phone numbers, error messages, config names, file names: Normal text

**Status Colors:**
- Gray: Not started
- Blue: Preparing
- Cyan: Connecting
- Green: Running
- Yellow: Waiting
- Orange: Retrying
- Purple: Transferring
- Red: Failed
- White: Finished

**Component Library:**
- Cards as primary UI containers
- Progress bars for multi-step processes
- Color-coded status indicators
- Plain-language event feed
- Cyber styling only on headers and status labels
- All interactive elements use normal, readable text

### Backend Architecture Bible

**Framework Stack:**
- Python 3.11+ with type hints
- Flask + Flask-SocketIO for web layer
- SQLAlchemy for database ORM
- Celery + Redis for background task queue
- Flask-Login for authentication
- Flask-Migrate for database migrations
- Flask-WTF for forms
- Flask-RESTful for API endpoints

**Architecture Patterns:**
- Application factory pattern (`create_app()`)
- Single Flask initialization — no duplicates
- Blueprint-based modular routing
- Service layer for business logic
- Repository pattern for data access
- Event bus for real-time communication
- REST API + WebSocket for automation

**Coding Standards:**
- Type hints on all public functions
- Docstrings on every public class and function
- snake_case for variables, PascalCase for classes, SCREAMING_SNAKE_CASE for constants
- render_template() instead of render_template_string() or manual string replacement
- All user-facing text in plain English
- All technical terms translated to plain language in UI

### Database Schema

**Core Tables:**
- `users` — id, email, name, role, status, mfa_enabled, created_at, last_login_at
- `roles` — id, name, permissions, description
- `campaigns` — id, name, type, status, created_at, started_at, finished_at, created_by, settings, results
- `campaign_templates` — id, campaign_id, name, category, settings, audio_ids, template_ids
- `campaign_runs` — id, campaign_id, run_number, status, started_at, finished_at, total_contacts, success_count, failed_count, cost, duration
- `contacts` — id, first_name, last_name, phone, email, company, tags, consent_status, consent_date, language, timezone, notes, created_at, updated_at, interaction_history
- `contact_lists` — id, name, source, contact_ids, total_count, valid_count, duplicate_count, invalid_count, blocked_count, created_at, updated_at
- `assets` — id, name, type, subtype, file_path, file_size, file_format, version, versions, tags, created_by, created_at, updated_at, metadata
- `providers` — id, name, type, provider_type, status, credentials, connection_params, priority, health_status, last_health_check, failover_provider_id, rate_limit, created_at, updated_at
- `connections` — id, provider_id, status, connected_at, disconnected_at, last_used_at, health_check_result, latency_ms, error_message
- `messages` — id, campaign_run_id, contact_id, channel, provider_id, status, status_history, content, template_id, attachments, sent_at, delivered_at, opened_at, clicked_at, replied_at, error_message, cost
- `calls` — id, campaign_run_id, contact_id, provider_id, status, status_history, caller_id, duration_seconds, intro_asset_id, hold_asset_id, agent_connect_asset_id, outro_asset_id, voicemail_asset_id, press1_detected, transferred_to, recording_url, sent_at, answered_at, completed_at, cost
- `conversations` — id, contact_id, campaign_run_id, messages, calls, status, started_at, ended_at, outcome, summary, next_action
- `workflows` — id, name, campaign_type, steps, created_by, created_at, updated_at
- `rules` — id, workflow_id, name, condition, action, delay_seconds, max_retries, priority
- `triggers` — id, workflow_id, event_type, condition, action_id
- `actions` — id, workflow_id, name, action_type, parameters
- `events` — id, event_type, entity_type, entity_id, data, timestamp, processed
- `notifications` — id, user_id, type, title, message, read, created_at, action_url
- `analytics` — id, campaign_run_id, channel, metric, value, metadata, timestamp
- `stored_files` — id, name, path, size, type, version, created_by, created_at
- `config_entries` — id, key, value, environment, version, created_at
- `audit_logs` — id, user_id, action, entity_type, entity_id, details, timestamp, ip_address

### API Specification

**Authentication:**
- `POST /api/auth/login` — Login with email/password
- `POST /api/auth/logout` — Logout
- `POST /api/auth/register` — Register new user
- `GET /api/auth/me` — Get current user
- `POST /api/auth/refresh` — Refresh session

**Campaigns:**
- `GET /api/campaigns` — List campaigns
- `POST /api/campaigns` — Create campaign
- `GET /api/campaigns/{id}` — Get campaign details
- `PUT /api/campaigns/{id}` — Update campaign
- `DELETE /api/campaigns/{id}` — Delete campaign
- `POST /api/campaigns/{id}/launch` — Launch campaign
- `POST /api/campaigns/{id}/pause` — Pause campaign
- `POST /api/campaigns/{id}/stop` — Stop campaign
- `GET /api/campaigns/{id}/runs` — Get campaign runs
- `GET /api/campaigns/{id}/report` — Get campaign report

**Contacts:**
- `GET /api/contacts` — List contacts
- `POST /api/contacts` — Create contact
- `GET /api/contacts/{id}` — Get contact details
- `PUT /api/contacts/{id}` — Update contact
- `DELETE /api/contacts/{id}` — Delete contact
- `POST /api/contacts/upload` — Upload contact list

**Providers:**
- `GET /api/providers` — List providers
- `POST /api/providers` — Connect provider
- `GET /api/providers/{id}` — Get provider details
- `PUT /api/providers/{id}` — Update provider
- `DELETE /api/providers/{id}` — Disconnect provider
- `POST /api/providers/{id}/test` — Test provider connection
- `POST /api/providers/{id}/reconnect` — Reconnect provider

**Assets:**
- `GET /api/assets` — List assets
- `POST /api/assets/upload` — Upload asset
- `GET /api/assets/{id}` — Get asset details
- `DELETE /api/assets/{id}` — Delete asset
- `POST /api/assets/{id}/version` — Create new version

**Files:**
- `POST /api/files/upload` — Upload file
- `GET /api/files/{id}` — Get file
- `DELETE /api/files/{id}` — Delete file
- `GET /api/files/{id}/versions` — Get version history

**Notifications:**
- `GET /api/notifications` — List notifications
- `POST /api/notifications/{id}/read` — Mark as read
- `POST /api/notifications/read-all` — Mark all as read

**Analytics:**
- `GET /api/analytics/campaigns` — Campaign analytics
- `GET /api/analytics/providers` — Provider analytics
- `GET /api/analytics/system` — System health metrics

### Testing & QA Plan

**Test Levels:**
| Level | Description | Frequency |
|-------|-------------|-----------|
| Unit Tests | Individual functions and methods | After each module |
| Integration Tests | Module-to-module interactions | After each stage |
| UI Tests | User interface flows and validation | Before each stage ships |
| Load Tests | Performance under concurrent usage | Before production |
| Manual Tests | Human verification of all user flows | Before each stage ships |
| Beta | Limited user testing with real data | Before production release |
| Production | Full deployment with monitoring | Final step |

**Per-Module Testing:** Each module must have its own unit test file in `tests/unit/` before integration testing begins.

**CI/CD Pipeline:**
| Trigger | Action |
|---------|--------|
| On commit | Run linter (flake8, black, isort) |
| On commit | Run type checker (mypy) |
| On commit | Run unit tests |
| On PR | Run integration tests |
| On PR | Run UI tests |
| On merge to main | Run load tests |
| On release | Run full test suite |
| On deploy | Run migration scripts |
| On deploy | Health check all services |

### Release Roadmap

| Phase | Milestone | Timeline | Deliverables |
|-------|-----------|----------|-------------|
| Phase 1 | Code Modernization | Week 1-2 | Refactored modular app, all tests passing |
| Phase 2 | New UI | Week 3-4 | Dashboard, upload center, provider center |
| Phase 3 | New Architecture | Week 5-6 | Event bus, workflow engine, campaign engine |
| Phase 4 | Implement All Modules | Week 7-12 | All 30 modules built and tested |
| Phase 5 | Version 1.0 Release | Week 13 | Full feature set, documentation, production deployment |

**Version 1.0 Definition:**
- All 30 modules built and tested
- All tests passing (unit, integration, UI, load)
- Documentation complete
- Support processes established
- Production deployment with monitoring
- Beta testing with real data completed
- User feedback incorporated

---

