from collections.abc import Sequence
from datetime import datetime
from typing import Protocol
from uuid import UUID

from github_sentinel.domain.entities import Delivery, Report, RepositoryEvent, Subscription


class SubscriptionRepository(Protocol):
    def save(self, subscription: Subscription) -> Subscription: ...

    def get(self, subscription_id: UUID) -> Subscription | None: ...

    def list(self) -> Sequence[Subscription]: ...

    def delete(self, subscription_id: UUID) -> bool: ...


class EventRepository(Protocol):
    def save_unique(self, events: Sequence[RepositoryEvent]) -> Sequence[RepositoryEvent]: ...

    def list_for_period(
        self,
        subscription_id: UUID,
        period_start: datetime,
        period_end: datetime,
    ) -> Sequence[RepositoryEvent]: ...


class ReportRepository(Protocol):
    def save(self, report: Report) -> Report: ...

    def get(self, report_id: UUID) -> Report | None: ...

    def list(self) -> Sequence[Report]: ...


class DeliveryRepository(Protocol):
    def save(self, delivery: Delivery) -> Delivery: ...
