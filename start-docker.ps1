# ============================================
# 🐳 START DOCKER SCRIPT for Windows PowerShell
# ============================================
# Uso: .\start-docker.ps1
# Inicia todos los servicios en Docker

Write-Host "`n🐳 Iniciando RestauTech con Docker..." -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$infoColor = "Cyan"
$errorColor = "Red"
$successColor = "Green"

# Verificar Docker
Write-Host "✓ Verificando Docker..." -ForegroundColor $infoColor
try {
    $dockerVersion = docker --version
    Write-Host "  ✓ $dockerVersion" -ForegroundColor $successColor
} catch {
    Write-Host "  ✗ Docker NO está instalado o no se ejecuta" -ForegroundColor $errorColor
    Write-Host "    Descargar: https://www.docker.com/products/docker-desktop" -ForegroundColor Yellow
    Write-Host "    Abre Docker Desktop e intenta nuevamente" -ForegroundColor Yellow
    exit 1
}

# Verificar Docker Compose
try {
    $composeVersion = docker-compose --version
    Write-Host "  ✓ $composeVersion" -ForegroundColor $successColor
} catch {
    Write-Host "  ✗ Docker Compose no disponible" -ForegroundColor $errorColor
    exit 1
}

# Detener contenedores anteriores
Write-Host "`n⏹️  Deteniendo contenedores anteriores (si existen)..." -ForegroundColor $infoColor
docker-compose down -q 2>$null

# Construir y levantar
Write-Host "`n🔨 Construyendo y levantando servicios..." -ForegroundColor $infoColor
docker-compose up -d

# Esperar a que PostgreSQL esté listo
Write-Host "`n⏳ Esperando a PostgreSQL (10 segundos)..." -ForegroundColor $infoColor
Start-Sleep -Seconds 10

# Verificar servicios
Write-Host "`n✓ Verificando estado:" -ForegroundColor $infoColor
docker-compose ps

# Verificar que el backend está listo
Write-Host "`n✓ Esperando a que Backend responda..." -ForegroundColor $infoColor
$attempt = 0
while ($attempt -lt 30) {
    try {
        $health = Invoke-WebRequest -Uri "http://localhost:8000/health" -UseBasicParsing -TimeoutSec 2 -ErrorAction Stop
        if ($health.StatusCode -eq 200) {
            Write-Host "  ✓ Backend listo!" -ForegroundColor $successColor
            break
        }
    } catch {
        $attempt++
        if ($attempt % 5 -eq 0) {
            Write-Host "  Intento $attempt/30..." -ForegroundColor Yellow
        }
        Start-Sleep -Seconds 1
    }
}

# Mostrar resumen
Write-Host "`n" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✓ RestauTech iniciado en DOCKER" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "📍 Acceso:" -ForegroundColor Cyan
Write-Host "   Frontend:    http://localhost:3000" -ForegroundColor Yellow
Write-Host "   Backend API: http://localhost:8000" -ForegroundColor Yellow
Write-Host "   API Docs:    http://localhost:8000/docs" -ForegroundColor Yellow
Write-Host "   pgAdmin:     http://localhost:5050 (opcional)`n" -ForegroundColor Yellow

Write-Host "🔐 Credenciales de prueba:" -ForegroundColor Cyan
Write-Host "   Email:    admin@restaurante.com" -ForegroundColor Yellow
Write-Host "   Password: admin123`n" -ForegroundColor Yellow

Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Abre http://localhost:3000 en tu navegador" -ForegroundColor White
Write-Host "   2. Inicia sesión con las credenciales arriba" -ForegroundColor White
Write-Host "   3. Explora el dashboard y las funciones`n" -ForegroundColor White

Write-Host "📊 Ver logs:" -ForegroundColor Cyan
Write-Host "   Todo:     docker-compose logs -f" -ForegroundColor White
Write-Host "   Backend:  docker-compose logs -f backend" -ForegroundColor White
Write-Host "   Frontend: docker-compose logs -f frontend`n" -ForegroundColor White

Write-Host "🛑 Detener servicios:" -ForegroundColor Cyan
Write-Host "   docker-compose down" -ForegroundColor White
Write-Host "   docker-compose down -v  (incluye volúmenes)`n" -ForegroundColor White

Write-Host "Presiona Ctrl+C en esta ventana para ver logs en tiempo real..." -ForegroundColor Yellow
Write-Host "O déjala abierta y abre otra terminal.`n" -ForegroundColor Yellow

# Mostrar logs
docker-compose logs -f
