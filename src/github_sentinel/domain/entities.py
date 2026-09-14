from __future__ import annotations

from dataclasses import dataclass, field
from datetime import UTC, datetime
from hashlib import sha256
from typing import Any
from uuid import UUID, uuid4
from zoneinfo import ZoneInfo, ZoneInfoNotFoundError

from github_sentinel.domain.enums import (
    DeliveryStatus,
    EventType,
    ReportStatus,
    ScheduleType,
)
from github_sentinel.domain.exceptions import InvalidRepositoryError


def utc_now() -> datetime:
    return datetime.now(UTC)


@dataclass(frozen=True, slots=True)
class RepositoryRef:
    owner: str
    name: str

    def __post_init__(self) -> None:
        owner = self.owner.strip()
        name = self.name.strip()
        if not owner or not name or "/" in owner or "/" in name:
            raise InvalidRepositoryError("仓库必须由有效的 owner 和 name 组成")
        object.__setattr__(self, "owner", owner)
        object.__setattr__(self, "name", name)

    @property
    def full_name(self) -> str:
        return f"{self.owner}/{self.name}"


@dataclass(slots=True)
class Subscription:
    repository: RepositoryRef
    schedule_type: ScheduleType
    timezone: str
    event_types: frozenset[EventType]
    notification_channels: tuple[str, ...] = ()
    enabled: bool = True
    id: UUID = field(default_factory=uuid4)
    last_synced_at: datetime | None = None
    created_at: datetime = field(default_factory=utc_now)
    updated_at: datetime = field(default_factory=utc_now)

    def __post_init__(self) -> None:
        if not self.event_types:
            raise ValueError("至少需要订阅一种事件类型")
        try:
            ZoneInfo(self.timezone)
        except ZoneInfoNotFoundError as exc:
            raise ValueError(f"未知时区: {self.timezone}") from exc


@dataclass(frozen=True, slots=True)
class RepositoryEvent:
    subscription_id: UUID
    github_event_id: str
    event_type: EventType
    title: str
    url: str
    author: str
    occurred_at: datetime
    raw_payload: dict[str, Any] = field(default_factory=dict)
    id: UUID = field(default_factory=uuid4)

    @property
    def deduplication_key(self) -> str:
        raw = f"{self.subscription_id}:{self.event_type}:{self.github_event_id}"
        return sha256(raw.encode()).hexdigest()


@dataclass(slots=True)
class Report:
    subscription_id: UUID
    period_start: datetime
    period_end: datetime
    summary: str
    markdown_content: str
    event_count: int
    status: ReportStatus = ReportStatus.GENERATED
    id: UUID = field(default_factory=uuid4)
    generated_at: datetime = field(default_factory=utc_now)

    @property
    def idempotency_key(self) -> str:
        raw = ":".join(
            (
                str(self.subscription_id),
                self.period_start.isoformat(),
                self.period_end.isoformat(),
            )
        )
        return sha256(raw.encode()).hexdigest()


@dataclass(slots=True)
class Delivery:
    report_id: UUID
    channel_type: str
    destination: str
    status: DeliveryStatus = DeliveryStatus.PENDING
    attempt_count: int = 0
    last_error: str | None = None
    delivered_at: datetime | None = None
    id: UUID = field(default_factory=uuid4)
