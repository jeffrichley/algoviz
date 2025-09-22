"""Custom OmegaConf Resolvers for Hydra-zen Parameter Templates.

This module provides custom resolvers for parameter template resolution in scene configurations,
enabling dynamic parameter substitution based on event data, timing configuration, and widget state.
"""

from omegaconf import OmegaConf
from typing import Any, Dict, Optional
import re


def register_custom_resolvers():
    """Register all custom OmegaConf resolvers for parameter templates."""
    
    # Event data resolver
    OmegaConf.register_new_resolver(
        "event_data", 
        _resolve_event_path,
        replace=True  # Allow re-registration
    )
    
    # Configuration value resolver
    OmegaConf.register_new_resolver(
        "config_value",
        _resolve_config_path,
        replace=True
    )
    
    # Timing value resolver
    OmegaConf.register_new_resolver(
        "timing_value",
        _resolve_timing_value,
        replace=True
    )
    
    # Widget state resolver
    OmegaConf.register_new_resolver(
        "widget_state",
        _resolve_widget_state,
        replace=True
    )


def _resolve_event_path(path: str) -> str:
    """Resolve event data path like 'event.node' or 'event.pos'.
    
    Note: This returns the template string for later resolution with actual context.
    The actual resolution happens in SceneEngine._resolve_parameters().
    """
    return f"${{{path}}}"


def _resolve_config_path(path: str, default: Any = None) -> Any:
    """Resolve configuration path like 'config.highlight_style'.
    
    Note: This is a placeholder that returns the default value.
    Actual resolution happens in SceneEngine._resolve_parameters() with context.
    """
    return default if default is not None else f"${{{path}}}"


def _resolve_timing_value(timing_key: str, mode: str = "normal") -> float:
    """Resolve timing values based on timing mode.
    
    Args:
        timing_key: The timing category (ui, events, effects, waits)
        mode: The timing mode (draft, normal, fast)
    
    Returns:
        Calculated timing value as a float
    """
    timing_multipliers = {
        "draft": 0.5,
        "normal": 1.0, 
        "fast": 0.25
    }
    
    base_timings = {
        "ui": 1.0,
        "events": 0.8,
        "effects": 0.5,
        "waits": 0.5
    }
    
    base_time = base_timings.get(timing_key, 1.0)
    multiplier = timing_multipliers.get(mode, 1.0)
    return base_time * multiplier


def _resolve_widget_state(widget_path: str) -> str:
    """Resolve widget state path like 'grid.current_position'.
    
    Note: This returns a template string for later resolution with widget context.
    """
    return f"${{widgets.{widget_path}}}"


# Advanced resolvers for complex parameter templates
def register_advanced_resolvers():
    """Register advanced resolvers for complex parameter template scenarios."""
    
    # Math operations resolver
    OmegaConf.register_new_resolver(
        "math",
        _resolve_math_expression,
        replace=True
    )
    
    # List operations resolver
    OmegaConf.register_new_resolver(
        "list_op",
        _resolve_list_operation,
        replace=True
    )
    
    # Conditional resolver
    OmegaConf.register_new_resolver(
        "if_then_else",
        _resolve_conditional,
        replace=True
    )


def _resolve_math_expression(expression: str) -> float:
    """Resolve simple math expressions like 'add(1,2)' or 'multiply(${event.x}, 2)'.
    
    Note: This is a basic implementation. In practice, would need more robust parsing.
    """
    # Simple implementation for common operations
    if expression.startswith("add(") and expression.endswith(")"):
        args = expression[4:-1].split(",")
        if len(args) == 2:
            try:
                return float(args[0].strip()) + float(args[1].strip())
            except ValueError:
                pass
    elif expression.startswith("multiply(") and expression.endswith(")"):
        args = expression[9:-1].split(",")
        if len(args) == 2:
            try:
                return float(args[0].strip()) * float(args[1].strip())
            except ValueError:
                pass
    
    # Fallback to returning the expression as string
    return expression


def _resolve_list_operation(operation: str, *args) -> Any:
    """Resolve list operations like 'length', 'first', 'last'."""
    if operation == "length" and len(args) == 1:
        try:
            return len(args[0]) if hasattr(args[0], '__len__') else 0
        except:
            return 0
    elif operation == "first" and len(args) == 1:
        try:
            return args[0][0] if args[0] else None
        except:
            return None
    elif operation == "last" and len(args) == 1:
        try:
            return args[0][-1] if args[0] else None
        except:
            return None
    
    return None


def _resolve_conditional(condition: str, true_value: Any, false_value: Any) -> Any:
    """Resolve conditional expressions like if_then_else('${event.is_goal}', 'success', 'continue')."""
    # Simple boolean evaluation
    if isinstance(condition, str):
        if condition.lower() in ('true', '1', 'yes'):
            return true_value
        elif condition.lower() in ('false', '0', 'no'):
            return false_value
    elif isinstance(condition, bool):
        return true_value if condition else false_value
    
    # Default to false_value if condition is unclear
    return false_value


# Utility functions for resolver context management
class ResolverContext:
    """Context manager for resolver state during parameter resolution."""
    
    def __init__(self, event=None, config=None, timing=None, widgets=None):
        self.event = event
        self.config = config
        self.timing = timing
        self.widgets = widgets
        self._previous_context = None
    
    def __enter__(self):
        # Store previous context if any
        self._previous_context = getattr(_resolve_event_path, '_context', None)
        
        # Set new context for resolvers
        _resolve_event_path._context = self
        _resolve_config_path._context = self
        _resolve_widget_state._context = self
        
        return self
    
    def __exit__(self, exc_type, exc_val, exc_tb):
        # Restore previous context
        if self._previous_context:
            _resolve_event_path._context = self._previous_context
            _resolve_config_path._context = self._previous_context
            _resolve_widget_state._context = self._previous_context
        else:
            # Clear context
            if hasattr(_resolve_event_path, '_context'):
                delattr(_resolve_event_path, '_context')
            if hasattr(_resolve_config_path, '_context'):
                delattr(_resolve_config_path, '_context')
            if hasattr(_resolve_widget_state, '_context'):
                delattr(_resolve_widget_state, '_context')


def get_available_resolvers() -> Dict[str, str]:
    """Get a dictionary of available resolvers and their descriptions."""
    return {
        "event_data": "Resolves event data paths like 'event.node' or 'event.pos'",
        "config_value": "Resolves configuration values with optional defaults",
        "timing_value": "Resolves timing values based on timing mode and category",
        "widget_state": "Resolves widget state properties",
        "math": "Performs simple math operations (advanced)",
        "list_op": "Performs list operations like length, first, last (advanced)",
        "if_then_else": "Conditional resolver for if-then-else logic (advanced)"
    }


def validate_resolver_syntax(template: str) -> bool:
    """Validate that a parameter template uses correct resolver syntax.
    
    Args:
        template: Parameter template string like "${event_data:event.node}"
    
    Returns:
        True if syntax is valid, False otherwise
    """
    if not isinstance(template, str):
        return True  # Non-string values don't need validation
    
    if not template.startswith("${") or not template.endswith("}"):
        return False  # Not a template - should be False for validation
    
    # Extract resolver and path
    content = template[2:-1]  # Remove ${ and }
    
    if ":" not in content:
        return False  # Missing resolver separator
    
    resolver, path = content.split(":", 1)
    
    # Check if resolver is registered
    available_resolvers = get_available_resolvers()
    if resolver not in available_resolvers:
        return False
    
    # Basic path validation (could be enhanced)
    if not path.strip():
        return False
    
    return True


# Initialize resolvers when module is imported
register_custom_resolvers()
