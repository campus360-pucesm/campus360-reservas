from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import date
import math

from app.dependencies import get_supabase, get_current_user, require_admin
from app.services import ReservaService
from app.schemas import (
    ReservaCreate,
    ReservaCancelar,
    ReservaResponse,
    ReservaDetalleResponse,
    FiltroReservas,
    MensajeResponse
)
from app.models import EstadoReserva, TipoRecurso

router = APIRouter(
    prefix="/reservas",
    tags=["reservas"]
)


@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def crear_reserva(
    reserva: ReservaCreate,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Crea una nueva reserva.
    
    RF2.1 - Permite crear una reserva seleccionando un recurso y un horario disponible.
    RF2.2 - Valida que el recurso siga disponible al momento de confirmar.
    RF2.3 - Registra la reserva con toda su información.
    RF2.5 - Bloquea la creación de reservas en horarios ya tomados.
    """
    service = ReservaService(db)
    nueva_reserva, error = await service.crear_reserva(reserva, current_user["id"])
    
    if error:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=error
        )
    
    return {
        "message": "Reserva creada exitosamente",
        "reserva": nueva_reserva
    }


@router.get("/mis-reservas")
async def listar_mis_reservas(
    estado: Optional[EstadoReserva] = Query(None, description="Filtrar por estado"),
    recurso_id: Optional[str] = Query(None, description="Filtrar por recurso"),
    fecha_desde: Optional[date] = Query(None, description="Fecha desde"),
    fecha_hasta: Optional[date] = Query(None, description="Fecha hasta"),
    tipo_recurso: Optional[TipoRecurso] = Query(None, description="Tipo de recurso"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Elementos por página"),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista las reservas del usuario autenticado.
    
    RF4.1 - Permite visualizar todas las reservas activas.
    RF4.2 - Permite consultar historial de reservas pasadas.
    RF4.3 - Permite filtrar por estado (activas, canceladas, finalizadas).
    """
    filtros = FiltroReservas(
        estado=estado,
        recurso_id=recurso_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta,
        tipo_recurso=tipo_recurso
    )
    
    service = ReservaService(db)
    reservas, total = await service.listar_reservas_usuario(
        current_user["id"],
        filtros,
        page,
        page_size
    )
    
    return {
        "items": reservas,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0
    }


@router.get("/activas")
async def listar_reservas_activas(
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista solo las reservas activas del usuario (pendientes, confirmadas, en curso).
    
    RF4.1 - Visualizar reservas activas.
    """
    service = ReservaService(db)
    filtros = FiltroReservas()
    
    # Obtener reservas y filtrar por estados activos
    reservas, _ = await service.listar_reservas_usuario(
        current_user["id"],
        None,
        1,
        100
    )
    
    estados_activos = ["pendiente", "confirmada", "en_curso"]
    reservas_activas = [r for r in reservas if r["estado"] in estados_activos]
    
    return {
        "items": reservas_activas,
        "total": len(reservas_activas)
    }


@router.get("/historial")
async def listar_historial_reservas(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista el historial de reservas pasadas (completadas, canceladas, no_show).
    
    RF4.2 - Consultar historial de reservas pasadas.
    """
    service = ReservaService(db)
    
    reservas, total = await service.listar_reservas_usuario(
        current_user["id"],
        None,
        1,
        1000
    )
    
    estados_pasados = ["completada", "cancelada", "no_show"]
    historial = [r for r in reservas if r["estado"] in estados_pasados]
    
    # Paginación manual
    start = (page - 1) * page_size
    end = start + page_size
    paginated = historial[start:end]
    
    return {
        "items": paginated,
        "total": len(historial),
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(len(historial) / page_size) if historial else 0
    }


@router.get("/{reserva_id}")
async def obtener_reserva(
    reserva_id: str,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los detalles de una reserva específica.
    """
    service = ReservaService(db)
    reserva = await service.obtener_reserva_detalle(reserva_id)
    
    if not reserva:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Reserva no encontrada"
        )
    
    # Verificar permisos
    if reserva["usuario_id"] != current_user["id"] and current_user["role"] not in ["admin", "docente"]:
        raise HTTPException(
            status_code=status.HTTP_403_FORBIDDEN,
            detail="No tienes permiso para ver esta reserva"
        )
    
    return reserva


@router.delete("/{reserva_id}", response_model=MensajeResponse)
async def cancelar_reserva(
    reserva_id: str,
    datos: Optional[ReservaCancelar] = None,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Cancela una reserva existente.
    
    RF2.4 - Permite cancelar una reserva activa.
    RF2.6 - Actualiza el estado del recurso.
    RF2.7 - Genera confirmación de cancelación.
    """
    service = ReservaService(db)
    
    motivo = datos.motivo_cancelacion if datos else None
    es_admin = current_user["role"] == "admin"
    
    success, message = await service.cancelar_reserva(
        reserva_id,
        current_user["id"],
        motivo,
        es_admin
    )
    
    if not success:
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail=message
        )
    
    return MensajeResponse(message=message, success=True)


# ============================================
# ENDPOINTS ADMINISTRATIVOS
# ============================================

@router.get("/admin/todas", dependencies=[Depends(require_admin)])
async def listar_todas_reservas(
    estado: Optional[EstadoReserva] = Query(None),
    recurso_id: Optional[str] = Query(None),
    fecha_desde: Optional[date] = Query(None),
    fecha_hasta: Optional[date] = Query(None),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=100),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Lista todas las reservas del sistema (solo admin).
    """
    filtros = FiltroReservas(
        estado=estado,
        recurso_id=recurso_id,
        fecha_desde=fecha_desde,
        fecha_hasta=fecha_hasta
    )
    
    service = ReservaService(db)
    reservas, total = await service.listar_todas_reservas(filtros, page, page_size)
    
    return {
        "items": reservas,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0
    }


@router.patch("/admin/{reserva_id}/estado", dependencies=[Depends(require_admin)])
async def cambiar_estado_reserva(
    reserva_id: str,
    nuevo_estado: EstadoReserva,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Cambia el estado de una reserva (solo admin).
    """
    try:
        response = db.table("reservas").update({
            "estado": nuevo_estado.value
        }).eq("id", reserva_id).execute()
        
        if not response.data:
            raise HTTPException(
                status_code=status.HTTP_404_NOT_FOUND,
                detail="Reserva no encontrada"
            )
        
        return {
            "message": f"Estado actualizado a {nuevo_estado.value}",
            "reserva": response.data[0]
        }
    except Exception as e:
        raise HTTPException(
            status_code=status.HTTP_500_INTERNAL_SERVER_ERROR,
            detail=str(e)
        )
