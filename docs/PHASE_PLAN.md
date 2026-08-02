# Street Smart NYC — Phased Build Plan

Operating mode (per founder directive 2026-08-01):
- Work in PHASES. Each phase has numbered SUBPLANS.
- After a phase completes, run an AUDIT (visual + token/consistency + test gate)
  and get founder sign-off BEFORE the next phase starts.
- No commits, no UI-linter, no deploy until the rendered UI is seen and approved.
- Single source of truth for brand + design tokens, shared web → Android.

---

## PHASE 1 — Web App Design System & Branding  (START HERE)
Goal: a cohesive, platform-consistent visual identity and component system,
applied across every web screen.

- 1.1 Brand Identity Foundation
      - Define dual brand: public "Street Smart NYC" (app-store/marketing safe)
        + internal codename "57R337 $M4R7 NYC" (UI flair).
      - Generate logo concepts (monogram, mascot, wordmark).
      - Lock core palette, typography, iconography, spacing, motion rules.
- 1.2 Design Token System (single source of truth)
      - Centralize tokens: CSS custom properties + Tailwind theme in base.html,
        plus a tokens reference doc. Web and Android both consume these.
- 1.3 Core Component Library
      - Reusable snippets: btn-cyber, card, data table, nav, status badge,
        form field, stat card, pulse indicator, scanline — all token-driven.
- 1.4 Apply to All Web Screens
      - dashboard, campaigns (list/new/edit/detail/report), upload, providers,
        settings, notifications, auth (login/register), errors (404/403/500).
      - Enforce consistency; remove one-off inline colors.
- 1.5 Marketing / Visual Assets
      - favicon, OG image, logo lockups (SVG+PNG), brand guidelines doc.
- 1.6 PHASE 1 AUDIT
      - Screenshot every route; token-consistency grep; contrast check;
        pytest green; founder visual sign-off.

## PHASE 2 — Android Mobile App Design
Goal: same identity, native-feeling mobile layout, token-consistent.

- 2.1 Adapt tokens to Android (Material3 / Compose theme from Phase 1.2).
- 2.2 Generate mobile screens via Stitch MOBILE project
      (15385791371130925331 "Street Smart NYC UI System").
- 2.3 Core mobile components (bottom nav, cards, lists, FAB, status).
- 2.4 Apply to key flows (login, dashboard, campaigns, upload, providers).
- 2.5 PHASE 2 AUDIT — emulator/device screenshots, token parity vs web.

## PHASE 3 — Infrastructure & Deployment (Module 00)
Dockerfile, .dockerignore, gunicorn entrypoint, nginx + ssl, docker-compose
repair, env matrix (.development/.testing/.beta/.production), Cloud Run deploy
script + cloudbuild + health endpoint. AUDIT before ship.

## PHASE 4 — Feature Completion & Hardening
Per-module test suites, API contracts, Celery/Redis wiring, auth roles,
file storage backends, notifications delivery. AUDIT per module.

## PHASE 5 — Launch Readiness
Security pass, performance, docs, runbooks. Final audit.

---
Audit gate rule: every phase ends with EVIDENCE (screenshots / test output /
token diff) and founder approval. No phase overlaps.
