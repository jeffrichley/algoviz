"""QueueWidget for BFS queue visualization.

This module provides the QueueWidget for visualizing BFS queue operations
with enqueue/dequeue animations and queue state management.
"""

from collections import deque
from typing import Any, Deque, Tuple
from manim import *
from agloviz.core.events import VizEvent, PayloadKey
from .protocol import Widget


class QueueWidget(Widget):
    """Visual representation of BFS queue with enqueue/dequeue animations.
    
    The QueueWidget maintains a visual queue that synchronizes with algorithm
    queue operations through VizEvent updates.
    """
    
    def __init__(self):
        self.queue_group: VGroup | None = None
        self.queue_items: Deque[VGroup] = deque()
        self.queue_data: Deque[Tuple[int, int]] = deque()
        self.max_visible_items: int = 8
        self.item_width: float = 1.0
        self.item_height: float = 0.6
        self.spacing: float = 0.1
    
    def show(self, scene: Any, **kwargs) -> None:
        """Initialize queue visualization.
        
        Args:
            scene: Manim scene instance
            **kwargs: Configuration parameters including max_items, run_time
        """
        self.max_visible_items = kwargs.get("max_items", 8)
        run_time = kwargs.get("run_time", 1.0)
        
        self._create_queue_container(scene)
        scene.play(FadeIn(self.queue_group), run_time=run_time)
    
    def update(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """Handle queue events from BFS routing.
        
        Args:
            scene: Manim scene instance
            event: VizEvent to process
            run_time: Duration for any animations
        """
        if event.type == "enqueue":
            self._highlight_enqueue(scene, event, run_time)
        elif event.type == "dequeue":
            self._highlight_dequeue(scene, event, run_time)
    
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
    
    def _highlight_enqueue(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """Handle queue.highlight_enqueue routing.
        
        Args:
            scene: Manim scene instance
            event: VizEvent containing node information
            run_time: Animation duration
        """
        if PayloadKey.NODE not in event.payload:
            return
        
        node = event.payload[PayloadKey.NODE]
        
        # Create new queue item
        item = Rectangle(width=self.item_width, height=self.item_height)
        item.set_fill(BLUE, opacity=0.8)
        item.set_stroke(WHITE, width=2)
        
        # Add node label
        label = Text(f"({node[0]},{node[1]})", font_size=16)
        label.move_to(item.get_center())
        
        item_group = VGroup(item, label)
        
        # Position at end of queue (right side)
        start_pos = self.container.get_right() + RIGHT * 2
        item_group.move_to(start_pos)
        
        # Add to scene
        scene.add(item_group)
        
        # Calculate target position in queue
        target_pos = self._get_queue_position(len(self.queue_items))
        
        # Animate into queue
        scene.play(
            item_group.animate.move_to(target_pos),
            run_time=run_time
        )
        
        # Add to queue state
        self.queue_items.append(item_group)
        self.queue_data.append(node)
        
        # Handle overflow if needed
        if len(self.queue_items) > self.max_visible_items:
            self._handle_queue_overflow(scene, run_time * 0.5)
    
    def _highlight_dequeue(self, scene: Any, event: VizEvent, run_time: float) -> None:
        """Handle queue.highlight_dequeue routing.
        
        Args:
            scene: Manim scene instance
            event: VizEvent containing node information
            run_time: Animation duration
        """
        if not self.queue_items:
            return
        
        # Remove from front of queue
        item = self.queue_items.popleft()
        self.queue_data.popleft()
        
        # Highlight and remove animation
        scene.play(
            Succession(
                item.animate.set_fill(YELLOW, opacity=1.0),
                FadeOut(item, shift=UP),
            ),
            run_time=run_time
        )
        
        # Slide remaining items forward
        if self.queue_items:
            self._slide_queue_forward(scene, run_time * 0.5)
    
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
