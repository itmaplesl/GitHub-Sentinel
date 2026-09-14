# Changelog

All notable changes to GitHub Sentinel are documented in this file.

## [0.0.1] - 2026-09-14

### Added

- Modular monolith architecture with ports and adapters.
- Subscription CRUD API with daily and weekly schedules.
- Domain models for repository events, reports, and deliveries.
- Event deduplication and report idempotency foundations.
- Manual synchronization and report-generation endpoints.
- Rule-based summary fallback for environments without an AI provider.
- Optional API key authentication and health-check endpoints.
- In-memory repositories for local development and integration testing.
- Docker Compose configuration, development tooling, and project documentation.

### Known limitations

- The GitHub client is a no-op adapter and does not fetch live repository data yet.
- Application data is held in memory and is cleared when the process restarts.
- Webhook delivery is a non-networking logging adapter; email delivery is not implemented.
- PostgreSQL persistence, Celery scheduling, and production notifications are planned for later releases.

[0.0.1]: https://github.com/itmaplesl/GitHub-Sentinel/releases/tag/v0.0.1
