# CAMPUS360 — RESERVAS

Microservicio desarrollado para el ecosistema CAMPUS360 en la materia Desarrollo de Sistemas de Información.

## 🚀 Tecnologías

- Python 3.10+
- FastAPI
- Uvicorn
- PostgreSQL
- Swagger UI (automático)

## 📁 Estructura del proyecto

    /app
        /routers
        /schemas
        /models
        /services

## ▶ Cómo ejecutar el proyecto

```bash
pip install -r requirements.txt
uvicorn app.main:app --reload
```

## 📌 Endpoints principales

| Método | Endpoint | Descripción          |
| ------ | -------- | -------------------- |
| GET    | /health  | Verificar servicio   |
| ...    | ...      | Funciones del módulo |

## 👥 Integrantes del Equipo

- Dev Principal: Santiago Esquetini Murillo
- Product Owner del módulo: Samuel Andres Vega Mendoza
- Scrum Master asignado: Andrea Valentina Campaña Intriago
