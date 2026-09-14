from collections.abc import Sequence
from datetime import UTC, datetime

from github_sentinel.application.services.report_service import ReportService
from github_sentinel.application.services.subscription_service import SubscriptionService
from github_sentinel.application.services.sync_service import SyncService
from github_sentinel.domain.entities import RepositoryEvent, Subscription
from github_sentinel.domain.enums import EventType, ScheduleType
from github_sentinel.infrastructure.ai.rule_based import RuleBasedSummarizer
from github_sentinel.infrastructure.database.repositories import (
    InMemoryDeliveryRepository,
    InMemoryEventRepository,
    InMemoryReportRepository,
    InMemoryStore,
    InMemorySubscriptionRepository,
)


class FakeGitHubClient:
    def fetch_events(
        self,
        subscription: Subscription,
        since: datetime,
        until: datetime,
    ) -> Sequence[RepositoryEvent]:
        return (
            RepositoryEvent(
                subscription_id=subscription.id,
                github_event_id="release-1",
                event_type=EventType.RELEASE,
                title="v1.0.0",
                url=f"https://github.com/{subscription.repository.full_name}/releases/tag/v1.0.0",
                author="maintainer",
                occurred_at=until,
            ),
        )


def test_sync_generates_one_report_and_deduplicates_repeated_event() -> None:
    store = InMemoryStore()
    subscriptions = SubscriptionService(InMemorySubscriptionRepository(store))
    event_repository = InMemoryEventRepository(store)
    reports = ReportService(InMemoryReportRepository(store), RuleBasedSummarizer())
    sync = SyncService(
        subscriptions=subscriptions,
        events=event_repository,
        reports=reports,
        github=FakeGitHubClient(),
        delivery_repository=InMemoryDeliveryRepository(store),
    )
    subscription = subscriptions.create(
        owner="openai",
        name="openai-python",
        schedule_type=ScheduleType.DAILY,
        timezone="Asia/Shanghai",
        event_types=frozenset({EventType.RELEASE}),
    )
    period_end = datetime(2026, 9, 14, 8, tzinfo=UTC)

    first = sync.sync(subscription.id, until=period_end)
    second = sync.sync(subscription.id, until=period_end)

    assert first.fetched_count == 1
    assert first.new_event_count == 1
    assert first.report is not None
    assert "release 1 条" in first.report.summary
    assert second.fetched_count == 1
    assert second.new_event_count == 0
    assert second.report is None
