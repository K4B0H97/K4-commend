"""Event logging for K4 task execution."""


class EventLog:
    """In-memory event log for the first scaffold."""

    def __init__(self) -> None:
        self.events: list[dict] = []

    def record(self, event_type: str, payload: dict) -> None:
        self.events.append({"type": event_type, **payload})

    def all(self) -> list[dict]:
        return list(self.events)
