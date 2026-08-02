# 57R337 $M4R7 NYC — Version 1.0 Frozen Spec

## Frozen: 2026-08-01

This document defines the Version 1.0 specification. It is frozen — no changes without a formal change request.

---

## 1. UI/UX Design Bible

### Design Tokens

| Token | Value |
|-------|-------|
| Background | `#050505` |
| Card | `#101418` |
| Border | `#1CEFFF` |
| Accent | `#00E5FF` |
| Warning | `#FFAA00` |
| Danger | `#FF3366` |
| Success | `#00FF99` |
| Purple | `#7B2EFF` |

### Typography Rules

- **Headers**: Cyber styling (neon, terminal font)
- **Body text**: Normal, readable sans-serif
- **Buttons**: Normal text, cyber border on hover
- **Status labels**: Cyber styling with color coding
- **Logs, phone numbers, error messages, config names, file names**: Normal text

### Status Colors

| Color | Meaning |
|-------|---------|
| Gray | Not started |
| Blue | Preparing |
| Cyan | Connecting |
| Green | Running |
| Yellow | Waiting |
| Orange | Retrying |
| Purple | Transferring |
| Red | Failed |
| White | Finished |

### Component Library

- Cards as primary UI containers
- Progress bars for multi-step processes
- Color-coded status indicators
- Plain-language event feed
- Cyber styling only on headers and status labels
- All interactive elements use normal, readable text

---

## 2. Backend Architecture Bible

### Framework Stack

- Python 3.11+ with type hints
- Flask + Flask-SocketIO for web layer
- SQLAlchemy for database ORM
- Celery + Redis for background task queue
- Flask-Login for authentication
- Flask-Migrate for database migrations
- Flask-WTF for forms
- Flask-RESTful for API endpoints

### Architecture Patterns

- Application factory pattern (`create_app()`)
- Single Flask initialization — no duplicates
- Blueprint-based modular routing
- Service layer for business logic
- Repository pattern for data access
- Event bus for real-time communication
- REST API + WebSocket for automation

### Coding Standards

- Type hints on all public functions
- Docstrings on every public class and function
- snake_case for variables, PascalCase for classes, SCREAMING_SNAKE_CASE for constants
- `render_template()` instead of `render_template_string()` or manual string replacement
- All user-facing text in plain English
- All technical terms translated to plain language in UI

---

## 3. Database Schema

### Core Tables

| Table | Key Fields |
|-------|-----------|
| `users` | id, email, name, role, status, mfa_enabled, created_at, last_login_at |
| `roles` | id, name, permissions, description |
| `campaigns` | id, name, type, status, created_at, started_at, finished_at, created_by, settings, results |
| `campaign_templates` | id, campaign_id, name, category, settings, audio_ids, template_ids |
| `campaign_runs` | id, campaign_id, run_number, status, started_at, finished_at, total_contacts, success_count, failed_count, cost, duration |
| `contacts` | id, first_name, last_name, phone, email, company, tags, consent_status, consent_date, language, timezone, notes, created_at, updated_at, interaction_history |
| `contact_lists` | id, name, source, contact_ids, total_count, valid_count, duplicate_count, invalid_count, blocked_count, created_at, updated_at |
| `assets` | id, name, type, subtype, file_path, file_size, file_format, version, versions, tags, created_by, created_at, updated_at, metadata |
| `providers` | id, name, type, provider_type, status, credentials, connection_params, priority, health_status, last_health_check, failover_provider_id, rate_limit, created_at, updated_at |
| `connections` | id, provider_id, status, connected_at, disconnected_at, last_used_at, health_check_result, latency_ms, error_message |
| `messages` | id, campaign_run_id, contact_id, channel, provider_id, status, status_history, content, template_id, attachments, sent_at, delivered_at, opened_at, clicked_at, replied_at, error_message, cost |
| `calls` | id, campaign_run_id, contact_id, provider_id, status, status_history, caller_id, duration_seconds, intro_asset_id, hold_asset_id, agent_connect_asset_id, outro_asset_id, voicemail_asset_id, press1_detected, transferred_to, recording_url, sent_at, answered_at, completed_at, cost |
| `conversations` | id, contact_id, campaign_run_id, messages, calls, status, started_at, ended_at, outcome, summary, next_action |
| `workflows` | id, name, campaign_type, steps, created_by, created_at, updated_at |
| `rules` | id, workflow_id, name, condition, action, delay_seconds, max_retries, priority |
| `triggers` | id, workflow_id, event_type, condition, action_id |
| `actions` | id, workflow_id, name, action_type, parameters |
| `events` | id, event_type, entity_type, entity_id, data, timestamp, processed |
| `notifications` | id, user_id, type, title, message, read, created_at, action_url |
| `analytics` | id, campaign_run_id, channel, metric, value, metadata, timestamp |
| `stored_files` | id, name, path, size, type, version, created_by, created_at |
| `config_entries` | id, key, value, environment, version, created_at |
| `audit_logs` | id, user_id, action, entity_type, entity_id, details, timestamp, ip_address |

---

## 4. API Specification

### Authentication

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/auth/login` | Login with email/password |
| POST | `/api/auth/logout` | Logout |
| POST | `/api/auth/register` | Register new user |
| GET | `/api/auth/me` | Get current user |
| POST | `/api/auth/refresh` | Refresh session |

### Campaigns

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/campaigns` | List campaigns |
| POST | `/api/campaigns` | Create campaign |
| GET | `/api/campaigns/{id}` | Get campaign details |
| PUT | `/api/campaigns/{id}` | Update campaign |
| DELETE | `/api/campaigns/{id}` | Delete campaign |
| POST | `/api/campaigns/{id}/launch` | Launch campaign |
| POST | `/api/campaigns/{id}/pause` | Pause campaign |
| POST | `/api/campaigns/{id}/stop` | Stop campaign |
| GET | `/api/campaigns/{id}/runs` | Get campaign runs |
| GET | `/api/campaigns/{id}/report` | Get campaign report |

### Contacts

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/contacts` | List contacts |
| POST | `/api/contacts` | Create contact |
| GET | `/api/contacts/{id}` | Get contact details |
| PUT | `/api/contacts/{id}` | Update contact |
| DELETE | `/api/contacts/{id}` | Delete contact |
| POST | `/api/contacts/upload` | Upload contact list |

### Providers

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/providers` | List providers |
| POST | `/api/providers` | Connect provider |
| GET | `/api/providers/{id}` | Get provider details |
| PUT | `/api/providers/{id}` | Update provider |
| DELETE | `/api/providers/{id}` | Disconnect provider |
| POST | `/api/providers/{id}/test` | Test provider connection |
| POST | `/api/providers/{id}/reconnect` | Reconnect provider |

### Assets

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/assets` | List assets |
| POST | `/api/assets/upload` | Upload asset |
| GET | `/api/assets/{id}` | Get asset details |
| DELETE | `/api/assets/{id}` | Delete asset |
| POST | `/api/assets/{id}/version` | Create new version |

### Files

| Method | Endpoint | Description |
|--------|----------|-------------|
| POST | `/api/files/upload` | Upload file |
| GET | `/api/files/{id}` | Get file |
| DELETE | `/api/files/{id}` | Delete file |
| GET | `/api/files/{id}/versions` | Get version history |

### Notifications

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/notifications` | List notifications |
| POST | `/api/notifications/{id}/read` | Mark as read |
| POST | `/api/notifications/read-all` | Mark all as read |

### Analytics

| Method | Endpoint | Description |
|--------|----------|-------------|
| GET | `/api/analytics/campaigns` | Campaign analytics |
| GET | `/api/analytics/providers` | Provider analytics |
| GET | `/api/analytics/system` | System health metrics |

---

## 5. Component Library

### Web Components (to be built with Tailwind CSS)

| Component | Description |
|-----------|-------------|
| `Card` | Primary UI container with border, background, padding |
| `StatusBadge` | Color-coded status indicator (gray/blue/cyan/green/yellow/orange/purple/red/white) |
| `ProgressBar` | Multi-step progress indicator |
| `EventFeed` | Plain-language event log with timestamps |
| `Toast` | Brief popup notification (auto-dismisses) |
| `Banner` | Persistent yellow/amber warning bar |
| `Alert` | Persistent red bar with sound option |
| `Badge` | Red circle with number for unread counts |
| `ProviderCard` | Provider status card with connect/test/reconnect |
| `UploadCard` | Drag-and-drop upload zone with preview |
| `CampaignCard` | Campaign status card with progress |
| `ContactRow` | Contact entry with status color |
| `CallDetail` | Individual call/message detail panel |
| `AIMessage` | AI assistant message bubble |
| `CommandPalette` | Keyboard-accessible command palette (Ctrl+K) |
| `Sidebar` | Navigation sidebar with collapsible sections |

---

## 6. Testing & QA Plan

### Test Levels

| Level | Description | Frequency |
|-------|-------------|-----------|
| Unit Tests | Individual functions and methods | After each module |
| Integration Tests | Module-to-module interactions | After each stage |
| UI Tests | User interface flows and validation | Before each stage ships |
| Load Tests | Performance under concurrent usage | Before production |
| Manual Tests | Human verification of all user flows | Before each stage ships |
| Beta | Limited user testing with real data | Before production release |
| Production | Full deployment with monitoring | Final step |

### CI/CD Pipeline

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

---

## 7. Release Roadmap

| Phase | Milestone | Timeline | Deliverables |
|-------|-----------|----------|-------------|
| Phase 1 | Code Modernization | Week 1-2 | Refactored modular app, all tests passing |
| Phase 2 | New UI | Week 3-4 | Dashboard, upload center, provider center |
| Phase 3 | New Architecture | Week 5-6 | Event bus, workflow engine, campaign engine |
| Phase 4 | Implement All Modules | Week 7-12 | All 30 modules built and tested |
| Phase 5 | Version 1.0 Release | Week 13 | Full feature set, documentation, production deployment |

### Version 1.0 Definition

- All 30 modules built and tested
- All tests passing (unit, integration, UI, load)
- Documentation complete
- Support processes established
- Production deployment with monitoring
- Beta testing with real data completed
- User feedback incorporated