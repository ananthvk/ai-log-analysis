import json
import re
from dataclasses import dataclass
from datetime import datetime
from typing import Any, Literal

TIMESTAMP_KEYS = ["timestamp", "@timestamp", "time", "ts"]
LEVEL_KEYS = ["level", "severity", "log_level", "logLevel"]
MESSAGE_KEYS = ["message", "msg", "log", "event"]
REQUEST_ID_KEYS = ["request_id", "req_id", "trace_id", "correlation_id", "requestId"]
ERROR_MESSAGE_KEYS = ["errorMessage", "error_message"]
ERROR_TYPE_KEYS = ["errorType", "error_type"]
SOURCE_ID_KEYS = ["sourceId", "source_id", "service", "serviceName"]

patterns = {
    "timestamp": [
        re.compile(
            r"[0-9]{4}-[0-9]{2}-[0-9]{2}T[0-9]{2}:[0-9]{2}:[0-9]{2}(\.[0-9]+)?([Zz]|([\+-])([01]\d|2[0-3]):?([0-5]\d)?)?",
            re.IGNORECASE,
        )
    ],
    "log_level": [re.compile(r"\b(DEBUG|INFO|WARN|ERROR|FATAL)\b", re.IGNORECASE)],
}


def extract_value(data: dict[str, Any], keys: list[str]) -> Any:
    """
    Extracts the value of the first key from `keys` that is present in data. The key is then removed from data
    Args:
        data (dict[str, Any]): Key-Value pairs from which the value needs to be extracted
        keys (list[str]): List of keys to search for in data
    Returns:
        Any: The value associated with any of the keys, if it exists. If a key does not exist, None is returned.
             It is not possible to differentiate between null value and abscence of key
    """
    for key in keys:
        if key in data:
            return data.pop(key)


@dataclass
class RawLog:
    """
    A raw log entry

    Attributes:
        source_id (str): Identifies the service that created this log entry, this is optional and may be None if
                         this needs to be parsed from the log message
        message (str): The log message
        timestamp (int): Unix timestamp at the time when this log was received, it can be used as a fallback if the log
                         does not include a timestamp
    """

    source_id: str | None
    message: str
    timestamp: int


@dataclass
class ParsedLog:
    """
    A structured representation of a parsed log entry.

    Attributes:
        source_id (str): Identifier of the application or service that generated this log
        timestamp (datetime): The time of occurence of this log event
        level (Literal["DEBUG", "INFO", "WARN", "ERROR", "FATAL", "UNKNOWN"]): The severity level of the log entry.
        parameters (dict[str, Any]): A dictionary of key-value pairs containing context, and parameters extracted from the log
        message (str): Message of the log
        request_id (str | None): An optional identifier to identify the request
    """

    source_id: str
    timestamp: datetime
    level: Literal["DEBUG", "INFO", "WARN", "ERROR", "FATAL", "UNKNOWN"]
    parameters: dict[str, Any]
    message: str
    request_id: str | None


def __parse_text_log(raw: RawLog) -> ParsedLog:
    timestamp = None
    level = None

    message_copy = raw.message

    for match in patterns["timestamp"]:
        timestamp_match = match.search(message_copy)
        if timestamp_match:
            timestamp = timestamp_match.group()
            start, end = timestamp_match.span()
            message_copy = message_copy[:start] + message_copy[end:]
            break

    for match in patterns["log_level"]:
        level_match = match.search(message_copy)
        if level_match:
            level = level_match.group().upper()
            start, end = level_match.span()
            message_copy = message_copy[:start] + message_copy[end:]
            break

    source_id = raw.source_id
    message = message_copy
    if isinstance(message, str):
        message = message.strip()

    if level is None or level not in ["DEBUG", "INFO", "WARN", "ERROR", "FATAL"]:
        level = "UNKNOWN"

    level = level.upper()

    try:
        parsed_ts = datetime.fromisoformat(timestamp)  # type: ignore
    except Exception:
        parsed_ts = datetime.fromtimestamp(raw.timestamp)

    return ParsedLog(
        source_id=source_id or "unknown",
        level=level,  # type: ignore
        message=message or "",
        request_id=None,
        timestamp=parsed_ts,
        parameters={},
    )
    # TODO: Parse additional parameters, key=value etc


def __parse_json_log(raw: RawLog) -> ParsedLog | None:
    try:
        parsed = json.loads(raw.message)
    except json.JSONDecodeError:
        return None

    # Check if the parsed JSON object is a dictionary
    if not isinstance(parsed, dict):
        return None

    timestamp = extract_value(parsed, TIMESTAMP_KEYS)
    level = extract_value(parsed, LEVEL_KEYS)
    message = extract_value(parsed, MESSAGE_KEYS)
    request_id = extract_value(parsed, REQUEST_ID_KEYS)

    source_id = raw.source_id
    if not source_id:
        source_id = extract_value(parsed, SOURCE_ID_KEYS)

    if not isinstance(message, str) and message is not None:
        message = str(message)

    if not isinstance(level, str) or level not in [
        "DEBUG",
        "INFO",
        "WARN",
        "ERROR",
        "FATAL",
    ]:
        level = "UNKNOWN"

    if level:
        level = level.upper()

    try:
        parsed_ts = datetime.fromisoformat(timestamp)
    except Exception:
        parsed_ts = datetime.fromtimestamp(raw.timestamp)

    # Upgrade error message keys / error type keys into message
    error_message = extract_value(parsed, ERROR_MESSAGE_KEYS)
    error_type = extract_value(parsed, ERROR_TYPE_KEYS)
    if not isinstance(error_message, str) and error_message is not None:
        error_message = str(error_message)

    if error_message:
        if level != "FATAL":
            level = "ERROR"
        if message is not None:
            message = f"{error_type}: {error_message.strip()}; message={message}"
        else:
            message = f"{error_type}: {error_message.strip()}"

    return ParsedLog(
        source_id=source_id,
        level=level,  # type: ignore
        message=message,
        request_id=request_id,
        timestamp=parsed_ts,
        parameters=parsed,
    )


def parse_log(raw_log: RawLog) -> ParsedLog:
    """
    Parses a raw log message into a structured format, it first attempts to parse it as JSON.
    If that fails, further processing using regex and other tools is attempted to extract structure from the text.
    Args:
        raw_log (RawLog): The raw log object containing the message to parse.
    Returns:
        ParsedLog: A parsed log object containing structured data extracted from the raw log
    """

    # Parse the log as structured log (JSON) if possible
    parsed = __parse_json_log(raw_log)
    if parsed is not None:
        return parsed
    else:
        return __parse_text_log(raw_log)


# log = """{"timestamp": "2026-02-27T17:34:11Z", "log_level": "ERROR", "errorMessage": "'n'", "errorType": "KeyError", "requestId": "b06f09e6-828a-4a43-8903-14bd221dc62b", "stackTrace": ["  File \\"/var/task/lambda_function.py\\", line 17, in lambda_handler\\n    n = int(body[\\"n\\"])  # Get n from the body\\n"]}"""
# print(parse_log(RawLog(message=log, source_id="lambda/x/yz", timestamp=3)))
