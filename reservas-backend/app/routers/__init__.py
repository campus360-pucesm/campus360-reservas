from app.routers.health import router as health_router
from app.routers.recursos import router as recursos_router
from app.routers.reservas import router as reservas_router
from app.routers.checkin import router as checkin_router

__all__ = [
    "health_router",
    "recursos_router",
    "reservas_router",
    "checkin_router"
]