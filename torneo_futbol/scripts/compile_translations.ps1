# compile_translations.ps1
# Script para compilar traducciones de Qt
# Genera archivos .qm desde los archivos .ts

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  Compilador de Traducciones Qt" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host ""

# Verificar que pyside6-lrelease existe
$lreleasePath = "C:\Users\Martina\AppData\Local\Programs\Python\Python313\Scripts\pyside6-lrelease.exe"

if (-not (Test-Path $lreleasePath)) {
    # Intentar buscar en el PATH
    $lrelease = Get-Command pyside6-lrelease -ErrorAction SilentlyContinue
    if ($lrelease) {
        $lreleasePath = $lrelease.Source
    } else {
        Write-Host "❌ ERROR: pyside6-lrelease no encontrado" -ForegroundColor Red
        Write-Host "   Instala PySide6 con: pip install PySide6" -ForegroundColor Yellow
        exit 1
    }
}

Write-Host "✓ pyside6-lrelease encontrado: $lreleasePath" -ForegroundColor Green
Write-Host ""

# Directorio de traducciones (relativo al directorio del script)
$scriptDir = Split-Path -Parent $MyInvocation.MyCommand.Path
$translationsDir = Join-Path (Split-Path -Parent $scriptDir) "translations"

if (-not (Test-Path $translationsDir)) {
    Write-Host "❌ ERROR: Directorio 'translations' no encontrado" -ForegroundColor Red
    exit 1
}

# Buscar archivos .ts
$tsFiles = Get-ChildItem -Path $translationsDir -Filter "*.ts"

if ($tsFiles.Count -eq 0) {
    Write-Host "⚠ ADVERTENCIA: No se encontraron archivos .ts" -ForegroundColor Yellow
    exit 0
}

Write-Host "Archivos .ts encontrados: $($tsFiles.Count)" -ForegroundColor Cyan
Write-Host ""

# Compilar cada archivo .ts a .qm
$successCount = 0
$errorCount = 0

foreach ($tsFile in $tsFiles) {
    $qmFile = $tsFile.FullName -replace '\.ts$', '.qm'
    $fileName = $tsFile.Name
    
    Write-Host "Compilando: $fileName" -ForegroundColor White
    
    # Ejecutar pyside6-lrelease
    & $lreleasePath $tsFile.FullName -qm $qmFile
    
    if ($LASTEXITCODE -eq 0) {
        Write-Host "  ✓ Generado: $(Split-Path $qmFile -Leaf)" -ForegroundColor Green
        $successCount++
    } else {
        Write-Host "  ❌ Error al compilar $fileName" -ForegroundColor Red
        $errorCount++
    }
    Write-Host ""
}

# Resumen
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "  RESUMEN" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Exitosos: $successCount" -ForegroundColor Green
Write-Host "Errores: $errorCount" -ForegroundColor $(if ($errorCount -gt 0) { "Red" } else { "Green" })
Write-Host ""

if ($successCount -gt 0) {
    Write-Host "✓ Las traducciones están listas para usar" -ForegroundColor Green
    Write-Host "  Los archivos .qm se han generado en: $translationsDir" -ForegroundColor Cyan
}

Write-Host ""
