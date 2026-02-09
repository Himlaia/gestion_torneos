# Script para empaquetar AMBOS ejecutables
# 1. TorneoFutbol.exe (aplicación completa)
# 2. DigitalClock_Demo.exe (componente standalone)

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "   Empaquetado Completo - Entrega Final     " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Establecer directorio raíz del proyecto
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "Directorio del proyecto: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Verificar PyInstaller
Write-Host "Verificando PyInstaller..." -ForegroundColor Yellow
$pyinstallerInstalled = py -m pip show pyinstaller 2>$null

if (-not $pyinstallerInstalled) {
    Write-Host "PyInstaller no está instalado. Instalando..." -ForegroundColor Yellow
    py -m pip install pyinstaller
    Write-Host "PyInstaller instalado correctamente.`n" -ForegroundColor Green
} else {
    Write-Host "PyInstaller ya está instalado.`n" -ForegroundColor Green
}

# ==================================================
# PASO 1: Limpiar builds anteriores
# ==================================================
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "  PASO 1: Limpiando builds anteriores       " -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow

if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "✓ Carpeta 'build' eliminada." -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "✓ Carpeta 'dist' eliminada." -ForegroundColor Green
}
Write-Host ""

# ==================================================
# PASO 2: Compilar aplicación principal
# ==================================================
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "  PASO 2: Compilando TorneoFutbol.exe       " -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "Esto puede tardar varios minutos..." -ForegroundColor Cyan
Write-Host ""

pyinstaller --clean torneo_futbol.spec

if (-not (Test-Path "dist\TorneoFutbol.exe")) {
    Write-Host "ERROR: No se pudo compilar TorneoFutbol.exe" -ForegroundColor Red
    exit 1
}

$size1 = (Get-Item "dist\TorneoFutbol.exe").Length / 1MB
Write-Host "✓ TorneoFutbol.exe generado ($([Math]::Round($size1, 2)) MB)" -ForegroundColor Green
Write-Host ""

# ==================================================
# PASO 3: Compilar demo del componente
# ==================================================
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "  PASO 3: Compilando DigitalClock_Demo.exe  " -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "Esto puede tardar varios minutos..." -ForegroundColor Cyan
Write-Host ""

pyinstaller --clean demo_digital_clock.spec

if (-not (Test-Path "dist\DigitalClock_Demo.exe")) {
    Write-Host "ERROR: No se pudo compilar DigitalClock_Demo.exe" -ForegroundColor Red
    exit 1
}

$size2 = (Get-Item "dist\DigitalClock_Demo.exe").Length / 1MB
Write-Host "✓ DigitalClock_Demo.exe generado ($([Math]::Round($size2, 2)) MB)" -ForegroundColor Green
Write-Host ""

# ==================================================
# PASO 4: Crear carpeta de entrega
# ==================================================
Write-Host "=============================================" -ForegroundColor Yellow
Write-Host "  PASO 4: Preparando carpeta de entrega     " -ForegroundColor Yellow
Write-Host "=============================================" -ForegroundColor Yellow

$entregaDir = "entrega_final"
if (Test-Path $entregaDir) {
    Remove-Item -Recurse -Force $entregaDir
}
New-Item -ItemType Directory -Path $entregaDir | Out-Null

# Copiar ejecutables
Copy-Item "dist\TorneoFutbol.exe" "$entregaDir\TorneoFutbol.exe"
Copy-Item "dist\DigitalClock_Demo.exe" "$entregaDir\DigitalClock_Demo.exe"
Write-Host "✓ Ejecutables copiados" -ForegroundColor Green

# Copiar código fuente del componente
New-Item -ItemType Directory -Path "$entregaDir\componente_codigo_fuente" -Force | Out-Null
Copy-Item "app\views\widgets\digital_clock.py" "$entregaDir\componente_codigo_fuente\digital_clock.py"
Copy-Item "app\views\widgets\README.md" "$entregaDir\componente_codigo_fuente\README.md"
Write-Host "✓ Código fuente del componente copiado" -ForegroundColor Green

# Copiar README de entrega
Copy-Item "README_ENTREGA.md" "$entregaDir\README.md"
Write-Host "✓ README de entrega copiado" -ForegroundColor Green

Write-Host ""

# ==================================================
# RESUMEN FINAL
# ==================================================
Write-Host "=============================================" -ForegroundColor Green
Write-Host "    ¡EMPAQUETADO COMPLETADO EXITOSAMENTE!   " -ForegroundColor Green
Write-Host "=============================================" -ForegroundColor Green
Write-Host ""
Write-Host "📦 Contenido de la entrega en: $entregaDir\" -ForegroundColor Cyan
Write-Host ""
Write-Host "  📁 Archivos generados:" -ForegroundColor Yellow
Write-Host "     ├─ TorneoFutbol.exe" -ForegroundColor White
Write-Host "     │  └─ Aplicación completa ($([Math]::Round($size1, 2)) MB)" -ForegroundColor Gray
Write-Host "     ├─ DigitalClock_Demo.exe" -ForegroundColor White
Write-Host "     │  └─ Demo del componente ($([Math]::Round($size2, 2)) MB)" -ForegroundColor Gray
Write-Host "     ├─ README.md" -ForegroundColor White
Write-Host "     │  └─ Instrucciones de uso" -ForegroundColor Gray
Write-Host "     └─ componente_codigo_fuente\" -ForegroundColor White
Write-Host "        ├─ digital_clock.py" -ForegroundColor White
Write-Host "        └─ README.md (documentación)" -ForegroundColor White
Write-Host ""
Write-Host "📝 Siguiente paso:" -ForegroundColor Yellow
Write-Host "   Comprime la carpeta '$entregaDir' en un archivo ZIP" -ForegroundColor White
Write-Host "   y súbelo a la plataforma de entrega." -ForegroundColor White
Write-Host ""
Write-Host "✅ Ambos ejecutables funcionan con doble clic." -ForegroundColor Green
Write-Host ""
