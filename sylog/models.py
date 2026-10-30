from dataclasses import dataclass

import arrow


@dataclass
class QueryItem:
    timestamp: str
    symptom: str
    severity: str
    description: str | None


@dataclass
class HistoryItem:
    id: int
    timestamp: str
    symptom: str
    severity: str
    description: str | None

    def human_timestamp(self) -> str:
        return arrow.get(self.timestamp).humanize()
