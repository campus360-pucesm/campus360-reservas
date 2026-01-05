from app.schemas.schemas import (
    # Recursos
    RecursoBase,
    RecursoCreate,
    RecursoUpdate,
    RecursoResponse,
    RecursoDisponibilidad,
    
    # Reservas
    ReservaBase,
    ReservaCreate,
    ReservaUpdate,
    ReservaCancelar,
    ReservaResponse,
    ReservaDetalleResponse,
    
    # Check-in
    CheckinCreate,
    CheckinResponse,
    CheckinValidacion,
    
    # Filtros y paginación
    FiltroRecursos,
    FiltroReservas,
    PaginacionParams,
    PaginatedResponse,
    
    # Generales
    MensajeResponse,
    ErrorResponse,
    
    # QR
    RecursoQRCreate,
    RecursoQRResponse
)

__all__ = [
    "RecursoBase",
    "RecursoCreate",
    "RecursoUpdate",
    "RecursoResponse",
    "RecursoDisponibilidad",
    "ReservaBase",
    "ReservaCreate",
    "ReservaUpdate",
    "ReservaCancelar",
    "ReservaResponse",
    "ReservaDetalleResponse",
    "CheckinCreate",
    "CheckinResponse",
    "CheckinValidacion",
    "FiltroRecursos",
    "FiltroReservas",
    "PaginacionParams",
    "PaginatedResponse",
    "MensajeResponse",
    "ErrorResponse",
    "RecursoQRCreate",
    "RecursoQRResponse"
]