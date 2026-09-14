from collections.abc import Sequence
from dataclasses import replace
from datetime import datetime
from uuid import UUID

from github_sentinel.application.ports.repositories import SubscriptionRepository
from github_sentinel.domain.entities import RepositoryRef, Subscription, utc_now
from github_sentinel.domain.enums import EventType, ScheduleType
from github_sentinel.domain.exceptions import EntityNotFoundError


class SubscriptionService:
    def __init__(self, repository: SubscriptionRepository) -> None:
        self._repository = repository

    def create(
        self,
        *,
        owner: str,
        name: str,
        schedule_type: ScheduleType,
        timezone: str,
        event_types: frozenset[EventType],
        notification_channels: tuple[str, ...] = (),
    ) -> Subscription:
        subscription = Subscription(
            repository=RepositoryRef(owner=owner, name=name),
            schedule_type=schedule_type,
            timezone=timezone,
            event_types=event_types,
            notification_channels=notification_channels,
        )
        return self._repository.save(subscription)

    def get(self, subscription_id: UUID) -> Subscription:
        subscription = self._repository.get(subscription_id)
        if subscription is None:
            raise EntityNotFoundError(f"订阅不存在: {subscription_id}")
        return subscription

    def list(self) -> Sequence[Subscription]:
        return self._repository.list()

    def update(
        self,
        subscription_id: UUID,
        *,
        schedule_type: ScheduleType | None = None,
        timezone: str | None = None,
        event_types: frozenset[EventType] | None = None,
        notification_channels: tuple[str, ...] | None = None,
        enabled: bool | None = None,
        last_synced_at: datetime | None = None,
    ) -> Subscription:
        current = self.get(subscription_id)
        updated = replace(
            current,
            schedule_type=schedule_type or current.schedule_type,
            timezone=timezone or current.timezone,
            event_types=event_types or current.event_types,
            notification_channels=(
                notification_channels
                if notification_channels is not None
                else current.notification_channels
            ),
            enabled=enabled if enabled is not None else current.enabled,
            last_synced_at=(
                last_synced_at if last_synced_at is not None else current.last_synced_at
            ),
            updated_at=utc_now(),
        )
        return self._repository.save(updated)

    def delete(self, subscription_id: UUID) -> None:
        if not self._repository.delete(subscription_id):
            raise EntityNotFoundError(f"订阅不存在: {subscription_id}")
