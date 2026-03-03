# AI Log Analysis

A Python tool for parsing, normalizing, and clustering log messages using fingerprinting. It automatically groups similar error logs together and tracks them as incidents, making it easier to identify recurring problems in your logs.

This is a personal learning project to explore log processing, fingerprinting, and AI-powered root cause analysis.

## What It Does

This project helps manage large volumes of logs by automatically detecting patterns. It processes raw log messages, normalizes them by removing variable elements (like UUIDs, IP addresses, timestamps), and groups similar logs together using fingerprinting. The system then tracks these groups as incidents and can optionally analyze them with an LLM to determine root causes.

The pipeline works as follows:

1. **Parse logs** - Converts JSON or text logs into structured data
2. **Normalize** - Removes variable elements (UUIDs, emails, IPs, hex values, timestamps, quoted strings)
3. **Fingerprint** - Creates a SHA-256 hash based on normalized content
4. **Store** - Persists incidents in SQLite for tracking
5. **Analyze** - Optionally sends to an LLM (DeepSeek R1 via Bedrock) for root cause analysis

## Why Normalization Matters

Without normalization, logs that represent the same underlying error would be treated as different because they contain different IDs, timestamps, or addresses. For example:

```
User 550e8400-e29b-41d4-a716-446655440000 failed to login from 192.168.1.1
User 6ba7b810-9dad-11d1-80b4-00c04fd430c8 failed to login from 10.0.0.1
```

After normalization, both become:

```
User <uuid> failed to login from <ipv4>
```

This allows the system to correctly identify these as the same error pattern.

## Fingerprinting

The system uses SHA-256 hashes to create fingerprints from normalized log content. There are two fingerprinting methods:

- `create_fingerprint()` - Uses only the log message and level
- `create_fingerprint_with_stack_trace()` - Also includes stack trace when available

The stack trace version is optimized to focus on relevant information:
- Only the first 5 lines of stack traces are considered (lines beyond this are typically framework code)
- For string stack traces, only the first 100 characters are used
- Both the message and stack trace are normalized before hashing

The fingerprint includes the log level, so identical messages with different severity levels produce different fingerprints.

## Incident Tracking

Fingerprinted logs are stored as incidents in SQLite. Each incident contains:

- `id` - Unique identifier (UUID7)
- `source_id` - Service that generated the log
- `fingerprint` - Hash used for grouping
- `count` - Number of occurrences
- `status` - Current state (NEW, PROCESSING, AWAIT_USER_ACTION, RESOLVED, etc.)
- `root_cause` - LLM analysis of what went wrong
- `recommendations` - Suggested actions from the LLM
- `timestamps` - first_seen, last_seen, and last_changed tracked separately

The database enforces uniqueness on `(source_id, fingerprint)` to prevent duplicate incidents for the same error from the same source.

## Usage

The `main.py` script runs the complete pipeline:

1. Reads logs from the sample file
2. Parses and fingerprints each log
3. Checks if an incident already exists (by source_id + fingerprint)
4. If it exists, increments the occurrence count
5. If it doesn't exist, creates a new incident and sends it to an LLM for analysis
6. Updates the incident with LLM findings

```bash
pdm run python main.py
```

**Note:** The LLM analysis uses AWS Bedrock with the DeepSeek R1 model (`us.deepseek.r1-v1:0`). You will need AWS credentials configured and access to this model. Without it, the fingerprinting and clustering will still work, but LLM analysis will fail.

Bedrock isn't strictly needed, since the `instructor` library supports various LLM providers

## Supported Log Formats

The parser expects CloudWatch-style JSON logs but is flexible enough to handle various formats. It recognizes common field names:

**Timestamps:** `timestamp`, `@timestamp`, `time`, `ts`
**Severity:** `level`, `severity`, `log_level`, `logLevel`
**Message:** `message`, `msg`, `log`, `event`
**Tracing:** `request_id`, `req_id`, `trace_id`, `correlation_id`, `requestId`
**Errors:** `errorMessage`, `error_message`, `errorType`, `error_type`
**Service:** `sourceId`, `source_id`, `service`, `serviceName`

If JSON parsing fails, the system falls back to regex-based text parsing to extract timestamps and log levels from plain text logs.

## Normalization Patterns

The normalizer replaces the following patterns with placeholders:

- UUIDs → `<uuid>`
- Email addresses → `<email>`
- IPv4 addresses → `<ipv4>`
- IPv6 addresses → `<ipv6>`
- Hexadecimal values → `<hex>`
- Double-quoted strings → `<str1>`
- Single-quoted strings → `<str2>`

##  Limitations

- The IPv6 regex does not fully handle compressed notation (e.g., `2001::1`). It matches partial addresses.
- The text parser does not yet extract `key=value` style parameters.
- Other status - `RESOLVED`, `FIXED`, etc are not yet implemented

## Installation

Install dependencies using PDM:

```bash
pdm install
```

Requires Python 3.14. For full LLM analysis functionality, you will need AWS credentials and access to AWS Bedrock with the DeepSeek R1 model (or any other model of your choice).