# 🚀 Guía Completa de Despliegue - TaoSistem

Esta guía te llevará paso a paso para desplegar tanto el frontend como el backend en producción.

## 📚 Documentos Disponibles

1. **VERCEL_DEPLOYMENT.md** - Despliegue del frontend en Vercel
2. **BACKEND_DEPLOYMENT.md** - Despliegue del backend en Railway/Render/Heroku
3. **Este archivo** - Coordinación completa del despliegue

## 🎯 Plan de Acción (2-3 horas)

### Fase 1: Preparación (30 min)

- [ ] Crear cuenta en Vercel (free tier)
- [ ] Crear cuenta en Railway o Render (con tarjeta de crédito)
- [ ] Subir código a GitHub (público o privado)
- [ ] Generar `SECRET_KEY` con: `python -c "import secrets; print(secrets.token_urlsafe(32))"`

### Fase 2: Backend (1 hora)

#### Opción A: Railway (Recomendado ⭐)

1. Ir a [railway.app](https://railway.app)
2. Conectar con GitHub
3. Nuevo proyecto desde repositorio
4. Railway detectará `requirements.txt` y `main.py`
5. Agregar PostgreSQL (Database)
6. Configurar variables de entorno:
   ```
   DATABASE_URL = [Auto-generado por Railway]
   SECRET_KEY = [Generado en Preparación]
   ENVIRONMENT = production
   REDIS_URL = [Opcional, Railway puede agregarlo]
   ```
7. Railway desplegará automáticamente
8. Copiar URL: `https://tu-app-railway.up.railway.app`

#### Opción B: Render

1. Ir a [render.com](https://render.com)
2. Crear Web Service desde GitHub
3. Settings:
   ```
   Name: taosistem-backend
   Environment: Python 3
   Build Command: pip install -r requirements.txt
   Start Command: python main.py
   ```
4. Agregar PostgreSQL Service
5. Copiar URL

### Fase 3: Frontend (30 min)

1. Ir a [vercel.com](https://vercel.com)
2. Nuevo proyecto desde GitHub
3. Seleccionar repositorio
4. Configuración:
   ```
   Framework: Vite
   Root Directory: frontend
   Build Command: npm run build (detectado automáticamente)
   Output: dist (detectado automáticamente)
   ```
5. Agregar variable de entorno:
   ```
   VITE_API_URL = https://tu-backend-url.com
   ```
6. Desplegar
7. Copiar URL: `https://taosistem-frontend.vercel.app`

### Fase 4: Validación (20 min)

1. Verificar que el frontend carga
2. Intentar login
3. Navegar por dashboards
4. Probar creación de usuarios
5. Verificar que se guarden órdenes

## 📊 Arquitectura Final

```
┌──────────────────────────────────────────┐
│         Usuario en Internet              │
└──────────────┬─────────────────────────┘
               │
         ┌─────▼─────┐
         │   HTTPS   │
         └─────┬─────┘
               │
    ┌──────────▼──────────────┐
    │  Frontend (Vercel)      │
    │ taosistem.vercel.app    │
    │ - React + TypeScript    │
    │ - Vite                  │
    │ - Tailwind CSS          │
    └──────────┬──────────────┘
               │
         ┌─────▼─────────────────────┐
         │  API Requests             │
         │ VITE_API_URL Configured   │
         └─────┬─────────────────────┘
               │
    ┌──────────▼──────────────────┐
    │  Backend (Railway/Render)   │
    │ api.railway.app             │
    │ - FastAPI                   │
    │ - Async SQLAlchemy          │
    │ - JWT Auth                  │
    └──────────┬──────────────────┘
               │
         ┌─────▼──────────────┐
         │   PostgreSQL       │
         │   Database         │
         │   (Railway/Render) │
         └────────────────────┘
```

## 🔑 Variables de Entorno Necesarias

### Backend (Railway/Render/Heroku)

```bash
DATABASE_URL=postgresql://user:pass@host/db
SECRET_KEY=tu-clave-secreta-de-32-caracteres
ENVIRONMENT=production
CORS_ORIGINS=https://tu-frontend-vercel.vercel.app
```

### Frontend (Vercel)

```bash
VITE_API_URL=https://tu-backend-url.com
```

## 🧪 Validación Pre-Despliegue

En tu máquina local:

```bash
# Backend
cd backend
python main.py
# Debe iniciar en puerto 8000

# Test
curl http://localhost:8000/docs

# Frontend
cd frontend
npm run build
# Debe generar carpeta `dist` sin errores
```

## 📱 Después del Despliegue

### 1. Crear Usuarios Iniciales

```bash
curl -X POST https://tu-backend.com/users \
  -H "Content-Type: application/json" \
  -H "Authorization: Bearer TOKEN" \
  -d '{
    "email": "admin@tudominio.com",
    "password": "contraseña-segura",
    "role": "admin"
  }'
```

### 2. Cargar Productos

Usar el panel de administración para agregar productos

### 3. Cambiar Credenciales Predeterminadas

```
Admin: admin@example.com / password123
Pasarela: pasarela@example.com / password123
Cocina: cocina@example.com / password123
```

## 🔒 Configuración CORS en Backend

Editar `backend/main.py`:

```python
from fastapi.middleware.cors import CORSMiddleware

CORS_ORIGINS = [
    "http://localhost:3000",  # Desarrollo local
    "https://taosistem-frontend.vercel.app",  # Vercel
    "https://tudominio.com",  # Dominio personalizado (si lo tienes)
]

app.add_middleware(
    CORSMiddleware,
    allow_origins=CORS_ORIGINS,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🌍 Dominio Personalizado (Opcional)

### Con Dominio Personalizado

1. Comprar dominio en GoDaddy, Namecheap, etc.
2. **Vercel:**
   - Settings > Domains
   - Agregar dominio
   - Apuntar DNS a Vercel (CNAME/A records)
3. **Railway:**
   - Railway no ofrece subdominios automáticos
   - Usar CNAME dinámico o proxy inverso

## 📊 Monitoreo Post-Despliegue

### Railway Dashboard
- Ver logs en tiempo real
- Monitorar consumo de recursos
- Ver métricas de base de datos

### Vercel Analytics
- Ver tráfico de usuarios
- Core Web Vitals
- Despliegues recientes

## 🚨 Troubleshooting Común

| Problema | Solución |
|----------|----------|
| "Cannot connect to API" | Verificar VITE_API_URL en Vercel |
| CORS error 403 | Agregar frontend URL a CORS_ORIGINS en backend |
| Database connection failed | Verificar DATABASE_URL, IP whitelist |
| Login no funciona | Verificar SECRET_KEY, credenciales en DB |
| Estilos rotos | Limpiar caché, verificar Tailwind build |

## 📞 Comandos Útiles

```bash
# Generar clave segura
python -c "import secrets; print(secrets.token_urlsafe(32))"

# Ver variables en Railway
railway env

# Ver logs
railway logs

# Deploy manual a Railway
railway up

# Build local para probar
npm run build
npm run preview
```

## ✅ Checklist Final

- [ ] Backend deploado en Railway/Render/Heroku
- [ ] Frontend deployado en Vercel
- [ ] VITE_API_URL configurada en Vercel
- [ ] CORS habilitado en backend para frontend
- [ ] Base de datos migrada con datos iniciales
- [ ] Login funciona correctamente
- [ ] Todos los dashboards cargan
- [ ] API endpoints responden correctamente
- [ ] Usuarios pueden crear órdenes
- [ ] Historial de pedidos se registra

## 🎉 ¡Ya Está Listo!

Tu aplicación está desplegada en producción:

- **Frontend:** https://taosistem-frontend.vercel.app
- **Backend:** https://tu-backend-railway.up.railway.app
- **Database:** PostgreSQL en Railway

---

## 📚 Documentación Adicional

- [VERCEL_DEPLOYMENT.md](./frontend/VERCEL_DEPLOYMENT.md) - Detalles específicos de Vercel
- [BACKEND_DEPLOYMENT.md](./BACKEND_DEPLOYMENT.md) - Detalles específicos de Railway/Render
- [README.md](./README.md) - Documentación general del proyecto
- [TESTING_GUIDE.md](./TESTING_GUIDE.md) - Guía de testing de endpoints

---

**Última actualización:** Marzo 2026
**Versión:** 1.3.0
