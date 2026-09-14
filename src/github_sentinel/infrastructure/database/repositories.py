from collections.abc import Sequence
from datetime import datetime
from threading import RLock
from uuid import UUID

from github_sentinel.domain.entities import Delivery, Report, RepositoryEvent, Subscription


class InMemoryStore:
    """Thread-safe development store shared by the in-memory repositories."""

    def __init__(self) -> None:
        self.lock = RLock()
        self.subscriptions: dict[UUID, Subscription] = {}
        self.events: dict[str, RepositoryEvent] = {}
        self.reports: dict[UUID, Report] = {}
        self.deliveries: dict[UUID, Delivery] = {}


class InMemorySubscriptionRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def save(self, subscription: Subscription) -> Subscription:
        with self._store.lock:
            self._store.subscriptions[subscription.id] = subscription
        return subscription

    def get(self, subscription_id: UUID) -> Subscription | None:
        with self._store.lock:
            return self._store.subscriptions.get(subscription_id)

    def list(self) -> Sequence[Subscription]:
        with self._store.lock:
            return tuple(self._store.subscriptions.values())

    def delete(self, subscription_id: UUID) -> bool:
        with self._store.lock:
            return self._store.subscriptions.pop(subscription_id, None) is not None


class InMemoryEventRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def save_unique(self, events: Sequence[RepositoryEvent]) -> Sequence[RepositoryEvent]:
        saved: list[RepositoryEvent] = []
        with self._store.lock:
            for event in events:
                key = event.deduplication_key
                if key in self._store.events:
                    continue
                self._store.events[key] = event
                saved.append(event)
        return tuple(saved)

    def list_for_period(
        self,
        subscription_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> Sequence[RepositoryEvent]:
        with self._store.lock:
            return tuple(
                event
                for event in self._store.events.values()
                if event.subscription_id == subscription_id
                and period_start <= event.occurred_at <= period_end
            )


class InMemoryReportRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def save(self, report: Report) -> Report:
        with self._store.lock:
            existing = next(
                (
                    item
                    for item in self._store.reports.values()
                    if item.idempotency_key == report.idempotency_key
                ),
                None,
            )
            if existing is not None:
                return existing
            self._store.reports[report.id] = report
        return report

    def get(self, report_id: UUID) -> Report | None:
        with self._store.lock:
            return self._store.reports.get(report_id)

    def list(self) -> Sequence[Report]:
        with self._store.lock:
            return tuple(self._store.reports.values())


class InMemoryDeliveryRepository:
    def __init__(self, store: InMemoryStore) -> None:
        self._store = store

    def save(self, delivery: Delivery) -> Delivery:
        with self._store.lock:
            self._store.deliveries[delivery.id] = delivery
        return delivery
