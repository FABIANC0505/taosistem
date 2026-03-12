# ============================================
# 🚀 START SCRIPT for Windows PowerShell
# ============================================
# Uso: .\start-dev.ps1
# Inicia Backend + Frontend en desarrollo

Write-Host "`n🚀 Iniciando RestauTech (Desarrollo Local)..." -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

# Colores para salida
$infoColor = "Cyan"
$errorColor = "Red"
$successColor = "Green"

# Verificar requisitos
Write-Host "✓ Verificando requisitos..." -ForegroundColor $infoColor

# Check Python
try {
    $pythonVersion = python --version 2>&1
    Write-Host "  ✓ Python: $pythonVersion" -ForegroundColor $successColor
} catch {
    Write-Host "  ✗ Python NO instalado" -ForegroundColor $errorColor
    Write-Host "    Descargar: https://www.python.org/downloads/" -ForegroundColor Yellow
    exit 1
}

# Check Node
try {
    $nodeVersion = node --version
    Write-Host "  ✓ Node.js: $nodeVersion" -ForegroundColor $successColor
} catch {
    Write-Host "  ✗ Node.js NO instalado" -ForegroundColor $errorColor
    Write-Host "    Descargar: https://nodejs.org/" -ForegroundColor Yellow
    exit 1
}

# Check PostgreSQL
Write-Host "`n  Verificando PostgreSQL..." -ForegroundColor $infoColor
try {
    $psqlTest = psql -U postgres -c "SELECT 1" 2>&1 | Out-String
    if ($psqlTest -match "1" -or $psqlTest -eq "") {
        Write-Host "  ✓ PostgreSQL accesible" -ForegroundColor $successColor
    }
} catch {
    Write-Host "  ⚠ PostgreSQL puede no estar corriendo" -ForegroundColor Yellow
    Write-Host "    Inicia el servicio o usa Docker" -ForegroundColor Yellow
}

# Setup Backend
Write-Host "`n📦 Configurando Backend..." -ForegroundColor $infoColor
Push-Location backend

# Copiar .env si no existe
if (-not (Test-Path ".env")) {
    if (Test-Path ".env.development") {
        Copy-Item ".env.development" ".env"
        Write-Host "  ✓ Copiado .env.development → .env" -ForegroundColor $successColor
    }
}

# Crear venv si no existe
if (-not (Test-Path "venv")) {
    Write-Host "  Creando virtual environment..." -ForegroundColor $infoColor
    python -m venv venv
    Write-Host "  ✓ Virtual environment listo" -ForegroundColor $successColor
}

# Activar venv
Write-Host "  Activando virtual environment..." -ForegroundColor $infoColor
& ".\venv\Scripts\Activate.ps1"
Write-Host "  ✓ Virtual environment activado" -ForegroundColor $successColor

# Instalar dependencias
Write-Host "  Instalando dependencias Python..." -ForegroundColor $infoColor
pip install -q -r requirements.txt
Write-Host "  ✓ Dependencias instaladas" -ForegroundColor $successColor

Pop-Location

# Setup Frontend
Write-Host "`n📦 Configurando Frontend..." -ForegroundColor $infoColor
Push-Location frontend

if (-not (Test-Path "node_modules")) {
    Write-Host "  Instalando dependencias npm..." -ForegroundColor $infoColor
    npm install -q
    Write-Host "  ✓ Dependencias npm instaladas" -ForegroundColor $successColor
}

Pop-Location

# Iniciar servicios en paralelo
Write-Host "`n🔥 Iniciando servicios...`n" -ForegroundColor $infoColor

# Backend en nueva ventana
Write-Host "Abriendo Backend en nueva ventana..." -ForegroundColor $infoColor
$backendStart = {
    cd "backend"
    . ".\venv\Scripts\Activate.ps1"
    Write-Host "`n✓ Backend iniciando en puerto 8000..." -ForegroundColor Green
    Write-Host "  📍 http://localhost:8000" -ForegroundColor Cyan
    Write-Host "  📚 Docs: http://localhost:8000/docs`n" -ForegroundColor Cyan
    uvicorn main:app --reload --host 0.0.0.0 --port 8000
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $backendStart

# Esperar a que backend esté listo
Start-Sleep -Seconds 3

# Frontend en nueva ventana
Write-Host "Abriendo Frontend en nueva ventana..." -ForegroundColor $infoColor
$frontendStart = {
    cd "frontend"
    Write-Host "`n✓ Frontend iniciando en puerto 3000..." -ForegroundColor Green
    Write-Host "  📍 http://localhost:3000" -ForegroundColor Cyan
    Write-Host "  🔐 Login: admin@restaurante.com / admin123`n" -ForegroundColor Cyan
    npm run dev
}
Start-Process powershell -ArgumentList "-NoExit", "-Command", $frontendStart

# Mostrar resumen
Write-Host "`n" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✓ RestauTech iniciado en MODO DESARROLLO" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "📍 Acceso:` " -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   API Docs:    http://localhost:8000/docs`n" -ForegroundColor Yellow

Write-Host "🔐 Credenciales de prueba:" -ForegroundColor Cyan
Write-Host "   Email:    admin@restaurante.com" -ForegroundColor Yellow
Write-Host "   Password: admin123`n" -ForegroundColor Yellow

Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "   2. Inicia sesión con las credenciales arriba" -ForegroundColor White
Write-Host "   3. Explora el dashboard y las funciones`n" -ForegroundColor White

Write-Host "⚠️  Para detener: Cierra ambas ventanas de PowerShell o presiona Ctrl+C`n" -ForegroundColor Yellow
