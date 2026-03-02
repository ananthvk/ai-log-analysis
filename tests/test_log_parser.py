from datetime import datetime

from log_analyser.core.log import RawLog, parse_log


class TestJSONLogParser:
    """Test suite for JSON log parsing functionality."""

    def test_empty_json_log(self):
        """Test parsing an empty JSON object {}."""
        raw = RawLog(
            source_id=None,
            message="{}",
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result is not None
        assert result.kind == "json"
        assert result.source_id == "unknown"
        assert result.level == "UNKNOWN"
        assert result.message == ""
        assert result.request_id is None
        # Empty dict for parameters since all keys were extracted
        assert isinstance(result.parameters, dict)

    def test_json_with_only_level(self):
        """Test parsing JSON with only the level field."""
        raw = RawLog(
            source_id="test-service",
            message='{"level": "ERROR"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.source_id == "test-service"
        assert result.level == "ERROR"
        assert result.message == ""
        assert result.request_id is None

    def test_json_with_unknown_level(self):
        """Test parsing JSON with unknown/invalid level."""
        raw = RawLog(
            source_id="test-service",
            message='{"level": "CRITICAL"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.level == "UNKNOWN"

    def test_json_with_lowercase_level(self):
        """Test parsing JSON with lowercase level gets normalized."""
        raw = RawLog(
            source_id="test-service",
            message='{"level": "error"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.level == "ERROR"

    def test_json_with_malformed_timestamp(self):
        """Test parsing JSON with malformed timestamp falls back to Unix timestamp."""
        raw = RawLog(
            source_id="test-service",
            message='{"message": "test"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        # Should fall back to the Unix timestamp from RawLog
        expected_ts = datetime.fromtimestamp(1772364888)
        assert result.timestamp == expected_ts

    def test_json_with_valid_iso_timestamp(self):
        """Test parsing JSON with valid ISO 8601 timestamp."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "message": "test"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        expected_ts = datetime.fromisoformat("2026-03-01T11:34:48Z")
        assert result.timestamp == expected_ts

    def test_json_with_message(self):
        """Test parsing JSON with message field."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "level": "INFO", "message": "User logged in"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.message == "User logged in"
        assert result.level == "INFO"

    def test_json_with_request_id(self):
        """Test parsing JSON with request ID."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "level": "INFO", "message": "Request processed", "requestId": "abc-123-def"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.request_id == "abc-123-def"

    def test_json_with_trace_id(self):
        """Test parsing JSON with trace_id variant."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "trace_id": "trace-456"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.request_id == "trace-456"

    def test_json_with_extra_parameters_stored(self):
        """Test that extra parameters are parsed and stored in parameters dict."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "level": "INFO", "message": "Request processed", "userId": "user123", "duration": 150, "endpoint": "/api/users"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        # Extra parameters should be in the parameters dict
        assert result.parameters["userId"] == "user123"
        assert result.parameters["duration"] == 150
        assert result.parameters["endpoint"] == "/api/users"

    def test_json_standard_fields_not_in_parameters(self):
        """Test that standard fields are not present in parameters dict."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "level": "INFO", "message": "test", "requestId": "123", "custom": "value"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        # Standard fields should be extracted and not in parameters
        assert "timestamp" not in result.parameters
        assert "level" not in result.parameters
        assert "message" not in result.parameters
        assert "requestId" not in result.parameters
        # Custom field should remain
        assert result.parameters.get("custom") == "value"

    def test_json_with_source_id(self):
        """Test parsing JSON with source_id field."""
        raw = RawLog(
            source_id=None,
            message='{"timestamp": "2026-03-01T11:34:48Z", "level": "INFO", "serviceName": "my-service"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.source_id == "my-service"

    def test_json_with_source_id_in_raw_takes_precedence(self):
        """Test that source_id in RawLog takes precedence over parsed one."""
        raw = RawLog(
            source_id="raw-service",
            message='{"serviceName": "parsed-service"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.source_id == "raw-service"

    def test_json_with_error_message_and_type(self):
        """Test parsing JSON with errorMessage and errorType."""
        raw = RawLog(
            source_id="test-service",
            message='{"errorMessage": "division by zero", "errorType": "ZeroDivisionError"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.level == "ERROR"
        assert "ZeroDivisionError: division by zero" in result.message

    def test_json_with_error_message_and_custom_message(self):
        """Test parsing JSON with both error fields and message."""
        raw = RawLog(
            source_id="test-service",
            message='{"errorMessage": "connection refused", "errorType": "ConnectionError", "message": "Failed to connect to database"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.level == "ERROR"
        # Should combine error type, error message, and original message
        assert "ConnectionError" in result.message
        assert "connection refused" in result.message
        assert "Failed to connect to database" in result.message

    def test_json_with_error_type_only(self):
        """Test parsing JSON with only errorType."""
        raw = RawLog(
            source_id="test-service",
            message='{"errorType": "ValueError"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.message == "ValueError error occurred"

    def test_json_with_timeout_keyword(self):
        """Test parsing JSON with 'timeout' keyword sets appropriate defaults."""
        raw = RawLog(
            source_id="test-service",
            message='{"timeout": true}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.level == "ERROR"
        assert result.message == "Timeout: time limit exceeded"

    def test_json_comprehensive_log_entry(self):
        """Test parsing a comprehensive JSON log entry with all fields."""
        raw = RawLog(
            source_id="lambda-service",
            message="""{
                "timestamp": "2026-03-01T11:34:48Z",
                "level": "ERROR",
                "message": "Function execution failed",
                "requestId": "e47d4d85-d84d-44d8-ad16-7cbbee79b3b3",
                "errorMessage": "division by zero",
                "errorType": "ZeroDivisionError",
                "userId": "user123",
                "functionName": "processData",
                "duration": 5432,
                "memoryUsage": 128
            }""",
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.source_id == "lambda-service"
        assert result.level == "ERROR"
        assert result.request_id == "e47d4d85-d84d-44d8-ad16-7cbbee79b3b3"
        assert "ZeroDivisionError" in result.message
        assert "division by zero" in result.message
        assert result.timestamp == datetime.fromisoformat("2026-03-01T11:34:48Z")
        # Extra parameters
        assert result.parameters["userId"] == "user123"
        assert result.parameters["functionName"] == "processData"
        assert result.parameters["duration"] == 5432
        assert result.parameters["memoryUsage"] == 128

    def test_json_with_msg_key_variant(self):
        """Test parsing JSON with 'msg' key instead of 'message'."""
        raw = RawLog(
            source_id="test-service",
            message='{"msg": "Alternative message key"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.message == "Alternative message key"

    def test_json_with_severity_key_variant(self):
        """Test parsing JSON with 'severity' key instead of 'level'."""
        raw = RawLog(
            source_id="test-service",
            message='{"severity": "WARN"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.level == "WARN"

    def test_json_with_at_timestamp(self):
        """Test parsing JSON with '@timestamp' key (Elasticsearch style)."""
        raw = RawLog(
            source_id="test-service",
            message='{"@timestamp": "2026-03-01T11:34:48Z", "message": "test"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.timestamp == datetime.fromisoformat("2026-03-01T11:34:48Z")

    def test_json_with_time_key_variant(self):
        """Test parsing JSON with 'time' key variant."""
        raw = RawLog(
            source_id="test-service",
            message='{"time": "2026-03-01T11:34:48Z"}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.timestamp == datetime.fromisoformat("2026-03-01T11:34:48Z")

    def test_json_with_all_level_variants(self):
        """Test all supported level key variants."""
        level_keys = ["level", "severity", "log_level", "logLevel"]
        for key in level_keys:
            raw = RawLog(
                source_id="test-service",
                message=f'{{"{key}": "ERROR"}}',
                timestamp=1772364888,
            )
            result = parse_log(raw)
            assert result.level == "ERROR", f"Failed for key: {key}"

    def test_json_with_all_timestamp_variants(self):
        """Test all supported timestamp key variants."""
        timestamp_keys = ["timestamp", "@timestamp", "time", "ts"]
        for key in timestamp_keys:
            raw = RawLog(
                source_id="test-service",
                message=f'{{"{key}": "2026-03-01T11:34:48Z"}}',
                timestamp=1772364888,
            )
            result = parse_log(raw)
            expected_ts = datetime.fromisoformat("2026-03-01T11:34:48Z")
            assert result.timestamp == expected_ts, f"Failed for key: {key}"

    def test_json_non_dict_falls_back_to_text_parser(self):
        """Test that JSON array falls back to text parsing."""
        raw = RawLog(
            source_id="test-service",
            message='["not", "a", "dict"]',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "text"

    def test_json_with_nested_objects(self):
        """Test parsing JSON with nested objects in extra parameters."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "metadata": {"user": "john", "session": "abc123"}}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.parameters["metadata"] == {"user": "john", "session": "abc123"}

    def test_json_with_array_in_parameters(self):
        """Test parsing JSON with array values in extra parameters."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "tags": ["production", "api", "v2"]}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.parameters["tags"] == ["production", "api", "v2"]

    def test_json_null_and_boolean_values(self):
        """Test parsing JSON with null and boolean values."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "active": false, "count": null}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.parameters["active"] is False
        assert result.parameters["count"] is None

    def test_json_with_numeric_values(self):
        """Test parsing JSON with various numeric types."""
        raw = RawLog(
            source_id="test-service",
            message='{"timestamp": "2026-03-01T11:34:48Z", "integer": 42, "float": 3.14, "negative": -10}',
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.parameters["integer"] == 42
        assert result.parameters["float"] == 3.14
        assert result.parameters["negative"] == -10

    def test_raw_field_preserved(self):
        """Test that the raw JSON string is preserved in the result."""
        original_message = '{"timestamp": "2026-03-01T11:34:48Z", "message": "test"}'
        raw = RawLog(
            source_id="test-service",
            message=original_message,
            timestamp=1772364888,
        )
        result = parse_log(raw)

        assert result.kind == "json"
        assert result.raw == original_message
