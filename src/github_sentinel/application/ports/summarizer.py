from collections.abc import Sequence
from typing import Protocol

from github_sentinel.domain.entities import RepositoryEvent


class Summarizer(Protocol):
    def summarize(self, events: Sequence[RepositoryEvent]) -> str: ...
