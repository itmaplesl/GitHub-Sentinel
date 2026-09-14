from datetime import UTC, datetime
from uuid import uuid4

import pytest

from github_sentinel.domain.entities import RepositoryEvent, RepositoryRef, Subscription
from github_sentinel.domain.enums import EventType, ScheduleType
from github_sentinel.domain.exceptions import InvalidRepositoryError


def test_repository_ref_exposes_full_name() -> None:
    repository = RepositoryRef(owner="openai", name="openai-python")

    assert repository.full_name == "openai/openai-python"


def test_repository_ref_rejects_nested_path() -> None:
    with pytest.raises(InvalidRepositoryError):
        RepositoryRef(owner="openai/team", name="repo")


def test_subscription_rejects_unknown_timezone() -> None:
    with pytest.raises(ValueError, match="未知时区"):
        Subscription(
            repository=RepositoryRef("owner", "repo"),
            schedule_type=ScheduleType.DAILY,
            timezone="Mars/Olympus",
            event_types=frozenset({EventType.RELEASE}),
        )


def test_event_deduplication_key_is_stable() -> None:
    subscription_id = uuid4()
    first = RepositoryEvent(
        subscription_id=subscription_id,
        github_event_id="42",
        event_type=EventType.ISSUE,
        title="Issue",
        url="https://github.com/owner/repo/issues/42",
        author="octocat",
        occurred_at=datetime(2026, 9, 14, tzinfo=UTC),
    )
    second = RepositoryEvent(
        subscription_id=subscription_id,
        github_event_id="42",
        event_type=EventType.ISSUE,
        title="Changed title",
        url="https://github.com/owner/repo/issues/42",
        author="octocat",
        occurred_at=datetime(2026, 9, 14, tzinfo=UTC),
    )

    assert first.deduplication_key == second.deduplication_key
