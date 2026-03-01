from ala.normalizer import default_normalizer
from ala.log import parse_log, RawLog
from ala.fingerprint import create_fingerprint
from collections import defaultdict
import json

with open("sample_logs/logs.json", "r") as f:
    error_batches = json.load(f)

error_messages = []

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

# Process all error messages and cluster by fingerprint
clusters = defaultdict(list)

for i, message in enumerate(error_messages):
    try:
        parsed_log = parse_log(message)

        normalized = default_normalizer.normalize(parsed_log.message)
        fingerprint = create_fingerprint(parsed_log, default_normalizer)

        clusters[fingerprint].append(
            {
                "index": i,
                "message": message,
                "parsed": parsed_log,
                "normalized": normalized,
            }
        )
    except Exception as e:
        print(f"Error processing message {i}: {e}")


# Print results clustered by fingerprint
print("=" * 100)
print("LOG ANALYSIS RESULTS - CLUSTERED BY FINGERPRINT")
print("=" * 100)
print()

for cluster_id, logs in clusters.items():
    print(f"CLUSTER: {cluster_id}")
    print(f"Count: {len(logs)} logs")
    print("-" * 100)

    for log in logs:
        print(f"\nLog #{log['index'] + 1}:")
        print(f"  Message: {log['parsed'].message}")
        print(f"  Normalized: {log['normalized']}")
        if log["parsed"].level:
            print(f"  Level: {log['parsed'].level}")
        if log["parsed"].request_id:
            print(f"  Request ID: {log['parsed'].request_id}")

    print("\n" + "=" * 100 + "\n")

print("Number of logs", len(error_messages))
print(f"Number of clusters: {len(clusters)}")