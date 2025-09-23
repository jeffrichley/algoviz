"""Event playback system for Director."""

from collections.abc import Iterator
from typing import Any

from agloviz.adapters.protocol import AlgorithmAdapter
from agloviz.config.models import ScenarioConfig
from agloviz.core.events import VizEvent
from agloviz.core.routing import RoutingMap


class EventPlayback:
    """Handles playback of algorithm events through widget routing."""

    def __init__(self, scene: Any, active_widgets: dict[str, Any]):
        self.scene = scene
        self.active_widgets = active_widgets

    def play_events(
        self,
        adapter: AlgorithmAdapter,
        scenario: ScenarioConfig,
        routing_map: RoutingMap,
        event_run_time: float,
    ) -> Iterator[VizEvent]:
        """Play algorithm events through widget routing."""

        # Generate events from adapter
        events = list(adapter.run(scenario))

        # Route each event to appropriate widgets
        for event in events:
            self._route_event(event, routing_map, event_run_time)
            yield event

    def _route_event(
        self, event: VizEvent, routing_map: RoutingMap, run_time: float
    ) -> None:
        """Route a single event to appropriate widget handlers."""
        if event.type not in routing_map:
            return

        handlers = routing_map[event.type]

        for handler_name in handlers:
            try:
                widget_name, method_name = handler_name.split(".", 1)

                if widget_name in self.active_widgets:
                    widget = self.active_widgets[widget_name]

                    # Call widget update method
                    widget.update(self.scene, event, run_time)

            except ValueError:
                # Invalid handler format, skip
                continue
            except Exception:
                # Widget update failed, continue with other handlers
                continue
