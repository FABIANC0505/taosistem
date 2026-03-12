# RestauTech - Panel Admin de Restaurante

Sistema completo de administración para restaurantes: **Dashboard con métricas (media/moda)**, gestión de usuarios, productos, descuentos y configuración.

**Tech Stack:** FastAPI + React + TypeScript + PostgreSQL + Redis

---

## ⚡ Inicio Rápido (Pick One)

### Opción A: Usar Docker (Recomendado - 1 Comando)
```powershell
.\start-docker.ps1
```
✅ Todo automático | ❌ Requiere Docker Desktop

### Opción B: Desarrollo Local (Python + Node.js)
```powershell
.\start-dev.ps1
```
✅ Control total | ❌ Requiere PostgreSQL local

### Opción C: Setup Manual
```powershell
# 1. Crear BD (primera vez)
.\setup-db.ps1

# 2. Backend
cd backend
python -m venv venv
.\venv\Scripts\Activate.ps1
pip install -r requirements.txt
uvicorn main:app --reload --host 0.0.0.0 --port 8000

# 3. Frontend (nueva ventana)
cd frontend
npm install
npm run dev
```

---

## 📍 Acceso Después de Iniciar

| Componente | URL | Notas |
|-----------|-----|-------|
| **Frontend** | http://localhost:3000 | Panel admin |
| **Backend API** | http://localhost:8000 | API REST |
| **API Docs** | http://localhost:8000/docs | Swagger UI |
| **pgAdmin** | http://localhost:5050 | (Solo Docker) |

**Credenciales de Prueba:**
- Email: `admin@restaurante.com`
- Password: `admin123`

> ℹ️ Las credenciales se crean automáticamente con el primer registro.

---

## 🎯 Características Principales

✅ **Dashboard Interactivo**
- 4 KPI cards (ingresos, órdenes, agotado, top producto)
- Gráficos de tendencia (Recharts)
- Cálculo automático de media y moda de ingresos

✅ **Gestión de Usuarios**
- CRUD completo
- Roles: Admin, Mesero, Cocina
- Activar/desactivar usuarios

✅ **Gestión de Productos**
- CRUD con upload de imágenes
- Marcar como agotado
- Filtrar por categoría

✅ **Descuentos & Promociones**
- Crear códigos de descuento
- Porcentajes personalizables

✅ **Configuración**
- Nombre y datos del restaurante
- Horarios de operación
- Impuestos y moneda

✅ **Autenticación**
- JWT tokens (480 min)
- Rutas protegidas
- Cierre de sesión automático

---

## 📁 Estructura del Proyecto

```
taosistem_backend/
├── backend/
│   ├── app/
│   │   ├── core/          # Configuración, BD, Redis, JWT
│   │   ├── models/        # Modelos SQLAlchemy
│   │   ├── routers/       # Endpoints API (auth, users, products, metrics)
│   │   ├── schemas/       # Esquemas Pydantic
│   │   └── services/      # Lógica de negocio
│   ├── alembic/           # Migraciones de BD
│   ├── uploads/           # Imágenes de productos
│   ├── main.py            # Punto de entrada
│   ├── requirements.txt   # Dependencias Python
│   ├── Dockerfile         # Imagen Docker
│   ├── .env.development   # Variables (localhost)
│   └── venv/              # Virtual environment
│
├── frontend/
│   ├── src/
│   │   ├── components/    # Navbar, Sidebar, AdminLayout
│   │   ├── pages/         # Login, Dashboard, Usuarios, etc
│   │   ├── services/      # API clients (auth, users, metrics)
│   │   ├── hooks/         # useAuth custom hook
│   │   ├── types/         # TypeScript interfaces
│   │   ├── utils/         # Axios interceptors
│   │   └── styles/        # CSS globals
│   ├── package.json       # Dependencias npm
│   ├── vite.config.ts     # Vite dev server + proxy
│   ├── tsconfig.json      # TypeScript config
│   ├── tailwind.config.js # Tailwind theme
│   └── .env               # API_URL config
│
├── docker-compose.yml     # Orquestación de servicios
├── QUICKSTART.md          # Guía detallada (este archivo)
├── start-dev.ps1          # Script para desarrollo local
├── start-docker.ps1       # Script para Docker
├── setup-db.ps1           # Script para crear BD
└── README.md              # Este archivo
```

---

## 🛠️ Tech Stack Detallado

**Backend:**
- FastAPI 0.110.0 (Framework)
- SQLAlchemy 2.0.29 + asyncpg (ORM + async DB)
- PostgreSQL 15+ (Base de datos)
- Redis (Caché/sesiones)
- Python-Jose + Passlib (Autenticación)
- Pydantic 2.6.4 (Validación de datos)

**Frontend:**
- React 18.2.0 + TypeScript
- Vite 7.3.1 (Build tool)
- React Router DOM (Navegación)
- Axios (HTTP client)
- Recharts (Gráficos)
- Tailwind CSS 3.4.17 (Estilos)
- Lucide React (Iconos)

---

## 📚 Documentación Adicional

- [QUICKSTART.md](QUICKSTART.md) - Guía completa de setup
- [Documentación API](http://localhost:8000/docs) - Swagger UI (en vivo)
- Archivos .env:
  - `backend/.env.development` - Config local
  - `backend/.env.production` - Config producción
  - `frontend/.env` - API endpoint

---

## 🔧 Desarrollo Local (sin Docker)

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

