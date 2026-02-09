# Documentación del Proyecto

Esta carpeta contiene la documentación del proyecto Gestión de Torneos de Fútbol.

## Contenido

- **GUIA_USUARIO.md**: Guía completa de usuario de la aplicación
- **Tarea4v2.txt**: Especificaciones y notas del proyecto
- **torneo_futbol.pro**: Archivo de proyecto Qt para actualización de traducciones

## Uso de traducciones

Para actualizar las traducciones desde el código fuente:
```powershell
cd ..
.\scripts\update_translations.ps1
```

Este comando extrae todos los textos marcados con `tr()` y actualiza los archivos `.ts` en la carpeta `translations/`.
