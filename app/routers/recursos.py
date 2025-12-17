from fastapi import APIRouter, Depends, HTTPException, status, Query
from supabase import Client
from typing import Optional
from datetime import date
import math

from app.dependencies import get_supabase, get_current_user, require_admin
from app.services import RecursoService
from app.schemas import (
    RecursoCreate,
    RecursoUpdate,
    RecursoResponse,
    FiltroRecursos,
    MensajeResponse
)
from app.models import TipoRecurso, TipoEquipo, EstadoRecurso

router = APIRouter(
    prefix="/recursos",
    tags=["recursos"]
)


@router.get("/")
async def listar_recursos(
    tipo: Optional[TipoRecurso] = Query(None, description="Tipo de recurso"),
    tipo_equipo: Optional[TipoEquipo] = Query(None, description="Tipo de equipo (solo para tipo=equipo)"),
    estado: Optional[EstadoRecurso] = Query(None, description="Estado del recurso"),
    ubicacion: Optional[str] = Query(None, description="Filtrar por ubicación"),
    capacidad_minima: Optional[int] = Query(None, ge=1, description="Capacidad mínima"),
    page: int = Query(1, ge=1, description="Número de página"),
    page_size: int = Query(10, ge=1, le=50, description="Elementos por página"),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Lista todos los recursos disponibles con filtros opcionales.
    
    RF1.1 - Visualizar disponibilidad de todos los recursos.
    RF1.2 - Filtrar por tipo de recurso.
    """
    filtros = FiltroRecursos(
        tipo=tipo,
        tipo_equipo=tipo_equipo,
        estado=estado,
        ubicacion=ubicacion,
        capacidad_minima=capacidad_minima
    )
    
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(filtros, page, page_size)
    
    return {
        "items": recursos,
        "total": total,
        "page": page,
        "page_size": page_size,
        "total_pages": math.ceil(total / page_size) if total > 0 else 0
    }


@router.get("/tipos")
async def listar_tipos_recursos(
    current_user: dict = Depends(get_current_user)
):
    """
    Lista los tipos de recursos disponibles.
    """
    return {
        "tipos_recurso": [
            {"value": t.value, "label": t.value.replace("_", " ").title()}
            for t in TipoRecurso
        ],
        "tipos_equipo": [
            {"value": t.value, "label": t.value.title()}
            for t in TipoEquipo
        ],
        "estados_recurso": [
            {"value": e.value, "label": e.value.replace("_", " ").title()}
            for e in EstadoRecurso
        ]
    }


@router.get("/salas")
async def listar_salas_estudio(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Lista todas las salas de estudio disponibles."""
    filtros = FiltroRecursos(tipo=TipoRecurso.SALA_ESTUDIO, estado=EstadoRecurso.DISPONIBLE)
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(filtros, page, page_size)
    
    return {"items": recursos, "total": total}


@router.get("/laboratorios")
async def listar_laboratorios(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Lista todos los laboratorios disponibles."""
    filtros = FiltroRecursos(tipo=TipoRecurso.LABORATORIO, estado=EstadoRecurso.DISPONIBLE)
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(filtros, page, page_size)
    
    return {"items": recursos, "total": total}


@router.get("/equipos")
async def listar_equipos(
    tipo_equipo: Optional[TipoEquipo] = Query(None, description="Tipo específico de equipo"),
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Lista todos los equipos disponibles (proyectores, laptops, cámaras)."""
    filtros = FiltroRecursos(
        tipo=TipoRecurso.EQUIPO, 
        tipo_equipo=tipo_equipo,
        estado=EstadoRecurso.DISPONIBLE
    )
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(filtros, page, page_size)
    
    return {"items": recursos, "total": total}


@router.get("/parqueaderos")
async def listar_parqueaderos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Lista todas las estaciones de parqueadero disponibles."""
    filtros = FiltroRecursos(tipo=TipoRecurso.PARQUEADERO, estado=EstadoRecurso.DISPONIBLE)
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(filtros, page, page_size)
    
    return {"items": recursos, "total": total}


@router.get("/cubiculos")
async def listar_cubiculos(
    page: int = Query(1, ge=1),
    page_size: int = Query(10, ge=1, le=50),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """Lista todos los cubículos de biblioteca disponibles."""
    filtros = FiltroRecursos(tipo=TipoRecurso.CUBICULO, estado=EstadoRecurso.DISPONIBLE)
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(filtros, page, page_size)
    
    return {"items": recursos, "total": total}


@router.get("/{recurso_id}")
async def obtener_recurso(
    recurso_id: str,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene los detalles de un recurso específico.
    
    RF1.4 - Consultar detalles del recurso (capacidad, ubicación, equipamiento, restricciones).
    """
    service = RecursoService(db)
    recurso = await service.obtener_recurso(recurso_id)
    
    if not recurso:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    return recurso


@router.get("/{recurso_id}/disponibilidad")
async def obtener_disponibilidad(
    recurso_id: str,
    fecha: date = Query(..., description="Fecha para consultar disponibilidad"),
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(get_current_user)
):
    """
    Obtiene la disponibilidad de un recurso para una fecha específica.
    
    RF1.1 - Visualizar disponibilidad.
    RF1.3 - Mostrar calendario/grilla de horarios disponibles y ocupados.
    """
    service = RecursoService(db)
    disponibilidad = await service.obtener_disponibilidad(recurso_id, fecha)
    
    if not disponibilidad:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    return disponibilidad


# ============================================
# ENDPOINTS ADMINISTRATIVOS
# ============================================

@router.post("/", response_model=dict, status_code=status.HTTP_201_CREATED)
async def crear_recurso(
    recurso: RecursoCreate,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Crea un nuevo recurso (solo admin).
    """
    service = RecursoService(db)
    nuevo_recurso = await service.crear_recurso(recurso)
    
    return {
        "message": "Recurso creado exitosamente",
        "recurso": nuevo_recurso
    }


@router.put("/{recurso_id}")
async def actualizar_recurso(
    recurso_id: str,
    recurso: RecursoUpdate,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Actualiza un recurso existente (solo admin).
    """
    service = RecursoService(db)
    
    # Verificar que existe
    existente = await service.obtener_recurso(recurso_id)
    if not existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    actualizado = await service.actualizar_recurso(recurso_id, recurso)
    
    return {
        "message": "Recurso actualizado exitosamente",
        "recurso": actualizado
    }


@router.delete("/{recurso_id}", response_model=MensajeResponse)
async def eliminar_recurso(
    recurso_id: str,
    db: Client = Depends(get_supabase),
    current_user: dict = Depends(require_admin)
):
    """
    Elimina (desactiva) un recurso (solo admin).
    """
    service = RecursoService(db)
    
    existente = await service.obtener_recurso(recurso_id)
    if not existente:
        raise HTTPException(
            status_code=status.HTTP_404_NOT_FOUND,
            detail="Recurso no encontrado"
        )
    
    await service.eliminar_recurso(recurso_id)
    
    return MensajeResponse(
        message="Recurso eliminado exitosamente",
        success=True
    )
