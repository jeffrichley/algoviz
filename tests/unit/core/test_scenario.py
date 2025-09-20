"""Tests for scenario runtime contract."""

import pytest

from agloviz.config.models import ScenarioConfig
from agloviz.core.scenario import ContractTestHarness, GridScenario, ScenarioLoader


@pytest.mark.unit
class TestGridScenario:
    """Test GridScenario implementation."""

    def test_create_simple_scenario(self):
        """Test creating a simple grid scenario."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 1.0,
            "obstacles": [],
            "weights": []
        }

        scenario = GridScenario(config, grid_data)

        assert scenario.width == 3
        assert scenario.height == 3
        assert scenario.start == (0, 0)
        assert scenario.goal == (2, 2)
        assert len(scenario.obstacles) == 0

    def test_scenario_with_obstacles(self):
        """Test scenario with obstacles."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 1.0,
            "obstacles": [[1, 1]],
            "weights": []
        }

        scenario = GridScenario(config, grid_data)

        assert (1, 1) in scenario.obstacles
        assert not scenario.passable((1, 1))
        assert scenario.passable((0, 0))

    def test_in_bounds(self):
        """Test in_bounds checking."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 1.0,
            "obstacles": [],
            "weights": []
        }

        scenario = GridScenario(config, grid_data)

        # Valid positions
        assert scenario.in_bounds((0, 0))
        assert scenario.in_bounds((2, 2))
        assert scenario.in_bounds((1, 1))

        # Invalid positions
        assert not scenario.in_bounds((-1, 0))
        assert not scenario.in_bounds((0, -1))
        assert not scenario.in_bounds((3, 2))
        assert not scenario.in_bounds((2, 3))

    def test_neighbors(self):
        """Test neighbor generation."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 1.0,
            "obstacles": [[1, 1]],
            "weights": []
        }

        scenario = GridScenario(config, grid_data)

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

    def test_cost_function(self):
        """Test cost function."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 2.0,
            "obstacles": [],
            "weights": [
                {"from": [0, 0], "to": [1, 0], "cost": 5.0}
            ]
        }

        scenario = GridScenario(config, grid_data)

        # Custom edge weight
        assert scenario.cost((0, 0), (1, 0)) == 5.0

        # Default cost for other edges
        assert scenario.cost((0, 0), (0, 1)) == 2.0

        # Non-adjacent nodes should return inf
        assert scenario.cost((0, 0), (2, 2)) == float('inf')


@pytest.mark.unit
class TestScenarioLoader:
    """Test ScenarioLoader factory."""

    def test_from_config(self):
        """Test loading scenario from config."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        scenario = ScenarioLoader.from_config(config)

        assert scenario.width == 3
        assert scenario.height == 3
        assert scenario.start == (0, 0)
        assert scenario.goal == (2, 2)

    def test_from_config_with_demo_grid(self):
        """Test loading demo grid."""
        config = ScenarioConfig(
            name="demo",
            grid_file="grids/demo.yaml",
            start=(0, 0),
            goal=(9, 9)
        )

        scenario = ScenarioLoader.from_config(config)

        assert scenario.width == 10
        assert scenario.height == 10
        assert len(scenario.obstacles) > 0  # Demo has obstacles


@pytest.mark.unit
class TestContractTestHarness:
    """Test contract validation harness."""

    def test_valid_scenario_passes(self):
        """Test that valid scenario passes contract validation."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        scenario = ScenarioLoader.from_config(config)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)
        assert violations == []

    def test_out_of_bounds_start_fails(self):
        """Test that out-of-bounds start position fails validation."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(-1, 0),  # Out of bounds
            goal=(2, 2)
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 1.0,
            "obstacles": [],
            "weights": []
        }

        scenario = GridScenario(config, grid_data)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)
        assert len(violations) > 0
        assert any("start position out of bounds" in v for v in violations)

    def test_out_of_bounds_goal_fails(self):
        """Test that out-of-bounds goal position fails validation."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test.yaml",
            start=(0, 0),
            goal=(5, 5)  # Out of bounds for 3x3 grid
        )

        grid_data = {
            "width": 3,
            "height": 3,
            "default_cost": 1.0,
            "obstacles": [],
            "weights": []
        }

        scenario = GridScenario(config, grid_data)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)
        assert len(violations) > 0
        assert any("goal position out of bounds" in v for v in violations)

    def test_neighbor_contract_validation(self):
        """Test validation of neighbor contract compliance."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        scenario = ScenarioLoader.from_config(config)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)

        # Should pass - neighbors should only return valid, passable positions
        neighbor_violations = [v for v in violations if "neighbors(" in v]
        assert len(neighbor_violations) == 0

    def test_cost_function_validation(self):
        """Test validation of cost function."""
        config = ScenarioConfig(
            name="test",
            grid_file="grids/test_simple.yaml",
            start=(0, 0),
            goal=(2, 2)
        )

        scenario = ScenarioLoader.from_config(config)
        harness = ContractTestHarness()

        violations = harness.verify_scenario(scenario)

        # Should pass - cost function should work correctly
        cost_violations = [v for v in violations if "cost(" in v]
        assert len(cost_violations) == 0
