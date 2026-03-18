param(
    [string]$BaseUrl = "http://localhost:8000",
    [string]$AdminEmail = "admin@restaurante.com",
    [string]$AdminPassword = "admin123",
    [string]$MeseroEmail = "mesero_1773843937@example.com",
    [string]$MeseroPassword = "mesero123",
    [string]$CocinaEmail = "cocina_1773843937@example.com",
    [string]$CocinaPassword = "cocina123"
)

$ErrorActionPreference = "Stop"

function Login-User {
    param(
        [string]$Email,
        [string]$Password,
        [string]$Label
    )

    $body = @{ email = $Email; password = $Password } | ConvertTo-Json
    $response = Invoke-RestMethod -Uri "$BaseUrl/auth/login" -Method Post -ContentType "application/json" -Body $body
    Write-Host "OK login $Label ($Email)"
    return $response
}

Write-Host "[1/4] Login users..."
$admin = Login-User -Email $AdminEmail -Password $AdminPassword -Label "ADMIN"
$mesero = Login-User -Email $MeseroEmail -Password $MeseroPassword -Label "MESERO"
$cocina = Login-User -Email $CocinaEmail -Password $CocinaPassword -Label "COCINA"

Write-Host "[2/4] Inject order as mesero..."
$orderBody = @{
    mesa_numero = 21
    items = @(
        @{
            product_id = "prod-e2e"
            nombre = "Pizza Personal"
            cantidad = 1
            precio_unitario = 30
        }
    )
    notas = "inyeccion realtime"
} | ConvertTo-Json -Depth 5

$newOrder = Invoke-RestMethod -Uri "$BaseUrl/orders" -Method Post -Headers @{ Authorization = "Bearer $($mesero.access_token)" } -ContentType "application/json" -Body $orderBody
Write-Host "OK order created: $($newOrder.id) status=$($newOrder.status) mesa=$($newOrder.mesa_numero)"

Write-Host "[3/4] Verify kitchen can see orders..."
$kitchenOrders = Invoke-RestMethod -Uri "$BaseUrl/orders" -Method Get -Headers @{ Authorization = "Bearer $($cocina.access_token)" }
$activeKitchenOrders = @($kitchenOrders | Where-Object { $_.status -ne "entregado" -and $_.status -ne "cancelado" })
Write-Host "OK kitchen orders total=$($kitchenOrders.Count) active=$($activeKitchenOrders.Count)"

Write-Host "[4/4] Verify admin dashboard metrics..."
$metrics = Invoke-RestMethod -Uri "$BaseUrl/metrics/dashboard" -Method Get -Headers @{ Authorization = "Bearer $($admin.access_token)" }
Write-Host "OK metrics total_ordenes=$($metrics.total_ordenes) ordenes_hoy=$($metrics.ordenes_hoy)"

Write-Host "DONE: injection flow works."
