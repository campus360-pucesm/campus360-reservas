from datetime import date, time, datetime, timedelta
from typing import Optional, List, Tuple
from supabase import Client
import hashlib
import secrets
import qrcode
import io
import base64

from app.config import get_settings
from app.models import TipoRecurso, EstadoRecurso, EstadoReserva
from app.schemas import (
    RecursoCreate, RecursoUpdate, RecursoResponse,
    ReservaCreate, ReservaResponse, ReservaDetalleResponse,
    FiltroRecursos, FiltroReservas,
    CheckinResponse
)

settings = get_settings()


class RecursoService:
    """Servicio para gestión de recursos"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def listar_recursos(
        self,
        filtros: Optional[FiltroRecursos] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Lista recursos con filtros opcionales"""
        query = self.db.table("recursos").select("*", count="exact")
        
        if filtros:
            if filtros.tipo:
                query = query.eq("tipo", filtros.tipo.value)
            if filtros.tipo_equipo:
                query = query.eq("tipo_equipo", filtros.tipo_equipo.value)
            if filtros.estado:
                query = query.eq("estado", filtros.estado.value)
            if filtros.ubicacion:
                query = query.ilike("ubicacion", f"%{filtros.ubicacion}%")
            if filtros.capacidad_minima:
                query = query.gte("capacidad", filtros.capacidad_minima)
        
        # Paginación
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("nombre")
        
        response = query.execute()
        return response.data, response.count or 0
    
    async def obtener_recurso(self, recurso_id: str) -> Optional[dict]:
        """Obtiene un recurso por ID"""
        response = self.db.table("recursos").select("*").eq("id", recurso_id).single().execute()
        return response.data
    
    async def crear_recurso(self, recurso: RecursoCreate) -> dict:
        """Crea un nuevo recurso"""
        data = recurso.model_dump()
        
        # Convertir time a string para Supabase
        data["horario_inicio"] = data["horario_inicio"].isoformat()
        data["horario_fin"] = data["horario_fin"].isoformat()
        data["estado"] = EstadoRecurso.DISPONIBLE.value
        
        response = self.db.table("recursos").insert(data).execute()
        return response.data[0]
    
    async def actualizar_recurso(self, recurso_id: str, recurso: RecursoUpdate) -> dict:
        """Actualiza un recurso existente"""
        data = recurso.model_dump(exclude_unset=True)
        
        # Convertir time a string si existe
        if "horario_inicio" in data and data["horario_inicio"]:
            data["horario_inicio"] = data["horario_inicio"].isoformat()
        if "horario_fin" in data and data["horario_fin"]:
            data["horario_fin"] = data["horario_fin"].isoformat()
        if "estado" in data and data["estado"]:
            data["estado"] = data["estado"].value
        
        response = self.db.table("recursos").update(data).eq("id", recurso_id).execute()
        return response.data[0]
    
    async def eliminar_recurso(self, recurso_id: str) -> bool:
        """Elimina un recurso (soft delete poniendo fuera_servicio)"""
        self.db.table("recursos").update({
            "estado": EstadoRecurso.FUERA_SERVICIO.value
        }).eq("id", recurso_id).execute()
        return True
    
    async def obtener_disponibilidad(
        self,
        recurso_id: str,
        fecha: date
    ) -> dict:
        """Obtiene la disponibilidad de un recurso para una fecha"""
        # Obtener recurso
        recurso = await self.obtener_recurso(recurso_id)
        if not recurso:
            return None
        
        # Verificar si el día está disponible
        dia_semana = fecha.isoweekday()  # 1=Lunes, 7=Domingo
        if dia_semana not in recurso.get("dias_disponibles", [1, 2, 3, 4, 5]):
            return {
                "recurso": recurso,
                "disponible": False,
                "mensaje": "El recurso no está disponible este día de la semana",
                "horarios_disponibles": [],
                "horarios_ocupados": []
            }
        
        # Obtener reservas del día
        reservas = self.db.table("reservas").select("hora_inicio, hora_fin, estado")\
            .eq("recurso_id", recurso_id)\
            .eq("fecha", fecha.isoformat())\
            .not_.in_("estado", ["cancelada", "no_show"])\
            .execute()
        
        # Calcular slots disponibles
        horario_inicio = datetime.strptime(recurso["horario_inicio"], "%H:%M:%S").time()
        horario_fin = datetime.strptime(recurso["horario_fin"], "%H:%M:%S").time()
        
        horarios_ocupados = []
        for r in reservas.data:
            horarios_ocupados.append({
                "inicio": r["hora_inicio"],
                "fin": r["hora_fin"]
            })
        
        # Generar slots disponibles (cada 30 minutos)
        horarios_disponibles = self._calcular_slots_disponibles(
            horario_inicio, horario_fin, horarios_ocupados
        )
        
        return {
            "recurso": recurso,
            "fecha": fecha.isoformat(),
            "disponible": len(horarios_disponibles) > 0,
            "horarios_disponibles": horarios_disponibles,
            "horarios_ocupados": horarios_ocupados
        }
    
    def _calcular_slots_disponibles(
        self,
        horario_inicio: time,
        horario_fin: time,
        ocupados: List[dict]
    ) -> List[dict]:
        """Calcula los slots de tiempo disponibles"""
        slots = []
        slot_duracion = timedelta(minutes=30)
        
        current = datetime.combine(date.today(), horario_inicio)
        end = datetime.combine(date.today(), horario_fin)
        
        while current + slot_duracion <= end:
            slot_inicio = current.time()
            slot_fin = (current + slot_duracion).time()
            
            # Verificar si el slot está ocupado
            ocupado = False
            for o in ocupados:
                o_inicio = datetime.strptime(o["inicio"], "%H:%M:%S").time()
                o_fin = datetime.strptime(o["fin"], "%H:%M:%S").time()
                
                # El slot está ocupado si hay solapamiento
                if not (slot_fin <= o_inicio or slot_inicio >= o_fin):
                    ocupado = True
                    break
            
            if not ocupado:
                slots.append({
                    "inicio": slot_inicio.strftime("%H:%M"),
                    "fin": slot_fin.strftime("%H:%M")
                })
            
            current += slot_duracion
        
        return slots


class ReservaService:
    """Servicio para gestión de reservas"""
    
    def __init__(self, db: Client):
        self.db = db
        self.recurso_service = RecursoService(db)
    
    async def crear_reserva(
        self,
        reserva: ReservaCreate,
        usuario_id: str
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Crea una nueva reserva.
        Retorna (reserva, None) si tiene éxito, o (None, mensaje_error) si falla.
        """
        # 1. Verificar que el recurso existe y está disponible
        recurso = await self.recurso_service.obtener_recurso(reserva.recurso_id)
        if not recurso:
            return None, "El recurso no existe"
        
        if recurso["estado"] not in [EstadoRecurso.DISPONIBLE.value, "disponible"]:
            return None, f"El recurso no está disponible (estado: {recurso['estado']})"
        
        # 2. Verificar que la fecha no sea pasada
        hoy = date.today()
        if reserva.fecha < hoy:
            return None, "No se pueden hacer reservas en fechas pasadas"
        
        # 3. Verificar anticipación mínima
        if reserva.fecha == hoy:
            ahora = datetime.now().time()
            min_hora = (datetime.combine(hoy, ahora) + timedelta(minutes=settings.ANTICIPACION_MINIMA_MINUTOS)).time()
            if reserva.hora_inicio < min_hora:
                return None, f"Debe reservar con al menos {settings.ANTICIPACION_MINIMA_MINUTOS} minutos de anticipación"
        
        # 4. Verificar anticipación máxima
        max_fecha = hoy + timedelta(days=settings.ANTICIPACION_MAXIMA_DIAS)
        if reserva.fecha > max_fecha:
            return None, f"Solo puede reservar con máximo {settings.ANTICIPACION_MAXIMA_DIAS} días de anticipación"
        
        # 5. Verificar que el día de la semana esté habilitado
        dia_semana = reserva.fecha.isoweekday()
        if dia_semana not in recurso.get("dias_disponibles", [1, 2, 3, 4, 5]):
            return None, "El recurso no está disponible este día de la semana"
        
        # 6. Verificar que esté dentro del horario del recurso
        horario_inicio = datetime.strptime(recurso["horario_inicio"], "%H:%M:%S").time()
        horario_fin = datetime.strptime(recurso["horario_fin"], "%H:%M:%S").time()
        
        if reserva.hora_inicio < horario_inicio or reserva.hora_fin > horario_fin:
            return None, f"La reserva debe estar entre {horario_inicio} y {horario_fin}"
        
        # 7. Verificar duración mínima y máxima
        duracion = datetime.combine(hoy, reserva.hora_fin) - datetime.combine(hoy, reserva.hora_inicio)
        if duracion < timedelta(minutes=settings.TIEMPO_MINIMO_RESERVA_MINUTOS):
            return None, f"La reserva mínima es de {settings.TIEMPO_MINIMO_RESERVA_MINUTOS} minutos"
        if duracion > timedelta(hours=settings.TIEMPO_MAXIMO_RESERVA_HORAS):
            return None, f"La reserva máxima es de {settings.TIEMPO_MAXIMO_RESERVA_HORAS} horas"
        
        # 8. Verificar conflictos con otras reservas
        conflictos = self.db.table("reservas").select("id")\
            .eq("recurso_id", reserva.recurso_id)\
            .eq("fecha", reserva.fecha.isoformat())\
            .not_.in_("estado", ["cancelada", "no_show"])\
            .execute()
        
        for r in conflictos.data:
            # Obtener detalles de la reserva existente
            existente = self.db.table("reservas").select("hora_inicio, hora_fin")\
                .eq("id", r["id"]).single().execute()
            
            if existente.data:
                e_inicio = datetime.strptime(existente.data["hora_inicio"], "%H:%M:%S").time()
                e_fin = datetime.strptime(existente.data["hora_fin"], "%H:%M:%S").time()
                
                # Verificar solapamiento
                if not (reserva.hora_fin <= e_inicio or reserva.hora_inicio >= e_fin):
                    return None, "Ya existe una reserva en ese horario"
        
        # 9. Verificar límite de reservas por día del usuario
        reservas_usuario_hoy = self.db.table("reservas").select("id", count="exact")\
            .eq("usuario_id", usuario_id)\
            .eq("fecha", reserva.fecha.isoformat())\
            .not_.in_("estado", ["cancelada", "no_show"])\
            .execute()
        
        if reservas_usuario_hoy.count >= settings.MAX_RESERVAS_POR_DIA:
            return None, f"Has alcanzado el límite de {settings.MAX_RESERVAS_POR_DIA} reservas por día"
        
        # 10. Crear la reserva
        data = {
            "usuario_id": usuario_id,
            "recurso_id": reserva.recurso_id,
            "fecha": reserva.fecha.isoformat(),
            "hora_inicio": reserva.hora_inicio.isoformat(),
            "hora_fin": reserva.hora_fin.isoformat(),
            "estado": EstadoReserva.CONFIRMADA.value if not recurso.get("requiere_aprobacion") else EstadoReserva.PENDIENTE.value,
            "motivo": reserva.motivo,
            "notas": reserva.notas
        }
        
        response = self.db.table("reservas").insert(data).execute()
        return response.data[0], None
    
    async def obtener_reserva(self, reserva_id: str) -> Optional[dict]:
        """Obtiene una reserva por ID"""
        response = self.db.table("reservas").select("*").eq("id", reserva_id).single().execute()
        return response.data
    
    async def obtener_reserva_detalle(self, reserva_id: str) -> Optional[dict]:
        """Obtiene una reserva con detalles del recurso"""
        reserva = await self.obtener_reserva(reserva_id)
        if not reserva:
            return None
        
        # Obtener recurso
        recurso = await self.recurso_service.obtener_recurso(reserva["recurso_id"])
        
        # Obtener nombre de usuario
        usuario = self.db.table("users").select("full_name")\
            .eq("id", reserva["usuario_id"]).single().execute()
        
        reserva["recurso"] = recurso
        reserva["usuario_nombre"] = usuario.data.get("full_name") if usuario.data else None
        
        return reserva
    
    async def listar_reservas_usuario(
        self,
        usuario_id: str,
        filtros: Optional[FiltroReservas] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Lista las reservas de un usuario"""
        query = self.db.table("reservas").select("*", count="exact")\
            .eq("usuario_id", usuario_id)
        
        if filtros:
            if filtros.estado:
                query = query.eq("estado", filtros.estado.value)
            if filtros.recurso_id:
                query = query.eq("recurso_id", filtros.recurso_id)
            if filtros.fecha_desde:
                query = query.gte("fecha", filtros.fecha_desde.isoformat())
            if filtros.fecha_hasta:
                query = query.lte("fecha", filtros.fecha_hasta.isoformat())
        
        # Paginación
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("fecha", desc=True).order("hora_inicio", desc=True)
        
        response = query.execute()
        
        # Agregar información del recurso a cada reserva
        for reserva in response.data:
            recurso = await self.recurso_service.obtener_recurso(reserva["recurso_id"])
            reserva["recurso"] = recurso
        
        return response.data, response.count or 0
    
    async def cancelar_reserva(
        self,
        reserva_id: str,
        usuario_id: str,
        motivo: Optional[str] = None,
        es_admin: bool = False
    ) -> Tuple[bool, str]:
        """
        Cancela una reserva.
        Retorna (True, mensaje) si tiene éxito, o (False, mensaje_error) si falla.
        """
        reserva = await self.obtener_reserva(reserva_id)
        if not reserva:
            return False, "La reserva no existe"
        
        # Verificar permisos
        if not es_admin and reserva["usuario_id"] != usuario_id:
            return False, "No tienes permiso para cancelar esta reserva"
        
        # Verificar estado
        if reserva["estado"] in [EstadoReserva.CANCELADA.value, "cancelada"]:
            return False, "La reserva ya está cancelada"
        
        if reserva["estado"] in [EstadoReserva.COMPLETADA.value, "completada"]:
            return False, "No se puede cancelar una reserva completada"
        
        # Cancelar
        self.db.table("reservas").update({
            "estado": EstadoReserva.CANCELADA.value,
            "cancelado_at": datetime.now().isoformat(),
            "cancelado_por": usuario_id,
            "motivo_cancelacion": motivo
        }).eq("id", reserva_id).execute()
        
        return True, "Reserva cancelada exitosamente"
    
    async def listar_todas_reservas(
        self,
        filtros: Optional[FiltroReservas] = None,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Lista todas las reservas (para admin)"""
        query = self.db.table("reservas").select("*", count="exact")
        
        if filtros:
            if filtros.estado:
                query = query.eq("estado", filtros.estado.value)
            if filtros.recurso_id:
                query = query.eq("recurso_id", filtros.recurso_id)
            if filtros.fecha_desde:
                query = query.gte("fecha", filtros.fecha_desde.isoformat())
            if filtros.fecha_hasta:
                query = query.lte("fecha", filtros.fecha_hasta.isoformat())
        
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("fecha", desc=True).order("hora_inicio", desc=True)
        
        response = query.execute()
        
        for reserva in response.data:
            recurso = await self.recurso_service.obtener_recurso(reserva["recurso_id"])
            reserva["recurso"] = recurso
            
            usuario = self.db.table("users").select("full_name, email")\
                .eq("id", reserva["usuario_id"]).single().execute()
            reserva["usuario_nombre"] = usuario.data.get("full_name") if usuario.data else None
            reserva["usuario_email"] = usuario.data.get("email") if usuario.data else None
        
        return response.data, response.count or 0


class CheckinService:
    """Servicio para gestión de check-ins"""
    
    def __init__(self, db: Client):
        self.db = db
        self.reserva_service = ReservaService(db)
    
    async def realizar_checkin(
        self,
        reserva_id: str,
        usuario_id: str,
        qr_token: Optional[str] = None,
        dispositivo_info: Optional[str] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Realiza el check-in de una reserva.
        Retorna (checkin, None) si tiene éxito, o (None, mensaje_error) si falla.
        """
        # 1. Obtener la reserva
        reserva = await self.reserva_service.obtener_reserva(reserva_id)
        if not reserva:
            return None, "La reserva no existe"
        
        # 2. Verificar que el usuario sea el dueño de la reserva
        if reserva["usuario_id"] != usuario_id:
            return None, "Esta reserva no te pertenece"
        
        # 3. Verificar estado de la reserva
        if reserva["estado"] not in [EstadoReserva.CONFIRMADA.value, "confirmada", 
                                      EstadoReserva.PENDIENTE.value, "pendiente"]:
            return None, f"No se puede hacer check-in: la reserva está {reserva['estado']}"
        
        # 4. Verificar que sea el día de la reserva
        fecha_reserva = datetime.strptime(reserva["fecha"], "%Y-%m-%d").date()
        if fecha_reserva != date.today():
            return None, "Solo puedes hacer check-in el día de tu reserva"
        
        # 5. Verificar ventana de tiempo para check-in
        ahora = datetime.now()
        hora_reserva = datetime.strptime(reserva["hora_inicio"], "%H:%M:%S")
        hora_reserva_completa = datetime.combine(date.today(), hora_reserva.time())
        
        ventana_inicio = hora_reserva_completa - timedelta(minutes=settings.VENTANA_CHECKIN_MINUTOS)
        ventana_fin = hora_reserva_completa + timedelta(minutes=settings.VENTANA_CHECKIN_MINUTOS)
        
        if ahora < ventana_inicio:
            return None, f"El check-in está disponible desde {ventana_inicio.strftime('%H:%M')}"
        
        if ahora > ventana_fin:
            return None, "La ventana de check-in ha expirado"
        
        # 6. Verificar que no haya check-in duplicado
        checkin_existente = self.db.table("checkins").select("id")\
            .eq("reserva_id", reserva_id)\
            .eq("es_valido", True)\
            .execute()
        
        if checkin_existente.data:
            return None, "Ya realizaste check-in para esta reserva"
        
        # 7. Si hay QR token, validarlo
        qr_valido = True
        if qr_token:
            qr_valido = await self._validar_qr_token(qr_token, reserva["recurso_id"])
            if not qr_valido:
                # Registrar intento inválido pero no bloquear
                pass
        
        # 8. Crear el check-in
        checkin_data = {
            "reserva_id": reserva_id,
            "usuario_id": usuario_id,
            "metodo": "qr" if qr_token else "manual",
            "ubicacion_validada": qr_valido,
            "dispositivo_info": dispositivo_info,
            "es_valido": True
        }
        
        response = self.db.table("checkins").insert(checkin_data).execute()
        
        # 9. Actualizar estado de la reserva
        self.db.table("reservas").update({
            "estado": EstadoReserva.EN_CURSO.value
        }).eq("id", reserva_id).execute()
        
        checkin = response.data[0]
        checkin["mensaje"] = "Check-in realizado exitosamente"
        
        return checkin, None
    
    async def _validar_qr_token(self, token: str, recurso_id: str) -> bool:
        """Valida un token QR contra el recurso"""
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        qr = self.db.table("recursos_qr").select("*")\
            .eq("token_hash", token_hash)\
            .eq("recurso_id", recurso_id)\
            .eq("activo", True)\
            .single().execute()
        
        if not qr.data:
            return False
        
        # Verificar expiración
        if qr.data.get("fecha_expiracion"):
            expiracion = datetime.fromisoformat(qr.data["fecha_expiracion"].replace("Z", "+00:00"))
            if expiracion < datetime.now(expiracion.tzinfo):
                return False
        
        return True
    
    async def validar_checkin(
        self,
        reserva_id: str,
        usuario_id: str
    ) -> dict:
        """Valida si se puede hacer check-in sin ejecutarlo"""
        reserva = await self.reserva_service.obtener_reserva(reserva_id)
        
        if not reserva:
            return {"puede_checkin": False, "mensaje": "La reserva no existe", "reserva": None}
        
        if reserva["usuario_id"] != usuario_id:
            return {"puede_checkin": False, "mensaje": "Esta reserva no te pertenece", "reserva": None}
        
        fecha_reserva = datetime.strptime(reserva["fecha"], "%Y-%m-%d").date()
        if fecha_reserva != date.today():
            return {"puede_checkin": False, "mensaje": "Solo puedes hacer check-in el día de tu reserva", "reserva": reserva}
        
        ahora = datetime.now()
        hora_reserva = datetime.strptime(reserva["hora_inicio"], "%H:%M:%S")
        hora_reserva_completa = datetime.combine(date.today(), hora_reserva.time())
        
        ventana_inicio = hora_reserva_completa - timedelta(minutes=settings.VENTANA_CHECKIN_MINUTOS)
        ventana_fin = hora_reserva_completa + timedelta(minutes=settings.VENTANA_CHECKIN_MINUTOS)
        
        if ahora < ventana_inicio:
            return {
                "puede_checkin": False, 
                "mensaje": f"Check-in disponible desde {ventana_inicio.strftime('%H:%M')}",
                "reserva": reserva
            }
        
        if ahora > ventana_fin:
            return {"puede_checkin": False, "mensaje": "La ventana de check-in ha expirado", "reserva": reserva}
        
        return {"puede_checkin": True, "mensaje": "Puedes realizar check-in", "reserva": reserva}
    
    async def obtener_historial_checkins(
        self,
        usuario_id: str,
        page: int = 1,
        page_size: int = 10
    ) -> Tuple[List[dict], int]:
        """Obtiene el historial de check-ins de un usuario"""
        offset = (page - 1) * page_size
        
        response = self.db.table("checkins").select("*", count="exact")\
            .eq("usuario_id", usuario_id)\
            .range(offset, offset + page_size - 1)\
            .order("timestamp", desc=True)\
            .execute()
        
        return response.data, response.count or 0


class QRService:
    """Servicio para gestión de códigos QR de recursos"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def generar_qr_recurso(
        self,
        recurso_id: str,
        duracion_horas: int = 24
    ) -> Tuple[Optional[dict], Optional[str]]:
        """Genera un código QR para un recurso"""
        # Verificar que el recurso existe
        recurso = self.db.table("recursos").select("id, nombre")\
            .eq("id", recurso_id).single().execute()
        
        if not recurso.data:
            return None, "El recurso no existe"
        
        # Generar token único
        token = secrets.token_urlsafe(32)
        token_hash = hashlib.sha256(token.encode()).hexdigest()
        
        # Fecha de expiración
        expiracion = datetime.now() + timedelta(hours=duracion_horas)
        
        # Desactivar QRs anteriores del recurso
        self.db.table("recursos_qr").update({"activo": False})\
            .eq("recurso_id", recurso_id).execute()
        
        # Crear nuevo QR en la base de datos
        qr_data = {
            "recurso_id": recurso_id,
            "token_hash": token_hash,
            "fecha_expiracion": expiracion.isoformat(),
            "activo": True
        }
        
        response = self.db.table("recursos_qr").insert(qr_data).execute()
        
        # Generar imagen QR
        qr_content = f"CAMPUS360:CHECKIN:{recurso_id}:{token}"
        qr_image = qrcode.make(qr_content)
        
        # Convertir a base64
        buffer = io.BytesIO()
        qr_image.save(buffer, format="PNG")
        qr_base64 = base64.b64encode(buffer.getvalue()).decode()
        
        return {
            "id": response.data[0]["id"],
            "recurso_id": recurso_id,
            "recurso_nombre": recurso.data["nombre"],
            "qr_code_base64": qr_base64,
            "fecha_expiracion": expiracion.isoformat(),
            "activo": True
        }, None
