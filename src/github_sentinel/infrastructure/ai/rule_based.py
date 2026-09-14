from collections import Counter
from collections.abc import Sequence

from github_sentinel.domain.entities import RepositoryEvent


class RuleBasedSummarizer:
    def summarize(self, events: Sequence[RepositoryEvent]) -> str:
        if not events:
            return "本周期没有新动态。"
        counts = Counter(event.event_type.value for event in events)
        details = "、".join(
            f"{event_type} {count} 条" for event_type, count in sorted(counts.items())
        )
        return f"本周期共发现 {len(events)} 条新动态：{details}。"
