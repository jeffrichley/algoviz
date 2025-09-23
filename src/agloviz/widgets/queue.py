"""QueueWidget for BFS queue visualization.

This module provides the QueueWidget for visualizing BFS queue operations
with enqueue/dequeue animations and queue state management.
"""

from typing import Any

from manim import *

# No longer import VizEvent - widgets are pure visual
from .protocol import Widget


class QueueWidget(Widget):
    """Visual representation of BFS queue with enqueue/dequeue animations.
    
    The QueueWidget maintains a visual queue that synchronizes with algorithm
    queue operations through VizEvent updates.
    """

    def __init__(self, max_visible_items: int = 8, item_width: float = 1.0, item_height: float = 0.6, spacing: float = 0.1):
        self.queue_group: VGroup | None = None
        self.queue_items: list = []  # Changed to list for pure visual operations
        self.queue_data: list = []   # Changed to list for pure visual operations
        self.max_visible_items: int = max_visible_items
        self.item_width: float = item_width
        self.item_height: float = item_height
        self.spacing: float = spacing

    def show(self, scene: Any, **kwargs) -> None:
        """Initialize queue visualization.
        
        Args:
            scene: Manim scene instance
            **kwargs: Optional runtime parameters like run_time
        """
        run_time = kwargs.get("run_time", 1.0)

        self._create_queue_container(scene)
        scene.play(FadeIn(self.queue_group), run_time=run_time)


    def hide(self, scene: Any) -> None:
        """Clean teardown of queue visualization.
        
        Args:
            scene: Manim scene instance
        """
        if self.queue_group:
            scene.play(FadeOut(self.queue_group))
            self.queue_group = None
            self.queue_items.clear()
            self.queue_data.clear()

    def _create_queue_container(self, scene: Any) -> None:
        """Create queue container structure.
        
        Args:
            scene: Manim scene instance
        """
        # Create queue label
        queue_label = Text("Queue:", font_size=24)
        queue_label.to_edge(LEFT + UP)

        # Create queue container outline
        container_width = (self.item_width + self.spacing) * self.max_visible_items
        container = Rectangle(width=container_width, height=self.item_height + 0.2)
        container.set_stroke(WHITE, width=2)
        container.set_fill(BLACK, opacity=0.1)
        container.next_to(queue_label, DOWN, buff=0.3)

        self.queue_group = VGroup(queue_label, container)
        self.container = container  # Store reference for positioning

    def add_element(self, element: Any, label: str | None = None):
        """Pure visual operation: add element to queue.
        
        Args:
            element: Element to add (any data)
            label: Optional text label for the element
        """
        from .primitives import MarkerWidget

        # Create visual representation
        item_widget = MarkerWidget(width=self.item_width, height=self.item_height)
        item_widget.highlight(BLUE, opacity=0.8)

        if label:
            item_widget.set_label(label)
        elif hasattr(element, '__str__'):
            item_widget.set_label(str(element))

        # Add to queue state
        self.queue_items.append(item_widget)
        self.queue_data.append(element)

        # Arrange queue items horizontally using Manim's layout
        if len(self.queue_items) > 1:
            queue_group = VGroup(*self.queue_items)
            queue_group.arrange(RIGHT, buff=0.1)

        return item_widget  # Return for potential animation

    def remove_element(self, index: int = 0):
        """Pure visual operation: remove element from queue.
        
        Args:
            index: Index of element to remove (default: 0 for FIFO)
            
        Returns:
            Tuple of (removed_data, removed_widget) for potential animation
        """
        if not self.queue_items or index >= len(self.queue_items):
            return None, None

        # Remove from state
        removed_widget = self.queue_items[index]
        removed_data = self.queue_data[index]

        del self.queue_items[index]
        del self.queue_data[index]

        # Rearrange remaining items using Manim's layout
        if self.queue_items:
            from .primitives import ContainerGroup
            queue_group = ContainerGroup(*self.queue_items)
            queue_group.arrange_horizontal(spacing=0.1)

        return removed_data, removed_widget

    def _get_queue_position(self, index: int) -> list[float]:
        """Calculate position for queue item at given index.
        
        Args:
            index: Queue position index
            
        Returns:
            Position coordinates [x, y, z]
        """
        container_left = self.container.get_left()
        x_offset = index * (self.item_width + self.spacing) + self.item_width / 2
        x_pos = container_left[0] + x_offset + 0.1  # Small padding
        y_pos = self.container.get_center()[1]

        return [x_pos, y_pos, 0]

    def _slide_queue_forward(self, scene: Any, run_time: float) -> None:
        """Slide all queue items forward after dequeue.
        
        Args:
            scene: Manim scene instance
            run_time: Animation duration
        """
        animations = []

        for i, item in enumerate(self.queue_items):
            target_pos = self._get_queue_position(i)
            animations.append(item.animate.move_to(target_pos))

        if animations:
            scene.play(*animations, run_time=run_time)

    def _handle_queue_overflow(self, scene: Any, run_time: float) -> None:
        """Handle queue overflow by removing leftmost items.
        
        Args:
            scene: Manim scene instance
            run_time: Animation duration
        """
        while len(self.queue_items) > self.max_visible_items:
            # Remove oldest item (leftmost)
            old_item = self.queue_items.popleft()
            self.queue_data.popleft()

            # Fade out the overflow item
            scene.play(FadeOut(old_item, shift=LEFT), run_time=run_time)

        # Slide remaining items to proper positions
        self._slide_queue_forward(scene, run_time)
