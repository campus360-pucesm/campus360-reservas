"""
Router de Recursos
Endpoints para consultar recursos del campus
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
from datetime import date

from app.dependencies import get_supabase
from app.services.services import RecursoService

router = APIRouter(
    prefix="/recursos",
    tags=["Recursos"]
)


@router.get("/")
async def listar_recursos(
    tipo: Optional[str] = Query(None, description="Filtrar por tipo: sala_estudio, laboratorio, modulo_biblioteca, parqueadero, equipo"),
    estado: Optional[str] = Query("disponible", description="Estado del recurso"),
    page: int = Query(1, ge=1),
    page_size: int = Query(50, ge=1, le=100),
    db: Client = Depends(get_supabase)
):
    """
    Lista todos los recursos disponibles del campus.
    
    Tipos disponibles:
    - sala_estudio: Salas de estudio (5 disponibles, capacidad 10)
    - laboratorio: Laboratorios de computacion (5 disponibles, capacidad 20)
    - modulo_biblioteca: Modulos de biblioteca (5 disponibles, capacidad 4)
    - parqueadero: Estacionamientos (20 disponibles, capacidad 1)
    - equipo: Equipos prestables (5 disponibles, capacidad 1)
    """
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(tipo, estado, page, page_size)
    
    return {
        "success": True,
        "data": recursos,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/tipos")
async def obtener_tipos_recursos(db: Client = Depends(get_supabase)):
    """
    Obtiene un resumen de los tipos de recursos disponibles.
    """
    service = RecursoService(db)
    
    tipos = {}
    for tipo in ["sala_estudio", "laboratorio", "modulo_biblioteca", "parqueadero", "equipo"]:
        recursos, total = await service.listar_recursos(tipo=tipo)
        if total > 0:
            tipos[tipo] = {
                "cantidad": total,
                "capacidad_tipica": recursos[0]["capacidad"] if recursos else 0,
                "recursos": [{"codigo": r["codigo"], "nombre": r["nombre"]} for r in recursos]
            }
    
    return {
        "success": True,
        "tipos_disponibles": tipos
    }


@router.get("/salas")
async def listar_salas_estudio(db: Client = Depends(get_supabase)):
    """Lista las 5 salas de estudio disponibles (capacidad: 10 personas)"""
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(tipo="sala_estudio")
    return {"success": True, "data": recursos, "total": total}


@router.get("/laboratorios")
async def listar_laboratorios(db: Client = Depends(get_supabase)):
    """Lista los 5 laboratorios de computacion disponibles (capacidad: 20 personas)"""
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(tipo="laboratorio")
    return {"success": True, "data": recursos, "total": total}


@router.get("/biblioteca")
async def listar_modulos_biblioteca(db: Client = Depends(get_supabase)):
    """Lista los 5 modulos de biblioteca disponibles (capacidad: 4 personas)"""
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(tipo="modulo_biblioteca")
    return {"success": True, "data": recursos, "total": total}


@router.get("/parqueaderos")
async def listar_parqueaderos(db: Client = Depends(get_supabase)):
    """Lista los 20 parqueaderos disponibles (capacidad: 1 vehiculo)"""
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(tipo="parqueadero")
    return {"success": True, "data": recursos, "total": total}


@router.get("/equipos")
async def listar_equipos(db: Client = Depends(get_supabase)):
    """Lista los equipos disponibles para prestamo"""
    service = RecursoService(db)
    recursos, total = await service.listar_recursos(tipo="equipo")
    return {"success": True, "data": recursos, "total": total}


@router.get("/{recurso_id}")
async def obtener_recurso(
    recurso_id: str,
    db: Client = Depends(get_supabase)
):
    """Obtiene los detalles de un recurso especifico"""
    service = RecursoService(db)
    recurso = await service.obtener_recurso(recurso_id)
    
    if not recurso:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    
    return {"success": True, "data": recurso}


@router.get("/{recurso_id}/disponibilidad")
async def obtener_disponibilidad(
    recurso_id: str,
    fecha: date = Query(..., description="Fecha para consultar disponibilidad (YYYY-MM-DD)"),
    db: Client = Depends(get_supabase)
):
    """
    Consulta la disponibilidad de un recurso para una fecha especifica.
    
    Retorna los horarios disponibles y ocupados.
    """
    service = RecursoService(db)
    disponibilidad = await service.obtener_disponibilidad(recurso_id, fecha)
    
    if not disponibilidad:
        raise HTTPException(status_code=404, detail="Recurso no encontrado")
    
    return {"success": True, "data": disponibilidad}