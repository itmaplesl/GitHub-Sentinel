from datetime import UTC, datetime

from github_sentinel.domain.entities import Delivery, Report
from github_sentinel.domain.enums import DeliveryStatus


class LoggingWebhookNotifier:
    """Non-networking stage-one notifier used to verify orchestration."""

    def supports(self, destination: str) -> bool:
        return destination.startswith(("http://", "https://"))

    def deliver(self, report: Report, destination: str) -> Delivery:
        return Delivery(
            report_id=report.id,
            channel_type="webhook",
            destination=destination,
            status=DeliveryStatus.DELIVERED,
            attempt_count=1,
            delivered_at=datetime.now(UTC),
        )
