"""Error taxonomy and structured error handling for ALGOViz.

This module provides a comprehensive error classification system with actionable
messages, intelligent suggestions, and consistent formatting across all components.
"""

import json
from abc import ABC, abstractmethod
from enum import Enum
from typing import Any

from rich.console import Console
from rich.panel import Panel
from rich.text import Text


class ErrorCategory(str, Enum):
    """Categories of errors in ALGOViz."""

    CONFIG = "ConfigError"
    STORYBOARD = "StoryboardError"
    ADAPTER = "AdapterError"
    SCENARIO = "ScenarioError"
    REGISTRY = "RegistryError"
    RENDER = "RenderError"
    VOICEOVER = "VoiceoverError"
    PLUGIN = "PluginError"


class ErrorSeverity(str, Enum):
    """Severity levels for errors."""

    CRITICAL = "critical"  # Cannot continue
    ERROR = "error"  # Can continue with degraded functionality
    WARNING = "warning"  # Suboptimal but functional
    INFO = "info"  # Informational only


class ErrorContext(ABC):
    """Abstract base class for error context providers."""

    @abstractmethod
    def format_location(self) -> str:
        """Format the location where the error occurred."""
        pass

    @abstractmethod
    def get_metadata(self) -> dict[str, Any]:
        """Get structured metadata for logging."""
        pass


class FileContext(ErrorContext):
    """Context for file-based errors."""

    def __init__(
        self, file_path: str, line_number: int | None = None, column: int | None = None
    ):
        self.file_path = file_path
        self.line_number = line_number
        self.column = column

    def format_location(self) -> str:
        """Format file location as 'file:line:column'."""
        location = self.file_path
        if self.line_number is not None:
            location += f":{self.line_number}"
            if self.column is not None:
                location += f":{self.column}"
        return location

    def get_metadata(self) -> dict[str, Any]:
        """Get file context metadata."""
        return {
            "file_path": self.file_path,
            "line_number": self.line_number,
            "column": self.column,
        }


class StoryboardContext(ErrorContext):
    """Context for storyboard-related errors."""

    def __init__(self, act: str, shot: str, beat: str):
        self.act = act
        self.shot = shot
        self.beat = beat

    def format_location(self) -> str:
        """Format storyboard location as 'Act X/Shot Y/Beat Z'."""
        return f"Act {self.act}/Shot {self.shot}/Beat {self.beat}"

    def get_metadata(self) -> dict[str, Any]:
        """Get storyboard context metadata."""
        return {
            "act": self.act,
            "shot": self.shot,
            "beat": self.beat,
        }


class AlgorithmContext(ErrorContext):
    """Context for algorithm execution errors."""

    def __init__(
        self,
        algorithm: str,
        step_index: int,
        current_state: dict[str, Any] | None = None,
    ):
        self.algorithm = algorithm
        self.step_index = step_index
        self.current_state = current_state or {}

    def format_location(self) -> str:
        """Format algorithm location as 'Algorithm[step]'."""
        return f"{self.algorithm}[step {self.step_index}]"

    def get_metadata(self) -> dict[str, Any]:
        """Get algorithm context metadata."""
        return {
            "algorithm": self.algorithm,
            "step_index": self.step_index,
            "current_state": self.current_state,
        }


class SuggestionEngine:
    """Intelligent suggestion system for error remediation."""

    def __init__(self, max_suggestions: int = 3, min_similarity: float = 0.6):
        self.max_suggestions = max_suggestions
        self.min_similarity = min_similarity

    def suggest_corrections(
        self, input_str: str, valid_options: list[str], context: str | None = None
    ) -> list[str]:
        """Generate intelligent suggestions for typos and similar inputs.

        Args:
            input_str: The invalid input string
            valid_options: List of valid options to suggest from
            context: Optional context for context-aware suggestions

        Returns:
            List of suggested corrections, ranked by relevance
        """
        if not valid_options:
            return []

        suggestions = []

        # 1. Exact case-insensitive match
        for option in valid_options:
            if option.lower() == input_str.lower():
                suggestions.append(option)

        # 2. Levenshtein distance-based suggestions
        levenshtein_suggestions = self._get_levenshtein_suggestions(
            input_str, valid_options
        )
        suggestions.extend(levenshtein_suggestions)

        # 3. Fuzzy matching (substring and prefix matching)
        fuzzy_suggestions = self._get_fuzzy_suggestions(input_str, valid_options)
        suggestions.extend(fuzzy_suggestions)

        # 4. Context-aware suggestions (if context provided)
        if context:
            context_suggestions = self._get_context_suggestions(
                input_str, valid_options, context
            )
            suggestions.extend(context_suggestions)

        # Remove duplicates while preserving order
        seen = set()
        unique_suggestions = []
        for suggestion in suggestions:
            if suggestion not in seen:
                seen.add(suggestion)
                unique_suggestions.append(suggestion)

        return unique_suggestions[: self.max_suggestions]

    def _get_levenshtein_suggestions(
        self, input_str: str, valid_options: list[str]
    ) -> list[str]:
        """Get suggestions based on Levenshtein distance."""
        suggestions = []

        for option in valid_options:
            distance = self._levenshtein_distance(input_str.lower(), option.lower())
            similarity = 1 - (distance / max(len(input_str), len(option)))

            if similarity >= self.min_similarity:
                suggestions.append((option, similarity))

        # Sort by similarity (highest first)
        suggestions.sort(key=lambda x: x[1], reverse=True)
        return [suggestion[0] for suggestion in suggestions]

    def _get_fuzzy_suggestions(
        self, input_str: str, valid_options: list[str]
    ) -> list[str]:
        """Get suggestions based on fuzzy matching."""
        suggestions = []
        input_lower = input_str.lower()

        for option in valid_options:
            option_lower = option.lower()

            # Substring match
            if input_lower in option_lower or option_lower in input_lower:
                suggestions.append(option)
            # Prefix match
            elif option_lower.startswith(input_lower) or input_lower.startswith(
                option_lower
            ):
                suggestions.append(option)

        return suggestions

    def _get_context_suggestions(
        self, input_str: str, valid_options: list[str], context: str
    ) -> list[str]:
        """Get context-aware suggestions based on common usage patterns."""
        # Context-specific suggestion logic can be enhanced based on usage patterns
        context_lower = context.lower()
        suggestions = []

        # For timing context, suggest timing-related options
        if "timing" in context_lower:
            timing_options = [
                opt
                for opt in valid_options
                if any(
                    keyword in opt.lower()
                    for keyword in ["ui", "event", "effect", "wait", "mode"]
                )
            ]
            suggestions.extend(timing_options)

        # For render context, suggest render-related options
        elif "render" in context_lower:
            render_options = [
                opt
                for opt in valid_options
                if any(
                    keyword in opt.lower()
                    for keyword in ["quality", "format", "resolution", "frame"]
                )
            ]
            suggestions.extend(render_options)

        # For scenario context, suggest scenario-related options
        elif "scenario" in context_lower:
            scenario_options = [
                opt
                for opt in valid_options
                if any(
                    keyword in opt.lower()
                    for keyword in ["start", "goal", "grid", "obstacle", "weight"]
                )
            ]
            suggestions.extend(scenario_options)

        return suggestions

    def _levenshtein_distance(self, s1: str, s2: str) -> int:
        """Calculate Levenshtein distance between two strings."""
        if len(s1) < len(s2):
            return self._levenshtein_distance(s2, s1)

        if len(s2) == 0:
            return len(s1)

        previous_row = list(range(len(s2) + 1))
        for i, c1 in enumerate(s1):
            current_row = [i + 1]
            for j, c2 in enumerate(s2):
                insertions = previous_row[j + 1] + 1
                deletions = current_row[j] + 1
                substitutions = previous_row[j] + (c1 != c2)
                current_row.append(min(insertions, deletions, substitutions))
            previous_row = current_row

        return previous_row[-1]


class AGLOVizError(Exception):
    """Base class for all ALGOViz errors with structured messaging and suggestions."""

    def __init__(
        self,
        issue: str,
        context: ErrorContext | None = None,
        remedy: str | None = None,
        suggestions: list[str] | None = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        metadata: dict[str, Any] | None = None,
    ):
        self.issue = issue
        self.context = context
        self.remedy = remedy
        self.suggestions = suggestions or []
        self.severity = severity
        self.metadata = metadata or {}
        self.category = self.__class__.__name__

        super().__init__(self.format_message())

    def format_message(self) -> str:
        """Format the error message with consistent structure."""
        parts = [self.category]

        if self.context:
            parts.append(self.context.format_location())

        parts.append(self.issue)

        if self.remedy:
            parts.append(self.remedy)

        return " - ".join(parts)

    def format_rich_message(self, console: Console | None = None) -> None:
        """Display a rich formatted error message with suggestions and context."""
        if console is None:
            console = Console()

        # Main error message with appropriate color
        severity_colors = {
            ErrorSeverity.CRITICAL: "bold red",
            ErrorSeverity.ERROR: "red",
            ErrorSeverity.WARNING: "yellow",
            ErrorSeverity.INFO: "blue",
        }

        color = severity_colors.get(self.severity, "red")

        # Create error panel
        error_text = Text()
        error_text.append(f"{self.category}: ", style="bold")

        if self.context:
            error_text.append(f"{self.context.format_location()}\n", style="dim")

        error_text.append(self.issue, style=color)

        if self.remedy:
            error_text.append(f"\n\n💡 Remedy: {self.remedy}", style="blue")

        # Add suggestions if available
        if self.suggestions:
            error_text.append("\n\n🔍 Suggestions:", style="bold blue")
            for i, suggestion in enumerate(self.suggestions, 1):
                error_text.append(f"\n  {i}. {suggestion}", style="cyan")

        # Display in a panel
        panel = Panel(
            error_text,
            title=f"[bold {color}]{self.severity.value.upper()}[/bold {color}]",
            border_style=color,
            padding=(1, 2),
        )

        console.print(panel)

    def to_dict(self) -> dict[str, Any]:
        """Convert error to dictionary for structured logging."""
        error_dict = {
            "category": self.category,
            "issue": self.issue,
            "severity": self.severity.value,
            "suggestions": self.suggestions,
            "metadata": self.metadata,
        }

        if self.context:
            error_dict["context"] = {
                "location": self.context.format_location(),
                "metadata": self.context.get_metadata(),
            }

        if self.remedy:
            error_dict["remedy"] = self.remedy

        return error_dict

    def to_json(self) -> str:
        """Convert error to JSON for structured logging."""
        return json.dumps(self.to_dict(), indent=2)


class ConfigError(AGLOVizError):
    """Configuration-related errors with enhanced validation and suggestions."""

    def __init__(
        self,
        issue: str,
        context: ErrorContext | None = None,
        remedy: str | None = None,
        suggestions: list[str] | None = None,
        config_key: str | None = None,
        expected_type: str | None = None,
        actual_type: str | None = None,
        valid_options: list[str] | None = None,
    ):
        # Enhanced metadata for config errors
        metadata = {
            "config_key": config_key,
            "expected_type": expected_type,
            "actual_type": actual_type,
            "valid_options": valid_options,
        }

        # Auto-generate suggestions for config errors
        if not suggestions and valid_options:
            suggestion_engine = SuggestionEngine()

            # Try to extract invalid value from the issue text
            invalid_value = None
            import re

            # Look for patterns like "Invalid value 'X'" or "Invalid X 'Y'"
            value_match = re.search(r"'([^']+)'", issue)
            if value_match:
                invalid_value = value_match.group(1)

            # Generate suggestions for the invalid value if found, otherwise for config_key
            search_term = invalid_value if invalid_value else config_key
            if search_term:
                suggestions = suggestion_engine.suggest_corrections(
                    search_term, valid_options, context="config"
                )

        # Auto-generate remedy for common config error patterns
        if not remedy:
            remedy = self._generate_config_remedy(
                config_key, expected_type, actual_type, valid_options
            )

        super().__init__(
            issue=issue,
            context=context,
            remedy=remedy,
            suggestions=suggestions,
            severity=ErrorSeverity.ERROR,
            metadata=metadata,
        )

    def _generate_config_remedy(
        self,
        config_key: str | None,
        expected_type: str | None,
        actual_type: str | None,
        valid_options: list[str] | None,
    ) -> str | None:
        """Generate helpful remedy suggestions for config errors."""
        if expected_type and actual_type:
            return f"Change {config_key} from {actual_type} to {expected_type}"

        if valid_options and len(valid_options) <= 5:
            options_str = ", ".join(valid_options)
            return f"Use one of: {options_str}"

        if config_key:
            return f"Check the documentation for valid {config_key} values"

        return "Verify configuration syntax and field types"


class StoryboardError(AGLOVizError):
    """Storyboard DSL and parsing errors."""

    def __init__(
        self,
        issue: str,
        act: str,
        shot: str,
        beat: str,
        action: str | None = None,
        suggestions: list[str] | None = None,
    ):
        context = StoryboardContext(act=act, shot=shot, beat=beat)

        # Enhanced metadata for storyboard errors
        metadata = {
            "action": action,
            "storyboard_location": {
                "act": act,
                "shot": shot,
                "beat": beat,
            },
        }

        super().__init__(
            issue=issue,
            context=context,
            suggestions=suggestions,
            severity=ErrorSeverity.ERROR,
            metadata=metadata,
        )


class AdapterError(AGLOVizError):
    """Algorithm adapter execution errors."""

    def __init__(
        self,
        issue: str,
        algorithm: str,
        step_index: int,
        current_state: dict[str, Any] | None = None,
        remedy: str | None = None,
    ):
        context = AlgorithmContext(
            algorithm=algorithm, step_index=step_index, current_state=current_state
        )

        # Auto-generate remedy for adapter errors
        if not remedy:
            remedy = f"Try with minimal scenario for debugging {algorithm} at step {step_index}"

        metadata = {
            "algorithm": algorithm,
            "step_index": step_index,
            "state_snapshot": current_state,
        }

        super().__init__(
            issue=issue,
            context=context,
            remedy=remedy,
            severity=ErrorSeverity.ERROR,
            metadata=metadata,
        )


class ScenarioError(AGLOVizError):
    """Scenario contract violation errors."""

    def __init__(
        self,
        issue: str,
        contract_violation: str,
        location: str,
        remedy: str | None = None,
        entity: str | None = None,
        position: tuple | None = None,
    ):
        context = FileContext(file_path=location) if location else None

        metadata = {
            "contract_violation": contract_violation,
            "entity": entity,
            "position": position,
        }

        super().__init__(
            issue=issue,
            context=context,
            remedy=remedy,
            severity=ErrorSeverity.ERROR,
            metadata=metadata,
        )


class RegistryError(AGLOVizError):
    """Component registry and widget errors."""

    def __init__(
        self,
        issue: str,
        component_type: str,
        component_name: str | None = None,
        available_options: list[str] | None = None,
        suggestions: list[str] | None = None,
    ):
        # Auto-generate suggestions for registry errors
        if not suggestions and component_name and available_options:
            suggestion_engine = SuggestionEngine()
            suggestions = suggestion_engine.suggest_corrections(
                component_name, available_options, context=component_type
            )

        metadata = {
            "component_type": component_type,
            "component_name": component_name,
            "available_options": available_options,
        }

        super().__init__(
            issue=issue,
            suggestions=suggestions,
            severity=ErrorSeverity.ERROR,
            metadata=metadata,
        )

    @classmethod
    def missing_component(cls, name: str, available: list[str]) -> "RegistryError":
        """Factory method for missing component errors."""
        return cls(
            issue=f"Widget '{name}' not registered",
            component_type="widget",
            component_name=name,
            available_options=available,
        )

    @classmethod
    def collision(cls, message: str) -> "RegistryError":
        """Factory method for component collision errors."""
        return cls(
            issue=message,
            component_type="widget",
        )


class RenderError(AGLOVizError):
    """Rendering pipeline and export errors."""

    def __init__(
        self,
        issue: str,
        stage: str,
        remedy: str | None = None,
        severity: ErrorSeverity = ErrorSeverity.ERROR,
        required_tool: str | None = None,
        install_command: str | None = None,
    ):
        # Auto-generate remedy for missing tools
        if not remedy and required_tool and install_command:
            remedy = f"Install {required_tool} with: {install_command}"

        metadata = {
            "render_stage": stage,
            "required_tool": required_tool,
            "install_command": install_command,
        }

        super().__init__(
            issue=issue,
            remedy=remedy,
            severity=severity,
            metadata=metadata,
        )


class VoiceoverError(AGLOVizError):
    """Voiceover and TTS-related errors."""

    def __init__(
        self,
        issue: str,
        component: str,
        fallback_action: str,
        voice: str | None = None,
        language: str | None = None,
        severity: ErrorSeverity = ErrorSeverity.WARNING,  # Usually non-critical
    ):
        remedy = f"Fallback: {fallback_action}"

        metadata = {
            "voiceover_component": component,
            "fallback_action": fallback_action,
            "voice": voice,
            "language": language,
        }

        super().__init__(
            issue=issue,
            remedy=remedy,
            severity=severity,
            metadata=metadata,
        )


class PluginError(AGLOVizError):
    """Plugin system errors."""

    def __init__(
        self,
        issue: str,
        plugin_name: str,
        action_taken: str,
        plugin_version: str | None = None,
        required_version: str | None = None,
        current_version: str | None = None,
        severity: ErrorSeverity = ErrorSeverity.WARNING,  # Usually non-critical
    ):
        remedy = f"Action taken: {action_taken}"

        metadata = {
            "plugin_name": plugin_name,
            "plugin_version": plugin_version,
            "required_version": required_version,
            "current_version": current_version,
            "action_taken": action_taken,
        }

        super().__init__(
            issue=issue,
            remedy=remedy,
            severity=severity,
            metadata=metadata,
        )


# Factory functions for common error patterns
def create_unknown_key_error(
    unknown_key: str,
    valid_keys: list[str],
    file_context: FileContext | None = None,
) -> ConfigError:
    """Factory for unknown configuration key errors."""
    suggestion_engine = SuggestionEngine()
    suggestions = suggestion_engine.suggest_corrections(
        unknown_key, valid_keys, "config"
    )

    return ConfigError(
        issue=f"Unknown config key '{unknown_key}'",
        context=file_context,
        config_key=unknown_key,
        valid_options=valid_keys,
        suggestions=suggestions,
    )


def create_type_mismatch_error(
    key: str,
    expected_type: str,
    actual_type: str,
    file_context: FileContext | None = None,
) -> ConfigError:
    """Factory for type mismatch errors."""
    return ConfigError(
        issue=f"Expected {expected_type} for '{key}', got {actual_type}",
        context=file_context,
        config_key=key,
        expected_type=expected_type,
        actual_type=actual_type,
    )


def create_missing_field_error(
    field: str,
    file_context: FileContext | None = None,
) -> ConfigError:
    """Factory for missing required field errors."""
    return ConfigError(
        issue=f"Missing required field '{field}'",
        context=file_context,
        config_key=field,
        remedy="Add the required field to your configuration",
    )


def create_invalid_enum_error(
    key: str,
    invalid_value: str,
    valid_options: list[str],
    file_context: FileContext | None = None,
) -> ConfigError:
    """Factory for invalid enum value errors."""
    suggestion_engine = SuggestionEngine()
    suggestions = suggestion_engine.suggest_corrections(invalid_value, valid_options)

    return ConfigError(
        issue=f"Invalid value '{invalid_value}' for '{key}'",
        context=file_context,
        config_key=key,
        valid_options=valid_options,
        suggestions=suggestions,
    )


# Registry error factory methods
def create_missing_component_error(
    component_name: str,
    component_type: str,
    available_options: list[str],
) -> RegistryError:
    """Factory for missing component errors."""
    return RegistryError(
        issue=f"{component_type.capitalize()} '{component_name}' not registered",
        component_type=component_type,
        component_name=component_name,
        available_options=available_options,
    )


def create_component_collision_error(
    component_name: str,
    component_type: str,
) -> RegistryError:
    """Factory for component collision errors."""
    return RegistryError(
        issue=f"{component_type.capitalize()} '{component_name}' is already registered",
        component_type=component_type,
        component_name=component_name,
    )


class DirectorError(AGLOVizError):
    """Errors during Director execution."""

    pass


def create_director_error(
    context: str, issue: str, remedy: str = None
) -> DirectorError:
    """Factory for Director errors."""
    return DirectorError(
        category="DirectorError", context=context, issue=issue, remedy=remedy
    )


def create_action_error(
    action: str, location: str, issue: str, remedy: str = None
) -> DirectorError:
    """Factory for action execution errors."""
    return DirectorError(
        category="ActionError",
        context=f"Action '{action}' at {location}",
        issue=issue,
        remedy=remedy,
    )
