"""
CAMPUS360 - Modulo de Reservas
API Backend para gestion de reservas de recursos universitarios
"""
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from app.config import get_settings
from app.routers import recursos, reservas, checkin, health

settings = get_settings()

# Crear aplicacion FastAPI
app = FastAPI(
    title="CAMPUS360 - Sistema de Reservas",
    description="""
## Sistema de Reservas de Recursos Universitarios

Este API permite gestionar:

### Recursos Disponibles:
- **5 Salas de Estudio** (capacidad: 10 personas c/u)
- **5 Laboratorios de Computacion** (capacidad: 20 personas c/u)
- **5 Modulos de Biblioteca** (capacidad: 4 personas c/u)
- **20 Parqueaderos** (capacidad: 1 vehiculo c/u)
- **5 Equipos** (proyectores, laptops, camara)

### Flujo de Uso:
1. **Consultar recursos** - Ver que hay disponible
2. **Ver disponibilidad** - Consultar horarios libres de un recurso
3. **Crear reserva** - Apartar un recurso para una fecha/hora
4. **Check-in via QR** - Confirmar asistencia escaneando codigo QR

### Control de Capacidad:
- Cada recurso tiene una capacidad maxima
- El check-in cuenta asistentes hasta llenar capacidad
- Cuando esta lleno: "Capacidad completa, no hay mas lugares"
    """,
    version="2.0.0",
    docs_url="/docs",
    redoc_url="/redoc"
)

# Configurar CORS para frontend
app.add_middleware(
    CORSMiddleware,
    allow_origins=["http://localhost:5173", "http://localhost:3000", "http://127.0.0.1:5173", "*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Incluir routers
app.include_router(health.router)
app.include_router(recursos.router)
app.include_router(reservas.router)
app.include_router(checkin.router)


@app.get("/", tags=["Info"])
async def root():
    """Informacion del servicio"""
    return {
        "servicio": "CAMPUS360 - Sistema de Reservas",
        "version": "2.0.0",
        "estado": "activo",
        "documentacion": "/docs",
        "endpoints": {
            "recursos": "/recursos - Ver recursos disponibles",
            "reservas": "/reservas - Gestionar reservas",
            "checkin": "/checkin - Realizar check-in via QR"
        }
    }