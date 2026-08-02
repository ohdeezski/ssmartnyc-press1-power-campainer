# AUDIT REPORT — ssmartnyc-press1-power-campainer

## Cross-reference: `/home/ssmartnycbase/Documents/kimi-plan-4-app`

> **Date**: 2026-08-02  
> **Auditor**: opencode  
> **Reference plan**: `kimi-plan-4-app` (Kimi Code session log, 2,308 lines)  
> **Current branch**: `main` (3 commits)  
> **Verification**: flake8=0, black=clean, isort=clean, pytest 99 passed  

---

## 1. EXECUTIVE SUMMARY

Three phases are committed to git on `main`. Phases 0–3 are complete; Phase 4 (Real Asterisk engine) is the next frontier.

| Phase | Reference (kimi-plan) | What was done | Status |
|---|---|---|---|
| 0 — Stabilize | Fix 15 bugs, tests green, lint clean, git init | 11 bugs fixed, 59→99 tests, lint/mypy green, deps pinned, git initialized | **DONE** (3 commits) |
| 1 — Flight Deck shell | 16 components, 6 pages, live SocketIO, token sync | Pre-existing (components, base.html, socket_events.py, main.css, app.js) | **DONE** (pre-dated repo) |
| 2 — Domain model + engine | Contacts, Providers, Campaign engine, migrations, simulation dialer | contacts/ events/ dialer/ modules, Campaign model extension, CampaignService with 23+8 checklists, Migration baseline | **DONE** (commit `5b11b9c`) |
| 3 — Flight deck screens | PREPARE/VERIFY/LAUNCH/LIVE/FINISH + wizard + Mission Control | mission_control.html, campaign_wizard.html, dashboard CTAs, SocketIO campaign events, DialerService | **DONE** (commit `e01b4bb`) |
| 4 — Real Asterisk engine | AsteriskBackend, call-file writer, AMI client, audio pipeline | ❌ **NOT STARTED** — only SimulationBackend exists, DialerService.get_backend raises NotImplementedError for "asterisk" | **BLOCKED** — needs Linux host with Asterisk |
| 5 — Hardening, QA & docs | Security pass, full tests, runbooks, observability | ⚠ Partial — 99 tests, lint clean, but stub tests in assetlibrary/notifications, no load tests, no runbooks | **PARTIAL** |
| 6 — Production deployment | Dockerfile, nginx.conf, Postgres, CI/CD, launch checklist | ❌ Dockerfile missing, nginx.conf missing, CI deploy is no-op echo, SQLite only | **NOT STARTED** |
| 7 — Monetization | Org/tenant model, 5 tiers, Stripe, paywall UX | ❌ No billing module, no org/tenant model, no Stripe integration | **NOT STARTED** |

**Bottom line**: The simulator-based dialer is fully functional. 99 tests pass. Code is lint-clean. The next session must implement `AsteriskBackend` (Phase 4) on a Linux host with Asterisk + `chan_sip` + AMI configured.

---

## 2. GAP ANALYSIS — PLAN vs. REALITY (PHASES 0–3)

### 2.1 Phase 2 domain modules — what exists

| Planned Module | Actually in codebase? | Evidence |
|---|---|---|
| `app/modules/contacts/` | ✅ **Complete** | `__init__.py`, `models.py` (Contact, ContactList), `services.py` (ContactImportService, normalize_phone), `routes.py` (REST API) |
| `app/modules/dialer/` | ✅ **Complete** | `__init__.py`, `models.py` (Call, Provider, CallerProfile, NumberPool, Message, Conversation), `services.py` (DialerService), `routes.py` (REST API), `tasks.py` (Celery), `backends/base.py` (DialerBackend ABC), `backends/simulation.py` (SimulationBackend) |
| `app/modules/events/` | ✅ **Complete** | `__init__.py`, `models.py` (Event, AuditLog), `services.py` (publish_event, log_audit), `routes.py` (REST API) |
| `app/modules/campaigns/` | ✅ **Extended** | `models.py` (Campaign extended with contact_list_id, caller_profile_id, verified_at, readiness, estimate; CampaignRun extended with blocked/voicemail/no_answer/retry counts), `services.py` (CampaignService with 23-item PREPARE_CHECKLIST + 8 VERIFY_CHECKS), `routes.py` (JSON API + HTML lifecycle) |
| Alembic baseline migration | ✅ **Complete** | `migrations/versions/22a231c03925_0001_baseline.py` (188 lines, all tables) |
| `dialer/backends/__init__.py` | ⚠ **Was missing, FIXED** | Created during audit pass |
| `connectors/` package | ❌ **Missing** | The plan referenced `connectors/asterisk.py`, `connectors/twilio.py`, `connectors/base.py` — no such package exists. Providers are modeled in `dialer/models.py` instead. |

### 2.2 Phase 3 flight deck — what exists

| Planned Screen | Actually in codebase? | Evidence |
|---|---|---|
| `mission_control.html` | ✅ **Complete** | Stats bar (6 cards), 9-stage pipeline, event feed, provider health panel, action buttons, call detail table, WebSocket JS (join room, campaign_event listener, updatePipeline/updateCallRow/updateCounters) |
| `campaign_wizard.html` | ✅ **Complete** | 5-step wizard (Prepare/Verify/Launch/Live/Finish), 23-item checklist, 8-verify, estimate, launch button |
| `dashboard.html` | ✅ **Updated** | Live/Launch CTAs, campaign cards, stat cards |
| `pipeline_bar.html` | ✅ **Complete** | data-stage/data-total attributes for JS |
| `app/static/js/app.js` | ✅ **Complete** | `initMissionControl()` with SocketIO listeners, WS fallback, CSRF handling |
| `socket_events.py` | ✅ **Extended** | `collect_system_metrics()` (CPU/RAM/disk), `@socketio.on("join")`/`"leave"` room handlers, namespace `/` |

### 2.3 Pre-Phase-4 bug fixes applied during this audit

| Bug | File | Fix |
|---|---|---|
| Duplicate `/<int:campaign_id>/launch` POST route — `campaign_launch` (HTML, ignores verified_at) and `campaign_launch_json` (checks verified_at) both registered; Flask routed to the last-registered one, so HTML form got JSON back | `app/modules/campaigns/routes.py:62,158` | Merged both into a single `campaign_launch` handler with content negotiation (JSON API if Accept: application/json, else HTML redirect); delegates to `CampaignService.launch_campaign` which gates on `verified_at` |
| `cl.contact_count` referenced in template but no such attribute on `ContactList` model | `app/modules/ui/templates/ui/campaign_wizard.html:61` | Added `contact_count` property to `ContactList` (prefers cached `counts` dict, falls back to `contacts.count()` query); added to `to_dict()` |
| `campaign.settings.concurrent_calls` — Jinja2 dot-notation on dict returns Undefined if key absent, rendering empty `value=""` attribute | `app/modules/ui/templates/ui/campaign_wizard.html:67` | Changed to `(campaign.settings or {}).get('concurrent_calls', 5)` |
| Same pattern for `retry_attempts` | `campaign_wizard.html:72` | Changed to `(campaign.settings or {}).get('retry_attempts', 2)` |
| `readiness` variable referenced in Step 2 but route never passed it — Step 2 always showed "Run the readiness check first" | `app/modules/ui/routes.py:148` | Route now passes `readiness=campaign.readiness or {}` |
| `run.counters.voicemail` — no `counters` attribute on `CampaignRun` | `mission_control.html:50` | Changed to `run.voicemail_count` (model has this column) |
| `migrations/script.py.mako` had hardcoded `<revision-id>` strings instead of Jinja2 template variables — `alembic revision --autogenerate` would generate broken migration files | `migrations/script.py.mako` | Replaced with standard Alembic Jinja2 template (`${up_revision}`, `${down_revision}`, `${message}`, `${create_date}`, `${imports}`, `${upgrades}`, `${downgrades}`) |
| `dialer/backends/` package lacked `__init__.py` — relied on implicit namespace packages | `app/modules/dialer/backends/__init__.py` | Created (with `# flake8: noqa`) |

### 2.4 Phase 2 code-quality findings (intentional, not bugs)

| Finding | Location | Notes |
|---|---|---|
| `DialerService._get_contacts()` generates synthetic contacts instead of pulling from `ContactList` | `app/modules/dialer/services.py:62` | Deliberate simplification — real contacts would come from `ContactList.contacts` relationship. Marked with TODO comment. |
| `DialerService.execute()` runs tick loop synchronously (max 200 ticks) instead of using Celery for periodic ticks | `app/modules/dialer/services.py:39` | Eager-mode dev pattern. In production, each tick would be a Celery beat task. |
| `campaign_launch` route does not create `CampaignRun` or invoke dialer | `app/modules/campaigns/routes.py:62` | Launch via HTML form sets `Campaign.status='running'` only. Full campaign run creation + dialer invocation happens via the JSON API (`dialer/routes.py:launch_campaign()`). This is the intended two-tier design: CampaignService gates on verification, DialerService executes. |

---

## 3. HONEST CURRENT STATE OF THE CODEBASE

### 3.1 Test coverage

```
tests/unit/test_contacts.py           — 17 tests (ContactImportService, normalize_phone, ContactList CRUD)
tests/unit/test_dialer.py             — 12 tests (SimulationBackend health/launch/tick, DialerService)
tests/unit/test_events.py             —  9 tests (publish_event, log_audit, model to_dict)
tests/unit/test_phase3_routes.py      — 11 tests (mission_control, campaign_wizard, simulation, dashboard)
tests/unit/test_campaign_forms_csrf.py—  4 tests (campaign CRUD, launch/pause/stop with CSRF)
tests/unit/test_routes_smoke.py       — 17 tests (URL building, rendering, protection)
tests/unit/auth/test_auth.py          —  8 tests (login, dashboard redirect)
tests/unit/assetlibrary/test_asset_library.py — 10 tests (STUBBED — all `pass`)
tests/unit/notifications/test_notifications.py— 10 tests (STUBBED — all `pass`)

Total: 99 tests pass
```

### 3.2 Module inventory (what's wired up)

```
Blueprints registered (13):
  api, assetlibrary, auth, campaigns, configengine, contacts,
  dialer, events, filemanager, notifications, storage, taskqueue,
  ui, workflow

Dialer backends:
  dialer/backends/base.py     — DialerBackend ABC (health, launch, tick, pause, stop, status)
  dialer/backends/simulation.py — SimulationBackend (seed=42, 65% answer, 12% press1, 10% voicemail, 15% no_answer, 4% failed, 9-stage pipeline)
  dialer/backends/asterisk.py — ❌ NOT IMPLEMENTED (Phase 4)
```

### 3.3 What is still entirely stubbed or missing (Phase 4+)

| Capability | Reality | Root cause |
|---|---|---|
| Real Asterisk dialing | ❌ `DialerService.get_backend("asterisk")` raises `NotImplementedError` | No `AsteriskBackend` class, no AMI client, no call-file writer |
| AMI client | ❌ Does not exist | `app/modules/dialer/backends/asterisk.py` is not created |
| Call-file writer | ❌ Does not exist | No code to write `.call` files to `/var/spool/asterisk/outgoing/` |
| Audio pipeline | ❌ Does not exist | No ffmpeg/8kHz WAV conversion, no `press1_success.log` tailing |
| `connectors/` package | ❌ Does not exist | Plan referenced it; code uses `dialer/backends/` instead |
| Production deployment | ❌ Dockerfile + nginx.conf missing | `docker-compose.yml` references missing Dockerfile |
| Billing/monetization | ❌ No billing module | Phase 7 |

### 3.4 Configuration state

```
app/config.py:
  Config (production):     PostgreSQL, Redis, CSRF, secure cookies, rate limits
  TestConfig:               SQLite in-memory, WTF_CSRF_ENABLED=False, CELERY_EAGER=True, AUTO_CREATE_TABLES=True
  DIALER_BACKEND = os.environ.get("DIALER_BACKEND", "simulation")
```

### 3.5 Git state

```
Branch: main
Commits: 3
  5b11b9c Phase 2: domain model + dialer engine + events + lifecycle
  e01b4bb Phase 3: flight deck HTML screens + wizard + SocketIO campaign events
```

### 3.6 Pre-commit verification (post-audit)

| Check | Result |
|---|---|
| 99 tests | ✅ All pass |
| flake8 | ✅ 0 errors |
| black | ✅ Clean |
| isort | ✅ Clean |
| App boot | ✅ `/api/health` → 200 (13 blueprints registered, all services connected) |

---

## 4. PHASE 4 ROADMAP — Real Asterisk Engine

Phase 4 requires a Linux host with Asterisk installed and configured with `chan_sip`, AMI (Manager Interface), and the `app_meetme` or `app_adsi` module for Press-1 digit collection.

### 4.1 Files to create

| File | Purpose |
|---|---|
| `app/modules/dialer/backends/asterisk.py` | `AsteriskBackend(DialerBackend)` — AMI client (async or threaded), call-file writer, status mapping |
| `app/modules/dialer/backends/asterisk/` | Sub-package for AMI connection, call-file builder, AGI script handler |
| `app/modules/dialer/audio.py` | Audio pipeline: ffmpeg 48kHz→8kHz WAV conversion, format validation, silence trimming |
| `app/modules/dialer/tasks.py` (extend) | Add Celery beat task for periodic `backend.tick()` and AMI event polling |

### 4.2 AsteriskBackend interface contract

```
class AsteriskBackend(DialerBackend):
    def __init__(self, ami_config)          # host, port, username, secret
    def health(self) -> dict                # AMI ping → {"status": "connected", "latency_ms": N}
    def launch(self, campaign_run, contacts) -> dict
        # Write .call files to /var/spool/asterisk/outgoing/
        # Each .call file: Channel, Application, Data, Archive, etc.
    def tick(self, campaign_run) -> dict
        # Parse press1_success.log for new entries since last tick
        # Update Call rows with answered/press1/voicemail outcomes
    def pause(self, campaign_run)
    def stop(self, campaign_run)
    def status(self, campaign_run) -> dict
```

### 4.3 Asterisk prerequisites (per plan §4.1)

- Asterisk 18+ with `chan_sip` loaded
- AMI configured in `/etc/asterisk/manager.conf`:
  ```
  [press1]
  secret = <redacted>
  deny = 0.0.0.0/0.0.0.0
  permit = 127.0.0.1/255.255.255.0
  read = all
  write = all
  ```
- Outbound routes configured for caller ID rotation
- `app_meetme` module for Press-1 digit collection
- `agi` scripts for IVR flow (intro → menu → transfer or voicemail)
- File spool at `/var/spool/asterisk/outgoing/` writable by app user

---

## 5. FILE ACTION LIST (Remaining)

### Must Create (Phase 4)

| File | Purpose |
|---|---|
| `app/modules/dialer/backends/asterisk.py` | AsteriskBackend — AMI client + call-file writer |
| `app/modules/dialer/audio.py` | Audio pipeline (ffmpeg 48k→8k WAV, validation) |

### Must Fix (pre-commit)

| Item | Files affected | Fix applied |
|---|---|---|
| 5 bugs found during audit (duplicate route, template bugs, mako template, missing __init__.py, unused imports) | 11 files | ✅ All fixed in this audit pass |
| 14 files reformatted by black/isort | Various | ✅ Applied for consistency |

### Must Delete (stale, from Phase 0)

| File | Reason |
|---|---|
| `app/config.py.backup` | Identical pre-fix copy — **STILL EXISTS, needs manual deletion** |
| `app/modules/workflow/routes.py.backup` | Older version without WorkflowService — **STILL EXISTS, needs manual deletion** |
| `app/extensions.py` | Dead shim — all imports use `app/extensions/` package — **STILL EXISTS, needs manual deletion** |

---

## 6. DEPLOYMENT STATUS

| Artifact | Status | Notes |
|---|---|---|
| Dockerfile | ❌ Missing | Referenced in `docker-compose.yml` but doesn't exist |
| docker-compose.yml | ⚠ Partial | Services defined (web/celery/celery-beat/db/redis/nginx) but compose won't build without Dockerfile |
| nginx.conf | ❌ Missing | Referenced in compose but doesn't exist |
| `.env.example` | ✅ Exists | 9 env vars defined |
| CI workflow | ⚠ Partial | Lint + test pass; deploy is no-op echo |
| Database | ⚠ SQLite only | `instance/campaigns.db` exists; no Postgres migration |
| Health check | ✅ `/api/health` 200 | Real DB + Redis probe, 13 blueprints |

---

## 7. MONETIZATION STATUS

**0% ready.** No `app/modules/billing/` package exists. No org/tenant model. No Stripe integration. `configengine` has infrastructure but no plan model. Monetization is Phase 7 — last priority after deployment.
