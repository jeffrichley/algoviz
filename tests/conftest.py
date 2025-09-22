"""Test configuration for ALGOViz.

This module provides pytest fixtures and configuration for all tests,
ensuring clean state and proper setup.
"""

import pytest
import logging
from agloviz.config.store_manager import StoreManager
from agloviz.config.models import ScenarioConfig
from agloviz.adapters.bfs import BFSAdapter
from agloviz.adapters.protocol import AdapterWrapper

# Configure logging for tests
logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(__name__)

@pytest.fixture(autouse=True)
def clean_store():
    """Ensure clean store state for each test.
    
    This fixture runs before and after each test to ensure
    that the hydra-zen store is in a clean state.
    """
    # Reset store before test
    StoreManager.reset_for_testing()
    logger.debug("Store reset before test")
    
    yield
    
    # Reset store after test
    StoreManager.reset_for_testing()
    logger.debug("Store reset after test")


@pytest.fixture
def initialized_store():
    """Provide a clean, initialized store for tests that need it."""
    StoreManager.setup_store_for_testing()
    yield StoreManager
    StoreManager.reset_for_testing()


@pytest.fixture
def mock_store():
    """Provide a mock store manager for tests that need to mock store behavior."""
    from unittest.mock import Mock
    mock_manager = Mock(spec=StoreManager)
    mock_manager.is_initialized.return_value = True
    mock_manager.get_registered_groups.return_value = {
        'renderer': True,
        'scenario': True,
        'theme': True,
        'timing': True,
        'scene': True
    }
    return mock_manager


# ============================================================================
# ScenarioConfig Fixtures
# ============================================================================

@pytest.fixture
def simple_scenario_config():
    """Basic 3x3 scenario for simple tests.
    
    Most common pattern found in tests - used for basic functionality testing.
    """
    return ScenarioConfig(
        name="test",
        start=(0, 0),
        goal=(2, 2),
        grid_size=(3, 3)
    )


@pytest.fixture
def small_scenario_config():
    """2x2 scenario for minimal tests.
    
    Used for testing edge cases and minimal scenarios.
    """
    return ScenarioConfig(
        name="test",
        start=(0, 0),
        goal=(1, 1),
        grid_size=(2, 2)
    )


@pytest.fixture
def complex_scenario_config():
    """5x5 scenario with obstacles for complex tests.
    
    Used for testing algorithms with obstacles and more complex pathfinding.
    """
    return ScenarioConfig(
        name="maze",
        start=(0, 0),
        goal=(4, 4),
        grid_size=(5, 5),
        obstacles=[(1, 1), (2, 2), (3, 1)]
    )


@pytest.fixture
def unreachable_scenario_config():
    """Scenario with unreachable goal for testing failure cases.
    
    Used for testing algorithm behavior when goal cannot be reached.
    """
    return ScenarioConfig(
        name="unreachable",
        start=(0, 0),
        goal=(2, 2),
        grid_size=(3, 3),
        obstacles=[(1, 0), (1, 1), (1, 2)]  # Wall blocking path
    )


@pytest.fixture
def start_equals_goal_scenario_config():
    """Scenario where start equals goal.
    
    Used for testing edge case where no pathfinding is needed.
    """
    return ScenarioConfig(
        name="test",
        start=(0, 0),
        goal=(0, 0),  # Same as start
        grid_size=(1, 1)
    )


@pytest.fixture
def large_scenario_config():
    """10x10 scenario for testing larger grids.
    
    Used for testing performance and behavior on larger grids.
    """
    return ScenarioConfig(
        name="demo",
        start=(0, 0),
        goal=(9, 9),
        grid_size=(10, 10),
        obstacles=[(1, 1), (2, 2), (3, 3)]
    )


@pytest.fixture
def out_of_bounds_start_scenario_config():
    """Scenario with out-of-bounds start position.
    
    Used for testing validation and error handling.
    """
    return ScenarioConfig(
        name="test",
        start=(-1, 0),  # Out of bounds
        goal=(2, 2),
        grid_size=(3, 3)
    )


@pytest.fixture
def out_of_bounds_goal_scenario_config():
    """Scenario with out-of-bounds goal position.
    
    Used for testing validation and error handling.
    """
    return ScenarioConfig(
        name="test",
        start=(0, 0),
        goal=(5, 5),  # Out of bounds for 3x3 grid
        grid_size=(3, 3)
    )


@pytest.fixture
def scenario_config_with_custom_name():
    """Scenario with custom name for testing name handling.
    
    Used for testing scenario identification and naming.
    """
    return ScenarioConfig(
        name="custom_test_scenario",
        start=(0, 0),
        goal=(2, 2),
        grid_size=(3, 3)
    )


# ============================================================================
# ScenarioConfig Parameterized Fixtures
# ============================================================================

@pytest.fixture(params=[
    (0, 0), (1, 1), (2, 2), (0, 2), (2, 0)
])
def valid_start_position(request):
    """Valid start positions for 3x3 grid."""
    return request.param


@pytest.fixture(params=[
    (0, 0), (1, 1), (2, 2), (0, 2), (2, 0)
])
def valid_goal_position(request):
    """Valid goal positions for 3x3 grid."""
    return request.param


@pytest.fixture
def scenario_config_with_positions(valid_start_position, valid_goal_position):
    """Scenario config with parameterized start and goal positions."""
    return ScenarioConfig(
        name="test",
        start=valid_start_position,
        goal=valid_goal_position,
        grid_size=(3, 3)
    )


# ============================================================================
# Grid Data Fixtures (for GridScenario tests)
# ============================================================================

@pytest.fixture
def simple_grid_data():
    """Basic 3x3 grid data for GridScenario tests."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": [],
        "weights": []
    }


@pytest.fixture
def grid_data_with_obstacles():
    """3x3 grid data with obstacles."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": [[1, 1]],
        "weights": []
    }


@pytest.fixture
def grid_data_with_weights():
    """3x3 grid data with custom edge weights."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 2.0,
        "obstacles": [],
        "weights": [{"from": [0, 0], "to": [1, 0], "cost": 5.0}]
    }


@pytest.fixture
def large_grid_data():
    """10x10 grid data for larger scenarios."""
    return {
        "width": 10,
        "height": 10,
        "default_cost": 1.0,
        "obstacles": [[1, 1], [2, 2], [3, 3]],
        "weights": []
    }


@pytest.fixture
def grid_data_with_multiple_obstacles():
    """3x3 grid data with multiple obstacles."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": [[1, 1], [2, 1]],  # Multiple obstacles
        "weights": []
    }


@pytest.fixture
def grid_data_with_custom_default_cost():
    """3x3 grid data with custom default cost."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 2.0,  # Custom default cost
        "obstacles": [],
        "weights": []
    }


@pytest.fixture
def grid_data_with_complex_weights():
    """3x3 grid data with multiple custom edge weights."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": [],
        "weights": [
            {"from": [0, 0], "to": [1, 0], "cost": 5.0},
            {"from": [1, 0], "to": [2, 0], "cost": 3.0},
            {"from": [0, 0], "to": [0, 1], "cost": 2.0}
        ]
    }


@pytest.fixture
def grid_data_for_validation_tests():
    """3x3 grid data specifically for validation testing."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": [],
        "weights": []
    }


# ============================================================================
# Grid Data Parameterized Fixtures
# ============================================================================

@pytest.fixture(params=[1.0, 2.0, 5.0, 10.0])
def grid_data_with_variable_cost(request):
    """3x3 grid data with parameterized default cost."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": request.param,
        "obstacles": [],
        "weights": []
    }


@pytest.fixture(params=[
    [],  # No obstacles
    [[1, 1]],  # Single obstacle
    [[1, 1], [2, 2]],  # Multiple obstacles
    [[0, 1], [1, 0], [1, 2], [2, 1]]  # Many obstacles
])
def grid_data_with_variable_obstacles(request):
    """3x3 grid data with parameterized obstacles."""
    return {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": request.param,
        "weights": []
    }


# ============================================================================
# BFS Adapter and Wrapper Fixtures
# ============================================================================

@pytest.fixture
def bfs_adapter():
    """BFS adapter instance for testing."""
    return BFSAdapter()


@pytest.fixture
def bfs_wrapper(bfs_adapter):
    """BFS adapter with wrapper for step indexing."""
    return AdapterWrapper(bfs_adapter)


@pytest.fixture
def bfs_events_simple(bfs_wrapper, simple_scenario_config):
    """BFS events for simple scenario."""
    return list(bfs_wrapper.run_with_indexing(simple_scenario_config))


@pytest.fixture
def bfs_events_small(bfs_wrapper, small_scenario_config):
    """BFS events for small scenario."""
    return list(bfs_wrapper.run_with_indexing(small_scenario_config))


@pytest.fixture
def bfs_events_complex(bfs_wrapper, complex_scenario_config):
    """BFS events for complex scenario with obstacles."""
    return list(bfs_wrapper.run_with_indexing(complex_scenario_config))


@pytest.fixture
def bfs_events_unreachable(bfs_wrapper, unreachable_scenario_config):
    """BFS events for unreachable scenario."""
    return list(bfs_wrapper.run_with_indexing(unreachable_scenario_config))


@pytest.fixture
def bfs_events_start_equals_goal(bfs_wrapper, start_equals_goal_scenario_config):
    """BFS events for start equals goal scenario."""
    return list(bfs_wrapper.run_with_indexing(start_equals_goal_scenario_config))


# ============================================================================
# Mock Adapter Fixtures (for protocol testing)
# ============================================================================

@pytest.fixture
def mock_events_basic():
    """Basic mock events for testing."""
    from agloviz.core.events import VizEvent
    return [
        VizEvent(type="enqueue", payload={"node": (0, 0)}, step_index=999),
        VizEvent(type="dequeue", payload={"node": (0, 0)}, step_index=999),
        VizEvent(type="goal_found", payload={"node": (1, 1)}, step_index=999),
    ]


@pytest.fixture
def mock_events_with_metadata():
    """Mock events with metadata for testing."""
    from agloviz.core.events import VizEvent
    return [
        VizEvent(
            type="enqueue",
            payload={"node": (0, 0)},
            step_index=999,
            metadata={"complexity": 5}
        )
    ]


@pytest.fixture
def mock_adapter_basic(mock_events_basic):
    """Mock adapter with basic events."""
    from agloviz.config.models import ScenarioConfig
    from agloviz.core.events import VizEvent
    
    class MockAdapter:
        """Mock adapter for testing."""
        name = "mock"

        def __init__(self, events: list[VizEvent]):
            self.events = events

        def run(self, scenario: ScenarioConfig):
            """Yield mock events."""
            for event in self.events:
                yield event
    
    return MockAdapter(mock_events_basic)


@pytest.fixture
def mock_adapter_with_metadata(mock_events_with_metadata):
    """Mock adapter with events containing metadata."""
    from agloviz.config.models import ScenarioConfig
    from agloviz.core.events import VizEvent
    
    class MockAdapter:
        """Mock adapter for testing."""
        name = "mock"

        def __init__(self, events: list[VizEvent]):
            self.events = events

        def run(self, scenario: ScenarioConfig):
            """Yield mock events."""
            for event in self.events:
                yield event
    
    return MockAdapter(mock_events_with_metadata)


@pytest.fixture
def mock_wrapper_basic(mock_adapter_basic):
    """Mock adapter with wrapper for step indexing."""
    return AdapterWrapper(mock_adapter_basic)


@pytest.fixture
def mock_wrapper_with_metadata(mock_adapter_with_metadata):
    """Mock adapter with metadata and wrapper for step indexing."""
    return AdapterWrapper(mock_adapter_with_metadata)


# ============================================================================
# Registry Management Fixtures
# ============================================================================

@pytest.fixture(autouse=True)
def clean_registries():
    """Auto-clean all registries before/after each test."""
    from agloviz.adapters.registry import AdapterRegistry
    from agloviz.core.routing import RoutingRegistry
    
    AdapterRegistry.clear()
    RoutingRegistry.clear()
    yield
    AdapterRegistry.clear()
    RoutingRegistry.clear()


@pytest.fixture
def registered_bfs_adapter():
    """BFS adapter registered in registry."""
    from agloviz.adapters.registry import AdapterRegistry
    
    AdapterRegistry.register(BFSAdapter)
    yield
    AdapterRegistry.clear()


@pytest.fixture
def bfs_adapter_from_registry(registered_bfs_adapter):
    """BFS adapter instance obtained from registry."""
    from agloviz.adapters.registry import AdapterRegistry
    
    adapter_class = AdapterRegistry.get("bfs")
    return adapter_class()


@pytest.fixture
def bfs_wrapper_from_registry(bfs_adapter_from_registry):
    """BFS adapter with wrapper obtained from registry."""
    return AdapterWrapper(bfs_adapter_from_registry)


# ============================================================================
# Scenario Factory Fixtures
# ============================================================================

@pytest.fixture
def contract_test_harness():
    """ContractTestHarness instance for validation testing."""
    from agloviz.core.scenario import ContractTestHarness
    return ContractTestHarness()


@pytest.fixture
def scenario_loader():
    """ScenarioLoader for creating scenarios from configs."""
    from agloviz.core.scenario import ScenarioLoader
    return ScenarioLoader


# ============================================================================
# Scenario Creation Factory Fixtures
# ============================================================================

@pytest.fixture
def scenario_from_loader(simple_scenario_config, scenario_loader):
    """Scenario created from config using ScenarioLoader."""
    return scenario_loader.from_config(simple_scenario_config)


@pytest.fixture
def large_scenario_from_loader(large_scenario_config, scenario_loader):
    """Large scenario created from config using ScenarioLoader."""
    return scenario_loader.from_config(large_scenario_config)


@pytest.fixture
def scenario_with_obstacles_from_loader(complex_scenario_config, scenario_loader):
    """Scenario with obstacles created from config using ScenarioLoader."""
    return scenario_loader.from_config(complex_scenario_config)


# ============================================================================
# Validation Testing Fixtures
# ============================================================================

@pytest.fixture
def valid_scenario_for_validation(simple_scenario_config, scenario_loader, contract_test_harness):
    """Complete validation setup: valid scenario + harness."""
    scenario = scenario_loader.from_config(simple_scenario_config)
    return {
        "scenario": scenario,
        "harness": contract_test_harness,
        "violations": contract_test_harness.verify_scenario(scenario)
    }


@pytest.fixture
def invalid_start_scenario_for_validation(out_of_bounds_start_scenario_config, grid_data_for_validation_tests, contract_test_harness):
    """Complete validation setup: invalid start scenario + harness."""
    from agloviz.core.scenario import GridScenario
    scenario = GridScenario(out_of_bounds_start_scenario_config, grid_data_for_validation_tests)
    return {
        "scenario": scenario,
        "harness": contract_test_harness,
        "violations": contract_test_harness.verify_scenario(scenario)
    }


@pytest.fixture
def invalid_goal_scenario_for_validation(out_of_bounds_goal_scenario_config, grid_data_for_validation_tests, contract_test_harness):
    """Complete validation setup: invalid goal scenario + harness."""
    from agloviz.core.scenario import GridScenario
    scenario = GridScenario(out_of_bounds_goal_scenario_config, grid_data_for_validation_tests)
    return {
        "scenario": scenario,
        "harness": contract_test_harness,
        "violations": contract_test_harness.verify_scenario(scenario)
    }
