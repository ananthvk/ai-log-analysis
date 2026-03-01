from typing import Any
from .log import ParsedLog
from .normalizer import Normalizer
import hashlib

STACK_TRACE_MAX_CHARS = 100
STACK_TRACE_MAX_LINES = 5


def create_fingerprint(log: ParsedLog, normalizer: Normalizer) -> str:
    """
    Create a unique fingerprint for a log entry, that can be used to group similar log messages together
    """

    stack_trace = log.parameters.get("stackTrace", None)
    if stack_trace is None:
        stack_trace = ""
    else:
        if isinstance(stack_trace, list):
            combined = ""
            for i, line in enumerate(stack_trace):
                if not isinstance(line, str):
                    line = str(line)
                if i > STACK_TRACE_MAX_LINES:
                    break
                combined += line.lower().strip()
            stack_trace = combined
        elif isinstance(stack_trace, str):
            stack_trace = stack_trace.lower().strip()[:STACK_TRACE_MAX_CHARS]

    message_normalized = normalizer.normalize(log.message.strip())
    stack_trace_normalized = normalizer.normalize(stack_trace)
    fingerprint_input = f"{log.level}{message_normalized}{stack_trace_normalized}"
    return hashlib.sha256(fingerprint_input.encode("utf-8")).hexdigest()
