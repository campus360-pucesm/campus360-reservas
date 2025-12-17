from pydantic import BaseModel, Field, field_validator
from typing import Optional, List
from datetime import date, time, datetime
from enum import Enum

from app.models import TipoRecurso, TipoEquipo, EstadoRecurso, EstadoReserva


# ============================================
# SCHEMAS DE RECURSOS
# ============================================

class RecursoBase(BaseModel):
    """Schema base para recursos"""
    nombre: str = Field(..., min_length=1, max_length=100, description="Nombre del recurso")
    descripcion: Optional[str] = Field(None, max_length=500)
    tipo: TipoRecurso
    tipo_equipo: Optional[TipoEquipo] = None
    ubicacion: Optional[str] = Field(None, max_length=200)
    capacidad: int = Field(default=1, ge=1, le=500)
    equipamiento: Optional[List[str]] = None
    restricciones: Optional[str] = None
    imagen_url: Optional[str] = None
    horario_inicio: time = Field(default=time(7, 0))
    horario_fin: time = Field(default=time(21, 0))
    dias_disponibles: List[int] = Field(default=[1, 2, 3, 4, 5])  # 1=Lunes, 7=Domingo
    requiere_aprobacion: bool = False

    @field_validator('tipo_equipo')
    @classmethod
    def validar_tipo_equipo(cls, v, info):
        """tipo_equipo solo es válido si tipo es 'equipo'"""
        if v is not None and info.data.get('tipo') != TipoRecurso.EQUIPO:
            raise ValueError("tipo_equipo solo aplica cuando tipo es 'equipo'")
        return v

    @field_validator('dias_disponibles')
    @classmethod
    def validar_dias(cls, v):
        """Valida que los días estén entre 1 y 7"""
        for dia in v:
            if dia < 1 or dia > 7:
                raise ValueError("Los días deben estar entre 1 (Lunes) y 7 (Domingo)")
        return v


class RecursoCreate(RecursoBase):
    """Schema para crear un recurso"""
    pass


class RecursoUpdate(BaseModel):
    """Schema para actualizar un recurso (campos opcionales)"""
    nombre: Optional[str] = Field(None, min_length=1, max_length=100)
    descripcion: Optional[str] = Field(None, max_length=500)
    tipo_equipo: Optional[TipoEquipo] = None
    ubicacion: Optional[str] = Field(None, max_length=200)
    capacidad: Optional[int] = Field(None, ge=1, le=500)
    equipamiento: Optional[List[str]] = None
    restricciones: Optional[str] = None
    estado: Optional[EstadoRecurso] = None
    imagen_url: Optional[str] = None
    horario_inicio: Optional[time] = None
    horario_fin: Optional[time] = None
    dias_disponibles: Optional[List[int]] = None
    requiere_aprobacion: Optional[bool] = None


class RecursoResponse(RecursoBase):
    """Schema de respuesta para un recurso"""
    id: str
    estado: EstadoRecurso
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True


class RecursoDisponibilidad(BaseModel):
    """Schema para mostrar disponibilidad de un recurso"""
    recurso: RecursoResponse
    horarios_disponibles: List[dict]  # [{inicio: "08:00", fin: "09:00"}, ...]
    horarios_ocupados: List[dict]


# ============================================
# SCHEMAS DE RESERVAS
# ============================================

class ReservaBase(BaseModel):
    """Schema base para reservas"""
    recurso_id: str = Field(..., description="ID del recurso a reservar")
    fecha: date = Field(..., description="Fecha de la reserva")
    hora_inicio: time = Field(..., description="Hora de inicio")
    hora_fin: time = Field(..., description="Hora de fin")
    motivo: Optional[str] = Field(None, max_length=300, description="Motivo de la reserva")
    notas: Optional[str] = Field(None, max_length=500, description="Notas adicionales")

    @field_validator('hora_fin')
    @classmethod
    def validar_hora_fin(cls, v, info):
        """Valida que hora_fin sea mayor que hora_inicio"""
        hora_inicio = info.data.get('hora_inicio')
        if hora_inicio and v <= hora_inicio:
            raise ValueError("La hora de fin debe ser posterior a la hora de inicio")
        return v


class ReservaCreate(ReservaBase):
    """Schema para crear una reserva"""
    pass


class ReservaUpdate(BaseModel):
    """Schema para actualizar una reserva"""
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None
    motivo: Optional[str] = Field(None, max_length=300)
    notas: Optional[str] = Field(None, max_length=500)


class ReservaCancelar(BaseModel):
    """Schema para cancelar una reserva"""
    motivo_cancelacion: Optional[str] = Field(None, max_length=300)


class ReservaResponse(BaseModel):
    """Schema de respuesta para una reserva"""
    id: str
    usuario_id: str
    recurso_id: str
    fecha: date
    hora_inicio: time
    hora_fin: time
    estado: EstadoReserva
    motivo: Optional[str]
    notas: Optional[str]
    created_at: datetime
    updated_at: datetime
    cancelado_at: Optional[datetime]
    cancelado_por: Optional[str]
    motivo_cancelacion: Optional[str]

    class Config:
        from_attributes = True


class ReservaDetalleResponse(ReservaResponse):
    """Schema de respuesta con detalles del recurso incluido"""
    recurso: Optional[RecursoResponse] = None
    usuario_nombre: Optional[str] = None


# ============================================
# SCHEMAS DE CHECK-IN
# ============================================

class CheckinCreate(BaseModel):
    """Schema para realizar check-in"""
    qr_token: str = Field(..., description="Token del código QR escaneado")
    reserva_id: Optional[str] = Field(None, description="ID de la reserva (opcional si se deduce del QR)")
    dispositivo_info: Optional[str] = None


class CheckinResponse(BaseModel):
    """Schema de respuesta para check-in"""
    id: str
    reserva_id: str
    usuario_id: str
    timestamp: datetime
    metodo: str
    es_valido: bool
    motivo_invalidez: Optional[str]
    mensaje: str

    class Config:
        from_attributes = True


class CheckinValidacion(BaseModel):
    """Schema para validar un check-in sin ejecutarlo"""
    puede_checkin: bool
    mensaje: str
    reserva: Optional[ReservaResponse] = None


# ============================================
# SCHEMAS DE FILTROS Y PAGINACIÓN
# ============================================

class FiltroRecursos(BaseModel):
    """Filtros para buscar recursos"""
    tipo: Optional[TipoRecurso] = None
    tipo_equipo: Optional[TipoEquipo] = None
    estado: Optional[EstadoRecurso] = None
    ubicacion: Optional[str] = None
    capacidad_minima: Optional[int] = None
    fecha: Optional[date] = None
    hora_inicio: Optional[time] = None
    hora_fin: Optional[time] = None


class FiltroReservas(BaseModel):
    """Filtros para buscar reservas"""
    estado: Optional[EstadoReserva] = None
    recurso_id: Optional[str] = None
    fecha_desde: Optional[date] = None
    fecha_hasta: Optional[date] = None
    tipo_recurso: Optional[TipoRecurso] = None


class PaginacionParams(BaseModel):
    """Parámetros de paginación"""
    page: int = Field(default=1, ge=1)
    page_size: int = Field(default=10, ge=1, le=100)


class PaginatedResponse(BaseModel):
    """Respuesta paginada genérica"""
    items: List
    total: int
    page: int
    page_size: int
    total_pages: int


# ============================================
# SCHEMAS DE RESPUESTAS GENERALES
# ============================================

class MensajeResponse(BaseModel):
    """Respuesta simple con mensaje"""
    message: str
    success: bool = True


class ErrorResponse(BaseModel):
    """Respuesta de error"""
    detail: str
    error_code: Optional[str] = None


# ============================================
# SCHEMAS PARA QR
# ============================================

class RecursoQRCreate(BaseModel):
    """Schema para crear un QR de recurso"""
    recurso_id: str
    duracion_horas: Optional[int] = Field(default=24, ge=1, le=8760)  # Máximo 1 año


class RecursoQRResponse(BaseModel):
    """Schema de respuesta para QR de recurso"""
    id: str
    recurso_id: str
    qr_code_base64: str  # Imagen QR en base64
    fecha_expiracion: Optional[datetime]
    activo: bool

    class Config:
        from_attributes = True
