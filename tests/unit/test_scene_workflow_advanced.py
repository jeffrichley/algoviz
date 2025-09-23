"""Advanced scene workflow tests."""

from hydra_zen import instantiate

from agloviz.config.hydra_zen import BFSDynamicSceneConfig
from agloviz.config.models import TimingConfig, TimingMode
from agloviz.core.scene import SceneEngine


class TestSceneWorkflowAdvanced:
    """Advanced scene workflow tests."""

    def test_dynamic_scene_event_bindings(self):
        """Test dynamic scene event bindings."""
        scene_config = instantiate(BFSDynamicSceneConfig)
        timing_config = TimingConfig(mode=TimingMode.NORMAL)
        scene_engine = SceneEngine(scene_config, timing_config)
        assert "enqueue" in scene_engine.event_bindings
        assert "dequeue" in scene_engine.event_bindings
        enqueue_bindings = scene_engine.event_bindings["enqueue"]
        assert len(enqueue_bindings) == 2
        first_binding = enqueue_bindings[0]
        assert "element" in first_binding.params
        assert "duration" in first_binding.params
