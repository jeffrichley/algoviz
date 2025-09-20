"""Timing system for ALGOViz.

This module provides timing configuration and tracking functionality for
consistent pacing across algorithm visualizations.
"""

import csv
import json
from dataclasses import dataclass
from pathlib import Path

from rich.console import Console

console = Console()


@dataclass
class TimingRecord:
    """Record of a single timing event."""
    beat_name: str
    action: str
    expected_duration: float
    actual_duration: float
    mode: str
    timestamp: float
    act: str | None = None
    shot: str | None = None


class TimingTracker:
    """Tracks actual vs expected timing for analysis and debugging."""

    def __init__(self):
        self.records: list[TimingRecord] = []
        self.console = Console()

    def log(
        self,
        beat_name: str,
        action: str,
        expected: float,
        actual: float,
        mode: str,
        act: str | None = None,
        shot: str | None = None,
    ) -> None:
        """Log a timing record for a beat execution.

        Args:
            beat_name: Name of the beat being executed
            action: Action type being performed
            expected: Expected duration in seconds
            actual: Actual duration in seconds
            mode: Timing mode (draft/normal/fast)
            act: Act name (optional)
            shot: Shot name (optional)
        """
        import time

        record = TimingRecord(
            beat_name=beat_name,
            action=action,
            expected_duration=expected,
            actual_duration=actual,
            mode=mode,
            timestamp=time.time(),
            act=act,
            shot=shot,
        )

        self.records.append(record)

        # Log timing discrepancies
        variance = abs(actual - expected) / expected if expected > 0 else 0
        if variance > 0.2:  # More than 20% variance
            status = "⚠️" if variance < 0.5 else "🔴"
            console.print(
                f"{status} Timing variance in {beat_name}: "
                f"expected {expected:.2f}s, actual {actual:.2f}s "
                f"({variance:.1%} difference)"
            )

    def export_csv(self, output_path: str) -> None:
        """Export timing records to CSV file for analysis.

        Args:
            output_path: Path to write CSV file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, 'w', newline='') as csvfile:
                fieldnames = [
                    'beat_name', 'action', 'expected_duration', 'actual_duration',
                    'variance', 'variance_percent', 'mode', 'act', 'shot', 'timestamp'
                ]
                writer = csv.DictWriter(csvfile, fieldnames=fieldnames)

                writer.writeheader()
                for record in self.records:
                    variance = record.actual_duration - record.expected_duration
                    variance_percent = (
                        variance / record.expected_duration * 100
                        if record.expected_duration > 0 else 0
                    )

                    writer.writerow({
                        'beat_name': record.beat_name,
                        'action': record.action,
                        'expected_duration': record.expected_duration,
                        'actual_duration': record.actual_duration,
                        'variance': variance,
                        'variance_percent': variance_percent,
                        'mode': record.mode,
                        'act': record.act,
                        'shot': record.shot,
                        'timestamp': record.timestamp,
                    })

            console.print(f"✅ Timing data exported to: [bold blue]{output_path}[/bold blue]")

        except Exception as e:
            console.print(f"⚠️ Failed to export timing data: {e}")

    def export_json(self, output_path: str) -> None:
        """Export timing records to JSON file for programmatic analysis.

        Args:
            output_path: Path to write JSON file
        """
        try:
            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            records_data = []
            for record in self.records:
                variance = record.actual_duration - record.expected_duration
                variance_percent = (
                    variance / record.expected_duration * 100
                    if record.expected_duration > 0 else 0
                )

                records_data.append({
                    'beat_name': record.beat_name,
                    'action': record.action,
                    'expected_duration': record.expected_duration,
                    'actual_duration': record.actual_duration,
                    'variance': variance,
                    'variance_percent': variance_percent,
                    'mode': record.mode,
                    'act': record.act,
                    'shot': record.shot,
                    'timestamp': record.timestamp,
                })

            with open(output_file, 'w') as f:
                json.dump(records_data, f, indent=2)

            console.print(f"✅ Timing data exported to: [bold blue]{output_path}[/bold blue]")

        except Exception as e:
            console.print(f"⚠️ Failed to export timing data: {e}")

    def get_summary_stats(self) -> dict[str, float]:
        """Get summary statistics for timing analysis."""
        if not self.records:
            return {}

        variances = []
        for record in self.records:
            if record.expected_duration > 0:
                variance_percent = abs(
                    record.actual_duration - record.expected_duration
                ) / record.expected_duration * 100
                variances.append(variance_percent)

        if not variances:
            return {}

        return {
            'total_records': len(self.records),
            'mean_variance_percent': sum(variances) / len(variances),
            'max_variance_percent': max(variances),
            'min_variance_percent': min(variances),
            'records_over_20_percent': sum(1 for v in variances if v > 20),
            'records_over_50_percent': sum(1 for v in variances if v > 50),
        }

    def print_summary(self) -> None:
        """Print a summary of timing statistics to console."""
        stats = self.get_summary_stats()

        if not stats:
            console.print("📊 No timing records available")
            return

        console.print("\n📊 [bold blue]Timing Summary Statistics[/bold blue]")
        console.print(f"Total records: {stats['total_records']}")
        console.print(f"Mean variance: {stats['mean_variance_percent']:.1f}%")
        console.print(f"Max variance: {stats['max_variance_percent']:.1f}%")
        console.print(f"Records >20% variance: {stats['records_over_20_percent']}")
        console.print(f"Records >50% variance: {stats['records_over_50_percent']}")

        # Color-coded status
        if stats['mean_variance_percent'] < 10:
            console.print("✅ [green]Timing accuracy: Excellent[/green]")
        elif stats['mean_variance_percent'] < 20:
            console.print("⚠️ [yellow]Timing accuracy: Good[/yellow]")
        else:
            console.print("🔴 [red]Timing accuracy: Needs attention[/red]")

    def clear(self) -> None:
        """Clear all timing records."""
        self.records.clear()
        console.print("🗑️ Timing records cleared")


def create_timing_tracker() -> TimingTracker:
    """Factory function to create a new TimingTracker instance."""
    return TimingTracker()
