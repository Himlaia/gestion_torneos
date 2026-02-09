# Scripts de Utilidad

Esta carpeta contiene scripts para gestionar el proyecto.

## Scripts principales

### Compilación y Empaquetado

- **build_all.ps1**: 🎯 **[RECOMENDADO PARA ENTREGA]** Empaqueta TODO
  ```powershell
  .\scripts\build_all.ps1
  ```
  Genera:
  - `dist/TorneoFutbol.exe` - Aplicación completa
  - `dist/DigitalClock_Demo.exe` - Demo del componente
  - `entrega_final/` - Carpeta lista para comprimir y entregar
  
  **Este es el script principal para generar la entrega del proyecto.**

- **build.ps1**: Empaqueta solo la aplicación principal
  ```powershell
  .\scripts\build.ps1
  ```
  Genera el ejecutable en `dist/TorneoFutbol.exe`

- **build_demo.ps1**: Empaqueta solo el demo del componente
  ```powershell
  .\scripts\build_demo.ps1
  ```
  Genera el ejecutable en `dist/DigitalClock_Demo.exe`

### Traducciones

- **compile_translations.ps1**: Compila archivos `.ts` a `.qm` (formato binario optimizado)
  ```powershell
  .\scripts\compile_translations.ps1
  ```

- **compile_translations.py**: Alternativa en Python para compilar traducciones
  ```powershell
  python .\scripts\compile_translations.py
  ```

- **update_translations.ps1**: Extrae textos traducibles del código fuente
  ```powershell
  .\scripts\update_translations.ps1
  ```
  Lee el archivo `docs/torneo_futbol.pro` y actualiza los archivos `.ts` en `translations/`

## Herramientas de desarrollo

### translation_helpers/

Contiene scripts temporales utilizados durante el desarrollo para agregar traducciones manualmente:

- `agregar_paginas_trad.py`
- `agregar_trad.py`
- `agregar_traducciones_bracket.py`
- `agregar_traducciones_completas.py`
- `agregar_traducciones_detalle.py`

Estos scripts modifican directamente los archivos XML `.ts` para agregar traducciones específicas.

## Notas

- Todos los scripts PowerShell están diseñados para ejecutarse desde cualquier ubicación
- Los scripts de Python requieren tener PySide6 instalado: `pip install PySide6`
