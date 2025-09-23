"""Structured logging system for ALGOViz.

This module provides comprehensive logging with error taxonomy integration,
rich console output, and structured metadata for debugging and monitoring.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any

from rich.console import Console
from rich.logging import RichHandler
from rich.panel import Panel
from rich.text import Text

from .errors import AGLOVizError, ErrorSeverity


class AGLOVizLogger:
    """Structured logger with rich console output and error taxonomy integration."""

    def __init__(
        self,
        name: str = "agloviz",
        level: str = "INFO",
        enable_rich: bool = True,
        enable_file_logging: bool = False,
        log_file_path: str | None = None,
    ):
        self.name = name
        self.console = Console() if enable_rich else None
        self.debug_mode = False

        # Set up Python logger
        self.logger = logging.getLogger(name)
        self.logger.setLevel(getattr(logging, level.upper()))

        # Clear existing handlers
        self.logger.handlers.clear()

        # Add rich console handler if enabled
        if enable_rich:
            rich_handler = RichHandler(
                console=self.console,
                show_time=True,
                show_path=True,
                markup=True,
                rich_tracebacks=True,
            )
            rich_handler.setFormatter(
                logging.Formatter(
                    fmt="%(message)s",
                    datefmt="[%X]",
                )
            )
            self.logger.addHandler(rich_handler)

        # Add file handler if enabled
        if enable_file_logging:
            file_path = (
                log_file_path
                or f"logs/{name}_{datetime.now().strftime('%Y%m%d_%H%M%S')}.log"
            )
            Path(file_path).parent.mkdir(parents=True, exist_ok=True)

            file_handler = logging.FileHandler(file_path)
            file_handler.setFormatter(
                logging.Formatter(
                    fmt="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
                    datefmt="%Y-%m-%d %H:%M:%S",
                )
            )
            self.logger.addHandler(file_handler)

    def enable_debug_mode(self, enabled: bool = True) -> None:
        """Enable or disable debug mode with enhanced output."""
        self.debug_mode = enabled
        if enabled:
            self.logger.setLevel(logging.DEBUG)
            if self.console:
                self.console.print(
                    "🐛 [bold yellow]Debug mode enabled[/bold yellow] - Full stack traces will be shown"
                )
        else:
            self.logger.setLevel(logging.INFO)

    def log_error(
        self,
        error: AGLOVizError,
        additional_context: dict[str, Any] | None = None,
        show_rich: bool = True,
    ) -> None:
        """Log an ALGOViz error with structured metadata.

        Args:
            error: The AGLOVizError instance to log
            additional_context: Additional context metadata
            show_rich: Whether to display rich formatted output
        """
        # Create structured log entry
        log_data = error.to_dict()
        if additional_context:
            log_data["additional_context"] = additional_context

        # Log to Python logger with structured data
        self.logger.error(
            "ALGOViz Error: %s",
            error.format_message(),
            extra={"structured_data": log_data},
        )

        # Display rich formatted error if enabled
        if show_rich and self.console:
            error.format_rich_message(self.console)

        # Show debug information if in debug mode
        if self.debug_mode and self.console:
            self._show_debug_info(error, additional_context)

    def log_warning(
        self,
        message: str,
        category: str = "General",
        context: str | None = None,
        suggestions: list[str] | None = None,
    ) -> None:
        """Log a warning message with optional suggestions.

        Args:
            message: Warning message
            category: Warning category
            context: Optional context information
            suggestions: Optional list of suggestions
        """
        # Create structured warning
        warning_data = {
            "category": category,
            "message": message,
            "context": context,
            "suggestions": suggestions or [],
            "severity": "warning",
        }

        # Log to Python logger
        self.logger.warning(
            "Warning [%s]: %s",
            category,
            message,
            extra={"structured_data": warning_data},
        )

        # Display rich formatted warning
        if self.console:
            warning_text = Text()
            warning_text.append("⚠️ Warning", style="bold yellow")

            if context:
                warning_text.append(f" [{context}]", style="dim")

            warning_text.append(f": {message}", style="yellow")

            if suggestions:
                warning_text.append("\n🔍 Suggestions:", style="bold blue")
                for i, suggestion in enumerate(suggestions, 1):
                    warning_text.append(f"\n  {i}. {suggestion}", style="cyan")

            self.console.print(warning_text)

    def log_suggestion(
        self,
        original: str,
        suggestions: list[str],
        context: str | None = None,
    ) -> None:
        """Log suggestions for user input corrections.

        Args:
            original: The original invalid input
            suggestions: List of suggested corrections
            context: Optional context for the suggestion
        """
        if not suggestions:
            return

        suggestion_data = {
            "original": original,
            "suggestions": suggestions,
            "context": context,
        }

        self.logger.info(
            "Suggestions for '%s': %s",
            original,
            ", ".join(suggestions),
            extra={"structured_data": suggestion_data},
        )

        if self.console:
            suggestion_text = Text()
            suggestion_text.append("💡 Did you mean", style="bold blue")

            if context:
                suggestion_text.append(f" [{context}]", style="dim")

            suggestion_text.append(":", style="bold blue")

            for i, suggestion in enumerate(suggestions, 1):
                suggestion_text.append(f"\n  {i}. {suggestion}", style="cyan")

            self.console.print(suggestion_text)

    def log_info(self, message: str, **kwargs: Any) -> None:
        """Log an informational message."""
        self.logger.info(message, extra={"structured_data": kwargs})

        if self.console:
            self.console.print(f"ℹ️ {message}", style="blue")

    def log_success(self, message: str, **kwargs: Any) -> None:
        """Log a success message."""
        self.logger.info(f"SUCCESS: {message}", extra={"structured_data": kwargs})

        if self.console:
            self.console.print(f"✅ {message}", style="bold green")

    def log_debug(self, message: str, **kwargs: Any) -> None:
        """Log a debug message (only shown in debug mode)."""
        self.logger.debug(message, extra={"structured_data": kwargs})

        if self.debug_mode and self.console:
            self.console.print(f"🐛 [dim]{message}[/dim]")

    def _show_debug_info(
        self,
        error: AGLOVizError,
        additional_context: dict[str, Any] | None = None,
    ) -> None:
        """Show detailed debug information for an error."""
        if not self.console:
            return

        debug_text = Text()
        debug_text.append("🐛 Debug Information:\n", style="bold yellow")

        # Error metadata
        debug_text.append("📊 Error Metadata:\n", style="bold")
        for key, value in error.metadata.items():
            debug_text.append(f"  {key}: {value}\n", style="dim")

        # Context metadata
        if error.context:
            debug_text.append("\n📍 Context Metadata:\n", style="bold")
            for key, value in error.context.get_metadata().items():
                debug_text.append(f"  {key}: {value}\n", style="dim")

        # Additional context
        if additional_context:
            debug_text.append("\n🔍 Additional Context:\n", style="bold")
            for key, value in additional_context.items():
                debug_text.append(f"  {key}: {value}\n", style="dim")

        # JSON representation
        debug_text.append("\n📋 JSON Representation:\n", style="bold")
        debug_text.append(error.to_json(), style="dim")

        panel = Panel(
            debug_text,
            title="[bold yellow]Debug Information[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

        self.console.print(panel)

    def aggregate_errors(self, errors: list[AGLOVizError]) -> None:
        """Display multiple errors in an aggregated format.

        Args:
            errors: List of errors to display together
        """
        if not errors:
            return

        if len(errors) == 1:
            self.log_error(errors[0])
            return

        error_groups = self._group_errors_by_category(errors)
        self._log_errors_individually(errors)
        self._display_aggregated_output(errors, error_groups)

    def _group_errors_by_category(
        self, errors: list[AGLOVizError]
    ) -> dict[str, list[AGLOVizError]]:
        """Group errors by category."""
        error_groups: dict[str, list[AGLOVizError]] = {}
        for error in errors:
            category = error.category
            if category not in error_groups:
                error_groups[category] = []
            error_groups[category].append(error)
        return error_groups

    def _log_errors_individually(self, errors: list[AGLOVizError]) -> None:
        """Log each error individually for structured logging."""
        for error in errors:
            self.logger.error(
                "Aggregated Error: %s",
                error.format_message(),
                extra={"structured_data": error.to_dict()},
            )

    def _display_aggregated_output(
        self, errors: list[AGLOVizError], error_groups: dict[str, list[AGLOVizError]]
    ) -> None:
        """Display aggregated rich output."""
        if not self.console:
            return

        self.console.print(f"\n❌ [bold red]Found {len(errors)} errors:[/bold red]\n")

        for category, category_errors in error_groups.items():
            self._display_category_errors(category, category_errors)

    def _display_category_errors(
        self, category: str, category_errors: list[AGLOVizError]
    ) -> None:
        """Display errors for a specific category."""
        self.console.print(
            f"📂 [bold]{category}[/bold] ({len(category_errors)} errors):"
        )

        for i, error in enumerate(category_errors, 1):
            self._display_single_error(i, error)

        self.console.print()  # Empty line between categories

    def _display_single_error(self, index: int, error: AGLOVizError) -> None:
        """Display a single error with its details."""
        location = (
            error.context.format_location() if error.context else "Unknown location"
        )
        self.console.print(f"  {index}. [{location}] {error.issue}")

        if error.suggestions:
            suggestions_str = ", ".join(error.suggestions[:2])
            self.console.print(f"     💡 Try: {suggestions_str}", style="cyan")

    def export_error_log(self, output_path: str, errors: list[AGLOVizError]) -> None:
        """Export errors to a structured JSON file for analysis.

        Args:
            output_path: Path to write the error log
            errors: List of errors to export
        """
        try:
            export_data = {
                "timestamp": datetime.now().isoformat(),
                "total_errors": len(errors),
                "errors": [error.to_dict() for error in errors],
                "summary": self._generate_error_summary(errors),
            }

            output_file = Path(output_path)
            output_file.parent.mkdir(parents=True, exist_ok=True)

            with open(output_file, "w") as f:
                json.dump(export_data, f, indent=2, default=str)

            if self.console:
                self.console.print(
                    f"📄 Error log exported to: [bold blue]{output_path}[/bold blue]"
                )

        except Exception as e:
            self.logger.error(f"Failed to export error log: {e}")
            if self.console:
                self.console.print(f"❌ Failed to export error log: {e}", style="red")

    def _generate_error_summary(self, errors: list[AGLOVizError]) -> dict[str, Any]:
        """Generate summary statistics for a list of errors."""
        if not errors:
            return {}

        # Count by category
        category_counts = {}
        severity_counts = {}

        for error in errors:
            category = error.category
            severity = error.severity.value

            category_counts[category] = category_counts.get(category, 0) + 1
            severity_counts[severity] = severity_counts.get(severity, 0) + 1

        return {
            "total_errors": len(errors),
            "by_category": category_counts,
            "by_severity": severity_counts,
            "has_critical": any(e.severity == ErrorSeverity.CRITICAL for e in errors),
            "has_suggestions": sum(1 for e in errors if e.suggestions),
        }


# Global logger instance
_global_logger: AGLOVizLogger | None = None


def get_logger(
    name: str = "agloviz",
    level: str = "INFO",
    enable_rich: bool = True,
    enable_file_logging: bool = False,
) -> AGLOVizLogger:
    """Get or create the global ALGOViz logger instance.

    Args:
        name: Logger name
        level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        enable_rich: Whether to enable rich console output
        enable_file_logging: Whether to enable file logging

    Returns:
        AGLOVizLogger instance
    """
    global _global_logger

    if _global_logger is None:
        _global_logger = AGLOVizLogger(
            name=name,
            level=level,
            enable_rich=enable_rich,
            enable_file_logging=enable_file_logging,
        )

    return _global_logger


def configure_logging(
    level: str = "INFO",
    debug_mode: bool = False,
    enable_file_logging: bool = False,
    log_file_path: str | None = None,
) -> AGLOVizLogger:
    """Configure the global logging system.

    Args:
        level: Logging level
        debug_mode: Whether to enable debug mode
        enable_file_logging: Whether to enable file logging
        log_file_path: Optional custom log file path

    Returns:
        Configured AGLOVizLogger instance
    """
    global _global_logger

    _global_logger = AGLOVizLogger(
        name="agloviz",
        level=level,
        enable_rich=True,
        enable_file_logging=enable_file_logging,
        log_file_path=log_file_path,
    )

    if debug_mode:
        _global_logger.enable_debug_mode(True)

    return _global_logger


# Convenience functions for common logging operations
def log_error(error: AGLOVizError, **kwargs: Any) -> None:
    """Log an error using the global logger."""
    logger = get_logger()
    logger.log_error(error, additional_context=kwargs)


def log_warning(message: str, category: str = "General", **kwargs: Any) -> None:
    """Log a warning using the global logger."""
    logger = get_logger()
    logger.log_warning(message, category=category, **kwargs)


def log_info(message: str, **kwargs: Any) -> None:
    """Log an info message using the global logger."""
    logger = get_logger()
    logger.log_info(message, **kwargs)


def log_success(message: str, **kwargs: Any) -> None:
    """Log a success message using the global logger."""
    logger = get_logger()
    logger.log_success(message, **kwargs)


def log_debug(message: str, **kwargs: Any) -> None:
    """Log a debug message using the global logger."""
    logger = get_logger()
    logger.log_debug(message, **kwargs)


def enable_debug() -> None:
    """Enable debug mode for the global logger."""
    logger = get_logger()
    logger.enable_debug_mode(True)


def disable_debug() -> None:
    """Disable debug mode for the global logger."""
    logger = get_logger()
    logger.enable_debug_mode(False)


class ErrorCollector:
    """Collects multiple errors for batch processing and display."""

    def __init__(self, max_errors: int = 10):
        self.errors: list[AGLOVizError] = []
        self.max_errors = max_errors
        self.logger = get_logger()

    def add_error(self, error: AGLOVizError) -> None:
        """Add an error to the collection.

        Args:
            error: Error to add to the collection
        """
        self.errors.append(error)

        # If we've hit the max, log and clear
        if len(self.errors) >= self.max_errors:
            self.flush()

    def add_config_error(
        self,
        issue: str,
        config_key: str | None = None,
        file_path: str | None = None,
        line_number: int | None = None,
        **kwargs: Any,
    ) -> None:
        """Add a configuration error to the collection."""
        from .errors import ConfigError, FileContext

        context = FileContext(file_path, line_number) if file_path else None
        error = ConfigError(
            issue=issue, context=context, config_key=config_key, **kwargs
        )
        self.add_error(error)

    def has_errors(self) -> bool:
        """Check if there are any errors in the collection."""
        return len(self.errors) > 0

    def has_critical_errors(self) -> bool:
        """Check if there are any critical errors in the collection."""
        return any(error.severity == ErrorSeverity.CRITICAL for error in self.errors)

    def get_error_count(self) -> int:
        """Get the total number of errors."""
        return len(self.errors)

    def get_errors_by_category(self, category: str) -> list[AGLOVizError]:
        """Get all errors of a specific category."""
        return [error for error in self.errors if error.category == category]

    def flush(self) -> list[AGLOVizError]:
        """Flush all collected errors and return them.

        Returns:
            List of all collected errors
        """
        if not self.errors:
            return []

        # Log aggregated errors
        self.logger.aggregate_errors(self.errors)

        # Return and clear
        errors = self.errors.copy()
        self.errors.clear()
        return errors

    def clear(self) -> None:
        """Clear all collected errors without logging."""
        self.errors.clear()

    def export_to_file(self, output_path: str) -> None:
        """Export collected errors to a file."""
        self.logger.export_error_log(output_path, self.errors)
