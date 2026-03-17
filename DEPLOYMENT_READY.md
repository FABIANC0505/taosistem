# ✅ Despliegue en Vercel - Checklist Completo

## 📋 Archivos Creados para el Despliegue

| Archivo | Ubicación | Propósito |
|---------|-----------|----------|
| `vercel.json` | `/frontend/` | Configuración de despliegue en Vercel |
| `VERCEL_DEPLOYMENT.md` | `/frontend/` | Guía detallada del despliegue frontend |
| `BACKEND_DEPLOYMENT.md` | `/` | Guía detallada del despliegue backend |
| `DEPLOYMENT_GUIDE.md` | `/` | Guía completa de ambos despliegues |
| `.gitignore` | `/frontend/` | Actualizado para ignorar variables de entorno |
| `vite.config.ts` | `/frontend/` | Optimizado para producción |

## 🎯 Verificación de Configuración

### Frontend - vercel.json ✅
```json
{
  "buildCommand": "npm run build",
  "outputDirectory": "dist",
  "env": {
    "VITE_API_URL": "@vite_api_url"
  },
  "rewrites": [
    {
      "source": "/(.*)",
      "destination": "/index.html"
    }
  ]
}
```

**Qué significa:**
- `buildCommand`: Vite compilará el código
- `outputDirectory`: Los archivos irán a carpeta `dist`
- `env`: VITE_API_URL se reemplazará con el valor de Vercel
- `rewrites`: SPA routing funciona correctamente (React Router)

### vite.config.ts ✅
```typescript
- Build output: dist
- Source maps disabled (más rápido)
- Code splitting: recharts y vendor por separado
```

### npm run build ✅
```
✓ 2475 modules transformed
✓ CSS optimizado: 4.80 kB (gzip)
✓ JavaScript optimizado: 99.01 kB (gzip) 
✓ Recharts: 115.56 kB (gzip)
✓ Build en 8.92s
```

## 🚀 Pasos Siguientes (Paso a Paso)

### 1️⃣ Preparar GitHub (5 min)

```bash
# Asegúrate que el repositorio está limpio
git status

# Agregar todos los archivos nuevos
git add .

# Commit
git commit -m "Feat: Preparación para despliegue en Vercel - agregar vercel.json, DEPLOYMENT_GUIDE.md, optimizaciones"

# Push
git push origin main
```

### 2️⃣ Desplegar Backend (30-45 min)

**Opción A: Railway (⭐ Recomendado)**

```
1. Ir a https://railway.app
2. Sign in con GitHub
3. New Project > Deploy from GitHub
4. Selecciona tu repositorio
5. Railway detectará requirements.txt
6. Click "Deploy"
7. Agregar PostgreSQL:
   - Resources > + > PostgreSQL
8. Configurar variables:
   DATABASE_URL = [auto]
   SECRET_KEY = [generar con Python]
   ENVIRONMENT = production
   CORS_ORIGINS = https://tu-vercel-domain.vercel.app
9. Copiar URL del servicio: 
   https://tu-app-railway.up.railway.app
```

**Opción B: Render**

```
1. Ir a https://render.com
2. Sign in con GitHub
3. New > Web Service
4. Conectar repositorio
5. Settings:
   - Name: taosistem-backend
   - Environment: Python 3
   - Build: pip install -r requirements.txt
   - Start: python main.py
6. Agregar PostgreSQL
7. Deploy
```

### 3️⃣ Desplegar Frontend (15-20 min)

```
1. Ir a https://vercel.com
2. Sign in con GitHub
3. Import Project
4. Seleccionar tu repositorio
5. Configuración:
   ✅ Framework: Vite (detectado automáticamente)
   ✅ Root Directory: frontend
   ✅ Build: npm run build (detectado)
   ✅ Output: dist (detectado)
6. Environment Variables:
   VITE_API_URL = https://tu-backend-railway.up.railway.app
7. Click "Deploy"
```

### 4️⃣ Validar Despliegue (10 min)

```bash
# Test 1: Frontend carga
curl https://tu-frontend.vercel.app

# Test 2: Backend responde
curl https://tu-backend-railway.up.railway.app/docs

# Test 3: CORS funciona
curl -X OPTIONS https://tu-backend-railway.up.railway.app \
  -H "Origin: https://tu-frontend.vercel.app"

# Test 4: Login funciona
curl -X POST https://tu-backend-railway.up.railway.app/auth/login \
  -H "Content-Type: application/json" \
  -d '{"email":"admin@example.com","password":"password123"}'
```

## 📚 Documentación Disponible

| Documento | Para | Ubicación |
|-----------|------|-----------|
| DEPLOYMENT_GUIDE.md | Guía completa | `/DEPLOYMENT_GUIDE.md` |
| VERCEL_DEPLOYMENT.md | Solo frontend | `/frontend/VERCEL_DEPLOYMENT.md` |
| BACKEND_DEPLOYMENT.md | Solo backend | `/BACKEND_DEPLOYMENT.md` |
| README.md | General del proyecto | `/README.md` |

## 🔒 Variables de Entorno Necesarias

### Backend (Railway Dashboard)
```
DATABASE_URL=postgresql://...  # Auto-generada
SECRET_KEY=generate-con-python
ENVIRONMENT=production
CORS_ORIGINS=https://tu-vercel-url.vercel.app
```

### Frontend (Vercel Dashboard)
```
VITE_API_URL=https://tu-backend-url.com
```

## ⚠️ Casos Especiales

### Si tienes dominio personalizado:

1. **Frontend (Vercel):**
   - Ir a Project Settings > Domains
   - Agregar dominio
   - Configurar DNS

2. **Backend (Railway):**
   - Railway no ofrece dominios personalizados gratuitos
   - Opción: usar un proxy inverso (Cloudflare, etc.)

### Si tienes datos existentes:

1. Exportar de local:
   ```bash
   pg_dump -h localhost -U usuario db > backup.sql
   ```

2. Importar a producción:
   ```bash
   psql -h prod-host -U usuario -d db < backup.sql
   ```

## 🆘 Troubleshooting

| Problema | Causa | Solución |
|----------|-------|----------|
| Build falla en Vercel | Node modules faltando | Verificar package.json |
| "Cannot find dist/" | Bad build command | Usar `npm run build` |
| CORS error | Frontend no en CORS_ORIGINS | Actualizar backend |
| Login falla | SECRET_KEY diferente | Usar mismo SECRET_KEY en prod |
| API no responde | URL incorrecta | Verificar VITE_API_URL |

## ✨ Estado Final Esperado

✅ Frontend en: `https://taosistem-frontend.vercel.app`  
✅ Backend en: `https://api-backend-railway.up.railway.app`  
✅ Base de datos: PostgreSQL en Railway  
✅ SSL/TLS: Automático (https://)  
✅ CI/CD: Automático en cada push

## 📞 Contacto y Soporte

- **Vercel Docs:** https://vercel.com/docs
- **Railway Docs:** https://docs.railway.app
- **FastAPI Docs:** https://fastapi.tiangolo.com
- **React Docs:** https://react.dev

---

**Estado:** ✅ Listo para despliegue  
**Fecha:** Marzo 2026  
**Versión:** 1.3.0
