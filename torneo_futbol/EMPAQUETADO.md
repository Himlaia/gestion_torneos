# Instrucciones de Empaquetado

## Requisitos Previos

1. **Python 3.x instalado**
2. **Dependencias instaladas:**
   ```bash
   pip install -r requirements.txt
   pip install pyinstaller
   ```

## Método 1: Usando el Script Automatizado (Recomendado)

### Windows (PowerShell)

1. Abre PowerShell en la carpeta `torneo_futbol`
2. Ejecuta el script de construcción:
   ```powershell
   .\build.ps1
   ```

Si recibes un error de política de ejecución, ejecuta primero:
```powershell
Set-ExecutionPolicy -ExecutionPolicy RemoteSigned -Scope CurrentUser
```

## Método 2: Comando Manual

```bash
pyinstaller --clean torneo_futbol.spec
```

## Método 3: Crear desde Cero

Si quieres crear el ejecutable sin el archivo .spec:

```bash
pyinstaller --name="TorneoFutbol" ^
            --windowed ^
            --onefile ^
            --add-data="app/resources;app/resources" ^
            --add-data="app/views/ui;app/views/ui" ^
            --hidden-import=PySide6.QtCore ^
            --hidden-import=PySide6.QtGui ^
            --hidden-import=PySide6.QtWidgets ^
            --hidden-import=PySide6.QtUiTools ^
            --hidden-import=sqlite3 ^
            main.py
```

## Estructura Resultante

Después del empaquetado, encontrarás:

```
dist/
├── TorneoFutbol.exe    # Ejecutable principal
└── data/               # Se crea automáticamente al ejecutar
    └── torneo.db       # Base de datos (se genera en primera ejecución)
```

## Distribución

Para distribuir tu aplicación:

1. Copia toda la carpeta `dist`
2. Renómbrala a algo como `TorneoFutbol_v1.0`
3. Comprime en ZIP o crea un instalador
4. Los usuarios solo necesitan:
   - Ejecutar `TorneoFutbol.exe`
   - No necesitan Python instalado
   - La base de datos se crea automáticamente

## Problemas Comunes

### Error: "PyInstaller no encontrado"
```bash
pip install pyinstaller
```

### Error: "No se pueden encontrar recursos"
Verifica que las rutas en `torneo_futbol.spec` sean correctas:
- `app/resources` debe existir
- `app/views/ui` debe contener los archivos .ui

### El ejecutable no abre
- Verifica la consola ejecutando desde CMD: `TorneoFutbol.exe`
- Revisa los logs en `build/TorneoFutbol/warn-TorneoFutbol.txt`

### Tamaño del ejecutable muy grande
Es normal. El ejecutable incluye:
- Python completo
- PySide6 (Qt framework)
- Todas las dependencias
- Recursos (imágenes, fuentes, estilos)

Tamaño esperado: ~100-200 MB

## Optimización (Opcional)

Para reducir el tamaño del ejecutable:

1. Edita `torneo_futbol.spec` y cambia `upx=True` a `upx=True` (requiere UPX instalado)
2. Usa `--onefile` para un único archivo o elimínalo para múltiples archivos (más rápido)

## Testing

Antes de distribuir:

1. Prueba el ejecutable en un sistema limpio (sin Python)
2. Verifica todas las funcionalidades
3. Comprueba que los temas (claro/oscuro) funcionen
4. Asegúrate de que la base de datos se cree correctamente
