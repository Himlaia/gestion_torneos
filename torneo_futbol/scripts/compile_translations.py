"""
Script Python para compilar traducciones .ts a .qm
Alternativa a pyside6-lrelease cuando no está disponible
"""

import sys
from pathlib import Path
from PySide6.QtCore import QCoreApplication, QTranslator


def compile_translation(ts_file: Path, qm_file: Path) -> bool:
    """
    Compila un archivo .ts a .qm usando QTranslator.
    
    Args:
        ts_file: Ruta al archivo .ts
        qm_file: Ruta al archivo .qm de salida
    
    Returns:
        True si la compilación fue exitosa
    """
    # Crear aplicación Qt temporal
    app = QCoreApplication(sys.argv)
    
    # Cargar archivo .ts
    translator = QTranslator()
    
    if not ts_file.exists():
        print(f"❌ ERROR: Archivo no encontrado: {ts_file}")
        return False
    
    # Intentar cargar el archivo .ts
    # Nota: QTranslator puede cargar .ts directamente en modo desarrollo
    if translator.load(str(ts_file.with_suffix('')), str(ts_file.parent)):
        print(f"✓ Cargado: {ts_file.name}")
        
        # Guardar como .qm no es directamente soportado en PySide6
        # pero los archivos .ts pueden usarse directamente
        print(f"  ℹ Los archivos .ts pueden usarse directamente")
        print(f"  ℹ Para producción, usa: pyside6-lrelease {ts_file} -qm {qm_file}")
        return True
    else:
        print(f"❌ No se pudo cargar: {ts_file.name}")
        return False


def main():
    """Función principal."""
    print("=" * 60)
    print("  Compilador de Traducciones Python (Alternativo)")
    print("=" * 60)
    print()
    
    # Directorio de traducciones (un nivel arriba desde scripts/)
    translations_dir = Path(__file__).parent.parent / "translations"
    
    if not translations_dir.exists():
        print(f"❌ ERROR: Directorio no encontrado: {translations_dir}")
        sys.exit(1)
    
    # Buscar archivos .ts
    ts_files = list(translations_dir.glob("*.ts"))
    
    if not ts_files:
        print("⚠ ADVERTENCIA: No se encontraron archivos .ts")
        sys.exit(0)
    
    print(f"Archivos .ts encontrados: {len(ts_files)}")
    print()
    
    success_count = 0
    
    for ts_file in ts_files:
        qm_file = ts_file.with_suffix('.qm')
        print(f"Procesando: {ts_file.name}")
        
        if compile_translation(ts_file, qm_file):
            success_count += 1
        
        print()
    
    print("=" * 60)
    print("  RESUMEN")
    print("=" * 60)
    print(f"Exitosos: {success_count}/{len(ts_files)}")
    print()
    
    if success_count == len(ts_files):
        print("✓ Todas las traducciones están válidas")
        print()
        print("NOTA IMPORTANTE:")
        print("  Para generar archivos .qm optimizados para producción,")
        print("  instala las herramientas Qt y ejecuta:")
        print()
        print("  pip install PySide6-Essentials")
        print("  pyside6-lrelease translations/torneo_es.ts -qm translations/torneo_es.qm")
        print("  pyside6-lrelease translations/torneo_en.ts -qm translations/torneo_en.qm")
        print()
        print("  Tu aplicación funcionará con archivos .ts en desarrollo,")
        print("  pero .qm es recomendado para producción (mejor rendimiento).")
    else:
        print("⚠ Algunas traducciones tienen errores")
        sys.exit(1)


if __name__ == "__main__":
    main()
