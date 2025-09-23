"""Tests for TimingTracker logging, export, and summary generation."""

import json
import tempfile
from pathlib import Path

import pytest

from agloviz.config.timing import TimingRecord, TimingTracker


class TestTimingTracker:
    """Test TimingTracker functionality."""

    def test_timing_tracker_initialization(self):
        """Test TimingTracker initializes with empty records."""
        tracker = TimingTracker()
        assert tracker.records == []

    def test_timing_record_creation(self):
        """Test TimingRecord creation with all fields."""
        record = TimingRecord(
            beat_name="0-0-0",
            action="show_title",
            expected_duration=1.0,
            actual_duration=0.8,
            variance=-0.2,
            mode="normal",
            act="Act 1",
            shot="Shot 1",
            timestamp=1234567890.0
        )

        assert record.beat_name == "0-0-0"
        assert record.action == "show_title"
        assert record.expected_duration == 1.0
        assert record.actual_duration == 0.8
        assert record.variance == pytest.approx(-0.2)
        assert record.mode == "normal"
        assert record.act == "Act 1"
        assert record.shot == "Shot 1"
        assert record.timestamp == 1234567890.0

    def test_timing_record_auto_timestamp(self):
        """Test TimingRecord creates timestamp automatically."""
        record = TimingRecord(
            beat_name="0-0-0",
            action="show_title",
            expected_duration=1.0,
            actual_duration=0.8,
            variance=-0.2,
            mode="normal",
            act="Act 1",
            shot="Shot 1"
        )

        assert record.timestamp is not None
        assert isinstance(record.timestamp, float)

    def test_timing_tracker_log(self):
        """Test TimingTracker.log() method."""
        tracker = TimingTracker()

        tracker.log(
            beat_name="0-0-0",
            action="show_title",
            expected=1.0,
            actual=0.8,
            mode="normal",
            act="Act 1",
            shot="Shot 1"
        )

        assert len(tracker.records) == 1
        record = tracker.records[0]
        assert record.beat_name == "0-0-0"
        assert record.action == "show_title"
        assert record.expected_duration == 1.0
        assert record.actual_duration == 0.8
        assert record.variance == pytest.approx(-0.2)
        assert record.mode == "normal"
        assert record.act == "Act 1"
        assert record.shot == "Shot 1"

    def test_timing_tracker_multiple_logs(self):
        """Test TimingTracker with multiple log entries."""
        tracker = TimingTracker()

        # Log multiple records
        tracker.log("0-0-0", "show_title", 1.0, 0.8, "normal", "Act 1", "Shot 1")
        tracker.log("0-0-1", "show_grid", 0.5, 0.6, "normal", "Act 1", "Shot 1")
        tracker.log("1-0-0", "visit_node", 0.8, 0.7, "normal", "Act 2", "Shot 1")

        assert len(tracker.records) == 3
        assert tracker.records[0].beat_name == "0-0-0"
        assert tracker.records[1].beat_name == "0-0-1"
        assert tracker.records[2].beat_name == "1-0-0"

    def test_timing_tracker_export_csv(self):
        """Test TimingTracker CSV export."""
        tracker = TimingTracker()

        # Add some test data
        tracker.log("0-0-0", "show_title", 1.0, 0.8, "normal", "Act 1", "Shot 1")
        tracker.log("0-0-1", "show_grid", 0.5, 0.6, "normal", "Act 1", "Shot 1")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.csv', delete=False) as f:
            temp_path = Path(f.name)

        try:
            tracker.export_csv(temp_path)

            # Read and verify CSV content
            with open(temp_path) as f:
                lines = f.readlines()

            assert len(lines) == 3  # Header + 2 data rows
            assert "beat_name,action,expected_duration,actual_duration,variance,mode,act,shot,timestamp" in lines[0]
            assert "0-0-0,show_title,1.0,0.8" in lines[1] and "normal,Act 1,Shot 1" in lines[1]
            assert "0-0-1,show_grid,0.5,0.6" in lines[2] and "normal,Act 1,Shot 1" in lines[2]

        finally:
            temp_path.unlink()

    def test_timing_tracker_export_json(self):
        """Test TimingTracker JSON export."""
        tracker = TimingTracker()

        # Add some test data
        tracker.log("0-0-0", "show_title", 1.0, 0.8, "normal", "Act 1", "Shot 1")
        tracker.log("0-0-1", "show_grid", 0.5, 0.6, "normal", "Act 1", "Shot 1")

        with tempfile.NamedTemporaryFile(mode='w', suffix='.json', delete=False) as f:
            temp_path = Path(f.name)

        try:
            tracker.export_json(temp_path)

            # Read and verify JSON content
            with open(temp_path) as f:
                data = json.load(f)

            assert 'records' in data
            assert 'summary' in data
            assert len(data['records']) == 2
            assert data['records'][0]['beat_name'] == "0-0-0"
            assert data['records'][1]['beat_name'] == "0-0-1"
            assert data['summary']['record_count'] == 2

        finally:
            temp_path.unlink()

    def test_timing_tracker_summary_generation(self):
        """Test TimingTracker summary statistics."""
        tracker = TimingTracker()

        # Add test data with known values
        tracker.log("0-0-0", "show_title", 1.0, 0.8, "normal", "Act 1", "Shot 1")
        tracker.log("0-0-1", "show_grid", 0.5, 0.6, "normal", "Act 1", "Shot 1")
        tracker.log("1-0-0", "visit_node", 0.8, 0.7, "normal", "Act 2", "Shot 1")

        summary = tracker._generate_summary()

        assert summary['total_expected_duration'] == 2.3  # 1.0 + 0.5 + 0.8
        assert summary['total_actual_duration'] == 2.1    # 0.8 + 0.6 + 0.7
        assert summary['total_variance'] == pytest.approx(-0.2)          # 2.1 - 2.3
        assert summary['average_variance'] == pytest.approx(-0.2 / 3)    # -0.2 / 3 records
        assert summary['record_count'] == 3

    def test_timing_tracker_empty_summary(self):
        """Test TimingTracker summary with no records."""
        tracker = TimingTracker()

        summary = tracker._generate_summary()
        assert summary == {}

    def test_timing_tracker_variance_calculation(self):
        """Test variance calculation in log method."""
        tracker = TimingTracker()

        # Test positive variance (actual > expected)
        tracker.log("0-0-0", "show_title", 1.0, 1.2, "normal", "Act 1", "Shot 1")
        assert tracker.records[0].variance == pytest.approx(0.2)

        # Test negative variance (actual < expected)
        tracker.log("0-0-1", "show_grid", 0.5, 0.3, "normal", "Act 1", "Shot 1")
        assert tracker.records[1].variance == pytest.approx(-0.2)

        # Test zero variance (actual == expected)
        tracker.log("1-0-0", "visit_node", 0.8, 0.8, "normal", "Act 2", "Shot 1")
        assert tracker.records[2].variance == 0.0
