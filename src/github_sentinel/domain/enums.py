from enum import StrEnum


class ScheduleType(StrEnum):
    DAILY = "daily"
    WEEKLY = "weekly"


class EventType(StrEnum):
    RELEASE = "release"
    PULL_REQUEST = "pull_request"
    ISSUE = "issue"
    COMMIT = "commit"


class ReportStatus(StrEnum):
    PENDING = "pending"
    GENERATED = "generated"
    DELIVERED = "delivered"
    FAILED = "failed"


class DeliveryStatus(StrEnum):
    PENDING = "pending"
    DELIVERED = "delivered"
    FAILED = "failed"
