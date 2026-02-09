# update_translations.ps1
# Script para actualizar archivos .ts desde el código fuente
# Extrae todos los textos marcados con tr() y actualiza los archivos .ts

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Actualizador de Traducciones Qt" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que pyside6-lupdate existe
$lupdate = Get-Command pyside6-lupdate -ErrorAction SilentlyContinue

if (-not $lupdate) {
    Write-Host "❌ ERROR: pyside6-lupdate no encontrado" -ForegroundColor Red
    Write-Host "   Instala PySide6 con: pip install PySide6" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ pyside6-lupdate encontrado" -ForegroundColor Green
Write-Host ""

# Directorio del script y raíz del proyecto
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir

# Verificar archivo .pro (ahora en docs/)
$proFile = Join-Path (Join-Path $projectRoot "docs") "torneo_futbol.pro"

if (-not (Test-Path $proFile)) {
    Write-Host "❌ ERROR: Archivo torneo_futbol.pro no encontrado" -ForegroundColor Red
    Write-Host "   Ruta esperada: $proFile" -ForegroundColor Yellow
    exit 1
}

Write-Host "✓ Archivo torneo_futbol.pro encontrado" -ForegroundColor Green
Write-Host ""

# Cambiar al directorio raíz para ejecutar lupdate
Set-Location $projectRoot

# Ejecutar pyside6-lupdate
Write-Host "Extrayendo textos traducibles..." -ForegroundColor Cyan
Write-Host ""

& pyside6-lupdate $proFile

if ($LASTEXITCODE -eq 0) {
    Write-Host ""
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "  ✓ ÉXITO" -ForegroundColor Green
    Write-Host "========================================" -ForegroundColor Cyan
    Write-Host "Los archivos .ts han sido actualizados" -ForegroundColor Green
    Write-Host ""
    Write-Host "Próximos pasos:" -ForegroundColor Cyan
    Write-Host "  1. Edita los archivos .ts en translations/" -ForegroundColor White
    Write-Host "  2. Ejecuta: .\compile_translations.ps1" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "❌ ERROR: Falló la actualización de traducciones" -ForegroundColor Red
    exit 1
}
