"""Scenario runtime contract for ALGOViz.

This module provides the Scenario protocol that defines the interface
between algorithms and their execution environment, along with implementations
and validation tools.
"""

from pathlib import Path
from typing import Any, Protocol

import yaml

from agloviz.config.models import ScenarioConfig


class Scenario(Protocol):
    """Runtime contract for algorithm scenarios.
    
    This protocol defines the interface that all scenario implementations
    must provide for algorithms to interact with their environment.
    """
    width: int
    height: int
    start: tuple[int, int]
    goal: tuple[int, int]

    def neighbors(self, node: tuple[int, int]) -> list[tuple[int, int]]:
        """Get valid neighbors for a node.
        
        Args:
            node: The node to get neighbors for
            
        Returns:
            List of valid neighbor positions
        """
        ...

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        """Check if position is within grid bounds.
        
        Args:
            pos: Position to check
            
        Returns:
            True if position is within bounds
        """
        ...

    def passable(self, pos: tuple[int, int]) -> bool:
        """Check if position is passable (not an obstacle).
        
        Args:
            pos: Position to check
            
        Returns:
            True if position is passable
        """
        ...

    def cost(self, from_node: tuple[int, int], to_node: tuple[int, int]) -> float:
        """Get movement cost between adjacent nodes.
        
        Args:
            from_node: Starting position
            to_node: Destination position
            
        Returns:
            Movement cost, or float('inf') if not adjacent
        """
        ...


class GridScenario:
    """Grid-based scenario implementation.
    
    Implements the Scenario protocol for 2D grid environments with
    obstacles and optional edge weights.
    """

    def __init__(self, config: ScenarioConfig, grid_data: dict[str, Any]):
        """Initialize grid scenario.
        
        Args:
            config: Scenario configuration
            grid_data: Grid data loaded from YAML file
        """
        self.width = grid_data["width"]
        self.height = grid_data["height"]
        self.start = tuple(config.start)
        self.goal = tuple(config.goal)
        self.obstacles = set(tuple(pos) for pos in grid_data.get("obstacles", []))
        self.default_cost = grid_data.get("default_cost", 1.0)
        self.edge_weights = self._parse_edge_weights(grid_data.get("weights", []))

    def _parse_edge_weights(self, weights_data: list[dict[str, Any]]) -> dict[tuple[tuple[int, int], tuple[int, int]], float]:
        """Parse edge weights from YAML data.
        
        Args:
            weights_data: List of weight specifications from YAML
            
        Returns:
            Dictionary mapping (from, to) tuples to costs
        """
        edge_weights = {}
        for weight_spec in weights_data:
            from_pos = tuple(weight_spec["from"])
            to_pos = tuple(weight_spec["to"])
            cost = weight_spec["cost"]
            edge_weights[(from_pos, to_pos)] = cost
        return edge_weights

    def neighbors(self, node: tuple[int, int]) -> list[tuple[int, int]]:
        """Get 4-directional neighbors (N, S, E, W), filtered by bounds and passability."""
        x, y = node
        candidates = [(x+1, y), (x-1, y), (x, y+1), (x, y-1)]
        return [pos for pos in candidates
                if self.in_bounds(pos) and self.passable(pos)]

    def in_bounds(self, pos: tuple[int, int]) -> bool:
        """Check if position is within grid bounds."""
        x, y = pos
        return 0 <= x < self.width and 0 <= y < self.height

    def passable(self, pos: tuple[int, int]) -> bool:
        """Check if position is passable (not an obstacle)."""
        return pos not in self.obstacles

    def cost(self, from_node: tuple[int, int], to_node: tuple[int, int]) -> float:
        """Get movement cost between adjacent nodes."""
        # Check edge weights first
        edge_key = (from_node, to_node)
        if edge_key in self.edge_weights:
            return self.edge_weights[edge_key]

        # Verify nodes are adjacent
        if to_node not in self.neighbors(from_node):
            return float('inf')

        return self.default_cost


class ScenarioLoader:
    """Factory for loading scenarios from configuration.
    
    Provides static methods for creating Scenario objects from various sources.
    """

    @staticmethod
    def from_file(path: str) -> Scenario:
        """Load scenario from YAML file path.
        
        Args:
            path: Path to scenario YAML file
            
        Returns:
            Scenario object
        """
        # This would load both scenario and grid files
        # For now, simplified implementation
        raise NotImplementedError("from_file not yet implemented")

    @staticmethod
    def from_config(config: ScenarioConfig) -> Scenario:
        """Convert ScenarioConfig to runtime Scenario.
        
        Args:
            config: Scenario configuration
            
        Returns:
            Scenario object
        """
        # Load grid file referenced by config.grid_file
        grid_path = Path(config.grid_file)
        with open(grid_path) as f:
            grid_data = yaml.safe_load(f)
        return GridScenario(config, grid_data)

    @staticmethod
    def random_grid(width: int, height: int, obstacle_density: float = 0.2) -> Scenario:
        """Generate random grid scenario for testing.
        
        Args:
            width: Grid width
            height: Grid height
            obstacle_density: Fraction of cells that should be obstacles
            
        Returns:
            Random scenario
        """
        # For now, simplified implementation
        raise NotImplementedError("random_grid not yet implemented")


class ContractTestHarness:
    """Test harness for validating scenario contract compliance.
    
    Provides comprehensive validation that scenario implementations
    satisfy the Scenario protocol requirements.
    """

    def verify_scenario(self, scenario: Scenario) -> list[str]:
        """Return list of contract violations, empty if compliant.
        
        Args:
            scenario: Scenario to validate
            
        Returns:
            List of violation descriptions
        """
        violations = []

        # Basic bounds checking
        if not scenario.in_bounds(scenario.start):
            violations.append("start position out of bounds")
        if not scenario.in_bounds(scenario.goal):
            violations.append("goal position out of bounds")

        # Neighbor contract compliance
        for x in range(scenario.width):
            for y in range(scenario.height):
                node = (x, y)
                if scenario.passable(node):
                    neighbors = scenario.neighbors(node)
                    for neighbor in neighbors:
                        if not scenario.in_bounds(neighbor):
                            violations.append(f"neighbors({node}) returned out-of-bounds {neighbor}")
                        if not scenario.passable(neighbor):
                            violations.append(f"neighbors({node}) returned impassable {neighbor}")

        # Cost function compliance
        test_node = scenario.start
        neighbors = scenario.neighbors(test_node)
        if neighbors:
            try:
                cost = scenario.cost(test_node, neighbors[0])
                if cost < 0:
                    violations.append("cost() returned negative value")
            except Exception as e:
                violations.append(f"cost() failed for adjacent nodes: {e}")

            # Test non-adjacent cost (should raise or return inf)
            non_adjacent = (scenario.width + 10, scenario.height + 10)
            try:
                cost = scenario.cost(test_node, non_adjacent)
                if cost != float('inf'):
                    violations.append("cost() should return inf or raise for non-adjacent nodes")
            except ValueError:
                pass  # Expected behavior

        return violations
