from ala.normalizer import default_normalizer
from ala.log import parse_log, RawLog
from ala.fingerprint import create_fingerprint
import time

message = """
{
  "timestamp": "2026-02-27T17:33:05Z",
  "log_level": "ERROR",
  "errorMessage": "division by zero",
  "errorType": "ZeroDivisionError",
  "requestId": "a8516e9d-95e3-4a63-98b2-0e5d21d50d4a",
  "stackTrace": ["  File \\"/var/task/lambda_function.py\\", line 19, in lambda_handler\\n    result = m / n\\n"]
}
"""
source = "/aws/lambda/faultyLambda"

parsed_log = parse_log(
    raw_log=RawLog(message=message, source_id=source, timestamp=int(time.time()))
)

print("=== Parsed ===")
print(parsed_log)

print("=== Message ===")
print(parsed_log.message)

print("=== Normalized ===")
print(default_normalizer.normalize(parsed_log.message))

print("=== Fingerprint ===")
fingerprint = create_fingerprint(parsed_log, default_normalizer)
print(fingerprint)