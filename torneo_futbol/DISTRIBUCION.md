# Guía de Distribución del Ejecutable

## ✅ Empaquetado Completado

Una vez finalizado el proceso de PyInstaller, encontrarás:

### Estructura de Archivos Generados

```
torneo_futbol/
├── build/                    # Archivos temporales (puedes eliminar)
├── dist/                     # CARPETA DE DISTRIBUCIÓN
│   └── TorneoFutbol.exe     # Tu ejecutable (100-200 MB aprox.)
└── torneo_futbol.spec       # Configuración de PyInstaller
```

## 📦 Preparar para Distribución

### Paso 1: Crear estructura final

1. Crea una carpeta nueva llamada `TorneoFutbol_v1.0`
2. Copia `dist/TorneoFutbol.exe` a esta carpeta
3. Crea una subcarpeta `data` (opcional, se creará automáticamente)

```
TorneoFutbol_v1.0/
├── TorneoFutbol.exe
├── data/                 # Se genera automáticamente al ejecutar
│   ├── torneo.db         # Base de datos (primera ejecución)
│   └── escudos/          # Escudos de equipos
└── LEEME.txt            # Instrucciones para el usuario
```

### Paso 2: Crear archivo LEEME.txt

```txt
===========================================
  GESTIÓN DE TORNEO DE FÚTBOL - v1.0
===========================================

INSTRUCCIONES DE USO:

1. Ejecuta TorneoFutbol.exe
2. La aplicación creará automáticamente la base de datos
3. ¡Listo para usar!

REQUISITOS:
- Windows 10/11
- No necesita Python instalado
- No necesita instalación

CARACTERÍSTICAS:
- Gestión de equipos y participantes
- Calendario de partidos
- Cuadro de eliminatorias automático
- Temas claro y oscuro
- Exportación de resultados a CSV

SOPORTE:
Para reportar problemas o sugerencias, contacta con el desarrollador.

===========================================
```

## 🧪 Testing Antes de Distribuir

### Checklist de Pruebas

- [ ] El ejecutable abre sin errores
- [ ] La base de datos se crea en `data/torneo.db`
- [ ] Puedes crear equipos
- [ ] Puedes crear participantes
- [ ] El cuadro de eliminatorias funciona
- [ ] Los temas (claro/oscuro) cambian correctamente
- [ ] Se pueden guardar resultados de partidos
- [ ] La exportación CSV funciona
- [ ] Los escudos se pueden subir y visualizar

### Probar en PC Limpia

**IMPORTANTE:** Prueba el ejecutable en un ordenador sin Python instalado para asegurarte de que funciona correctamente.

## 📤 Métodos de Distribución

### Opción 1: ZIP Portable

1. Comprime la carpeta `TorneoFutbol_v1.0` en un archivo ZIP
2. Distribuye el ZIP
3. Los usuarios solo tienen que descomprimir y ejecutar

**Ventajas:**
- Simple y directo
- No requiere permisos de administrador
- Portable (USB, carpeta compartida, etc.)

### Opción 2: Crear Instalador (Avanzado)

Usa herramientas como:
- **Inno Setup** (gratuito, recomendado)
- **NSIS** (gratuito)
- **Advanced Installer** (versión free disponible)

**Ejemplo con Inno Setup:**

```iss
[Setup]
AppName=Gestión de Torneo de Fútbol
AppVersion=1.0
DefaultDirName={pf}\TorneoFutbol
DefaultGroupName=Torneo Fútbol
OutputDir=installer
OutputBaseFilename=TorneoFutbol_Setup_v1.0

[Files]
Source: "dist\TorneoFutbol.exe"; DestDir: "{app}"

[Icons]
Name: "{group}\Torneo de Fútbol"; Filename: "{app}\TorneoFutbol.exe"
Name: "{commondesktop}\Torneo de Fútbol"; Filename: "{app}\TorneoFutbol.exe"
```

### Opción 3: OneDrive/Google Drive

1. Sube el ZIP a la nube
2. Genera un enlace compartido
3. Distribuye el enlace

## 🔍 Solución de Problemas Comunes

### El ejecutable tarda en abrir
- **Normal:** La primera ejecución puede tardar 5-10 segundos
- Qt y Python se están inicializando

### Aparece error de "falta DLL"
- Raro con PyInstaller onefile
- Si ocurre, instala Visual C++ Redistributable

### La base de datos no se crea
- Verifica permisos de escritura en la carpeta
- Ejecuta como administrador (una vez)

### El ejecutable es muy grande (>150 MB)
- **Normal:** Incluye Python + PySide6 + dependencias
- No se puede reducir significativamente

### Windows Defender bloquea el ejecutable
- Normal para ejecutables nuevos sin firma digital
- Opciones:
  1. Firma el ejecutable (requiere certificado)
  2. Pide a los usuarios que agreguen excepción
  3. Sube a VirusTotal para verificación

## 🎯 Mejoras Futuras

### Reducir tamaño del ejecutable
1. Usa `--onedir` en lugar de `--onefile` (múltiples archivos pero más rápido)
2. Excluye módulos no usados en el .spec

### Agregar icono personalizado
1. Crea un icono .ico (256x256 px recomendado)
2. Guárdalo como `app/resources/img/icon.ico`
3. Modifica el .spec:
   ```python
   icon='app/resources/img/icon.ico'
   ```

### Versionado
Agrega información de versión al ejecutable:
```python
exe = EXE(
    # ...
    version='file_version_info.txt'
)
```

## 📊 Tamaños Esperados

- **Ejecutable:** 100-150 MB
- **Base de datos vacía:** ~20 KB
- **Base de datos con datos:** 1-5 MB
- **ZIP distribución:** 50-80 MB (comprimido)

## 🚀 Publicación

### Plataformas Recomendadas
- **GitHub Releases:** Gratuito, profesional
- **SourceForge:** Para software open source
- **itch.io:** Para aplicaciones indie
- **Sitio web propio:** Máximo control

### Información a Incluir
- Descripción clara de la aplicación
- Screenshots
- Requisitos del sistema
- Instrucciones de instalación
- Changelog (historial de versiones)
- Licencia (si aplica)

## ✅ Checklist Final

Antes de distribuir:

- [ ] Ejecutable probado en múltiples PCs
- [ ] Todas las funcionalidades verificadas
- [ ] README/LEEME incluido
- [ ] Versión claramente identificada
- [ ] Capturas de pantalla preparadas
- [ ] Método de soporte definido (email, GitHub Issues, etc.)
- [ ] Backup del código fuente guardado

---

**¡Tu aplicación está lista para compartir con el mundo!** 🎉
