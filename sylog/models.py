from dataclasses import dataclass

import arrow


@dataclass
class SavedData:
    date: str
    time: str
    symptom: str
    severity: str
    description: str | None


@dataclass
class DatabaseHistoryItem:
    timestamp: str
    symptom: str
    severity: str
    description: str | None

    def human_timestamp(self) -> str:
        return arrow.get(self.timestamp).humanize()
