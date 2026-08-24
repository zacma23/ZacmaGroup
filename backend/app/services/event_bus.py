"""Internal Event Bus for Platform-wide Cross-Module Coordination.

Allows decoupled publication and consumption of lifecycle events:
- organization.inquiry.created
- lead.created
- lead.updated
- contact.created
- student.registered
- course.enrolled
- payment.successful
- payment.failed
- campaign.sent
- activity.created
"""

import logging
from typing import Any, Callable, Coroutine, Union

logger = logging.getLogger("zacma.events")

HandlerType = Union[Callable[[str, dict[str, Any]], None], Callable[[str, dict[str, Any]], Coroutine[Any, Any, None]]]

_SUBSCRIBERS: dict[str, list[HandlerType]] = {}


class EventBus:
    """Lightweight in-process event bus with synchronous and asynchronous dispatch."""

    @staticmethod
    def subscribe(event_name: str, handler: HandlerType):
        """Register a handler for a specific event name or wildcard '*'."""
        if event_name not in _SUBSCRIBERS:
            _SUBSCRIBERS[event_name] = []
        _SUBSCRIBERS[event_name].append(handler)

    @staticmethod
    def publish(tenant_id: str, event_name: str, payload: dict[str, Any]):
        """Dispatch event to all registered handlers."""
        logger.info("EventBus: Publishing '%s' for tenant '%s'", event_name, tenant_id)
        handlers = _SUBSCRIBERS.get(event_name, []) + _SUBSCRIBERS.get("*", [])
        for handler in handlers:
            try:
                handler(tenant_id, payload)
            except Exception as exc:
                logger.error("EventBus error in handler for '%s': %s", event_name, exc, exc_info=True)


# Convenience singleton
event_bus = EventBus()
