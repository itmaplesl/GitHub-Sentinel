from collections.abc import Sequence
from dataclasses import dataclass
from datetime import UTC, datetime, timedelta
from uuid import UUID

from github_sentinel.application.ports.github import GitHubClient
from github_sentinel.application.ports.notifier import Notifier
from github_sentinel.application.ports.repositories import DeliveryRepository, EventRepository
from github_sentinel.application.services.report_service import ReportService
from github_sentinel.application.services.subscription_service import SubscriptionService
from github_sentinel.domain.entities import Delivery, Report
from github_sentinel.domain.enums import ScheduleType


@dataclass(frozen=True, slots=True)
class SyncResult:
    fetched_count: int
    new_event_count: int
    report: Report | None
    deliveries: tuple[Delivery, ...]


class SyncService:
    def __init__(
        self,
        subscriptions: SubscriptionService,
        events: EventRepository,
        reports: ReportService,
        github: GitHubClient,
        delivery_repository: DeliveryRepository,
        notifiers: Sequence[Notifier] = (),
    ) -> None:
        self._subscriptions = subscriptions
        self._events = events
        self._reports = reports
        self._github = github
        self._delivery_repository = delivery_repository
        self._notifiers = notifiers

    def sync(self, subscription_id: UUID, *, until: datetime | None = None) -> SyncResult:
        subscription = self._subscriptions.get(subscription_id)
        if not subscription.enabled:
            return SyncResult(0, 0, None, ())

        period_end = until or datetime.now(UTC)
        default_delta = (
            timedelta(days=1)
            if subscription.schedule_type is ScheduleType.DAILY
            else timedelta(days=7)
        )
        period_start = subscription.last_synced_at or period_end - default_delta
        fetched = tuple(self._github.fetch_events(subscription, period_start, period_end))
        saved = tuple(self._events.save_unique(fetched))

        self._subscriptions.update(subscription.id, last_synced_at=period_end)
        if not saved:
            return SyncResult(len(fetched), 0, None, ())

        report = self._reports.generate(subscription, saved, period_start, period_end)
        deliveries: list[Delivery] = []
        for destination in subscription.notification_channels:
            notifier = next(
                (candidate for candidate in self._notifiers if candidate.supports(destination)),
                None,
            )
            if notifier is None:
                continue
            deliveries.append(self._delivery_repository.save(notifier.deliver(report, destination)))

        return SyncResult(len(fetched), len(saved), report, tuple(deliveries))
