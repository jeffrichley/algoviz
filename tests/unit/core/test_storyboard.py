"""Unit tests for ALGOViz storyboard DSL implementation."""

import tempfile
from pathlib import Path
from unittest.mock import Mock

import pytest
import yaml
from pydantic import ValidationError

from agloviz.core.errors import ConfigError
from agloviz.core.storyboard import (
    Act,
    ActionRegistry,
    Beat,
    Shot,
    Storyboard,
    StoryboardLoader,
    get_action_registry,
    register_action,
)


@pytest.mark.unit
class TestBeat:
    """Test Beat Pydantic model."""

    def test_beat_creation_minimal(self):
        """Test creating a minimal beat."""
        beat = Beat(action="show_title")
        assert beat.action == "show_title"
        assert beat.args == {}
        assert beat.narration is None
        assert beat.bookmarks == {}
        assert beat.min_duration is None
        assert beat.max_duration is None

    def test_beat_creation_full(self):
        """Test creating a beat with all fields."""
        beat = Beat(
            action="play_events",
            args={"routing": "bfs_routing"},
            narration="We enqueue nodes.",
            bookmarks={"enqueue": "queue.highlight"},
            min_duration=1.0,
            max_duration=5.0
        )
        assert beat.action == "play_events"
        assert beat.args == {"routing": "bfs_routing"}
        assert beat.narration == "We enqueue nodes."
        assert beat.bookmarks == {"enqueue": "queue.highlight"}
        assert beat.min_duration == 1.0
        assert beat.max_duration == 5.0

    def test_beat_validation_valid(self):
        """Test Beat validation with valid data."""
        data = {
            "action": "show_title",
            "args": {"text": "Hello"},
            "narration": "Welcome to the video.",
            "bookmarks": {"welcome": "title.highlight"},
            "min_duration": 1.0,
            "max_duration": 3.0
        }
        beat = Beat(**data)
        assert beat.action == "show_title"
        assert beat.args == {"text": "Hello"}
        assert beat.narration == "Welcome to the video."
        assert beat.bookmarks == {"welcome": "title.highlight"}
        assert beat.min_duration == 1.0
        assert beat.max_duration == 3.0

    def test_beat_validation_invalid_duration(self):
        """Test Beat validation with invalid duration."""
        data = {
            "action": "show_title",
            "min_duration": -1.0  # Invalid: negative
        }
        with pytest.raises(ValidationError) as exc_info:
            Beat(**data)

        error = exc_info.value
        assert "min_duration" in str(error)

    def test_beat_validation_missing_action(self):
        """Test Beat validation with missing required action."""
        data = {"args": {"text": "Hello"}}
        with pytest.raises(ValidationError) as exc_info:
            Beat(**data)

        error = exc_info.value
        assert "action" in str(error)


@pytest.mark.unit
class TestShot:
    """Test Shot Pydantic model."""

    def test_shot_creation(self):
        """Test creating a shot with beats."""
        beat1 = Beat(action="show_title")
        beat2 = Beat(action="show_grid")
        shot = Shot(beats=[beat1, beat2])

        assert len(shot.beats) == 2
        assert shot.beats[0].action == "show_title"
        assert shot.beats[1].action == "show_grid"

    def test_shot_validation_valid(self):
        """Test Shot validation with valid data."""
        data = {
            "beats": [
                {"action": "show_title", "args": {"text": "Hello"}},
                {"action": "show_grid", "narration": "Here's the grid."}
            ]
        }
        shot = Shot(**data)
        assert len(shot.beats) == 2
        assert shot.beats[0].action == "show_title"
        assert shot.beats[1].action == "show_grid"

    def test_shot_validation_empty_beats(self):
        """Test Shot validation with empty beats list."""
        data = {"beats": []}
        shot = Shot(**data)
        assert len(shot.beats) == 0

    def test_shot_validation_invalid_beat(self):
        """Test Shot validation with invalid beat."""
        data = {
            "beats": [
                {"action": "show_title"},  # Valid
                {"min_duration": -1.0}     # Invalid: missing action
            ]
        }
        with pytest.raises(ValidationError):
            Shot(**data)


@pytest.mark.unit
class TestAct:
    """Test Act Pydantic model."""

    def test_act_creation(self):
        """Test creating an act with shots."""
        shot1 = Shot(beats=[Beat(action="show_title")])
        shot2 = Shot(beats=[Beat(action="show_grid")])
        act = Act(title="Introduction", shots=[shot1, shot2])

        assert act.title == "Introduction"
        assert len(act.shots) == 2

    def test_act_validation_valid(self):
        """Test Act validation with valid data."""
        data = {
            "title": "Algorithm Execution",
            "shots": [
                {"beats": [{"action": "show_title"}]},
                {"beats": [{"action": "play_events"}]}
            ]
        }
        act = Act(**data)
        assert act.title == "Algorithm Execution"
        assert len(act.shots) == 2

    def test_act_validation_missing_title(self):
        """Test Act validation with missing title."""
        data = {
            "shots": [{"beats": [{"action": "show_title"}]}]
        }
        with pytest.raises(ValidationError) as exc_info:
            Act(**data)

        error = exc_info.value
        assert "title" in str(error)


@pytest.mark.unit
class TestStoryboard:
    """Test Storyboard Pydantic model."""

    def test_storyboard_creation(self):
        """Test creating a storyboard with acts."""
        act1 = Act(title="Intro", shots=[Shot(beats=[Beat(action="show_title")])])
        act2 = Act(title="Algorithm", shots=[Shot(beats=[Beat(action="play_events")])])
        storyboard = Storyboard(acts=[act1, act2])

        assert len(storyboard.acts) == 2
        assert storyboard.acts[0].title == "Intro"
        assert storyboard.acts[1].title == "Algorithm"

    def test_storyboard_validation_valid(self):
        """Test Storyboard validation with valid data."""
        data = {
            "acts": [
                {
                    "title": "Introduction",
                    "shots": [{"beats": [{"action": "show_title"}]}]
                },
                {
                    "title": "Results",
                    "shots": [{"beats": [{"action": "trace_path"}]}]
                }
            ]
        }
        storyboard = Storyboard(**data)
        assert len(storyboard.acts) == 2
        assert storyboard.acts[0].title == "Introduction"
        assert storyboard.acts[1].title == "Results"

    def test_storyboard_validation_empty_acts(self):
        """Test Storyboard validation with empty acts list."""
        data = {"acts": []}
        storyboard = Storyboard(**data)
        assert len(storyboard.acts) == 0


@pytest.mark.unit
class TestActionRegistry:
    """Test ActionRegistry functionality."""

    def test_registry_creation(self):
        """Test creating an action registry."""
        registry = ActionRegistry()
        assert len(registry.list_actions()) == 0

    def test_register_action(self):
        """Test registering an action."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register("show_title", handler)
        assert "show_title" in registry.list_actions()
        assert registry.get("show_title") == handler

    def test_register_duplicate_action(self):
        """Test registering duplicate action raises error."""
        registry = ActionRegistry()
        handler1 = Mock()
        handler2 = Mock()

        registry.register("show_title", handler1)
        with pytest.raises(ConfigError) as exc_info:
            registry.register("show_title", handler2)

        error = exc_info.value
        assert "already registered" in error.issue

    def test_register_invalid_action_name(self):
        """Test registering with invalid action name."""
        registry = ActionRegistry()
        handler = Mock()

        with pytest.raises(ConfigError) as exc_info:
            registry.register("", handler)

        error = exc_info.value
        assert "Invalid action name" in error.issue

    def test_get_nonexistent_action(self):
        """Test getting nonexistent action raises error."""
        registry = ActionRegistry()

        with pytest.raises(ConfigError) as exc_info:
            registry.get("nonexistent")

        error = exc_info.value
        assert "Unknown action" in error.issue

    def test_clear_registry(self):
        """Test clearing the registry."""
        registry = ActionRegistry()
        handler = Mock()

        registry.register("show_title", handler)
        assert len(registry.list_actions()) == 1

        registry.clear()
        assert len(registry.list_actions()) == 0


@pytest.mark.unit
class TestStoryboardLoader:
    """Test StoryboardLoader functionality."""

    def test_loader_creation(self):
        """Test creating a storyboard loader."""
        loader = StoryboardLoader()
        assert loader is not None

    def test_load_valid_yaml(self):
        """Test loading a valid storyboard YAML."""
        yaml_content = {
            "acts": [
                {
                    "title": "Introduction",
                    "shots": [
                        {
                            "beats": [
                                {
                                    "action": "show_title",
                                    "args": {"text": "Hello World"},
                                    "narration": "Welcome to the video."
                                }
                            ]
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            temp_path = f.name

        try:
            loader = StoryboardLoader()
            storyboard = loader.load_from_yaml(temp_path)

            assert len(storyboard.acts) == 1
            assert storyboard.acts[0].title == "Introduction"
            assert len(storyboard.acts[0].shots) == 1
            assert len(storyboard.acts[0].shots[0].beats) == 1

            beat = storyboard.acts[0].shots[0].beats[0]
            assert beat.action == "show_title"
            assert beat.args == {"text": "Hello World"}
            assert beat.narration == "Welcome to the video."

        finally:
            Path(temp_path).unlink()

    def test_load_nonexistent_file(self):
        """Test loading nonexistent file raises error."""
        loader = StoryboardLoader()

        with pytest.raises(ConfigError) as exc_info:
            loader.load_from_yaml("nonexistent.yaml")

        error = exc_info.value
        assert "not found" in error.issue

    def test_load_invalid_yaml(self):
        """Test loading invalid YAML raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("invalid: yaml: content: [")
            temp_path = f.name

        try:
            loader = StoryboardLoader()
            with pytest.raises(ConfigError) as exc_info:
                loader.load_from_yaml(temp_path)

            error = exc_info.value
            assert "Invalid YAML syntax" in error.issue

        finally:
            Path(temp_path).unlink()

    def test_load_empty_file(self):
        """Test loading empty file raises error."""
        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            f.write("")
            temp_path = f.name

        try:
            loader = StoryboardLoader()
            with pytest.raises(ConfigError) as exc_info:
                loader.load_from_yaml(temp_path)

            error = exc_info.value
            assert "empty" in error.issue

        finally:
            Path(temp_path).unlink()

    def test_load_invalid_structure(self):
        """Test loading YAML with invalid structure raises error."""
        yaml_content = {
            "invalid": "structure"
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            temp_path = f.name

        try:
            loader = StoryboardLoader()
            with pytest.raises(ConfigError) as exc_info:
                loader.load_from_yaml(temp_path)

            error = exc_info.value
            assert "validation failed" in error.issue

        finally:
            Path(temp_path).unlink()

    def test_validate_actions(self):
        """Test validating actions against registry."""
        yaml_content = {
            "acts": [
                {
                    "title": "Test Act",
                    "shots": [
                        {
                            "beats": [
                                {"action": "show_title"},
                                {"action": "unknown_action"}
                            ]
                        }
                    ]
                }
            ]
        }

        with tempfile.NamedTemporaryFile(mode='w', suffix='.yaml', delete=False) as f:
            yaml.dump(yaml_content, f)
            temp_path = f.name

        try:
            loader = StoryboardLoader()
            storyboard = loader.load_from_yaml(temp_path)

            registry = ActionRegistry()
            registry.register("show_title", Mock())

            unknown_actions = loader.validate_actions(storyboard, registry)
            assert len(unknown_actions) == 1
            assert "unknown_action" in unknown_actions[0]
            assert "Act 1/Shot 1/Beat 2" in unknown_actions[0]

        finally:
            Path(temp_path).unlink()


@pytest.mark.unit
class TestGlobalRegistry:
    """Test global registry functions."""

    def test_get_action_registry(self):
        """Test getting the global action registry."""
        registry = get_action_registry()
        assert isinstance(registry, ActionRegistry)

    def test_register_action_global(self):
        """Test registering an action globally."""
        handler = Mock()
        register_action("global_test", handler)

        registry = get_action_registry()
        assert "global_test" in registry.list_actions()
        assert registry.get("global_test") == handler
