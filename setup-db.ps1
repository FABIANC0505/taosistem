# ============================================
# 🔧 SETUP SCRIPT for Windows PowerShell
# ============================================
# Uso: .\setup-db.ps1
# Crea base de datos y usuario PostgreSQL

Write-Host "`n🔧 Setup de Base de Datos PostgreSQL..." -ForegroundColor Cyan
Write-Host "================================================`n" -ForegroundColor Cyan

$infoColor = "Cyan"
$errorColor = "Red"
$successColor = "Green"
$warningColor = "Yellow"

# Verificar PostgreSQL
Write-Host "✓ Verificando PostgreSQL..." -ForegroundColor $infoColor
try {
    $version = psql --version
    Write-Host "  ✓ $version" -ForegroundColor $successColor
} catch {
    Write-Host "  ✗ PostgreSQL NO está instalado" -ForegroundColor $errorColor
    Write-Host "`n  Opciones:" -ForegroundColor $warningColor
    Write-Host "    1. Descargar: https://www.postgresql.org/download/windows/" -ForegroundColor White
    Write-Host "    2. O usar Docker: .\start-docker.ps1`n" -ForegroundColor White
    exit 1
}

# Variables
$dbUser = "restautech_user"
$dbPassword = "restautech_pass_2026"
$dbName = "restautech_db"
$pgUser = "postgres"

Write-Host "`n📋 Configuración a crear:" -ForegroundColor $infoColor
Write-Host "   Usuario:    $dbUser" -ForegroundColor White
Write-Host "   Contraseña: $dbPassword" -ForegroundColor White
Write-Host "   Database:   $dbName`n" -ForegroundColor White

# Crear usuario y base de datos
Write-Host "⏳ Ejecutando comandos SQL..." -ForegroundColor $infoColor

# Comando SQL
$sqlCommands = @"
-- Crear usuario
CREATE USER $dbUser WITH PASSWORD '$dbPassword';

-- Crear base de datos
CREATE DATABASE $dbName OWNER $dbUser;

-- Conceder privilegios
GRANT CONNECT ON DATABASE $dbName TO $dbUser;
GRANT USAGE ON SCHEMA public TO $dbUser;
GRANT CREATE ON SCHEMA public TO $dbUser;
GRANT SELECT, INSERT, UPDATE, DELETE ON ALL TABLES IN SCHEMA public TO $dbUser;
ALTER DEFAULT PRIVILEGES IN SCHEMA public GRANT SELECT, INSERT, UPDATE, DELETE ON TABLES TO $dbUser;

-- Mostrar resultado
SELECT 1 as resultado;
"@

try {
    $output = $sqlCommands | psql -U $pgUser 2>&1 | Out-String
    
    if ($output -match "CREATE ROLE" -or $output -match "resultado") {
        Write-Host "  ✓ Usuario y base de datos creados" -ForegroundColor $successColor
        Write-Host "    $output" -ForegroundColor Gray
    } else {
        Write-Host "  Advertencia: Posible error" -ForegroundColor $warningColor
        Write-Host "  $output" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Error ejecutando SQL: $_" -ForegroundColor $errorColor
    Write-Host "  Verifica que PostgreSQL está corriendo" -ForegroundColor $warningColor
    exit 1
}

# Verificar conexión
Write-Host "`n✓ Verificando conexión..." -ForegroundColor $infoColor
try {
    $testQuery = "SELECT version();"
    $result = $testQuery | psql -U $dbUser -d $dbName -h localhost 2>&1 | Out-String
    
    if ($result -match "PostgreSQL") {
        Write-Host "  ✓ Conexión exitosa a $dbName" -ForegroundColor $successColor
        Write-Host "  $($result.Split([Environment]::NewLine)[0])" -ForegroundColor Gray
    } else {
        Write-Host "  ✗ No se pudo conectar" -ForegroundColor $errorColor
        Write-Host "  Respuesta: $result" -ForegroundColor Gray
    }
} catch {
    Write-Host "  ✗ Error: $_" -ForegroundColor $errorColor
}

# Resumen
Write-Host "`n" -ForegroundColor Cyan
Write-Host "================================================" -ForegroundColor Cyan
Write-Host "  ✓ Setup completado" -ForegroundColor Green
Write-Host "================================================`n" -ForegroundColor Cyan

Write-Host "📝 Próximos pasos:" -ForegroundColor Cyan
Write-Host "   1. Ejecuta: .\start-dev.ps1" -ForegroundColor White
Write-Host "   2. O si prefieres Docker: .\start-docker.ps1`n" -ForegroundColor White

Write-Host "🔍 Verificar base de datos manualmente:" -ForegroundColor Cyan
Write-Host "   psql -U $dbUser -d $dbName -h localhost" -ForegroundColor White
Write-Host "   \dt  (listar tablas)" -ForegroundColor White
Write-Host "   \q  (salir)`n" -ForegroundColor White

Write-Host "Credenciales guardadas en backend\.env.development" -ForegroundColor Gray
