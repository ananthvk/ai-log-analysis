import sqlite3
import json
from datetime import datetime
from typing import override

from ..core.incident import Incident
from .incident_repository import IncidentRepository


class SQLiteIncidentRepository(IncidentRepository):
    """
    Incident repository backed by SQLite for local use
    """

    def __init__(self, db_path: str):
        self._db_path = db_path
        self._conn = sqlite3.connect(db_path)
        self._conn.row_factory = sqlite3.Row
        self._init_schema()

    def _init_schema(self) -> None:
        self._conn.execute(
            """
            CREATE TABLE IF NOT EXISTS incidents (
                id TEXT PRIMARY KEY,
                source_id TEXT NOT NULL,
                timestamp DATETIME NOT NULL,
                fingerprint TEXT NOT NULL,
                first_seen DATETIME NOT NULL,
                last_seen DATETIME NOT NULL,
                last_changed DATETIME NOT NULL,
                count INTEGER NOT NULL,
                status TEXT NOT NULL,
                recommendations TEXT NOT NULL,
                sample_log TEXT NOT NULL,
                root_cause TEXT NOT NULL
            )
        """
        )
        self._conn.execute(
            """
            CREATE UNIQUE INDEX IF NOT EXISTS idx_incidents_source_fingerprint
            ON incidents (source_id, fingerprint)
        """
        )
        self._conn.commit()

    @override
    def get(self, incident_id: str) -> Incident | None:
        cursor = self._conn.execute(
            "SELECT * FROM incidents WHERE id = ?", (incident_id,)
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return self._row_to_incident(row)

    @override
    def get_id_by_source_fingerprint(
        self, source_id: str, fingerprint: str
    ) -> str | None:
        cursor = self._conn.execute(
            "SELECT id FROM incidents WHERE source_id = ? AND fingerprint = ?",
            (source_id, fingerprint),
        )
        row = cursor.fetchone()
        if row is None:
            return None
        return row["id"]

    @override
    def create(self, incident: Incident) -> None:
        self._conn.execute(
            """INSERT INTO incidents (id, source_id, timestamp, fingerprint, first_seen, last_seen, last_changed, count, status, recommendations, sample_log, root_cause)
               VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)""",
            (
                incident.id,
                incident.source_id,
                incident.timestamp,
                incident.fingerprint,
                incident.first_seen,
                incident.last_seen,
                incident.timestamp,
                incident.count,
                incident.status,
                json.dumps(incident.recommendations),
                incident.sample_log,
                incident.root_cause
            ),
        )
        self._conn.commit()

    @override
    def update(self, incident: Incident) -> None:
        self._conn.execute(
            """UPDATE incidents
               SET source_id = ?, timestamp = ?, fingerprint = ?, first_seen = ?, last_seen = ?, last_changed = ?,
                   count = ?, status = ?, recommendations = ?, sample_log = ?, root_cause = ?
               WHERE id = ?""",
            (
                incident.source_id,
                incident.timestamp,
                incident.fingerprint,
                incident.first_seen,
                incident.last_seen,
                incident.last_changed,
                incident.count,
                incident.status,
                json.dumps(incident.recommendations),
                incident.sample_log,
                incident.root_cause,
                incident.id,
            ),
        )
        self._conn.commit()

    @override
    def increment_count(self, incident_id: str, timestamp: datetime) -> None:
        self._conn.execute(
            "UPDATE incidents SET count = count + 1, last_seen = ? WHERE id = ?",
            (timestamp, incident_id),
        )
        self._conn.commit()

    @override
    def change_status(self, incident_id: str, from_status: str, to_status: str) -> bool:
        cursor = self._conn.execute(
            "UPDATE incidents SET status = ?, last_changed = ? WHERE id = ? AND status = ?",
            (to_status, datetime.now(), incident_id, from_status),
        )
        self._conn.commit()
        return cursor.rowcount > 0

    def close(self) -> None:
        self._conn.close()

    @staticmethod
    def _row_to_incident(row: sqlite3.Row) -> Incident:
        return Incident(
            id=row["id"],
            source_id=row["source_id"],
            timestamp=datetime.fromisoformat(row["timestamp"]),
            fingerprint=row["fingerprint"],
            first_seen=datetime.fromisoformat(row["first_seen"]),
            last_seen=datetime.fromisoformat(row["last_seen"]),
            last_changed=datetime.fromisoformat(row["last_changed"]),
            count=row["count"],
            status=row["status"],
            recommendations=json.loads(row["recommendations"]),
            sample_log=row["sample_log"],
            root_cause=row["root_cause"],
        )
