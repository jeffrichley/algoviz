"""Tests for ConfigStore scene registration."""

from hydra.core.config_store import ConfigStore

from agloviz.core.scene import register_scene_configs


class TestConfigStoreSceneRegistration:
    """Test scene configuration registration with ConfigStore."""

    def test_register_scene_configs(self):
        """Test register_scene_configs() function."""
        cs = ConfigStore.instance()
        register_scene_configs()
        repo = cs.repo
        assert "scene_config_base.yaml" in repo
        assert "event_binding_base.yaml" in repo
        assert "widget_spec_base.yaml" in repo

    def test_configstore_scene_retrieval(self):
        """Test ConfigStore scene retrieval."""
        cs = ConfigStore.instance()
        register_scene_configs()
        repo = cs.repo
        assert "scene" in repo
        scene_group = repo["scene"]
        assert "bfs_pathfinding.yaml" in scene_group

    def test_scene_configuration_groups(self):
        """Test scene configuration groups."""
        cs = ConfigStore.instance()
        register_scene_configs()
        repo = cs.repo
        assert "scene" in repo
        scene_configs = repo["scene"]
        assert isinstance(scene_configs, dict)
        assert "bfs_pathfinding.yaml" in scene_configs
