from collections.abc import Sequence
from datetime import datetime

from github_sentinel.domain.entities import RepositoryEvent, Subscription


class NoOpGitHubClient:
    """Safe stage-one adapter; the real REST adapter is implemented in stage three."""

    def fetch_events(
        self,
        subscription: Subscription,
        since: datetime,
        until: datetime,
    ) -> Sequence[RepositoryEvent]:
        return ()
