"""API routers for the fertilizer timing optimization microservice."""

from .alert_routes import router as alert_router  # noqa: F401
from .calendar_routes import router as calendar_router  # noqa: F401
from .timing_routes import router as timing_router  # noqa: F401

__all__ = ["alert_router", "calendar_router", "timing_router"]
