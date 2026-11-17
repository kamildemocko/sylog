from dataclasses import dataclass

import arrow


@dataclass
class QueryItem:
    timestamp: str
    symptom: str
    severity: str
    description: str | None
    profile_id: int


@dataclass
class HistoryItem:
    id: int
    timestamp: str
    symptom: str
    severity: str
    description: str | None

    def human_timestamp(self) -> str:
        return arrow.get(self.timestamp).humanize()

@dataclass
class Profile:
    id: int
    name: str


@dataclass
class QueryItemDaily:
    timestamp: str
    name: str
    rvalue: str
    note: str | None
    profile_id: int


@dataclass
class DailyItem:
    id: int
    timestamp: str
    name: str
    rvalue: str
    note: str | None

    def human_timestamp(self) -> str:
        return arrow.get(self.timestamp).humanize(granularity="day")
