from typing import Protocol

from github_sentinel.domain.entities import Delivery, Report


class Notifier(Protocol):
    def supports(self, destination: str) -> bool: ...

    def deliver(self, report: Report, destination: str) -> Delivery: ...
