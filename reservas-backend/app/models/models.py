from enum import Enum


class TipoRecurso(str, Enum):
    """Tipos de recursos disponibles"""
    SALA_ESTUDIO = "sala_estudio"
    LABORATORIO = "laboratorio"
    EQUIPO = "equipo"
    PARQUEADERO = "parqueadero"
    CUBICULO = "cubiculo"


class TipoEquipo(str, Enum):
    """Tipos de equipos (solo para recursos tipo 'equipo')"""
    PROYECTOR = "proyector"
    LAPTOP = "laptop"
    CAMARA = "camara"
    TABLET = "tablet"
    OTRO = "otro"


class EstadoRecurso(str, Enum):
    """Estados posibles de un recurso"""
    DISPONIBLE = "disponible"
    OCUPADO = "ocupado"
    MANTENIMIENTO = "mantenimiento"
    FUERA_SERVICIO = "fuera_servicio"


class EstadoReserva(str, Enum):
    """Estados posibles de una reserva"""
    PENDIENTE = "pendiente"
    CONFIRMADA = "confirmada"
    EN_CURSO = "en_curso"
    COMPLETADA = "completada"
    CANCELADA = "cancelada"
    NO_SHOW = "no_show"