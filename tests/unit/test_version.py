"""Test version information and CLI functionality."""

import pytest

from agloviz import __version__


@pytest.mark.unit
def test_version_defined():
    """Test that version is properly defined."""
    assert __version__ is not None
    assert isinstance(__version__, str)
    assert len(__version__) > 0


@pytest.mark.unit
def test_version_format():
    """Test that version follows semantic versioning."""
    # Should be in format X.Y.Z
    parts = __version__.split(".")
    assert len(parts) == 3
    for part in parts:
        assert part.isdigit()
