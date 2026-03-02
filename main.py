from log_analyser.core.normalizer import default_normalizer
from datetime import datetime
from log_analyser.core.log import parse_log, RawLog
from log_analyser.core.fingerprint import create_fingerprint_with_stack_trace
from log_analyser.store.incident_repository import IncidentRepository
from log_analyser.store.sqlite_repository import SQLiteIncidentRepository
from log_analyser.core.incident import Incident
from log_analyser.rca.root_cause import RootCause, infer
import instructor

from uuid import uuid7
import time

repo: IncidentRepository = SQLiteIncidentRepository("logs/incidents.db")
# TODO: Close it later
model_name = "us.deepseek.r1-v1:0"


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

fingerprint = create_fingerprint_with_stack_trace(parsed_log, default_normalizer)


# Check if the incident already exists
id = repo.get_id_by_source_fingerprint(source_id=source, fingerprint=fingerprint)
if id is not None:
    # For now just increase the count and exit
    print("Incident already exists, incrementing count...")
    repo.increment_count(id, datetime.now())
    exit(0)

# The incident does not exist, try creating it. Note: This can fail if it was created in the meanwhile
id = str(uuid7())
now = datetime.now()
incident = Incident(
    id=id,
    source_id=source,
    timestamp=now,
    fingerprint=fingerprint,
    first_seen=now,
    last_seen=now,
    last_changed=now,
    count=1,
    status="PROCESSING",
    root_cause="",
    recommendations=[],
    sample_log=parsed_log.raw,
)
repo.create(incident)

# Call the LLM to perform the analysis
instructor = instructor.from_provider(f"bedrock/${model_name}")
root_cause = infer(instructor, parsed_log, model_name)

# Update the record
repo.update_analysis_result(
    id=id,
    current_status="PROCESSING",
    recommendations=root_cause.recommended_actions,
    status="AWAIT_USER_ACTION",
    last_changed=datetime.now(),
    root_cause=f"{root_cause.description}: {root_cause.root_cause}",
)

print(root_cause)
