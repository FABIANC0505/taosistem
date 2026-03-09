# Taosistem - Sistema de Pedidos para Restaurante

Sistema de gestión de pedidos para restaurantes construido con FastAPI, PostgreSQL y Redis.

## 🚀 Inicio Rápido con Docker

### Prerrequisitos
- Docker y Docker Compose instalados
- Puerto 8000 (backend), 5432 (PostgreSQL) y 6379 (Redis) disponibles

### Levantar el proyecto

```bash
# Desde la raíz del proyecto
docker-compose up -d

# Ver logs
docker-compose logs -f backend

# Detener servicios
docker-compose down
```

### Acceso
- **API Backend:** http://localhost:8000
- **Documentación (Swagger):** http://localhost:8000/docs
- **PostgreSQL:** localhost:5432
- **Redis:** localhost:6379

## 📁 Estructura del Proyecto

```
backend/
├── app/
│   ├── core/          # Configuración, BD, Redis, Security
│   ├── models/        # Modelos SQLAlchemy
│   ├── routers/       # Endpoints API
│   ├── schemas/       # Esquemas Pydantic
│   └── services/      # Lógica de negocio
├── alembic/           # Migraciones de BD
├── uploads/           # Archivos subidos
├── main.py            # Punto de entrada
├── requirements.txt   # Dependencias Python
└── Dockerfile         # Imagen Docker
```

## 🔧 Desarrollo Local (sin Docker)

Si prefieres trabajar sin Docker:

```bash
cd backend

# Crear entorno virtual
python -m venv venv
venv\Scripts\activate  # Windows
source venv/bin/activate  # Linux/Mac

# Instalar dependencias
pip install -r requirements.txt

# Levantar servicios de BD (con Docker)
docker-compose up -d db redis

# Ejecutar aplicación
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

## 🗃️ Migraciones de Base de Datos

```bash
# Crear migración
docker-compose exec backend alembic revision --autogenerate -m "descripción"

# Aplicar migraciones
docker-compose exec backend alembic upgrade head
```

## 🛠️ Tecnologías

- **FastAPI** - Framework web moderno y rápido
- **PostgreSQL 15** - Base de datos relacional
- **Redis 7** - Cache y sesiones
- **SQLAlchemy 2.0** - ORM async
- **Alembic** - Migraciones de BD
- **Pydantic v2** - Validación de datos
- **Python-JOSE** - JWT autenticación
- **Passlib** - Hash de contraseñas

## 📝 Variables de Entorno

Ver archivo `backend/.env` para configuración completa.

