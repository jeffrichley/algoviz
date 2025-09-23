"""Tests for scenario runtime contract."""

import pytest

from agloviz.core.scenario import GridScenario


@pytest.mark.unit
class TestGridScenario:
    """Test GridScenario implementation."""

    def test_create_simple_scenario(self, simple_scenario_config, simple_grid_data):
        """Test creating a simple grid scenario."""
        scenario = GridScenario(simple_scenario_config, simple_grid_data)

        assert scenario.width == 3
        assert scenario.height == 3
        assert scenario.start == (0, 0)
        assert scenario.goal == (2, 2)
        assert len(scenario.obstacles) == 0

    def test_scenario_with_obstacles(
        self, simple_scenario_config, grid_data_with_obstacles
    ):
        """Test scenario with obstacles."""
        scenario = GridScenario(simple_scenario_config, grid_data_with_obstacles)

        assert (1, 1) in scenario.obstacles
        assert not scenario.passable((1, 1))
        assert scenario.passable((0, 0))

    def test_in_bounds(self, simple_scenario_config, simple_grid_data):
        """Test in_bounds checking."""
        scenario = GridScenario(simple_scenario_config, simple_grid_data)

        # Valid positions
        assert scenario.in_bounds((0, 0))
        assert scenario.in_bounds((2, 2))
        assert scenario.in_bounds((1, 1))

        # Invalid positions
        assert not scenario.in_bounds((-1, 0))
        assert not scenario.in_bounds((0, -1))
        assert not scenario.in_bounds((3, 2))
        assert not scenario.in_bounds((2, 3))

    def test_neighbors(self, simple_scenario_config, grid_data_with_obstacles):
        """Test neighbor generation."""
        scenario = GridScenario(simple_scenario_config, grid_data_with_obstacles)

        # Corner position - should have 2 neighbors
        neighbors = scenario.neighbors((0, 0))
        assert len(neighbors) == 2
        assert (1, 0) in neighbors
        assert (0, 1) in neighbors

        # Center position with obstacle - should filter out obstacle
        neighbors = scenario.neighbors((1, 0))
        assert (1, 1) not in neighbors  # Obstacle should be filtered

        # Edge position
        neighbors = scenario.neighbors((2, 1))
        expected = [(1, 1), (2, 0), (2, 2)]  # (1,1) is obstacle, should be filtered
        actual_expected = [pos for pos in expected if scenario.passable(pos)]
        assert set(neighbors) == set(actual_expected)

    def test_cost_function(self, simple_scenario_config, grid_data_with_weights):
        """Test cost function."""
        scenario = GridScenario(simple_scenario_config, grid_data_with_weights)

        # Custom edge weight
        assert scenario.cost((0, 0), (1, 0)) == 5.0

        # Default cost for other edges
        assert scenario.cost((0, 0), (0, 1)) == 2.0

        # Non-adjacent nodes should return inf
        assert scenario.cost((0, 0), (2, 2)) == float("inf")


@pytest.mark.unit
class TestScenarioLoader:
    """Test ScenarioLoader factory."""

    def test_from_config(self, scenario_from_loader):
        """Test loading scenario from config."""
        assert scenario_from_loader.width == 3
        assert scenario_from_loader.height == 3
        assert scenario_from_loader.start == (0, 0)
        assert scenario_from_loader.goal == (2, 2)

    def test_from_config_with_demo_grid(self, large_scenario_from_loader):
        """Test loading demo grid."""
        assert large_scenario_from_loader.width == 10
        assert large_scenario_from_loader.height == 10
        assert len(large_scenario_from_loader.obstacles) > 0  # Demo has obstacles


@pytest.mark.unit
class TestContractTestHarness:
    """Test contract validation harness."""

    def test_valid_scenario_passes(self, valid_scenario_for_validation):
        """Test that valid scenario passes contract validation."""
        assert valid_scenario_for_validation["violations"] == []

    def test_out_of_bounds_start_fails(self, invalid_start_scenario_for_validation):
        """Test that out-of-bounds start position fails validation."""
        violations = invalid_start_scenario_for_validation["violations"]
        assert len(violations) > 0
        assert any("start position out of bounds" in v for v in violations)

    def test_out_of_bounds_goal_fails(self, invalid_goal_scenario_for_validation):
        """Test that out-of-bounds goal position fails validation."""
        violations = invalid_goal_scenario_for_validation["violations"]
        assert len(violations) > 0
        assert any("goal position out of bounds" in v for v in violations)

    def test_neighbor_contract_validation(self, valid_scenario_for_validation):
        """Test validation of neighbor contract compliance."""
        violations = valid_scenario_for_validation["violations"]

        # Should pass - neighbors should only return valid, passable positions
        neighbor_violations = [v for v in violations if "neighbors(" in v]
        assert len(neighbor_violations) == 0

    def test_cost_function_validation(self, valid_scenario_for_validation):
        """Test validation of cost function."""
        violations = valid_scenario_for_validation["violations"]

        # Should pass - cost function should work correctly
        cost_violations = [v for v in violations if "cost(" in v]
        assert len(cost_violations) == 0
