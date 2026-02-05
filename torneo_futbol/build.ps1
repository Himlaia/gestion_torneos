# Script de empaquetado para Windows
# Ejecutar este script para crear el ejecutable

Write-Host "======================================" -ForegroundColor Cyan
Write-Host "  Empaquetado de Torneo de Fútbol    " -ForegroundColor Cyan
Write-Host "======================================" -ForegroundColor Cyan
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

# Limpiar builds anteriores
Write-Host "Limpiando builds anteriores..." -ForegroundColor Yellow
if (Test-Path "build") {
    Remove-Item -Recurse -Force "build"
    Write-Host "Carpeta 'build' eliminada." -ForegroundColor Green
}
if (Test-Path "dist") {
    Remove-Item -Recurse -Force "dist"
    Write-Host "Carpeta 'dist' eliminada." -ForegroundColor Green
}
Write-Host ""

# Ejecutar PyInstaller
Write-Host "Iniciando empaquetado..." -ForegroundColor Yellow
Write-Host "Esto puede tardar varios minutos...`n" -ForegroundColor Yellow

pyinstaller --clean torneo_futbol.spec

# Verificar resultado
if (Test-Path "dist\TorneoFutbol.exe") {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Green
    Write-Host "  ¡EMPAQUETADO EXITOSO!              " -ForegroundColor Green
    Write-Host "======================================" -ForegroundColor Green
    Write-Host ""
    Write-Host "El ejecutable se encuentra en:" -ForegroundColor Cyan
    Write-Host "  $(Get-Location)\dist\TorneoFutbol.exe" -ForegroundColor White
    Write-Host ""
    Write-Host "Tamaño del ejecutable:" -ForegroundColor Cyan
    $size = (Get-Item "dist\TorneoFutbol.exe").Length / 1MB
    Write-Host "  $([math]::Round($size, 2)) MB" -ForegroundColor White
    Write-Host ""
    
    # Crear carpeta data en dist si no existe
    if (-not (Test-Path "dist\data")) {
        New-Item -ItemType Directory -Path "dist\data" | Out-Null
        Write-Host "Carpeta 'data' creada en dist\" -ForegroundColor Green
    }
    
    Write-Host "Próximos pasos:" -ForegroundColor Yellow
    Write-Host "  1. Prueba el ejecutable: dist\TorneoFutbol.exe" -ForegroundColor White
    Write-Host "  2. La base de datos se creará automáticamente en: dist\data\torneo.db" -ForegroundColor White
    Write-Host "  3. Distribuye la carpeta 'dist' completa" -ForegroundColor White
    Write-Host ""
} else {
    Write-Host ""
    Write-Host "======================================" -ForegroundColor Red
    Write-Host "  ERROR EN EL EMPAQUETADO            " -ForegroundColor Red
    Write-Host "======================================" -ForegroundColor Red
    Write-Host ""
    Write-Host "Revisa los mensajes de error arriba." -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "Presiona cualquier tecla para continuar..." -ForegroundColor Gray
$null = $Host.UI.RawUI.ReadKey("NoEcho,IncludeKeyDown")
