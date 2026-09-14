from fastapi import FastAPI, Request, status
from fastapi.responses import JSONResponse

from github_sentinel import __version__
from github_sentinel.application.services.report_service import ReportService
from github_sentinel.application.services.subscription_service import SubscriptionService
from github_sentinel.application.services.sync_service import SyncService
from github_sentinel.config import Settings, get_settings
from github_sentinel.domain.exceptions import EntityNotFoundError, SentinelError
from github_sentinel.infrastructure.ai.rule_based import RuleBasedSummarizer
from github_sentinel.infrastructure.database.repositories import (
    InMemoryDeliveryRepository,
    InMemoryEventRepository,
    InMemoryReportRepository,
    InMemoryStore,
    InMemorySubscriptionRepository,
)
from github_sentinel.infrastructure.github.client import NoOpGitHubClient
from github_sentinel.infrastructure.notifications.webhook import LoggingWebhookNotifier
from github_sentinel.interfaces.http.dependencies import Container
from github_sentinel.interfaces.http.routes import health, reports, subscriptions


def build_container(settings: Settings) -> Container:
    store = InMemoryStore()
    subscription_repository = InMemorySubscriptionRepository(store)
    event_repository = InMemoryEventRepository(store)
    report_repository = InMemoryReportRepository(store)
    delivery_repository = InMemoryDeliveryRepository(store)
    subscription_service = SubscriptionService(subscription_repository)
    report_service = ReportService(report_repository, RuleBasedSummarizer())
    sync_service = SyncService(
        subscriptions=subscription_service,
        events=event_repository,
        reports=report_service,
        github=NoOpGitHubClient(),
        delivery_repository=delivery_repository,
        notifiers=(LoggingWebhookNotifier(),),
    )
    return Container(
        settings=settings,
        subscriptions=subscription_service,
        sync=sync_service,
        reports=report_service,
        event_repository=event_repository,
        report_repository=report_repository,
    )


def create_app(settings: Settings | None = None) -> FastAPI:
    resolved_settings = settings or get_settings()
    app = FastAPI(
        title=resolved_settings.app_name,
        version=__version__,
        description="定期汇总并推送 GitHub 仓库动态。",
    )
    app.state.container = build_container(resolved_settings)
    app.include_router(health.router)
    app.include_router(subscriptions.router)
    app.include_router(reports.router)

    @app.exception_handler(EntityNotFoundError)
    async def handle_not_found(_: Request, exc: EntityNotFoundError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_404_NOT_FOUND,
            content={"detail": str(exc)},
        )

    @app.exception_handler(SentinelError)
    async def handle_domain_error(_: Request, exc: SentinelError) -> JSONResponse:
        return JSONResponse(
            status_code=status.HTTP_400_BAD_REQUEST,
            content={"detail": str(exc)},
        )

    return app


app = create_app()
