from abc import abstractmethod, ABC
from ..core.incident import Incident
from datetime import datetime


class IncidentRepository:

    @abstractmethod
    def get(self, incident_id: str) -> Incident | None: ...

    @abstractmethod
    def get_id_by_source_fingerprint(
        self, source_id: str, fingerprint: str
    ) -> str | None: ...

    @abstractmethod
    def create(self, incident: Incident) -> None: ...

    @abstractmethod
    def update_analysis_result(
        self,
        id: str,
        root_cause: str,
        recommendations: list[str],
        status: str,
        last_changed: datetime,
        current_status: str,
    ) -> bool: ...

    @abstractmethod
    def update(self, incident: Incident) -> None:
        """
        Updates the incident with the new incident. Note: Partial writes are not yet supported
        and the whole object is replaced
        """
        ...

    @abstractmethod
    def increment_count(self, incident_id: str, timestamp) -> None:
        """
        This method must atomically increase the count of incident. If the incident
        does not exist, this method must do nothing
        """
        ...

    @abstractmethod
    def change_status(self, incident_id: str, from_status: str, to_status: str) -> bool:
        """
        This method must change the status of the incident from from_status to to_status.
        If the incident has a status other than from_status, it should not change the status and must return false.
        If the incident does not exist, it must do nothing, and return False
        """
        ...
