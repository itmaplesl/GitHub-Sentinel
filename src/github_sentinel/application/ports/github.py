from collections.abc import Sequence
from datetime import datetime
from typing import Protocol

from github_sentinel.domain.entities import RepositoryEvent, Subscription


class GitHubClient(Protocol):
    def fetch_events(
        self,
        subscription: Subscription,
        since: datetime,
        until: datetime,
    ) -> Sequence[RepositoryEvent]: ...
