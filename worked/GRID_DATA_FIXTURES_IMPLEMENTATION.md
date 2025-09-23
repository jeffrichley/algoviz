# Grid Data Fixtures Implementation

## Overview

This document outlines how the Grid Data creation patterns have been extracted into reusable pytest fixtures to eliminate duplication across test files.

## Problem Analysis

**Duplication Found:**
- Grid data dictionaries with `width`, `height`, `default_cost`, `obstacles`, `weights` appeared in **4+ test files**
- Common patterns: 3x3 grids, 5x5 grids, custom costs, edge weights
- Repeated parameter combinations in `test_scenario.py` and other test files

## Solution: Comprehensive Grid Data Fixture Library

### 1. Basic Grid Data Fixtures

#### `simple_grid_data`
```python
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
```
**Usage:** Most common pattern - basic 3x3 grid for simple tests.

#### `grid_data_with_obstacles`
```python
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
```
**Usage:** Testing obstacle handling and pathfinding around barriers.

#### `grid_data_with_weights`
```python
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
```
**Usage:** Testing cost function with custom edge weights.

### 2. Advanced Grid Data Fixtures

#### `large_grid_data`
```python
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
```
**Usage:** Testing performance and behavior on larger grids.

#### `grid_data_with_multiple_obstacles`
```python
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
```
**Usage:** Testing complex obstacle patterns and pathfinding.

#### `grid_data_with_custom_default_cost`
```python
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
```
**Usage:** Testing cost function with different default costs.

#### `grid_data_with_complex_weights`
```python
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
```
**Usage:** Testing complex weight scenarios with multiple custom edges.

#### `grid_data_for_validation_tests`
```python
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
```
**Usage:** Clean grid data for validation and error testing.

### 3. Parameterized Grid Data Fixtures

#### `grid_data_with_variable_cost`
```python
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
```
**Usage:** Testing with multiple cost values automatically.

#### `grid_data_with_variable_obstacles`
```python
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
```
**Usage:** Testing with various obstacle configurations automatically.

## Before/After Comparison

### Before (Duplicated Code)
```python
def test_create_simple_scenario(self):
    """Test creating a simple grid scenario."""
    config = ScenarioConfig(
        name="test",
        start=(0, 0),
        goal=(2, 2),
        grid_size=(3, 3)
    )

    grid_data = {
        "width": 3,
        "height": 3,
        "default_cost": 1.0,
        "obstacles": [],
        "weights": []
    }

    scenario = GridScenario(config, grid_data)
    # ... rest of test
```

### After (Using Fixtures)
```python
def test_create_simple_scenario(self, simple_scenario_config, simple_grid_data):
    """Test creating a simple grid scenario."""
    scenario = GridScenario(simple_scenario_config, simple_grid_data)
    # ... rest of test
```

## Benefits

1. **Eliminated Duplication:** Removed 6+ instances of grid data creation across test files
2. **Improved Maintainability:** Changes to grid data patterns only need to be made in one place
3. **Enhanced Readability:** Test methods focus on the actual test logic, not setup
4. **Consistent Test Data:** All tests use the same well-defined grid data patterns
5. **Easier Test Writing:** New tests can immediately use appropriate fixtures
6. **Parameterized Testing:** Automatic testing with multiple configurations

## Files Affected

The following test files can now use these fixtures instead of creating grid data manually:

- ✅ `tests/unit/core/test_scenario.py` **Refactored**
- `tests/unit/test_manim_integration_basic.py` (potential usage)
- Other test files that create GridScenario instances

## Usage Examples

### Basic Usage
```python
def test_scenario_creation(self, simple_scenario_config, simple_grid_data):
    # Use the fixtures directly
    scenario = GridScenario(simple_scenario_config, simple_grid_data)
    assert scenario.width == 3
    assert scenario.height == 3
```

### Testing with Obstacles
```python
def test_obstacle_handling(self, simple_scenario_config, grid_data_with_obstacles):
    # Test obstacle behavior
    scenario = GridScenario(simple_scenario_config, grid_data_with_obstacles)
    assert (1, 1) in scenario.obstacles
    assert not scenario.passable((1, 1))
```

### Testing with Custom Weights
```python
def test_cost_function(self, simple_scenario_config, grid_data_with_weights):
    # Test custom edge weights
    scenario = GridScenario(simple_scenario_config, grid_data_with_weights)
    assert scenario.cost((0, 0), (1, 0)) == 5.0
    assert scenario.cost((0, 0), (0, 1)) == 2.0  # Default cost
```

### Parameterized Testing
```python
def test_variable_costs(self, simple_scenario_config, grid_data_with_variable_cost):
    # Automatically tests with multiple cost values
    scenario = GridScenario(simple_scenario_config, grid_data_with_variable_cost)
    assert scenario.default_cost in [1.0, 2.0, 5.0, 10.0]
```

### Validation Testing
```python
def test_validation(self, out_of_bounds_scenario_config, grid_data_for_validation_tests):
    # Clean grid data for validation tests
    scenario = GridScenario(out_of_bounds_scenario_config, grid_data_for_validation_tests)
    violations = harness.verify_scenario(scenario)
    assert len(violations) > 0
```

## Implementation Status

- ✅ **Fixtures Created:** All grid data fixtures implemented in `tests/conftest.py`
- ✅ **Test Refactored:** `test_scenario.py` refactored to use fixtures
- ✅ **Verification:** Tests pass with fixture usage
- ✅ **Import Cleanup:** Removed unused ScenarioConfig import
- 🔄 **Remaining Work:** Apply fixtures to other test files that create GridScenario instances

## Grid Data Structure

All fixtures follow the standard grid data structure:

```python
{
    "width": int,           # Grid width
    "height": int,          # Grid height  
    "default_cost": float,  # Default edge cost
    "obstacles": list,      # List of [x, y] obstacle positions
    "weights": list         # List of custom edge weights
}
```

### Obstacle Format
```python
"obstacles": [[1, 1], [2, 2]]  # List of [x, y] coordinates
```

### Weight Format
```python
"weights": [
    {"from": [0, 0], "to": [1, 0], "cost": 5.0},
    {"from": [1, 0], "to": [2, 0], "cost": 3.0}
]
```

## Code Reduction Impact

**Estimated Reduction:**
- **Lines of Code:** ~40-50% reduction in grid data setup code
- **Duplication:** Eliminated 6+ instances of grid data creation
- **Maintainability:** Single source of truth for grid data patterns
- **Consistency:** Standardized grid data across all test files
- **Test Coverage:** Parameterized fixtures provide broader test coverage

## Next Steps

1. **Apply to Remaining Files:** Update other test files to use these fixtures
2. **Add More Fixtures:** Create additional fixtures for other common patterns
3. **Documentation:** Update test documentation to reference available fixtures
4. **Training:** Ensure team members understand fixture usage patterns

## Integration with ScenarioConfig Fixtures

These grid data fixtures work seamlessly with the ScenarioConfig fixtures:

```python
def test_complete_scenario(self, simple_scenario_config, simple_grid_data):
    # Combine both fixture types
    scenario = GridScenario(simple_scenario_config, simple_grid_data)
    # Test complete scenario functionality
```

This provides a complete testing framework for scenario and grid data combinations.
