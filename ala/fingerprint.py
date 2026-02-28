from typing import Any


def create_fingerprint(log: dict[str, Any] | str) -> str:
    """
    Create a unique fingerprint for a log entry, that can be used to group similar log messages together
    It removes ids, ip address, etc before creating the log.
    Args:
        log (dict[str, Any] | str): Either a dictionary containing log data with
            various fields, or a string representing a simple log message.
    Returns:
        str: A fingerprint string that identifes the log pattern
    """
    normalized_content = ""

    if isinstance(log, str):
        normalized_content += log

    return normalized_content
