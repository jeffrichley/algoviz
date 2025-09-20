"""CLI error display utilities for ALGOViz.

This module provides user-facing error display functionality with rich formatting,
file context display, and consistent exit codes across all CLI commands.
"""

from pathlib import Path

import typer
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.text import Text

from agloviz.core.errors import AGLOVizError, ErrorSeverity
from agloviz.core.logging import get_logger


class CLIErrorDisplay:
    """Handles user-facing error display in CLI commands."""

    def __init__(self, console: Console | None = None):
        self.console = console or Console()
        self.logger = get_logger()

    def display_error(
        self,
        error: AGLOVizError,
        show_context: bool = True,
        show_suggestions: bool = True,
        show_debug: bool = False,
    ) -> None:
        """Display a comprehensive error message to the user.

        Args:
            error: The error to display
            show_context: Whether to show file context/excerpts
            show_suggestions: Whether to show suggestions
            show_debug: Whether to show debug information
        """
        # Use the error's built-in rich formatting
        error.format_rich_message(self.console)

        # Show file context if available and requested
        if show_context and hasattr(error.context, 'file_path'):
            self.display_file_excerpt(
                error.context.file_path,
                getattr(error.context, 'line_number', None)
            )

        # Show debug information if requested
        if show_debug:
            self._display_debug_panel(error)

    def display_file_excerpt(
        self,
        file_path: str,
        line_number: int | None = None,
        context_lines: int = 3,
    ) -> None:
        """Display a file excerpt with syntax highlighting around an error.

        Args:
            file_path: Path to the file to display
            line_number: Line number where error occurred (1-indexed)
            context_lines: Number of lines to show before/after the error line
        """
        try:
            path = Path(file_path)
            if not path.exists():
                return

            with open(path) as f:
                lines = f.readlines()

            if not lines:
                return

            # Determine the range of lines to show
            if line_number is not None:
                start_line = max(1, line_number - context_lines)
                end_line = min(len(lines), line_number + context_lines)
                error_line = line_number
            else:
                # Show first few lines if no specific line number
                start_line = 1
                end_line = min(len(lines), 10)
                error_line = None

            # Extract the relevant lines
            excerpt_lines = lines[start_line - 1:end_line]

            # Create syntax-highlighted display
            file_extension = path.suffix.lstrip('.')
            language = self._get_language_for_extension(file_extension)

            # Build the excerpt text with line numbers
            excerpt_text = ""
            for i, line in enumerate(excerpt_lines, start=start_line):
                line_marker = "→" if i == error_line else " "
                excerpt_text += f"{line_marker} {i:3d} | {line}"

            # Display in a syntax-highlighted panel
            syntax = Syntax(
                excerpt_text,
                language,
                theme="monokai",
                line_numbers=False,  # We're adding our own
                background_color="default",
            )

            panel = Panel(
                syntax,
                title=f"[bold]📄 {path.name}[/bold]",
                subtitle=f"Lines {start_line}-{end_line}" + (
                    f" (error at line {error_line})" if error_line else ""
                ),
                border_style="blue",
                padding=(0, 1),
            )

            self.console.print(panel)

        except Exception:
            # Don't fail the error display if file reading fails
            self.console.print(f"📄 File: {file_path}" + (
                f" (line {line_number})" if line_number else ""
            ), style="dim")

    def display_suggestions(
        self,
        suggestions: list[str],
        category: str = "Suggestions",
        original_input: str | None = None,
    ) -> None:
        """Display suggestions in a formatted panel.

        Args:
            suggestions: List of suggestions to display
            category: Category of suggestions
            original_input: The original invalid input
        """
        if not suggestions:
            return

        suggestion_text = Text()

        if original_input:
            suggestion_text.append(f"Instead of '{original_input}', try:\n\n", style="dim")

        for i, suggestion in enumerate(suggestions, 1):
            suggestion_text.append(f"{i}. ", style="bold cyan")
            suggestion_text.append(f"{suggestion}\n", style="cyan")

        panel = Panel(
            suggestion_text,
            title=f"[bold blue]💡 {category}[/bold blue]",
            border_style="blue",
            padding=(1, 2),
        )

        self.console.print(panel)

    def get_exit_code(self, error: AGLOVizError) -> int:
        """Get appropriate exit code for an error.

        Args:
            error: The error to get exit code for

        Returns:
            Exit code (1-10 based on error category and severity)
        """
        # Base exit codes by category
        category_codes = {
            "ConfigError": 1,
            "StoryboardError": 2,
            "AdapterError": 3,
            "ScenarioError": 4,
            "RegistryError": 5,
            "RenderError": 6,
            "VoiceoverError": 7,
            "PluginError": 8,
        }

        base_code = category_codes.get(error.category, 9)

        # Adjust for severity
        if error.severity == ErrorSeverity.CRITICAL:
            return base_code  # Use base code for critical errors
        elif error.severity == ErrorSeverity.WARNING:
            return 0  # Don't exit for warnings
        else:
            return base_code  # Use base code for regular errors

    def handle_error_and_exit(
        self,
        error: AGLOVizError,
        show_context: bool = True,
        show_debug: bool = False,
    ) -> None:
        """Display an error and exit with appropriate code.

        Args:
            error: The error to display and exit for
            show_context: Whether to show file context
            show_debug: Whether to show debug information
        """
        self.display_error(error, show_context=show_context, show_debug=show_debug)

        exit_code = self.get_exit_code(error)
        if exit_code > 0:
            raise typer.Exit(exit_code)

    def _get_language_for_extension(self, extension: str) -> str:
        """Get syntax highlighting language for file extension."""
        language_map = {
            "py": "python",
            "yaml": "yaml",
            "yml": "yaml",
            "json": "json",
            "toml": "toml",
            "md": "markdown",
            "txt": "text",
            "log": "text",
        }

        return language_map.get(extension.lower(), "text")

    def _display_debug_panel(self, error: AGLOVizError) -> None:
        """Display debug information panel for an error."""
        debug_text = Text()
        debug_text.append("🔍 Error Details:\n", style="bold yellow")
        debug_text.append(f"Category: {error.category}\n", style="dim")
        debug_text.append(f"Severity: {error.severity.value}\n", style="dim")

        if error.metadata:
            debug_text.append("\n📊 Metadata:\n", style="bold")
            for key, value in error.metadata.items():
                debug_text.append(f"  {key}: {value}\n", style="dim")

        if error.context:
            debug_text.append("\n📍 Context:\n", style="bold")
            for key, value in error.context.get_metadata().items():
                debug_text.append(f"  {key}: {value}\n", style="dim")

        panel = Panel(
            debug_text,
            title="[bold yellow]🐛 Debug Information[/bold yellow]",
            border_style="yellow",
            padding=(1, 2),
        )

        self.console.print(panel)


class CLIErrorHandler:
    """Central error handler for CLI commands with consistent behavior."""

    def __init__(self, debug_mode: bool = False):
        self.display = CLIErrorDisplay()
        self.debug_mode = debug_mode
        self.logger = get_logger()

    def handle_config_error(self, error: Exception, config_file: str) -> None:
        """Handle configuration-related errors in CLI commands."""
        if isinstance(error, AGLOVizError):
            self.display.handle_error_and_exit(error, show_debug=self.debug_mode)
        else:
            # Convert generic exceptions to ALGOViz errors
            from agloviz.core.errors import ConfigError, FileContext

            context = FileContext(config_file) if config_file else None
            config_error = ConfigError(
                issue=f"Configuration error: {error}",
                context=context,
                remedy="Check configuration file syntax and values",
            )
            self.display.handle_error_and_exit(config_error, show_debug=self.debug_mode)

    def handle_file_not_found(self, file_path: str, file_type: str = "file") -> None:
        """Handle file not found errors with helpful suggestions."""
        from agloviz.core.errors import ConfigError, FileContext

        # Try to suggest similar files in the directory
        suggestions = []
        try:
            parent_dir = Path(file_path).parent
            if parent_dir.exists():
                similar_files = []
                file_name = Path(file_path).name
                file_stem = Path(file_path).stem.lower()
                file_suffix = Path(file_path).suffix.lower()

                for existing_file in parent_dir.iterdir():
                    if existing_file.is_file():
                        existing_name = existing_file.name.lower()
                        existing_stem = existing_file.stem.lower()
                        existing_suffix = existing_file.suffix.lower()

                        # Check various similarity criteria
                        is_similar = (
                            # Same stem (name without extension)
                            file_stem == existing_stem or
                            # Similar extension (yaml vs yml)
                            (file_suffix in ['.yaml', '.yml'] and existing_suffix in ['.yaml', '.yml']) or
                            # Partial name match
                            file_stem in existing_name or existing_stem in file_name.lower() or
                            # Levenshtein distance for typos
                            self._calculate_similarity(file_name.lower(), existing_name) > 0.6
                        )

                        if is_similar:
                            similar_files.append(str(existing_file))

                suggestions = similar_files[:3]  # Limit to 3 suggestions
        except Exception:
            pass  # Ignore errors in suggestion generation

        error = ConfigError(
            issue=f"{file_type.capitalize()} not found: {file_path}",
            context=FileContext(file_path),
            remedy=f"Verify the {file_type} path exists and is accessible",
            suggestions=suggestions,
        )

        self.display.handle_error_and_exit(error, show_debug=self.debug_mode)

    def _calculate_similarity(self, s1: str, s2: str) -> float:
        """Calculate similarity between two strings using Levenshtein distance."""
        if not s1 or not s2:
            return 0.0

        # Simple Levenshtein distance calculation
        len1, len2 = len(s1), len(s2)
        if len1 > len2:
            s1, s2 = s2, s1
            len1, len2 = len2, len1

        current_row = list(range(len1 + 1))
        for i in range(1, len2 + 1):
            previous_row, current_row = current_row, [i] + [0] * len1
            for j in range(1, len1 + 1):
                add, delete, change = previous_row[j] + 1, current_row[j - 1] + 1, previous_row[j - 1]
                if s1[j - 1] != s2[i - 1]:
                    change += 1
                current_row[j] = min(add, delete, change)

        distance = current_row[len1]
        max_len = max(len(s1), len(s2))
        return 1 - (distance / max_len) if max_len > 0 else 0.0

    def handle_validation_error(
        self,
        validation_error: Exception,
        context_file: str | None = None,
    ) -> None:
        """Handle Pydantic validation errors with enhanced formatting."""
        from pydantic import ValidationError

        from agloviz.core.errors import ConfigError, FileContext

        if isinstance(validation_error, ValidationError):
            # Extract field-level errors with suggestions
            error_messages = []
            suggestions = []

            for error_detail in validation_error.errors():
                field_path = '.'.join(str(loc) for loc in error_detail['loc'])
                error_msg = error_detail['msg']
                error_messages.append(f"  • {field_path}: {error_msg}")

                # Generate suggestions for common validation errors
                if 'enum' in error_msg.lower():
                    # Try to extract valid options from enum error message
                    import re
                    enum_match = re.search(r"Input should be (.+)", error_msg)
                    if enum_match:
                        suggestions.append(f"Valid options for {field_path}: {enum_match.group(1)}")

            formatted_errors = '\n'.join(error_messages)
            context = FileContext(context_file) if context_file else None

            config_error = ConfigError(
                issue=f"Configuration validation failed:\n{formatted_errors}",
                context=context,
                remedy="Fix the validation errors listed above",
                suggestions=suggestions,
            )
        else:
            # Generic validation error
            context = FileContext(context_file) if context_file else None
            config_error = ConfigError(
                issue=f"Validation error: {validation_error}",
                context=context,
                remedy="Check configuration syntax and field types",
            )

        self.display.handle_error_and_exit(config_error, show_debug=self.debug_mode)

    def handle_unexpected_error(
        self,
        error: Exception,
        operation: str = "operation",
        context: str | None = None,
    ) -> None:
        """Handle unexpected errors with helpful context."""
        from agloviz.core.errors import AGLOVizError, ErrorSeverity

        # Create a generic ALGOViz error
        agloviz_error = AGLOVizError(
            issue=f"Unexpected error during {operation}: {error}",
            remedy="This may be a bug. Please report it with the command you ran.",
            severity=ErrorSeverity.CRITICAL,
            metadata={
                "operation": operation,
                "context": context,
                "error_type": type(error).__name__,
                "error_message": str(error),
            }
        )

        self.display.handle_error_and_exit(agloviz_error, show_debug=True)


# Exit code constants for consistency
class ExitCodes:
    """Standard exit codes for ALGOViz CLI commands."""
    SUCCESS = 0
    CONFIG_ERROR = 1
    STORYBOARD_ERROR = 2
    ADAPTER_ERROR = 3
    SCENARIO_ERROR = 4
    REGISTRY_ERROR = 5
    RENDER_ERROR = 6
    VOICEOVER_ERROR = 7
    PLUGIN_ERROR = 8
    UNEXPECTED_ERROR = 9
    CRITICAL_ERROR = 10


def create_cli_error_handler(debug_mode: bool = False) -> CLIErrorHandler:
    """Factory function to create a CLI error handler.

    Args:
        debug_mode: Whether to enable debug mode

    Returns:
        Configured CLIErrorHandler instance
    """
    return CLIErrorHandler(debug_mode=debug_mode)


def handle_cli_exception(
    error: Exception,
    operation: str = "command",
    config_file: str | None = None,
    debug_mode: bool = False,
) -> None:
    """Global exception handler for CLI commands.

    Args:
        error: The exception that occurred
        operation: Description of the operation that failed
        config_file: Optional config file context
        debug_mode: Whether debug mode is enabled
    """
    handler = create_cli_error_handler(debug_mode=debug_mode)

    if isinstance(error, AGLOVizError):
        handler.display.handle_error_and_exit(error, show_debug=debug_mode)
    elif isinstance(error, FileNotFoundError):
        file_path = str(error).split("'")[1] if "'" in str(error) else config_file or "unknown"
        handler.handle_file_not_found(file_path)
    elif "ValidationError" in str(type(error)):
        handler.handle_validation_error(error, config_file)
    else:
        handler.handle_unexpected_error(error, operation, config_file)


def display_error_summary(errors: list[AGLOVizError], console: Console | None = None) -> None:
    """Display a summary of multiple errors.

    Args:
        errors: List of errors to summarize
        console: Optional console instance
    """
    if not errors:
        return

    if console is None:
        console = Console()

    # Count errors by category and severity
    category_counts: dict[str, int] = {}
    severity_counts: dict[str, int] = {}

    for error in errors:
        category_counts[error.category] = category_counts.get(error.category, 0) + 1
        severity_counts[error.severity.value] = severity_counts.get(error.severity.value, 0) + 1

    # Create summary text
    summary_text = Text()
    summary_text.append(f"📊 Error Summary ({len(errors)} total):\n\n", style="bold")

    # By category
    summary_text.append("By Category:\n", style="bold blue")
    for category, count in sorted(category_counts.items()):
        summary_text.append(f"  • {category}: {count}\n", style="cyan")

    # By severity
    summary_text.append("\nBy Severity:\n", style="bold blue")
    for severity, count in sorted(severity_counts.items()):
        severity_color = {
            "critical": "bold red",
            "error": "red",
            "warning": "yellow",
            "info": "blue",
        }.get(severity, "white")

        summary_text.append(f"  • {severity.title()}: {count}\n", style=severity_color)

    # Most common suggestions
    all_suggestions = []
    for error in errors:
        all_suggestions.extend(error.suggestions)

    if all_suggestions:
        # Count suggestion frequency
        suggestion_counts: dict[str, int] = {}
        for suggestion in all_suggestions:
            suggestion_counts[suggestion] = suggestion_counts.get(suggestion, 0) + 1

        # Show top 3 most common suggestions
        top_suggestions = sorted(
            suggestion_counts.items(),
            key=lambda x: x[1],
            reverse=True
        )[:3]

        if top_suggestions:
            summary_text.append("\nTop Suggestions:\n", style="bold blue")
            for suggestion, count in top_suggestions:
                summary_text.append(f"  • {suggestion} ({count}x)\n", style="green")

    panel = Panel(
        summary_text,
        title="[bold]📈 Error Analysis[/bold]",
        border_style="blue",
        padding=(1, 2),
    )

    console.print(panel)


def _get_language_for_extension(extension: str) -> str:
    """Get syntax highlighting language for file extension."""
    language_map = {
        "py": "python",
        "yaml": "yaml",
        "yml": "yaml",
        "json": "json",
        "toml": "toml",
        "md": "markdown",
        "txt": "text",
        "log": "text",
        "sh": "bash",
        "bash": "bash",
        "zsh": "bash",
    }

    return language_map.get(extension.lower(), "text")
