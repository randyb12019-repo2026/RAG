Write-Host "Descargando modelos de Ollama..." -ForegroundColor Cyan

$models = @(
    "embeddinggemma:300m",
    "gemma4:e2b"
)

foreach ($model in $models) {
    Write-Host "`n[$model] Descargando..." -ForegroundColor Yellow
    ollama pull $model
    if ($LASTEXITCODE -eq 0) {
        Write-Host "[$model] OK" -ForegroundColor Green
    } else {
        Write-Host "[$model] ERROR" -ForegroundColor Red
    }
}

Write-Host "`nProceso completado." -ForegroundColor Cyan
