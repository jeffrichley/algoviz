"""Timing tracking and configuration for ALGOViz.

This module provides timing tracking functionality to record actual vs expected
durations for algorithm visualization beats and actions.
"""

import csv
import json
from datetime import datetime
from pathlib import Path
from typing import Any

from pydantic import BaseModel, Field


class TimingRecord(BaseModel):
    """A single timing record for a beat/action."""
    beat_name: str = Field(..., description="Unique identifier for the beat (e.g., '0-0-0')")
    action: str = Field(..., description="Action that was executed")
    expected_duration: float = Field(..., description="Expected duration in seconds")
    actual_duration: float = Field(..., description="Actual duration in seconds")
    variance: float = Field(..., description="Difference between actual and expected")
    mode: str = Field(..., description="Timing mode used (draft, normal, fast)")
    act: str = Field(..., description="Act name (e.g., 'Act 1')")
    shot: str = Field(..., description="Shot name (e.g., 'Shot 1')")
    timestamp: float = Field(default_factory=lambda: datetime.now().timestamp())

    class Config:
        """Pydantic configuration."""
        extra = "forbid"


class TimingTracker(BaseModel):
    """Tracks timing records for algorithm visualization beats."""
    records: list[TimingRecord] = Field(default_factory=list, description="List of timing records")

    def log(
        self,
        beat_name: str,
        action: str,
        expected: float,
        actual: float,
        mode: str,
        act: str,
        shot: str
    ) -> None:
        """Log a timing record."""
        variance = actual - expected
        record = TimingRecord(
            beat_name=beat_name,
            action=action,
            expected_duration=expected,
            actual_duration=actual,
            variance=variance,
            mode=mode,
            act=act,
            shot=shot
        )
        self.records.append(record)

    def export_csv(self, path: Path) -> None:
        """Export timing records to CSV."""
        with open(path, 'w', newline='') as f:
            writer = csv.writer(f)
            writer.writerow([
                'beat_name', 'action', 'expected_duration', 'actual_duration',
                'variance', 'mode', 'act', 'shot', 'timestamp'
            ])
            for record in self.records:
                writer.writerow([
                    record.beat_name, record.action, record.expected_duration,
                    record.actual_duration, record.variance, record.mode,
                    record.act, record.shot, record.timestamp
                ])

    def export_json(self, path: Path) -> None:
        """Export timing records to JSON."""
        data = {
            'records': [record.dict() for record in self.records],
            'summary': self._generate_summary()
        }
        with open(path, 'w') as f:
            json.dump(data, f, indent=2)

    def _generate_summary(self) -> dict[str, Any]:
        """Generate timing summary statistics."""
        if not self.records:
            return {}

        total_expected = sum(r.expected_duration for r in self.records)
        total_actual = sum(r.actual_duration for r in self.records)

        return {
            'total_expected_duration': total_expected,
            'total_actual_duration': total_actual,
            'total_variance': total_actual - total_expected,
            'average_variance': sum(r.variance for r in self.records) / len(self.records),
            'record_count': len(self.records)
        }

    class Config:
        """Pydantic configuration."""
        extra = "forbid"
