"""YAML timing test."""

from omegaconf import OmegaConf


def test_yaml_timing_overrides():
    """Test YAML timing override behavior."""
    yaml_config = OmegaConf.load("configs/scene/bfs_dynamic.yaml")
    assert "event_bindings" in yaml_config
    enqueue_bindings = yaml_config.event_bindings.enqueue
    assert len(enqueue_bindings) == 2
    if "timing_overrides" in yaml_config:
        timing_overrides = yaml_config.timing_overrides
        assert timing_overrides.events == 0.8
        assert timing_overrides.effects == 0.5
