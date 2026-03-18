# 🚀 Deployment Local SIN Docker - Guía Rápida

## ❗ REQUISITO PREVIO: PostgreSQL

Para ejecutar este proyecto localmente sin Docker, necesitas **PostgreSQL 15+** instalado.

### Opción A: Instalar PostgreSQL en Windows (Recomendado)

1. Descarga PostgreSQL: https://www.postgresql.org/download/windows/
2. Durante la instalación:
   - Choose default port: **5432**
   - Set postgres password
   - Install pgAdmin (opcional pero útil)
3. Verifica instalación:
   ```powershell
   psql --version
   ```

### Opción B: Usar WSL2 + Docker (Alternativa)

Si tienes WSL2 disponible pero Docker Desktop no está corriendo en Windows:
```powershell
wsl -d Ubuntu
docker run -d --name postgres \
  -e POSTGRES_PASSWORD=restautech_pass_2026 \
  -p 5432:5432 \
  postgres:15
```

---

## 🏃 Arrancar el Sistema Local

### Paso 1: Crear Base de Datos

```powershell
# Desde la raíz del proyecto
.\setup-db.ps1
```

✅ Esto crea:
- Usuario: `restautech_user`
- Contraseña: `restautech_pass_2026`
- Base de datos: `restautech_db`

### Paso 2: Crear Usuarios de Prueba

```powershell
cd backend
c:/PRPDETO/taosistem_backend/.venv/Scripts/python.exe seed_data.py
```

✅ Usuarios creados:
- **Admin**: admin@restaurante.com / admin123
- **Mesero**: mesero@restaurante.com / mesero123
- **Cocina**: cocina@restaurante.com / cocina123

### Paso 3: Arrancar Backend

En una terminal **PowerShell nueva**:
```powershell
cd backend
c:/PRPDETO/taosistem_backend/.venv/Scripts/python.exe -m uvicorn main:app --reload --port 8000
```

✅ Backend corriendo en http://localhost:8000

### Paso 4: Arrancar Frontend

En otra terminal **PowerShell nueva**:
```powershell
cd frontend
npm install  # Si es primera vez
npm run dev
```

✅ Frontend corriendo en http://localhost:3000

---

## 🔨 Pruebas de Inyección de Pedidos

Una vez que ambos servicios están corriendo:

```powershell
.\test_order_injection.ps1
```

Este script:
1. ✅ Verifica backend health
2. ✅ Autentica con credenciales existentes
3. ✅ Inyecta 3 pedidos de prueba
4. ✅ Valida que aparezcan en panel de cocina
5. ✅ Valida que aparezcan en dashboard admin
6. ✅ Simula transiciones de estado

---

## 📱 Acceso a Paneles

### Login:
- URL: http://localhost:3000/login

### Roles & URLs:

| Rol    | Email                    | Password  | URL                         |
|--------|--------------------------|-----------|---------------------------|
| Admin  | admin@restaurante.com    | admin123  | http://localhost:3000/admin |
| Mesero | mesero@restaurante.com   | mesero123 | http://localhost:3000/mesero/pedidos |
| Cocina | cocina@restaurante.com   | cocina123 | http://localhost:3000/cocina/pedidos |

---

## 🔄 Sincronización en Tiempo Real

Los paneles se actualizan automáticamente cada 10 segundos:

1. **Mesero crea pedido** → POST /orders
2. **Cocina ve en 10s** → GET /orders (auto-refresh)
3. **Admin ve en 10s** → GET /metrics/dashboard (auto-refresh)
4. **Estados se sincronizan** → PUT /orders/{id}/status

---

## 🛠️ Troubleshooting

### "Connection refused" en backend

```
Error: Errno 10061 - PostgreSQL no está corriendo
```

**Solución**:
```powershell
# Verificar servicio PostgreSQL
Get-Service | Where-Object {$_.Name -like "*postgres*"}

# Si no existe, reinstala PostgreSQL
# O usa WSL2: wsl docker run postgresql...
```

### "Module not found" en backend

```
Error: ModuleNotFoundError
```

**Solución**:
```powershell
cd backend
c:/PRPDETO/taosistem_backend/.venv/Scripts/python.exe -m pip install -r requirements.txt
```

### Frontend no carga

```powershell
cd frontend
npm install
npm run dev
```

### Ports ya en uso

```powershell
# Port 8000 ocupado
netstat -ano | findstr :8000
taskkill /PID <PID> /F

# Port 3000 ocupado
netstat -ano | findstr :3000
taskkill /PID <PID> /F
```

---

## 📊 Flujo Completo de Prueba

1. **Login como Mesero**
   - http://localhost:3000/login
   - Email: mesero@restaurante.com
   - Password: mesero123

2. **Crear Pedido**
   - Click "Nuevo Pedido"
   - Selecciona Mesa (1-12)
   - Agrega productos del grid
   - Click "Guardar Pedido"

3. **Cambiar Tab → Login como Cocina**
   - http://localhost:3000/login
   - Email: cocina@restaurante.com
   - Password: cocina123
   - Abre http://localhost:3000/cocina/pedidos
   - ✅ **Deberías ver el pedido en ~10 segundos**

4. **Otra Tab → Dashboard Admin**
   - http://localhost:3000/login
   - Email: admin@restaurante.com
   - Password: admin123
   - Abre http://localhost:3000/admin
   - ✅ **Deberías ver métricas actualizadas**

5. **Cocina Marca como Entregado**
   - En panel cocina, click "Marcar como entregado"
   - Vuelve a Dashboard admin
   - ✅ **Métricas se actualizan en 10s (ingresos cambian)**

---

## 📝 Notas Importantes

- ✅ **NO crear nuevos usuarios**: Usa credenciales existentes
- ✅ **Auto-refresh**: Cocina y Admin se actualizan cada 10s
- ✅ **Sincronización**: Los pedidos inyectados aparecen en ambos paneles
- ✅ **Sin WebSocket**: Usa polling cada 10s (eficiente y simple)

---

## 🆘 Soporte

Si algo no funciona:
1. Verifica Backend health: http://localhost:8000/health
2. Revisa logs de backend en terminal
3. Abre Developer Tools (F12) en Frontend
4. Consulta http://localhost:8000/docs para API docs

