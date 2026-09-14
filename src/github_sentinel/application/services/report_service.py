from collections.abc import Sequence
from datetime import datetime

from github_sentinel.application.ports.repositories import ReportRepository
from github_sentinel.application.ports.summarizer import Summarizer
from github_sentinel.domain.entities import Report, RepositoryEvent, Subscription


class ReportService:
    def __init__(self, reports: ReportRepository, summarizer: Summarizer) -> None:
        self._reports = reports
        self._summarizer = summarizer

    def generate(
        self,
        subscription: Subscription,
        events: Sequence[RepositoryEvent],
        period_start: datetime,
        period_end: datetime,
    ) -> Report:
        summary = self._summarizer.summarize(events)
        event_lines = "\n".join(
            f"- [{event.event_type.value}] [{event.title}]({event.url}) — {event.author}"
            for event in events
        )
        markdown = (
            f"# {subscription.repository.full_name} 更新报告\n\n"
            f"> {period_start.isoformat()} 至 {period_end.isoformat()}\n\n"
            f"## 摘要\n\n{summary}\n\n"
            f"## 动态\n\n{event_lines or '- 本周期没有新动态。'}\n"
        )
        report = Report(
            subscription_id=subscription.id,
            period_start=period_start,
            period_end=period_end,
            summary=summary,
            markdown_content=markdown,
            event_count=len(events),
        )
        return self._reports.save(report)
