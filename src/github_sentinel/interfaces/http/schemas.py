from datetime import datetime
from uuid import UUID

from pydantic import BaseModel, ConfigDict, Field, field_validator, model_validator

from github_sentinel.application.services.sync_service import SyncResult
from github_sentinel.domain.entities import Report, Subscription
from github_sentinel.domain.enums import EventType, ReportStatus, ScheduleType


class SubscriptionCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    repository: str = Field(examples=["openai/openai-python"])
    schedule_type: ScheduleType = ScheduleType.DAILY
    timezone: str = "Asia/Shanghai"
    event_types: set[EventType] = Field(
        default_factory=lambda: set(EventType),
        min_length=1,
    )
    notification_channels: list[str] = Field(default_factory=list)

    @field_validator("repository")
    @classmethod
    def validate_repository(cls, value: str) -> str:
        parts = value.strip().split("/")
        if len(parts) != 2 or not all(parts):
            raise ValueError("repository 必须使用 owner/name 格式")
        return value.strip()

    @property
    def repository_parts(self) -> tuple[str, str]:
        owner, name = self.repository.split("/", maxsplit=1)
        return owner, name


class SubscriptionUpdate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    schedule_type: ScheduleType | None = None
    timezone: str | None = None
    event_types: set[EventType] | None = Field(default=None, min_length=1)
    notification_channels: list[str] | None = None
    enabled: bool | None = None


class SubscriptionResponse(BaseModel):
    id: UUID
    repository: str
    schedule_type: ScheduleType
    timezone: str
    event_types: list[EventType]
    notification_channels: list[str]
    enabled: bool
    last_synced_at: datetime | None
    created_at: datetime
    updated_at: datetime

    @classmethod
    def from_domain(cls, subscription: Subscription) -> "SubscriptionResponse":
        return cls(
            id=subscription.id,
            repository=subscription.repository.full_name,
            schedule_type=subscription.schedule_type,
            timezone=subscription.timezone,
            event_types=sorted(subscription.event_types, key=str),
            notification_channels=list(subscription.notification_channels),
            enabled=subscription.enabled,
            last_synced_at=subscription.last_synced_at,
            created_at=subscription.created_at,
            updated_at=subscription.updated_at,
        )


class ReportCreate(BaseModel):
    model_config = ConfigDict(extra="forbid")

    period_start: datetime
    period_end: datetime

    @model_validator(mode="after")
    def validate_period(self) -> "ReportCreate":
        if self.period_end <= self.period_start:
            raise ValueError("period_end 必须晚于 period_start")
        return self


class ReportResponse(BaseModel):
    id: UUID
    subscription_id: UUID
    period_start: datetime
    period_end: datetime
    status: ReportStatus
    summary: str
    markdown_content: str
    event_count: int
    generated_at: datetime

    @classmethod
    def from_domain(cls, report: Report) -> "ReportResponse":
        return cls(
            id=report.id,
            subscription_id=report.subscription_id,
            period_start=report.period_start,
            period_end=report.period_end,
            status=report.status,
            summary=report.summary,
            markdown_content=report.markdown_content,
            event_count=report.event_count,
            generated_at=report.generated_at,
        )


class SyncResponse(BaseModel):
    fetched_count: int
    new_event_count: int
    report_id: UUID | None
    delivery_count: int

    @classmethod
    def from_result(cls, result: SyncResult) -> "SyncResponse":
        return cls(
            fetched_count=result.fetched_count,
            new_event_count=result.new_event_count,
            report_id=result.report.id if result.report else None,
            delivery_count=len(result.deliveries),
        )


class HealthResponse(BaseModel):
    status: str
