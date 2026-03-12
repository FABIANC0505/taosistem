# 🚀 Guía de Arranque Rápido - RestauTech

## Opción 1: Con Docker (Recomendado)

### Requisitos
- Docker Desktop instalado y ejecutándose
- Windows PowerShell o WSL2

### Pasos

```powershell
cd c:\PRPDETO\taosistem_backend

# Levantar todos los servicios (DB, Redis, Backend)
docker-compose up -d

# Esperar 10 segundos a que PostgreSQL esté listo
Start-Sleep -Seconds 10

# Verificar que todo está corriendo
docker-compose ps

# Ver logs del backend
docker-compose logs backend
```

**Acceso:**
- Frontend: http://localhost:3000
- Backend: http://localhost:8000
- API Docs: http://localhost:8000/docs
- pgAdmin (opcional): http://localhost:5050

---

## Opción 2: Local (Sin Docker)

### Requisitos
- PostgreSQL 15+ instalado localmente
- Python 3.10+
- Node.js 18+

### Paso 1: Verificar PostgreSQL
```powershell
# En PowerShell
psql -U postgres

# Crear usuario si no existe
CREATE USER restautech_user WITH PASSWORD 'restautech_pass_2026';
CREATE DATABASE restautech_db OWNER restautech_user;

# Salir
\q
```

### Paso 2: Backend
```powershell
cd c:\PRPDETO\taosistem_backend\backend

# Copiar .env
cp ..\.env .env

# Editar .env (cambiar HOST a localhost)
# POSTGRES_HOST=localhost
# POSTGRES_PORT=5432

# Instalar dependencias
pip install -r requirements.txt

# Crear tabla (o usar alembic)
# python -c "from app.core.database import init_db; import asyncio; asyncio.run(init_db())"

# Levantar backend
uvicorn main:app --reload --host 0.0.0.0 --port 8000
```

El backend estará en: **http://localhost:8000**

### Paso 3: Frontend (nueva terminal)
```powershell
cd c:\PRPDETO\taosistem_backend\frontend

npm run dev
```

El frontend estará en: **http://localhost:3000**

---

## Crear Usuario Admin de Prueba

### Vía API (POST /auth/register)

**URL:** `http://localhost:8000/docs`

1. Abre Swagger UI
2. Busca `POST /auth/register`
3. Haz click en "Try it out"
4. Ingresa:
```json
{
  "nombre": "Admin Usuario",
  "email": "admin@restaurante.com",
  "password": "admin123"
}
```
5. Click en "Execute"

### O desde cURL
```powershell
$body = @{
  nombre = "Admin Usuario"
  email = "admin@restaurante.com"
  password = "admin123"
} | ConvertTo-Json

Invoke-WebRequest -Uri "http://localhost:8000/auth/register" `
  -Method POST `
  -Headers @{"Content-Type"="application/json"} `
  -Body $body
```

---

## Prueba del Sistema

### 1. Login
- URL: http://localhost:3000/login
- Email: `admin@restaurante.com`
- Password: `admin123`

### 2. Dashboard
- Deberías ver 4 KPI cards
- Gráficos de tendencia y top productos
- Media y Moda de ingresos

### 3. Prueba las páginas principales
- **/admin/usuarios** - Crear/editar usuarios
- **/admin/productos** - Crear productos con imágenes
- **/admin/descuentos** - Gestionar promociones
- **/admin/configuracion** - Ajustes del restaurante

---

## Verificar que Todo Funciona

```powershell
# 1. Backend API
curl http://localhost:8000/health

# Deberías ver:
# {"status":"ok","app":"RestauTech"}

# 2. Frontend
curl http://localhost:3000

# Deberías ver HTML del login
```

---

## Troubleshooting

### Error: Conexión a PostgreSQL rechazada
```
Error: could not connect to server: No such file or directory
```
**Solución:** Verificar que PostgreSQL está corriendo
```powershell
# Windows
Get-Service PostgreSQL-x64-15

# Si no está, iniciarlo
Start-Service PostgreSQL-x64-15
```

### Error: Puerto 8000 en uso
```
Address already in use
```
**Solución:**
```powershell
# Encontrar proceso usando puerto
netstat -ano | findstr :8000

# Matar proceso (reemplazar PID)
taskkill /PID <PID> /F

# O usar puerto diferente
uvicorn main:app --reload --port 8001
```

### Error: CORS / "No se puede conectar a la API"
```
Access to XMLHttpRequest has been blocked by CORS policy
```
**Solución:** Asegurar que en `.env` está:
```
FRONTEND_URL=http://localhost:3000
```

### Frontend en blanco o cargas lentamente
```powershell
# Limpiar caché
rm -r frontend\dist
npm run build
npm run dev
```

---

## Comandos Útiles

```powershell
# Backend - Ver logs
tail -f ../backend.log

# Frontend - Compilar optimizado
npm run build

# Limpiar todo
docker-compose down -v  # Si usas Docker
npm cache clean         # Si tienes problemas con npm
```

---

**Nota:** En la primera ejecución, puede tomar +1 minuto en inicializar tablas si usas Alembic. Las migraciones corren automáticamente en `app.core.database:init_db()`.

Generado: 11 de Marzo, 2026
