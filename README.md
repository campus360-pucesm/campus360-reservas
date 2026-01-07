# CAMPUS360 — Sistema de Reservas

Microservicio backend para la gestión de reservas de recursos universitarios, desarrollado como parte del ecosistema CAMPUS360 para la materia Desarrollo de Sistemas de Información.

## Descripción General

Este módulo permite a estudiantes y personal universitario reservar diferentes recursos del campus (salas de estudio, laboratorios, módulos de biblioteca, parqueaderos y equipos) y confirmar su asistencia mediante check-in con códigos QR.

## Tecnologías

- **Python 3.10+** — Lenguaje principal
- **FastAPI** — Framework web de alto rendimiento
- **Uvicorn** — Servidor ASGI
- **Supabase** — Base de datos PostgreSQL en la nube
- **Pydantic** — Validación de datos
- **Swagger UI** — Documentación interactiva automática

## Estructura del Proyecto

```
campus360-reservas/
├── app/
│   ├── __init__.py
│   ├── main.py              # Punto de entrada de la aplicación
│   ├── config.py            # Configuraciones y variables de entorno
│   ├── dependencies.py      # Conexión a Supabase
│   ├── models/
│   │   └── models.py        # Enums y tipos de datos
│   ├── routers/
│   │   ├── health.py        # Endpoints de health check
│   │   ├── recursos.py      # Endpoints de recursos
│   │   ├── reservas.py      # Endpoints de reservas
│   │   └── checkin.py       # Endpoints de check-in
│   ├── schemas/
│   │   └── schemas.py       # Esquemas Pydantic para validación
│   └── services/
│       └── services.py      # Lógica de negocio
├── tests/
│   └── test_health.py
├── .env                     # Variables de entorno (no incluir en git)
├── .env.example             # Plantilla de variables de entorno
├── .gitignore
├── requirements.txt
└── README.md
```

## Instalación y Ejecución

### 1. Clonar el repositorio

```bash
git clone <url-del-repositorio>
cd campus360-reservas
```

### 2. Crear entorno virtual

```bash
python -m venv .venv
```

### 3. Activar entorno virtual

**Windows (PowerShell):**
```powershell
.venv\Scripts\activate
```

**Windows (CMD):**
```cmd
.venv\Scripts\activate.bat
```

**Mac/Linux:**
```bash
source .venv/bin/activate
```

### 4. Instalar dependencias

```bash
pip install -r requirements.txt
```

### 5. Ejecutar el servidor

```bash
python -m uvicorn app.main:app --reload
```

El servidor estará disponible en `http://localhost:8000`

## Documentación de la API

Una vez ejecutando el servidor:

- **Swagger UI:** http://localhost:8000/docs
- **Health Check:** http://localhost:8000/health

## Recursos Disponibles

El sistema gestiona 5 tipos de recursos universitarios:

| Tipo | Cantidad | Capacidad | Código |
|------|----------|-----------|--------|
| Salas de Estudio | 5 | 10 personas | SAL-001 a SAL-005 |
| Laboratorios de Computación | 5 | 20 personas | LAB-001 a LAB-005 |
| Módulos de Biblioteca | 5 | 4 personas | BIB-001 a BIB-005 |
| Parqueaderos | 20 | 1 vehículo | PKG-001 a PKG-020 |
| Equipos (proyectores, laptops) | 5 | 1 persona | EQP-001 a EQP-005 |

## Flujo de Uso

El sistema sigue un flujo de 4 pasos:

```
┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐     ┌─────────────────┐
│  1. CONSULTAR   │────▶│  2. VERIFICAR   │────▶│  3. RESERVAR    │────▶│  4. CHECK-IN    │
│    RECURSOS     │     │  DISPONIBILIDAD │     │    RECURSO      │     │    VIA QR       │
└─────────────────┘     └─────────────────┘     └─────────────────┘     └─────────────────┘
```

### Paso 1: Consultar Recursos

Ver qué recursos están disponibles en el campus.

```bash
# Listar todos los recursos
GET /recursos/

# Filtrar por tipo
GET /recursos/?tipo=laboratorio

# Ver solo salas de estudio
GET /recursos/salas

# Ver solo laboratorios
GET /recursos/laboratorios
```

### Paso 2: Verificar Disponibilidad

Consultar los horarios disponibles de un recurso para una fecha específica.

```bash
# Ver disponibilidad de un recurso para una fecha
GET /recursos/{recurso_id}/disponibilidad?fecha=2025-01-20
```

Respuesta ejemplo:
```json
{
  "success": true,
  "data": {
    "recurso": { "nombre": "Laboratorio 1", "capacidad": 20 },
    "fecha": "2025-01-20",
    "disponible": true,
    "horarios_disponibles": [
      { "inicio": "07:00", "fin": "08:00" },
      { "inicio": "08:00", "fin": "09:00" },
      { "inicio": "14:00", "fin": "15:00" }
    ],
    "horarios_ocupados": [
      { "inicio": "09:00", "fin": "12:00", "motivo": "Clase de Programación" }
    ]
  }
}
```

### Paso 3: Crear Reserva

Reservar un recurso para una fecha y horario específico.

```bash
POST /reservas/
```

Body:
```json
{
  "recurso_id": "uuid-del-recurso",
  "fecha": "2025-01-20",
  "hora_inicio": "10:00",
  "hora_fin": "12:00",
  "usuario_id": "user-123",
  "usuario_nombre": "Juan Pérez",
  "usuario_email": "juan@universidad.edu",
  "motivo": "Clase de programación",
  "num_asistentes": 15
}
```

### Paso 4: Check-in vía QR

Al llegar al recurso, escanear el código QR para confirmar asistencia.

```bash
POST /checkin/
```

Body:
```json
{
  "codigo_qr": "QR-LAB-001",
  "usuario_id": "user-123",
  "usuario_nombre": "María García",
  "usuario_email": "maria@universidad.edu"
}
```

Respuesta exitosa:
```json
{
  "success": true,
  "message": "✅ ¡Bienvenido/a María García! Check-in #5 de 20 registrado en Laboratorio 1. Hay 15 lugares disponibles.",
  "data": {
    "numero_checkin": 5,
    "capacidad_total": 20,
    "lugares_restantes": 15,
    "porcentaje_ocupacion": 25.0
  }
}
```

## Estados de una Reserva

Las reservas pasan por diferentes estados durante su ciclo de vida:

```
                    ┌──────────────┐
                    │  CONFIRMADA  │ ← Estado inicial al crear
                    └──────┬───────┘
                           │
            ┌──────────────┼──────────────┐
            │              │              │
            ▼              ▼              ▼
    ┌──────────────┐ ┌──────────┐ ┌──────────────┐
    │  CANCELADA   │ │ EN_CURSO │ │   NO_SHOW    │
    │              │ │          │ │              │
    └──────────────┘ └────┬─────┘ └──────────────┘
                          │
                          ▼
                   ┌──────────────┐
                   │  COMPLETADA  │
                   └──────────────┘
```

- **CONFIRMADA:** Reserva creada y lista para usar
- **EN_CURSO:** Al menos una persona hizo check-in
- **COMPLETADA:** La reserva finalizó (hora_fin pasó)
- **CANCELADA:** El usuario canceló la reserva
- **NO_SHOW:** Nadie se presentó durante el horario reservado

## Control de Capacidad

El sistema controla automáticamente la capacidad de cada recurso:

1. Cada recurso tiene una **capacidad máxima** definida
2. Al hacer check-in, el sistema cuenta los asistentes registrados
3. Si la capacidad está llena, el check-in es **rechazado**
4. Se muestra información en tiempo real de ocupación

Ejemplo de capacidad llena:
```json
{
  "success": false,
  "detail": "¡Lo sentimos! La capacidad de Laboratorio 1 está completa (20/20 personas). No es posible registrar más asistentes."
}
```

## Endpoints Principales

### Health Check

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/health/` | Verificar que el servicio está activo |
| GET | `/health/db` | Verificar conexión a la base de datos |

### Recursos

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| GET | `/recursos/` | Listar todos los recursos |
| GET | `/recursos/tipos` | Resumen de tipos disponibles |
| GET | `/recursos/salas` | Listar salas de estudio |
| GET | `/recursos/laboratorios` | Listar laboratorios |
| GET | `/recursos/biblioteca` | Listar módulos de biblioteca |
| GET | `/recursos/parqueaderos` | Listar parqueaderos |
| GET | `/recursos/equipos` | Listar equipos |
| GET | `/recursos/{id}` | Obtener detalle de un recurso |
| GET | `/recursos/{id}/disponibilidad` | Ver horarios disponibles |

### Reservas

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/reservas/` | Crear nueva reserva |
| GET | `/reservas/` | Listar reservas (con filtros) |
| GET | `/reservas/usuario/{id}` | Reservas de un usuario |
| GET | `/reservas/fecha/{fecha}` | Reservas de una fecha |
| GET | `/reservas/{id}` | Detalle de una reserva |
| DELETE | `/reservas/{id}` | Cancelar reserva |

### Check-in

| Método | Endpoint | Descripción |
|--------|----------|-------------|
| POST | `/checkin/` | Realizar check-in con QR |
| GET | `/checkin/estado/{reserva_id}` | Estado de check-ins de una reserva |
| GET | `/checkin/usuario/{id}` | Historial de check-ins de un usuario |
| GET | `/checkin/qr/todos` | Listar todos los códigos QR |
| GET | `/checkin/qr/{recurso_id}` | Obtener QR de un recurso |
| GET | `/checkin/simular/{codigo_qr}` | Simular escaneo de QR (testing) |

## Base de Datos

### Tablas en Supabase

```
┌─────────────┐     ┌─────────────┐     ┌─────────────┐
│  recursos   │────▶│  reservas   │────▶│  checkins   │
└─────────────┘     └─────────────┘     └─────────────┘
      │
      ▼
┌─────────────┐
│ recursos_qr │
└─────────────┘
```

- **recursos:** Información de cada recurso (salas, labs, etc.)
- **reservas:** Registro de todas las reservas
- **checkins:** Registro de cada check-in realizado
- **recursos_qr:** Códigos QR asociados a cada recurso

## Validaciones del Sistema

El sistema realiza las siguientes validaciones:

**Al crear una reserva:**
- El recurso debe existir y estar disponible
- La fecha no puede ser pasada
- No puede haber conflictos de horario con otras reservas
- El número de asistentes no puede exceder la capacidad

**Al hacer check-in:**
- El código QR debe ser válido y activo
- Debe existir una reserva activa en el momento actual
- Se permite check-in desde 15 minutos antes de la hora de inicio
- El usuario no puede hacer check-in dos veces
- La capacidad no puede estar llena

## Errores Comunes

| Error | Causa | Solución |
|-------|-------|----------|
| "Recurso no encontrado" | ID inválido | Verificar el ID del recurso |
| "Ya existe una reserva en ese horario" | Conflicto de horarios | Elegir otro horario disponible |
| "Capacidad excedida" | Asistentes > capacidad | Reducir número de asistentes |
| "No hay reserva activa" | Check-in fuera de horario | Verificar hora de la reserva |
| "Ya realizaste check-in" | Check-in duplicado | Solo se permite un check-in por persona |

## Equipo de Desarrollo

- **Desarrollador Principal:** Santiago Esquetini Murillo
- **Product Owner:** Samuel Andrés Vega Mendoza
- **Scrum Master:** Andrea Valentina Campaña Intriago
