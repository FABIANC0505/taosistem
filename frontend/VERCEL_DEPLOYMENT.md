# Guía de Despliegue en Vercel

## 📋 Requisitos Previos

- Cuenta en [Vercel](https://vercel.com)
- Repositorio Git (GitHub, GitLab o Bitbucket) con el código
- Backend desplegado en un servidor (Railway, Render, Heroku, etc.)

## 🚀 Pasos para Desplegar el Frontend

### 1. Preparar el Repositorio

Asegúrate de que el repositorio tenga la siguiente estructura:

```
taosistem_backend/
├── frontend/          # El frontend se desplegará desde aquí
│   ├── src/
│   ├── public/
│   ├── package.json
│   ├── vite.config.ts
│   ├── tsconfig.json
│   └── vercel.json    # ✅ Archivo de configuración de Vercel
├── backend/           # Backend en otro servidor
└── docker-compose.yml
```

### 2. Conectar Vercel con tu Repositorio

1. Ve a [Vercel Dashboard](https://vercel.com/dashboard)
2. Haz clic en "New Project"
3. Selecciona tu repositorio Git
4. Configura lo siguiente:
   - **Project Name:** `taosistem-frontend` (o el que prefieras)
   - **Framework Preset:** Vite
   - **Root Directory:** `frontend` (muy importante)
   - **Build Command:** `npm run build` (Vercel lo detectará automáticamente)
   - **Output Directory:** `dist` (Vercel lo detectará automáticamente)

### 3. Configurar Variables de Entorno

En Vercel Dashboard, ve a **Project Settings > Environment Variables** y agrega:

```
VITE_API_URL = https://tu-backend-url.com
```

Por ejemplo, si tu backend está en Railway:
```
VITE_API_URL = https://tu-app-railway.up.railway.app
```

### 4. Desplegar

Después de hacer push a tu rama principal (main/master):
- Vercel automáticamente detectará los cambios
- Iniciará el build
- Desplegará en una URL como `https://taosistem-frontend.vercel.app`

## 📱 Configuración de Backend

El frontend está configurado para conectar con el backend a través de la variable `VITE_API_URL`.

### Endpoints Disponibles desde el Frontend

El frontend puede acceder a estos endpoints del backend:

```
GET  /users              - Listar usuarios
POST /users              - Crear usuario
GET  /users/{id}         - Obtener usuario
PUT  /users/{id}         - Actualizar usuario
DELETE /users/{id}       - Eliminar usuario

GET  /products           - Listar productos
POST /products           - Crear producto
GET  /products/{id}      - Obtener producto
PUT  /products/{id}      - Actualizar producto
DELETE /products/{id}    - Eliminar producto

GET  /orders             - Listar órdenes
POST /orders             - Crear orden
GET  /orders/{id}        - Obtener orden
PUT  /orders/{id}        - Actualizar orden

GET  /metrics            - Obtener métricas de dashboard
GET  /metrics/dispatched-history - Obtener historial de pedidos despachados

GET  /settings/history-retention      - Obtener retención del historial
PUT  /settings/history-retention      - Actualizar retención del historial

POST /auth/login         - Login de usuario
POST /auth/logout        - Logout de usuario
```

## 🔒 CORS y Seguridad

Verifica que tu backend backend tenga CORS configurado correctamente para aceptar solicitudes desde:

```
https://tu-dominio-vercel.vercel.app
https://*.vercel.app (para previews)
```

En tu `backend/main.py`, debe estar algo como:

```python
from fastapi.middleware.cors import CORSMiddleware

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "https://taosistem-frontend.vercel.app",
        # Agrega aquí tu dominio personalizado si lo deseas
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)
```

## 🌍 Dominio Personalizado (Opcional)

1. Ve a **Project Settings > Domains**
2. Haz clic en "Add"
3. Ingresa tu dominio (ej: `app.tudominio.com`)
4. Sigue las instrucciones para configurar los registros DNS

## 📊 Monitoreo y Logs

En Vercel Dashboard:
- **Analytics:** Ver tráfico y rendimiento
- **Deployments:** Ver historial de despliegues
- **Functions:** Ver logs de funciones (si las usas)
- **Settings:** Configurar webhooks, variables, dominios

## 🐛 Troubleshooting

### Error: "Cannot find module 'vite'"
**Solución:** Vercel detectará el root directory automáticamente, pero asegúrate de que `package.json` esté en la carpeta `/frontend`.

### Error: "VITE_API_URL is undefined"
**Solución:** La variable de entorno debe estar configurada en Vercel Dashboard bajo **Environment Variables**.

### Error CORS
**Solución:** Asegúrate de que el backend esté configurado con los orígenes correctos en CORSMiddleware.

### El frontend se ve mal o los estilos no cargan
**Solución:** Verifica que Tailwind CSS esté bien compilado. Ejecuta `npm run build` localmente primero.

## 📦 Detalles Técnicos

- **Framework:** React 19 + TypeScript
- **Build Tool:** Vite
- **Styling:** Tailwind CSS
- **HTTP Client:** Axios
- **Charting:** Recharts + Chart.js
- **UI Components:** Lucide React Icons
- **Routing:** React Router v7

## ✅ Checklist Pre-Despliegue

- [ ] Backend desplegado y accesible
- [ ] Variable `VITE_API_URL` configurada en Vercel
- [ ] CORS habilitado en el backend
- [ ] `vercel.json` presente en `/frontend`
- [ ] `npm run build` se ejecuta correctamente localmente
- [ ] Todas las variables de entorno removidas de archivos (usar solo Vercel Dashboard)
- [ ] Repositorio Git sincronizado

## 🎯 Próximos Pasos

1. **Desplegar Backend** (si no lo has hecho):
   - Usa Railway, Render, Heroku, AWS, GCP, etc.
   - Variables de entorno importante:
     ```
     DATABASE_URL=postgresql://user:pass@host/dbname
     REDIS_URL=redis://host:port
     SECRET_KEY=tu-secreto-jwt
     ```

2. **Actualizar VITE_API_URL** en Vercel con la URL de tu backend

3. **Configurar dominio personalizado** (opcional):
   - Usar tu propio dominio en lugar de vercel.app

4. **Monitorear despliegues** y hacer curl a los endpoints para validar

## 📞 Soporte

Para más información:
- Documentación oficial: https://vercel.com/docs
- Estado de Vercel: https://www.vercel-status.com
- Comunidad: https://github.com/vercel/next.js/discussions
