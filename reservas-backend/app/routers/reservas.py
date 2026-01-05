"""
Router de Reservas
Endpoints para crear y gestionar reservas
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
from datetime import date, time
from pydantic import BaseModel, Field

from app.dependencies import get_supabase
from app.services.services import ReservaService

router = APIRouter(
    prefix="/reservas",
    tags=["Reservas"]
)


# ==================== SCHEMAS ====================

class CrearReservaRequest(BaseModel):
    """Datos para crear una nueva reserva"""
    recurso_id: str = Field(..., description="ID del recurso a reservar")
    fecha: date = Field(..., description="Fecha de la reserva (YYYY-MM-DD)")
    hora_inicio: str = Field(..., description="Hora de inicio (HH:MM)")
    hora_fin: str = Field(..., description="Hora de fin (HH:MM)")
    usuario_id: str = Field(..., description="ID del usuario")
    usuario_nombre: str = Field(..., description="Nombre del usuario")
    usuario_email: str = Field(..., description="Email del usuario")
    motivo: Optional[str] = Field(None, description="Motivo de la reserva")
    num_asistentes: int = Field(1, ge=1, description="Numero de asistentes esperados")
    
    class Config:
        json_schema_extra = {
            "example": {
                "recurso_id": "uuid-del-recurso",
                "fecha": "2025-01-20",
                "hora_inicio": "10:00",
                "hora_fin": "12:00",
                "usuario_id": "user-123",
                "usuario_nombre": "Juan Perez",
                "usuario_email": "juan@universidad.edu",
                "motivo": "Clase de programacion",
                "num_asistentes": 20
            }
        }


class CancelarReservaRequest(BaseModel):
    """Datos para cancelar una reserva"""
    motivo: Optional[str] = Field(None, description="Motivo de la cancelacion")


# ==================== ENDPOINTS ====================

@router.post("/")
async def crear_reserva(
    datos: CrearReservaRequest,
    db: Client = Depends(get_supabase)
):
    """
    Crea una nueva reserva de un recurso.
    
    El sistema validara:
    - Que el recurso exista y este disponible
    - Que no haya conflictos de horario
    - Que el numero de asistentes no exceda la capacidad
    """
    service = ReservaService(db)
    
    # Parsear horas
    try:
        hora_inicio = time.fromisoformat(datos.hora_inicio)
        hora_fin = time.fromisoformat(datos.hora_fin)
    except ValueError:
        raise HTTPException(status_code=400, detail="Formato de hora invalido. Use HH:MM")
    
    reserva, error = await service.crear_reserva(
        recurso_id=datos.recurso_id,
        usuario_id=datos.usuario_id,
        usuario_nombre=datos.usuario_nombre,
        usuario_email=datos.usuario_email,
        fecha=datos.fecha,
        hora_inicio=hora_inicio,
        hora_fin=hora_fin,
        motivo=datos.motivo,
        num_asistentes=datos.num_asistentes
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "success": True,
        "message": "Reserva creada exitosamente",
        "data": reserva
    }


@router.get("/")
async def listar_reservas(
    usuario_id: Optional[str] = Query(None, description="Filtrar por usuario"),
    fecha: Optional[date] = Query(None, description="Filtrar por fecha"),
    tipo_recurso: Optional[str] = Query(None, description="Filtrar por tipo de recurso"),
    estado: Optional[str] = Query(None, description="Filtrar por estado"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_supabase)
):
    """
    Lista reservas con filtros opcionales.
    """
    service = ReservaService(db)
    
    if fecha:
        reservas = await service.listar_reservas_por_fecha(fecha, tipo_recurso)
        return {
            "success": True,
            "data": reservas,
            "total": len(reservas)
        }
    
    if usuario_id:
        reservas, total = await service.listar_reservas_usuario(usuario_id, estado, page, page_size)
        return {
            "success": True,
            "data": reservas,
            "total": total,
            "page": page,
            "page_size": page_size
        }
    
    # Si no hay filtros, retornar mensaje
    return {
        "success": True,
        "message": "Proporcione usuario_id o fecha para filtrar reservas",
        "data": []
    }


@router.get("/usuario/{usuario_id}")
async def listar_reservas_usuario(
    usuario_id: str,
    estado: Optional[str] = Query(None, description="Filtrar por estado: confirmada, en_curso, completada, cancelada"),
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_supabase)
):
    """
    Lista todas las reservas de un usuario especifico.
    """
    service = ReservaService(db)
    reservas, total = await service.listar_reservas_usuario(usuario_id, estado, page, page_size)
    
    return {
        "success": True,
        "data": reservas,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/fecha/{fecha}")
async def listar_reservas_fecha(
    fecha: date,
    tipo_recurso: Optional[str] = Query(None, description="Filtrar por tipo de recurso"),
    db: Client = Depends(get_supabase)
):
    """
    Lista todas las reservas de una fecha especifica.
    Util para ver la ocupacion del dia.
    """
    service = ReservaService(db)
    reservas = await service.listar_reservas_por_fecha(fecha, tipo_recurso)
    
    return {
        "success": True,
        "fecha": fecha.isoformat(),
        "data": reservas,
        "total": len(reservas)
    }


@router.get("/{reserva_id}")
async def obtener_reserva(
    reserva_id: str,
    db: Client = Depends(get_supabase)
):
    """
    Obtiene los detalles de una reserva especifica.
    Incluye informacion del recurso y estado de check-ins.
    """
    service = ReservaService(db)
    reserva = await service.obtener_reserva(reserva_id)
    
    if not reserva:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    return {"success": True, "data": reserva}


@router.delete("/{reserva_id}")
async def cancelar_reserva(
    reserva_id: str,
    usuario_id: str = Query(..., description="ID del usuario que cancela"),
    motivo: Optional[str] = Query(None, description="Motivo de cancelacion"),
    db: Client = Depends(get_supabase)
):
    """
    Cancela una reserva existente.
    Solo el usuario que creo la reserva puede cancelarla.
    """
    service = ReservaService(db)
    success, mensaje = await service.cancelar_reserva(reserva_id, usuario_id, motivo)
    
    if not success:
        raise HTTPException(status_code=400, detail=mensaje)
    
    return {
        "success": True,
        "message": mensaje
    }