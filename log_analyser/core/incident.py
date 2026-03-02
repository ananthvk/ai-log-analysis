from typing import Literal
from dataclasses import dataclass
from datetime import datetime


@dataclass
class Incident:
    id: str
    source_id: str
    timestamp: datetime
    fingerprint: str
    first_seen: datetime
    last_seen: datetime
    last_changed: datetime
    count: int
    status: Literal[
        "NEW",
        "PROCESSING",
        "NOTIFICATION_PENDING",
        "AWAIT_USER_ACTION",
        "IGNORED",
        "APPLYING_FIX",
        "RESOLVED",
        "MUTED",
        "FAILED",
    ]
    root_cause: str
    recommendations: list[str]
    sample_log: str
