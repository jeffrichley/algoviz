"""Test script to verify grid data fixtures work correctly."""

def test_simple_grid_data_fixture(simple_grid_data):
    """Test that simple_grid_data fixture works."""
    assert simple_grid_data["width"] == 3
    assert simple_grid_data["height"] == 3
    assert simple_grid_data["default_cost"] == 1.0
    assert simple_grid_data["obstacles"] == []
    assert simple_grid_data["weights"] == []

def test_grid_data_with_obstacles_fixture(grid_data_with_obstacles):
    """Test that grid_data_with_obstacles fixture works."""
    assert grid_data_with_obstacles["width"] == 3
    assert grid_data_with_obstacles["height"] == 3
    assert grid_data_with_obstacles["obstacles"] == [[1, 1]]

def test_grid_data_with_weights_fixture(grid_data_with_weights):
    """Test that grid_data_with_weights fixture works."""
    assert grid_data_with_weights["default_cost"] == 2.0
    assert len(grid_data_with_weights["weights"]) == 1
    assert grid_data_with_weights["weights"][0]["cost"] == 5.0

def test_parameterized_cost_fixture(grid_data_with_variable_cost):
    """Test that parameterized cost fixture works."""
    assert grid_data_with_variable_cost["default_cost"] in [1.0, 2.0, 5.0, 10.0]
    assert grid_data_with_variable_cost["width"] == 3
    assert grid_data_with_variable_cost["height"] == 3

def test_parameterized_obstacles_fixture(grid_data_with_variable_obstacles):
    """Test that parameterized obstacles fixture works."""
    obstacles = grid_data_with_variable_obstacles["obstacles"]
    assert obstacles in [[], [[1, 1]], [[1, 1], [2, 2]], [[0, 1], [1, 0], [1, 2], [2, 1]]]
    assert grid_data_with_variable_obstacles["width"] == 3
    assert grid_data_with_variable_obstacles["height"] == 3
