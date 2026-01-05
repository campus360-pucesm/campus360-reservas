"""
Router de Check-in
Endpoints para realizar check-in mediante QR con control de capacidad
"""
from fastapi import APIRouter, Depends, HTTPException, Query
from supabase import Client
from typing import Optional
from pydantic import BaseModel, Field

from app.dependencies import get_supabase
from app.services.services import CheckinService, QRService

router = APIRouter(
    prefix="/checkin",
    tags=["Check-in"]
)


# ==================== SCHEMAS ====================

class CheckinRequest(BaseModel):
    """Datos para realizar check-in"""
    codigo_qr: str = Field(..., description="Codigo QR escaneado (ej: QR-LAB-001)")
    usuario_id: str = Field(..., description="ID del usuario")
    usuario_nombre: str = Field(..., description="Nombre del usuario")
    usuario_email: str = Field(..., description="Email del usuario")
    dispositivo_info: Optional[str] = Field(None, description="Info del dispositivo")
    
    class Config:
        json_schema_extra = {
            "example": {
                "codigo_qr": "QR-LAB-001",
                "usuario_id": "user-123",
                "usuario_nombre": "Maria Garcia",
                "usuario_email": "maria@universidad.edu",
                "dispositivo_info": "iPhone 15 - Safari"
            }
        }


# ==================== ENDPOINTS ====================

@router.post("/")
async def realizar_checkin(
    datos: CheckinRequest,
    db: Client = Depends(get_supabase)
):
    """
    Realiza check-in escaneando el codigo QR de un recurso.
    
    El sistema:
    1. Valida que el codigo QR sea correcto
    2. Busca una reserva activa en este momento para ese recurso
    3. Verifica que el usuario no haya hecho check-in ya
    4. Verifica que no se haya alcanzado la capacidad maxima
    5. Registra el check-in
    
    Mensajes posibles:
    - Exito: "Bienvenido/a! Check-in #5 de 20 registrado"
    - Capacidad llena: "Lo sentimos! La capacidad esta completa (20/20)"
    - Sin reserva: "No hay ninguna reserva activa en este momento"
    - Duplicado: "Ya realizaste check-in para esta reserva"
    """
    service = CheckinService(db)
    
    resultado, error = await service.realizar_checkin(
        codigo_qr=datos.codigo_qr,
        usuario_id=datos.usuario_id,
        usuario_nombre=datos.usuario_nombre,
        usuario_email=datos.usuario_email,
        dispositivo_info=datos.dispositivo_info
    )
    
    if error:
        raise HTTPException(status_code=400, detail=error)
    
    return {
        "success": True,
        "message": resultado["mensaje"],
        "data": {
            "numero_checkin": resultado["numero_checkin"],
            "capacidad_total": resultado["capacidad_total"],
            "lugares_restantes": resultado["lugares_restantes"],
            "porcentaje_ocupacion": resultado["porcentaje_ocupacion"],
            "recurso": resultado["recurso"],
            "checkin": resultado["checkin"]
        }
    }


@router.get("/estado/{reserva_id}")
async def obtener_estado_checkins(
    reserva_id: str,
    db: Client = Depends(get_supabase)
):
    """
    Obtiene el estado actual de check-ins de una reserva.
    
    Muestra:
    - Capacidad total vs ocupada
    - Lista de personas que han hecho check-in
    - Si esta lleno o hay lugares disponibles
    """
    service = CheckinService(db)
    estado = await service.obtener_estado_checkins(reserva_id)
    
    if not estado:
        raise HTTPException(status_code=404, detail="Reserva no encontrada")
    
    return {
        "success": True,
        "data": estado
    }


@router.get("/usuario/{usuario_id}")
async def listar_checkins_usuario(
    usuario_id: str,
    page: int = Query(1, ge=1),
    page_size: int = Query(20, ge=1, le=100),
    db: Client = Depends(get_supabase)
):
    """
    Lista el historial de check-ins de un usuario.
    """
    service = CheckinService(db)
    checkins, total = await service.listar_checkins_usuario(usuario_id, page, page_size)
    
    return {
        "success": True,
        "data": checkins,
        "total": total,
        "page": page,
        "page_size": page_size
    }


@router.get("/qr/todos")
async def listar_codigos_qr(db: Client = Depends(get_supabase)):
    """
    Lista todos los codigos QR disponibles.
    Util para ver que codigo corresponde a cada recurso.
    """
    service = QRService(db)
    qrs = await service.listar_todos_qr()
    
    # Organizar por tipo de recurso
    por_tipo = {}
    for qr in qrs:
        recurso = qr.get("recursos", {})
        tipo = recurso.get("tipo", "otro")
        if tipo not in por_tipo:
            por_tipo[tipo] = []
        por_tipo[tipo].append({
            "codigo_qr": qr["codigo_qr"],
            "recurso_codigo": recurso.get("codigo"),
            "recurso_nombre": recurso.get("nombre"),
            "capacidad": recurso.get("capacidad"),
            "ubicacion": recurso.get("ubicacion")
        })
    
    return {
        "success": True,
        "data": por_tipo,
        "total": len(qrs)
    }


@router.get("/qr/{recurso_id}")
async def obtener_qr_recurso(
    recurso_id: str,
    db: Client = Depends(get_supabase)
):
    """
    Obtiene el codigo QR de un recurso especifico.
    """
    service = QRService(db)
    qr = await service.obtener_qr_recurso(recurso_id)
    
    if not qr:
        raise HTTPException(status_code=404, detail="QR no encontrado para este recurso")
    
    return {
        "success": True,
        "data": qr
    }


@router.get("/simular/{codigo_qr}")
async def simular_checkin(
    codigo_qr: str,
    db: Client = Depends(get_supabase)
):
    """
    Endpoint de prueba para simular un escaneo de QR.
    Muestra que recurso corresponde y si hay reserva activa.
    """
    # Buscar el QR
    qr_info = db.table("recursos_qr").select("*, recursos(*)")\
        .eq("codigo_qr", codigo_qr)\
        .eq("activo", True)\
        .execute()
    
    if not qr_info.data:
        return {
            "success": False,
            "message": "Codigo QR no encontrado o inactivo",
            "codigo_escaneado": codigo_qr
        }
    
    recurso = qr_info.data[0].get("recursos", {})
    
    # Buscar reserva activa
    from datetime import date, datetime
    hoy = date.today()
    ahora = datetime.now().strftime("%H:%M:%S")
    
    reservas = db.table("reservas").select("*")\
        .eq("recurso_id", recurso["id"])\
        .eq("fecha", hoy.isoformat())\
        .execute()
    
    reserva_activa = None
    for r in reservas.data:
        if r["hora_inicio"] <= ahora <= r["hora_fin"] and r["estado"] not in ["cancelada", "completada"]:
            reserva_activa = r
            break
    
    return {
        "success": True,
        "codigo_escaneado": codigo_qr,
        "recurso": {
            "codigo": recurso.get("codigo"),
            "nombre": recurso.get("nombre"),
            "tipo": recurso.get("tipo"),
            "capacidad": recurso.get("capacidad"),
            "ubicacion": recurso.get("ubicacion")
        },
        "hay_reserva_activa": reserva_activa is not None,
        "reserva_activa": reserva_activa,
        "mensaje": f"QR valido para {recurso.get('nombre')}" + (
            f". Reserva activa encontrada ({reserva_activa['hora_inicio']} - {reserva_activa['hora_fin']})" 
            if reserva_activa else ". No hay reserva activa en este momento."
        )
    }