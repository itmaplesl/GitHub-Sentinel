from dataclasses import dataclass
from typing import Annotated, cast

from fastapi import Depends, Header, HTTPException, Request, status

from github_sentinel.application.services.report_service import ReportService
from github_sentinel.application.services.subscription_service import SubscriptionService
from github_sentinel.application.services.sync_service import SyncService
from github_sentinel.config import Settings
from github_sentinel.infrastructure.database.repositories import (
    InMemoryEventRepository,
    InMemoryReportRepository,
)


@dataclass(slots=True)
class Container:
    settings: Settings
    subscriptions: SubscriptionService
    sync: SyncService
    reports: ReportService
    event_repository: InMemoryEventRepository
    report_repository: InMemoryReportRepository


def get_container(request: Request) -> Container:
    return cast(Container, request.app.state.container)


ContainerDependency = Annotated[Container, Depends(get_container)]


def require_api_key(
    container: ContainerDependency,
    x_api_key: Annotated[str | None, Header()] = None,
) -> None:
    expected = container.settings.api_key
    if expected is not None and x_api_key != expected:
        raise HTTPException(
            status_code=status.HTTP_401_UNAUTHORIZED,
            detail="无效的 API Key",
        )


ApiKeyDependency = Annotated[None, Depends(require_api_key)]
