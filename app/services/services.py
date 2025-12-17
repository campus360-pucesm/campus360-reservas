"""
Servicios de Logica de Negocio para el Modulo de Reservas
ACTUALIZADO con control de capacidad en check-ins
"""
from datetime import date, time, datetime, timedelta
from typing import Optional, List, Tuple
from supabase import Client
import hashlib
import secrets

from app.config import get_settings

settings = get_settings()


class RecursoService:
    """Servicio para gestion de recursos"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def listar_recursos(
        self,
        tipo: Optional[str] = None,
        estado: Optional[str] = None,
        page: int = 1,
        page_size: int = 50
    ) -> Tuple[List[dict], int]:
        """Lista recursos con filtros opcionales"""
        query = self.db.table("recursos").select("*", count="exact")
        
        if tipo:
            query = query.eq("tipo", tipo)
        if estado:
            query = query.eq("estado", estado)
        else:
            # Por defecto solo mostrar disponibles
            query = query.eq("estado", "disponible")
        
        # Paginacion
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("codigo")
        
        response = query.execute()
        return response.data, response.count or 0
    
    async def obtener_recurso(self, recurso_id: str) -> Optional[dict]:
        """Obtiene un recurso por ID"""
        response = self.db.table("recursos").select("*").eq("id", recurso_id).single().execute()
        return response.data
    
    async def obtener_recurso_por_codigo(self, codigo: str) -> Optional[dict]:
        """Obtiene un recurso por su codigo (ej: SAL-001)"""
        response = self.db.table("recursos").select("*").eq("codigo", codigo).single().execute()
        return response.data
    
    async def obtener_disponibilidad(
        self,
        recurso_id: str,
        fecha: date
    ) -> dict:
        """Obtiene la disponibilidad de un recurso para una fecha"""
        recurso = await self.obtener_recurso(recurso_id)
        if not recurso:
            return None
        
        # Verificar si el dia esta disponible
        dia_semana = fecha.isoweekday()
        if dia_semana not in recurso.get("dias_disponibles", [1, 2, 3, 4, 5, 6]):
            return {
                "recurso": recurso,
                "fecha": fecha.isoformat(),
                "disponible": False,
                "mensaje": "El recurso no esta disponible este dia de la semana",
                "horarios_disponibles": [],
                "horarios_ocupados": []
            }
        
        # Obtener reservas del dia
        reservas = self.db.table("reservas").select("hora_inicio, hora_fin, estado, motivo")\
            .eq("recurso_id", recurso_id)\
            .eq("fecha", fecha.isoformat())\
            .neq("estado", "cancelada")\
            .execute()
        
        horarios_ocupados = []
        for r in reservas.data:
            horarios_ocupados.append({
                "inicio": r["hora_inicio"],
                "fin": r["hora_fin"],
                "motivo": r.get("motivo", "Reservado")
            })
        
        # Calcular slots disponibles
        horarios_disponibles = self._calcular_slots_disponibles(
            recurso["horario_inicio"],
            recurso["horario_fin"],
            horarios_ocupados
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
        horario_inicio: str,
        horario_fin: str,
        ocupados: List[dict]
    ) -> List[dict]:
        """Calcula los slots de tiempo disponibles (cada hora)"""
        slots = []
        
        # Parsear horarios
        h_inicio = datetime.strptime(horario_inicio, "%H:%M:%S").time()
        h_fin = datetime.strptime(horario_fin, "%H:%M:%S").time()
        
        current = datetime.combine(date.today(), h_inicio)
        end = datetime.combine(date.today(), h_fin)
        
        while current < end:
            slot_inicio = current.time()
            slot_fin = (current + timedelta(hours=1)).time()
            
            # Verificar si el slot esta ocupado
            ocupado = False
            for o in ocupados:
                o_inicio = datetime.strptime(o["inicio"], "%H:%M:%S").time()
                o_fin = datetime.strptime(o["fin"], "%H:%M:%S").time()
                
                if not (slot_fin <= o_inicio or slot_inicio >= o_fin):
                    ocupado = True
                    break
            
            if not ocupado:
                slots.append({
                    "inicio": slot_inicio.strftime("%H:%M"),
                    "fin": slot_fin.strftime("%H:%M")
                })
            
            current += timedelta(hours=1)
        
        return slots


class ReservaService:
    """Servicio para gestion de reservas"""
    
    def __init__(self, db: Client):
        self.db = db
        self.recurso_service = RecursoService(db)
    
    async def crear_reserva(
        self,
        recurso_id: str,
        usuario_id: str,
        usuario_nombre: str,
        usuario_email: str,
        fecha: date,
        hora_inicio: time,
        hora_fin: time,
        motivo: Optional[str] = None,
        num_asistentes: int = 1
    ) -> Tuple[Optional[dict], Optional[str]]:
        """Crea una nueva reserva"""
        
        # 1. Verificar que el recurso existe
        recurso = await self.recurso_service.obtener_recurso(recurso_id)
        if not recurso:
            return None, "El recurso no existe"
        
        if recurso["estado"] != "disponible":
            return None, f"El recurso no esta disponible (estado: {recurso['estado']})"
        
        # 2. Verificar que la fecha no sea pasada
        if fecha < date.today():
            return None, "No se pueden hacer reservas en fechas pasadas"
        
        # 3. Verificar que el numero de asistentes no exceda la capacidad
        if num_asistentes > recurso["capacidad"]:
            return None, f"El numero de asistentes ({num_asistentes}) excede la capacidad del recurso ({recurso['capacidad']})"
        
        # 4. Verificar que no haya conflictos con otras reservas
        conflictos = self.db.table("reservas").select("id, hora_inicio, hora_fin")\
            .eq("recurso_id", recurso_id)\
            .eq("fecha", fecha.isoformat())\
            .neq("estado", "cancelada")\
            .execute()
        
        for r in conflictos.data:
            e_inicio = datetime.strptime(r["hora_inicio"], "%H:%M:%S").time()
            e_fin = datetime.strptime(r["hora_fin"], "%H:%M:%S").time()
            
            if not (hora_fin <= e_inicio or hora_inicio >= e_fin):
                return None, f"Ya existe una reserva en ese horario ({r['hora_inicio']} - {r['hora_fin']})"
        
        # 5. Crear la reserva
        data = {
            "usuario_id": usuario_id,
            "usuario_nombre": usuario_nombre,
            "usuario_email": usuario_email,
            "recurso_id": recurso_id,
            "fecha": fecha.isoformat(),
            "hora_inicio": hora_inicio.isoformat(),
            "hora_fin": hora_fin.isoformat(),
            "estado": "confirmada",
            "motivo": motivo,
            "num_asistentes_esperados": num_asistentes
        }
        
        response = self.db.table("reservas").insert(data).execute()
        
        reserva = response.data[0]
        reserva["recurso"] = recurso
        
        return reserva, None
    
    async def obtener_reserva(self, reserva_id: str) -> Optional[dict]:
        """Obtiene una reserva por ID con info del recurso"""
        response = self.db.table("reservas").select("*").eq("id", reserva_id).single().execute()
        
        if response.data:
            # Agregar info del recurso
            recurso = await self.recurso_service.obtener_recurso(response.data["recurso_id"])
            response.data["recurso"] = recurso
            
            # Contar check-ins
            checkins = self.db.table("checkins").select("id", count="exact")\
                .eq("reserva_id", reserva_id)\
                .eq("estado", "exitoso")\
                .execute()
            response.data["checkins_realizados"] = checkins.count or 0
            response.data["capacidad_total"] = recurso["capacidad"] if recurso else 0
        
        return response.data
    
    async def listar_reservas_usuario(
        self,
        usuario_id: str,
        estado: Optional[str] = None,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """Lista las reservas de un usuario"""
        query = self.db.table("reservas").select("*", count="exact")\
            .eq("usuario_id", usuario_id)
        
        if estado:
            query = query.eq("estado", estado)
        
        offset = (page - 1) * page_size
        query = query.range(offset, offset + page_size - 1)
        query = query.order("fecha", desc=True).order("hora_inicio", desc=True)
        
        response = query.execute()
        
        # Agregar info del recurso a cada reserva
        for reserva in response.data:
            recurso = await self.recurso_service.obtener_recurso(reserva["recurso_id"])
            reserva["recurso"] = recurso
        
        return response.data, response.count or 0
    
    async def listar_reservas_por_fecha(
        self,
        fecha: date,
        tipo_recurso: Optional[str] = None
    ) -> List[dict]:
        """Lista todas las reservas de una fecha"""
        query = self.db.table("reservas").select("*")\
            .eq("fecha", fecha.isoformat())\
            .neq("estado", "cancelada")
        
        response = query.execute()
        
        reservas = []
        for reserva in response.data:
            recurso = await self.recurso_service.obtener_recurso(reserva["recurso_id"])
            if tipo_recurso and recurso and recurso["tipo"] != tipo_recurso:
                continue
            reserva["recurso"] = recurso
            reservas.append(reserva)
        
        return reservas
    
    async def cancelar_reserva(
        self,
        reserva_id: str,
        usuario_id: str,
        motivo: Optional[str] = None
    ) -> Tuple[bool, str]:
        """Cancela una reserva"""
        reserva = await self.obtener_reserva(reserva_id)
        if not reserva:
            return False, "La reserva no existe"
        
        if reserva["usuario_id"] != usuario_id:
            return False, "No tienes permiso para cancelar esta reserva"
        
        if reserva["estado"] == "cancelada":
            return False, "La reserva ya esta cancelada"
        
        self.db.table("reservas").update({
            "estado": "cancelada",
            "cancelado_at": datetime.now().isoformat(),
            "motivo_cancelacion": motivo
        }).eq("id", reserva_id).execute()
        
        return True, "Reserva cancelada exitosamente"


class CheckinService:
    """Servicio para gestion de check-ins con control de capacidad"""
    
    def __init__(self, db: Client):
        self.db = db
        self.reserva_service = ReservaService(db)
    
    async def realizar_checkin(
        self,
        codigo_qr: str,
        usuario_id: str,
        usuario_nombre: str,
        usuario_email: str,
        dispositivo_info: Optional[str] = None
    ) -> Tuple[Optional[dict], Optional[str]]:
        """
        Realiza el check-in escaneando un codigo QR.
        Valida la capacidad del recurso.
        """
        
        # 1. Validar el codigo QR
        qr_info = self.db.table("recursos_qr").select("*, recursos(*)")\
            .eq("codigo_qr", codigo_qr)\
            .eq("activo", True)\
            .single().execute()
        
        if not qr_info.data:
            return None, "Codigo QR invalido o inactivo"
        
        recurso = qr_info.data.get("recursos")
        if not recurso:
            return None, "Recurso no encontrado"
        
        # 2. Buscar reserva activa para hoy en este recurso
        hoy = date.today()
        ahora = datetime.now().time()
        
        # Buscar reservas de hoy que esten en curso o confirmadas
        reservas_hoy = self.db.table("reservas").select("*")\
            .eq("recurso_id", recurso["id"])\
            .eq("fecha", hoy.isoformat())\
            .in_("estado", ["confirmada", "en_curso"])\
            .execute()
        
        reserva_activa = None
        for r in reservas_hoy.data:
            h_inicio = datetime.strptime(r["hora_inicio"], "%H:%M:%S").time()
            h_fin = datetime.strptime(r["hora_fin"], "%H:%M:%S").time()
            
            # Permitir check-in 15 minutos antes hasta el fin de la reserva
            h_inicio_con_margen = (datetime.combine(hoy, h_inicio) - timedelta(minutes=15)).time()
            
            if h_inicio_con_margen <= ahora <= h_fin:
                reserva_activa = r
                break
        
        if not reserva_activa:
            return None, f"No hay ninguna reserva activa en este momento para {recurso['nombre']}. Verifica el horario de tu reserva."
        
        # 3. Verificar si el usuario ya hizo check-in
        checkin_existente = self.db.table("checkins").select("id")\
            .eq("reserva_id", reserva_activa["id"])\
            .eq("usuario_id", usuario_id)\
            .eq("estado", "exitoso")\
            .execute()
        
        if checkin_existente.data:
            return None, "Ya realizaste check-in para esta reserva. No puedes registrarte dos veces."
        
        # 4. Contar check-ins actuales vs capacidad
        checkins_actuales = self.db.table("checkins").select("id", count="exact")\
            .eq("reserva_id", reserva_activa["id"])\
            .eq("estado", "exitoso")\
            .execute()
        
        num_checkins = checkins_actuales.count or 0
        capacidad = recurso["capacidad"]
        
        if num_checkins >= capacidad:
            # Registrar intento rechazado
            self.db.table("checkins").insert({
                "reserva_id": reserva_activa["id"],
                "usuario_id": usuario_id,
                "usuario_nombre": usuario_nombre,
                "usuario_email": usuario_email,
                "numero_checkin": num_checkins + 1,
                "estado": "rechazado",
                "mensaje": f"Capacidad completa ({capacidad}/{capacidad})",
                "dispositivo_info": dispositivo_info
            }).execute()
            
            return None, f"¡Lo sentimos! La capacidad de {recurso['nombre']} esta completa ({capacidad}/{capacidad} personas). No es posible registrar mas asistentes."
        
        # 5. Realizar check-in exitoso
        nuevo_numero = num_checkins + 1
        
        checkin_data = {
            "reserva_id": reserva_activa["id"],
            "usuario_id": usuario_id,
            "usuario_nombre": usuario_nombre,
            "usuario_email": usuario_email,
            "numero_checkin": nuevo_numero,
            "estado": "exitoso",
            "mensaje": f"Check-in exitoso ({nuevo_numero}/{capacidad})",
            "dispositivo_info": dispositivo_info
        }
        
        response = self.db.table("checkins").insert(checkin_data).execute()
        
        # 6. Si es el primer check-in, actualizar estado de reserva a "en_curso"
        if reserva_activa["estado"] == "confirmada":
            self.db.table("reservas").update({"estado": "en_curso"})\
                .eq("id", reserva_activa["id"]).execute()
        
        # 7. Preparar respuesta
        checkin = response.data[0]
        
        # Mensaje segun cuantos quedan
        lugares_restantes = capacidad - nuevo_numero
        if lugares_restantes == 0:
            mensaje_capacidad = "¡Capacidad completa! No hay mas lugares disponibles."
        elif lugares_restantes <= 3:
            mensaje_capacidad = f"¡Quedan solo {lugares_restantes} lugares!"
        else:
            mensaje_capacidad = f"Hay {lugares_restantes} lugares disponibles."
        
        return {
            "checkin": checkin,
            "recurso": recurso,
            "reserva": reserva_activa,
            "numero_checkin": nuevo_numero,
            "capacidad_total": capacidad,
            "lugares_restantes": lugares_restantes,
            "mensaje": f"✅ ¡Bienvenido/a {usuario_nombre}! Check-in #{nuevo_numero} de {capacidad} registrado en {recurso['nombre']}. {mensaje_capacidad}",
            "porcentaje_ocupacion": round((nuevo_numero / capacidad) * 100, 1)
        }, None
    
    async def obtener_estado_checkins(self, reserva_id: str) -> dict:
        """Obtiene el estado actual de check-ins de una reserva"""
        reserva = await self.reserva_service.obtener_reserva(reserva_id)
        if not reserva:
            return None
        
        checkins = self.db.table("checkins").select("*")\
            .eq("reserva_id", reserva_id)\
            .order("numero_checkin")\
            .execute()
        
        exitosos = [c for c in checkins.data if c["estado"] == "exitoso"]
        rechazados = [c for c in checkins.data if c["estado"] == "rechazado"]
        
        capacidad = reserva["recurso"]["capacidad"] if reserva.get("recurso") else 1
        
        return {
            "reserva": reserva,
            "capacidad_total": capacidad,
            "checkins_exitosos": len(exitosos),
            "checkins_rechazados": len(rechazados),
            "lugares_disponibles": max(0, capacidad - len(exitosos)),
            "porcentaje_ocupacion": round((len(exitosos) / capacidad) * 100, 1) if capacidad > 0 else 0,
            "lista_asistentes": exitosos,
            "lista_rechazados": rechazados,
            "esta_lleno": len(exitosos) >= capacidad
        }
    
    async def listar_checkins_usuario(
        self,
        usuario_id: str,
        page: int = 1,
        page_size: int = 20
    ) -> Tuple[List[dict], int]:
        """Lista los check-ins de un usuario"""
        offset = (page - 1) * page_size
        
        response = self.db.table("checkins").select("*", count="exact")\
            .eq("usuario_id", usuario_id)\
            .range(offset, offset + page_size - 1)\
            .order("timestamp", desc=True)\
            .execute()
        
        return response.data, response.count or 0


class QRService:
    """Servicio para gestion de codigos QR"""
    
    def __init__(self, db: Client):
        self.db = db
    
    async def obtener_qr_recurso(self, recurso_id: str) -> Optional[dict]:
        """Obtiene el QR de un recurso"""
        response = self.db.table("recursos_qr").select("*")\
            .eq("recurso_id", recurso_id)\
            .eq("activo", True)\
            .single().execute()
        
        return response.data
    
    async def listar_todos_qr(self) -> List[dict]:
        """Lista todos los codigos QR con info del recurso"""
        response = self.db.table("recursos_qr").select("*, recursos(*)")\
            .eq("activo", True)\
            .execute()
        
        return response.data
