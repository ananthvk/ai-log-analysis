from datetime import datetime

from log_analyser.core.fingerprint import (
    create_fingerprint,
    create_fingerprint_with_stack_trace,
)
from log_analyser.core.log import ParsedLog
from log_analyser.core.normalizer import DefaultNormalizer


class TestCreateFingerprint:
    """Test suite for create_fingerprint function (without stack trace)."""

    def test_same_message_returns_same_fingerprint(self):
        """Test that identical messages produce the same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection failed to database",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection failed to database",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_different_messages_return_different_fingerprints(self):
        """Test that different messages produce different fingerprints."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection timeout",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 != fp2

    def test_different_levels_change_fingerprint(self):
        """Test that different log levels produce different fingerprints."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="WARN",
            parameters={},
            message="Connection failed",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 != fp2

    def test_uuid_normalized_to_same_fingerprint(self):
        """Test that messages with different UUIDs produce the same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="User 550e8400-e29b-41d4-a716-446655440000 failed to login",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="User 6ba7b810-9dad-11d1-80b4-00c04fd430c8 failed to login",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_email_normalized_to_same_fingerprint(self):
        """Test that messages with different emails produce the same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Failed to send email to alice@example.com",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Failed to send email to bob@test.org",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_ipv4_normalized_to_same_fingerprint(self):
        """Test that messages with different IPv4 addresses produce the same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection refused from 192.168.1.1",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection refused from 10.0.0.1",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_hex_normalized_to_same_fingerprint(self):
        """Test that messages with different hex values produce the same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Memory access violation at 0x1A2B3C",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Memory access violation at 0xDEADBEEF",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_quoted_string_normalized_to_same_fingerprint(self):
        """Test that messages with different quoted strings produce the same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message='Error in "moduleA" at line 42',
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message='Error in "moduleB" at line 42',
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_multiple_patterns_simultaneously(self):
        """Test message with UUID, email, IPv4, hex, and quoted string all changing."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message='User 550e8400-e29b-41d4-a716-446655440000 at alice@test.com from 192.168.1.1 said "hello" at 0x1A2B',
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message='User 6ba7b810-9dad-11d1-80b4-00c04fd430c8 at bob@test.org from 10.0.0.1 said "world" at 0xDEADBEEF',
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        assert fp1 == fp2

    def test_whitespace_handling(self):
        """Test that whitespace is stripped from ends but internal spaces preserved."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="  Connection failed  ",
            request_id=None,
        )

        fp1 = create_fingerprint(log1, normalizer)
        fp2 = create_fingerprint(log2, normalizer)
        # The strip() is applied to message, so should be same
        assert fp1 == fp2


class TestCreateFingerprintWithStackTrace:
    """Test suite for create_fingerprint_with_stack_trace function."""

    def test_same_log_and_stack_trace_returns_same_fingerprint(self):
        """Test that identical logs with same stack trace produce same fingerprint."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["line 1", "line 2", "line 3"]},
            message="Connection failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["line 1", "line 2", "line 3"]},
            message="Connection failed",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        assert fp1 == fp2

    def test_different_stack_trace_changes_fingerprint(self):
        """Test that different stack traces produce different fingerprints."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["line A", "line B", "line C"]},
            message="Connection failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["line X", "line Y", "line Z"]},
            message="Connection failed",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        assert fp1 != fp2

    def test_no_stack_trace_treated_as_empty(self):
        """Test that missing stack trace is treated as empty string."""
        normalizer = DefaultNormalizer()
        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={},
            message="Connection failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": None},
            message="Connection failed",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        assert fp1 == fp2

    def test_stack_trace_list_respects_max_lines(self):
        """Test that only first STACK_TRACE_MAX_LINES (5) lines are considered from list."""
        normalizer = DefaultNormalizer()

        # Create a stack trace with 10 lines
        base_stack = [
            '  File "/app/module.py", line 25, in process',
            "    result = calculate()",
            '  File "/app/calc.py", line 10, in calculate',
            "    value = data[user_id]",
            '  File "/app/data.py", line 100, in __getitem__',
            "    return self._cache[key]",
            '  File "/app/cache.py", line 50, in get',
            "    raise NotFoundError()",
            '  File "/app/errors.py", line 5, in __init__',
            '    super().__init__("Not found")',
        ]

        # Same stack trace but with different data after line 5
        stack_trace_1 = base_stack.copy()
        stack_trace_2 = base_stack.copy()
        # Change lines 8-10 (beyond STACK_TRACE_MAX_LINES)
        stack_trace_2[7] = '  File "/app/different.py", line 99, in something_else'
        stack_trace_2[8] = "    return different_value"
        stack_trace_2[9] = '    super().__init__("Different error")'

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_1},
            message="KeyError occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_2},
            message="KeyError occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since changes are after STACK_TRACE_MAX_LINES
        assert fp1 == fp2

    def test_stack_trace_change_at_6th_line_changes_fingerprint(self):
        """Test that change at 6th line (within limit) changes fingerprint."""
        normalizer = DefaultNormalizer()

        base_stack = [
            '  File "/app/module.py", line 25, in process',
            "    result = calculate()",
            '  File "/app/calc.py", line 10, in calculate',
            "    value = data[user_id]",
            '  File "/app/data.py", line 100, in __getitem__',
            "    return self._cache[key]",  # Line 6 (index 5) - within limit
        ]

        stack_trace_1 = base_stack.copy()
        stack_trace_2 = base_stack.copy()
        # Change line 6
        stack_trace_2[5] = "    return self._different[key]"

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_1},
            message="KeyError occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_2},
            message="KeyError occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be different since change is at line 6 (within STACK_TRACE_MAX_LINES)
        assert fp1 != fp2

    def test_stack_trace_change_at_4th_line_changes_fingerprint(self):
        """Test that change at 4th line changes fingerprint."""
        normalizer = DefaultNormalizer()

        base_stack = [
            '  File "/app/module.py", line 25, in process',
            "    result = calculate()",
            '  File "/app/calc.py", line 10, in calculate',
            "    value = data[user_id]",  # Line 4 (index 3)
            '  File "/app/data.py", line 100, in __getitem__',
        ]

        stack_trace_1 = base_stack.copy()
        stack_trace_2 = base_stack.copy()
        # Change line 4
        stack_trace_2[3] = "    value = data[different_id]"

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_1},
            message="KeyError occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_2},
            message="KeyError occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be different since change is at line 4
        assert fp1 != fp2

    def test_stack_trace_string_only_first_100_chars_considered(self):
        """Test that only first 100 characters are considered for string stack trace."""
        normalizer = DefaultNormalizer()

        # Create a long string (> 100 chars)
        long_stack_1 = "A" * 50 + "UNIQUE1" + "B" * 50 + "IGNORED1" + "C" * 50
        long_stack_2 = "A" * 50 + "UNIQUE2" + "B" * 50 + "IGNORED2" + "C" * 50

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": long_stack_1},
            message="Error occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": long_stack_2},
            message="Error occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be different since UNIQUE parts are in first 100 chars
        assert fp1 != fp2

    def test_stack_trace_string_change_after_100_chars_same_fingerprint(self):
        """Test that changes after 100 chars don't affect fingerprint for string stack trace."""
        normalizer = DefaultNormalizer()

        # Two strings that differ only after 100 characters
        base = "A" * 95
        stack_trace_1 = base + "UNIQUE1" + "B" * 50
        stack_trace_2 = base + "UNIQUE2" + "C" * 50

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_1},
            message="Error occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_2},
            message="Error occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since changes are after 100 chars
        assert fp1 == fp2

    def test_stack_trace_normalization_applied(self):
        """Test that normalization is applied to stack trace."""
        normalizer = DefaultNormalizer()

        stack_trace_1 = [
            '  File "/app/module.py", line 25, in process',
            "    user_id = 550e8400-e29b-41d4-a716-446655440000",  # UUID in stack
        ]
        stack_trace_2 = [
            '  File "/app/module.py", line 25, in process',
            "    user_id = 6ba7b810-9dad-11d1-80b4-00c04fd430c8",  # Different UUID
        ]

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_1},
            message="Error occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_2},
            message="Error occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since UUIDs are normalized
        assert fp1 == fp2

    def test_message_and_stack_trace_both_normalized(self):
        """Test that both message and stack trace are normalized."""
        normalizer = DefaultNormalizer()

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={
                "stackTrace": [
                    "Error for user 550e8400-e29b-41d4-a716-446655440000 at 192.168.1.1",
                ]
            },
            message="User 550e8400-e29b-41d4-a716-446655440000 from 192.168.1.1 failed",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={
                "stackTrace": [
                    "Error for user 6ba7b810-9dad-11d1-80b4-00c04fd430c8 at 10.0.0.1",
                ]
            },
            message="User 6ba7b810-9dad-11d1-80b4-00c04fd430c8 from 10.0.0.1 failed",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since both message and stack trace are normalized
        assert fp1 == fp2

    def test_stack_trace_list_with_non_string_elements(self):
        """Test that non-string elements in stack trace list are converted to string."""
        normalizer = DefaultNormalizer()

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["line 1", 12345, "line 3"]},
            message="Error occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["line 1", "12345", "line 3"]},
            message="Error occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since number is converted to string
        assert fp1 == fp2

    def test_stack_trace_case_normalized(self):
        """Test that stack trace is lowercased."""
        normalizer = DefaultNormalizer()

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["FILE /APP/MODULE.PY", "ERROR MESSAGE"]},
            message="Error occurred",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": ["file /app/module.py", "error message"]},
            message="Error occurred",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since stack trace is lowercased
        assert fp1 == fp2

    def test_complex_stack_trace_with_patterns(self):
        """Test complex stack trace with multiple normalizable patterns."""
        normalizer = DefaultNormalizer()

        stack_trace_1 = [
            '  File "/app/module_abc.py", line 25, in process_request',
            '    user = User("alice@test.com", id="550e8400-e29b-41d4-a716-446655440000")',
            '    addr = "192.168.1.1"',
            "    ptr = 0x1A2B3C",
        ]
        stack_trace_2 = [
            '  File "/app/module_xyz.py", line 25, in process_request',
            '    user = User("bob@test.org", id="6ba7b810-9dad-11d1-80b4-00c04fd430c8")',
            '    addr = "10.0.0.1"',
            "    ptr = 0xDEADBEEF",
        ]

        log1 = ParsedLog(
            raw="raw1",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_1},
            message="Error in module",
            request_id=None,
        )
        log2 = ParsedLog(
            raw="raw2",
            kind="json",
            source_id="service",
            timestamp=datetime.now(),
            level="ERROR",
            parameters={"stackTrace": stack_trace_2},
            message="Error in module",
            request_id=None,
        )

        fp1 = create_fingerprint_with_stack_trace(log1, normalizer)
        fp2 = create_fingerprint_with_stack_trace(log2, normalizer)
        # Should be same since all patterns are normalized
        assert fp1 == fp2
