# Script de empaquetado para Demo DigitalClock Component
# Ejecutar este script para crear el ejecutable del componente

Write-Host "=============================================" -ForegroundColor Cyan
Write-Host "  Empaquetado Demo DigitalClock Component   " -ForegroundColor Cyan
Write-Host "=============================================" -ForegroundColor Cyan
Write-Host ""

# Establecer directorio raíz del proyecto
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$projectRoot = Split-Path -Parent $scriptDir
Set-Location $projectRoot

Write-Host "Directorio del proyecto: $projectRoot" -ForegroundColor Cyan
Write-Host ""

# Verificar si PyInstaller está instalado
Write-Host "Verificando PyInstaller..." -ForegroundColor Yellow
$pyinstallerInstalled = py -m pip show pyinstaller 2>$null

if (-not $pyinstallerInstalled) {
    Write-Host "PyInstaller no está instalado. Instalando..." -ForegroundColor Yellow
    py -m pip install pyinstaller
    Write-Host "PyInstaller instalado correctamente.`n" -ForegroundColor Green
} else {
    Write-Host "PyInstaller ya está instalado.`n" -ForegroundColor Green
}

# Limpiar builds anteriores del demo
Write-Host "Limpiando builds anteriores del demo..." -ForegroundColor Yellow
if (Test-Path "build\demo_digital_clock") {
    Remove-Item -Recurse -Force "build\demo_digital_clock"
    Write-Host "Carpeta build del demo eliminada." -ForegroundColor Green
}
if (Test-Path "dist\DigitalClock_Demo.exe") {
    Remove-Item -Force "dist\DigitalClock_Demo.exe"
    Write-Host "Ejecutable anterior del demo eliminado." -ForegroundColor Green
}
Write-Host ""

# Ejecutar PyInstaller para el demo
Write-Host "Iniciando empaquetado del demo..." -ForegroundColor Yellow
Write-Host "Esto puede tardar varios minutos...`n" -ForegroundColor Yellow

pyinstaller --clean demo_digital_clock.spec

# Verificar resultado
if (Test-Path "dist\DigitalClock_Demo.exe") {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host "   ¡Empaquetado completado exitosamente!    " -ForegroundColor Green
    Write-Host "=============================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "El ejecutable está en:" -ForegroundColor Yellow
    Write-Host "  $projectRoot\dist\DigitalClock_Demo.exe" -ForegroundColor White
    Write-Host ""
    
    # Calcular tamaño del archivo
    $fileSize = (Get-Item "dist\DigitalClock_Demo.exe").Length / 1MB
    Write-Host "Tamaño del ejecutable: $([Math]::Round($fileSize, 2)) MB" -ForegroundColor Cyan
    Write-Host ""
    
    Write-Host "Puedes ejecutar el demo con doble clic en el archivo." -ForegroundColor Green
} else {
    Write-Host ""
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host "   ERROR: El empaquetado ha fallado        " -ForegroundColor Red
    Write-Host "=============================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Revisa los mensajes de error anteriores." -ForegroundColor Yellow
    Write-Host "Intenta ejecutar manualmente:" -ForegroundColor Yellow
    Write-Host "  pyinstaller --clean demo_digital_clock.spec" -ForegroundColor White
    exit 1
}
