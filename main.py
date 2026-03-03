import time
from datetime import datetime
from uuid import uuid7

import instructor

from log_analyser.core.fingerprint import create_fingerprint_with_stack_trace
from log_analyser.core.incident import Incident
from log_analyser.core.log import RawLog, parse_log
from log_analyser.core.normalizer import default_normalizer
from log_analyser.rca.root_cause import infer
from log_analyser.store.incident_repository import IncidentRepository
from log_analyser.store.sqlite_repository import SQLiteIncidentRepository
import json

repo: IncidentRepository = SQLiteIncidentRepository("logs/incidents.db")
# TODO: Close it later
model_name = "us.deepseek.r1-v1:0"

with open("sample_logs/logs.json", "r") as f:
    error_batches = json.load(f)

error_messages: list[RawLog] = []

for batch in error_batches:
    payload = batch["message"]
    source_id = payload["logGroup"]
    for event in payload["logEvents"]:
        error_messages.append(
            RawLog(
                timestamp=event["timestamp"],
                source_id=source_id,
                message=event["message"],
            )
        )

for m in error_messages:
    print("Processing", m)
    print("=" * 50)

    source = m.source_id or "unknown"
    message = m.message
    ts = m.timestamp

    parsed_log = parse_log(
        raw_log=RawLog(message=message, source_id=source, timestamp=ts)
    )

    fingerprint = create_fingerprint_with_stack_trace(parsed_log, default_normalizer)

    # Check if the incident already exists
    id = repo.get_id_by_source_fingerprint(source_id=source, fingerprint=fingerprint)
    if id is not None:
        # For now just increase the count and exit
        print("Incident already exists, incrementing count...")
        repo.increment_count(id, datetime.now())
        continue

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
    try:
        repo.create(incident)
    except:
        print("Incident already exists, skipping....")
        # TODO: Make create return the id instead
        id = repo.get_id_by_source_fingerprint(
            source_id=source, fingerprint=fingerprint
        )
        if id is None:
            continue
        repo.increment_count(id, datetime.now())
        continue

    # Call the LLM to perform the analysis
    client = instructor.from_provider(f"bedrock/${model_name}")
    root_cause = infer(client, parsed_log, model_name)

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
    print("DONE")
    print("=" * 50)