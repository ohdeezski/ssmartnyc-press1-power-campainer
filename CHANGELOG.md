# Changelog

All notable changes to this project will be documented in this file.

The format is based on [Keep a Changelog](https://keepachangelog.com/en/1.0.0/),
and this project adheres to [Semantic Versioning](https://semver.org/spec/v2.0.0.html).

## [Unreleased]

### Added
- Initial project scaffold with modular Flask architecture
- 11 Stage 1 Foundation modules (auth, config, database, storage, logging, notifications, API, task queue, file manager, asset library, config engine)
- Dependency-based staging plan (Stage 0-9)
- Cyber styling UI with Street Smart NYC branding
- Version 1.0 frozen spec with 30-module feature matrix
- 15 missing features identified and incorporated (Guided Setup Wizard, Readiness Score, Dependency Checker, System Map, Queue Visualization, Campaign Replay, Provider Failover, Asset Versioning, Campaign Simulation, Contact Journey, AI Campaign Builder, Notification Center, Health Center, Global Search, Command Palette, Workspace Navigation)
- CI/CD pipeline (GitHub Actions)
- Docker Compose with Redis/Celery/PostgreSQL
- Static assets (CSS, JS)

### Changed
- Refactored from monolithic Flask app (9864 lines, 5 duplicate Flask inits) to modular architecture (990 lines, single init)
- Removed duplicate template files
- Removed 10 empty stub modules

## [0.1.0] - 2026-08-01

### Added
- Initial project structure
- Flask app factory with single initialization
- SQLAlchemy database setup
- Auth module with login/register
- Storage module with file management
- Logging module with structured logging
- Notifications module
- API module with REST endpoints
- Task queue module with Celery
- File manager module
- Asset library module
- Configuration engine module
- UI module with dashboard, upload center, providers, campaigns, settings, notifications pages
- Test suite (2/2 passing)
