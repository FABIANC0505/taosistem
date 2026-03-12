# 🚀 RESTAURECH - COMIENZA AQUÍ

**Bienvenido al panel administrativo de RestauTech.**
Este archivo contiene los pasos más rápidos para poner todo corriendo.

---

## ⚡ Opción A: Docker (Recomendado - 1 Comando)

**Requisito:** Docker Desktop instalado y ejecutándose

```powershell
# Desde la carpeta raíz del proyecto
.\start-docker.ps1
```

✅ **Espera 30 segundos**, luego:
- **Frontend:** http://localhost:3000
- **Backend:** http://localhost:8000/docs
- **Email:** admin@restaurante.com | **Password:** admin123

---

## 💻 Opción B: Desarrollo Local (Sin Docker)

**Requisitos:**
- Python 3.10+
- Node.js 18+
- PostgreSQL 15+ (o libreget installarlo con el script)

### Paso 1: Crear Base de Datos (primera vez)

```powershell
.\setup-db.ps1
```

### Paso 2: Iniciar Servicios

```powershell
.\start-dev.ps1
```

✅ **Espera 10 segundos**, se abren 2 ventanas:
- Backend (http://localhost:8000)
- Frontend (http://localhost:3000)

---

## 🔐 Primera vez: Crear un Usuario Admin

### Opción A: Vía Interfaz Gráfica ✨

1. Abre http://localhost:3000/login
2. Click en "¿No tienes cuenta? Regístrate"
3. Completa el formulario
4. Presiona "Registrarse"

### Opción B: Vía API (Swagger UI)

1. Abre http://localhost:8000/docs
2. Click en **POST /auth/register**
3. Click en "Try it out"
4. Ingresa:
```json
{
  "nombre": "Admin Usuario",
  "email": "admin@restaurante.com",
  "password": "admin123"
}
```
5. Click en "Execute"

---

## ✅ Verificar que Todo Funciona

| Recurso | URL | Estado |
|---------|-----|--------|
| Dashboard | http://localhost:3000/admin | ✅ Deberías ver KPIs |
| API Docs | http://localhost:8000/docs | ✅ Swagger UI completa |
| API Health | http://localhost:8000/health | ✅ `{"status":"ok"}` |

---

## 📚 Documentación Completa

Si necesitas más información:
- **QUICKSTART.md** - Guía detallada de setup
- **TESTING_GUIDE.md** - Cómo probar cada sección
- **README.md** - Descripción general del proyecto

---

## 🆘 Si Algo Falla

### "No puedo ver el frontend"
```powershell
cd frontend
npm install
npm run dev
```

### "Error de conexión a Base de Datos"
```powershell
# Verificar que PostgreSQL está corriendo (Windows)
Get-Service PostgreSQL* | Start-Service

# O simplemente usa Docker: .\start-docker.ps1
```

### "Puerto 8000 ya está en uso"
```powershell
netstat -ano | findstr :8000
taskkill /PID <PID> /F
```

---

## 🎯 Próximos Pasos

1. **Explora el Dashboard** - Ve los gráficos y KPIs
2. **Crea Productos** - Sube imágenes y precios
3. **Gestiona Usuarios** - Crea más roles (Mesero, Cocina)
4. **Configura el Restaurante** - Nombre, horarios, impuestos

---

**¿Preguntas?** Todos los endpoints están documentados en http://localhost:8000/docs

¡Que disfrutes! 🍕

---

*Proyecto: RestauTech v1.0.0*  
*Última actualización: Marzo 2026*

# Verifica Python
echo "✓ Verificando Python..."
python --version

# Inicia Backend
echo "\n📦 Iniciando Backend..."
echo "Navegando a backend/"
cd backend

# Verifica que poetry o pip está instalado
if command -v poetry &> /dev/null; then
    echo "Usando Poetry"
    poetry install
    poetry run uvicorn main:app --reload --host 0.0.0.0 --port 8000
else
    echo "Usando pip"
    pip install -r requirements.txt
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
fi &

sleep 2

# Inicia Frontend
echo "\n🎨 Iniciando Frontend..."
cd ../frontend
npm run dev

echo "\n✅ ¡RestauTech está listo!"
echo "📱 Frontend: http://localhost:3000"
echo "🔌 Backend: http://localhost:8000"
echo "📚 Docs API: http://localhost:8000/docs"
