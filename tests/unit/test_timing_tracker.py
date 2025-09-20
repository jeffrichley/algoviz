"""Unit tests for TimingTracker functionality."""

import json
import tempfile
from pathlib import Path
from unittest.mock import patch

import pytest

from agloviz.config.timing import TimingTracker


@pytest.mark.unit
class TestTimingTracker:
    """Test TimingTracker functionality for performance monitoring."""

    def test_initialization(self):
        """Test TimingTracker initialization."""
        tracker = TimingTracker()
        assert tracker.records == []
        assert tracker.console is not None

    def test_log_timing_record(self):
        """Test logging a basic timing record."""
        tracker = TimingTracker()

        tracker.log(
            beat_name="test_beat",
            action="search",
            expected=1.0,
            actual=1.1,
            mode="normal",
            act="act1",
            shot="shot1"
        )

        assert len(tracker.records) == 1
        record = tracker.records[0]
        assert record.beat_name == "test_beat"
        assert record.action == "search"
        assert record.expected_duration == 1.0
        assert record.actual_duration == 1.1
        assert record.mode == "normal"
        assert record.act == "act1"
        assert record.shot == "shot1"
        assert record.timestamp > 0

    def test_log_timing_record_minimal(self):
        """Test logging with minimal required parameters."""
        tracker = TimingTracker()

        tracker.log(
            beat_name="minimal_beat",
            action="render",
            expected=0.5,
            actual=0.6,
            mode="draft"
        )

        assert len(tracker.records) == 1
        record = tracker.records[0]
        assert record.beat_name == "minimal_beat"
        assert record.act is None
        assert record.shot is None

    @patch('agloviz.config.timing.console')
    def test_timing_variance_warning(self, mock_console):
        """Test that timing variance warnings are displayed."""
        tracker = TimingTracker()

        # 30% variance should trigger warning
        tracker.log("slow_beat", "search", 1.0, 1.3, "normal")

        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "⚠️" in call_args
        assert "Timing variance" in call_args
        assert "slow_beat" in call_args
        assert "30.0%" in call_args

    @patch('agloviz.config.timing.console')
    def test_timing_variance_error(self, mock_console):
        """Test that large timing variance shows error indicator."""
        tracker = TimingTracker()

        # 60% variance should trigger error indicator
        tracker.log("very_slow_beat", "render", 1.0, 1.6, "fast")

        mock_console.print.assert_called_once()
        call_args = mock_console.print.call_args[0][0]
        assert "🔴" in call_args
        assert "60.0%" in call_args

    @patch('agloviz.config.timing.console')
    def test_no_variance_warning_for_small_differences(self, mock_console):
        """Test that small timing differences don't trigger warnings."""
        tracker = TimingTracker()

        # 10% variance should not trigger warning
        tracker.log("good_beat", "search", 1.0, 1.1, "normal")

        mock_console.print.assert_not_called()

    @patch('agloviz.config.timing.console')
    def test_zero_expected_duration_handling(self, mock_console):
        """Test handling of zero expected duration."""
        tracker = TimingTracker()

        # Zero expected duration should not cause division by zero
        tracker.log("instant_beat", "check", 0.0, 0.1, "draft")

        # Should not crash and should not show warning (variance calculation handled)
        mock_console.print.assert_not_called()

    def test_export_csv(self):
        """Test exporting timing records to CSV."""
        tracker = TimingTracker()

        # Add some test records
        tracker.log("beat1", "search", 1.0, 1.1, "normal", "act1", "shot1")
        tracker.log("beat2", "render", 0.5, 0.6, "draft", "act2", "shot2")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            csv_path = f.name

        try:
            tracker.export_csv(csv_path)

            # Verify file was created and has content
            csv_file = Path(csv_path)
            assert csv_file.exists()

            content = csv_file.read_text()

            # Check CSV headers
            assert "beat_name" in content
            assert "action" in content
            assert "expected_duration" in content
            assert "actual_duration" in content
            assert "mode" in content
            assert "timestamp" in content

            # Check data rows
            assert "beat1" in content
            assert "beat2" in content
            assert "search" in content
            assert "render" in content
            assert "normal" in content
            assert "draft" in content

        finally:
            Path(csv_path).unlink(missing_ok=True)

    def test_export_json(self):
        """Test exporting timing records to JSON."""
        tracker = TimingTracker()

        # Add test records
        tracker.log("json_beat1", "algorithm", 2.0, 2.1, "normal", "act_a", "shot_x")
        tracker.log("json_beat2", "visualization", 1.5, 1.4, "fast")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        try:
            tracker.export_json(json_path)

            # Verify file was created and has valid JSON
            json_file = Path(json_path)
            assert json_file.exists()

            with open(json_path) as f:
                records = json.load(f)

            # Should be a list of records
            assert isinstance(records, list)
            assert len(records) == 2

            # Check first record
            record1 = records[0]
            assert record1["beat_name"] == "json_beat1"
            assert record1["action"] == "algorithm"
            assert record1["expected_duration"] == 2.0
            assert record1["actual_duration"] == 2.1
            assert record1["mode"] == "normal"
            assert record1["act"] == "act_a"
            assert record1["shot"] == "shot_x"

            # Check second record (with None values)
            record2 = records[1]
            assert record2["beat_name"] == "json_beat2"
            assert record2["act"] is None
            assert record2["shot"] is None

        finally:
            Path(json_path).unlink(missing_ok=True)

    def test_export_empty_records(self):
        """Test exporting when no records exist."""
        tracker = TimingTracker()

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            json_path = f.name

        try:
            tracker.export_json(json_path)

            with open(json_path) as f:
                records = json.load(f)

            # Should be an empty list
            assert isinstance(records, list)
            assert len(records) == 0

        finally:
            Path(json_path).unlink(missing_ok=True)

    def test_multiple_timing_records(self):
        """Test tracking multiple timing records over time."""
        tracker = TimingTracker()

        # Simulate a series of operations
        operations = [
            ("init", "setup", 0.1, 0.12, "normal"),
            ("search_start", "algorithm", 0.5, 0.48, "fast"),
            ("search_step_1", "algorithm", 0.2, 0.25, "fast"),
            ("search_step_2", "algorithm", 0.2, 0.19, "fast"),
            ("render_frame", "visualization", 0.3, 0.35, "normal"),
            ("cleanup", "teardown", 0.05, 0.04, "normal"),
        ]

        for beat_name, action, expected, actual, mode in operations:
            tracker.log(beat_name, action, expected, actual, mode)

        assert len(tracker.records) == 6

        # Verify records are in order
        beat_names = [record.beat_name for record in tracker.records]
        expected_names = [op[0] for op in operations]
        assert beat_names == expected_names

        # Verify different action types are tracked
        actions = {record.action for record in tracker.records}
        assert actions == {"setup", "algorithm", "visualization", "teardown"}

        # Verify different modes are tracked
        modes = {record.mode for record in tracker.records}
        assert modes == {"normal", "fast"}
