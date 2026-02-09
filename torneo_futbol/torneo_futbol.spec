# -*- mode: python ; coding: utf-8 -*-
from pathlib import Path

block_cipher = None

# Preparar datas con recursos obligatorios
datas = [
    ('app/resources', 'app/resources'),
    ('app/views/ui', 'app/views/ui'),
    ('translations', 'translations'),  # Incluir archivos de traducción .qm
]

# Incluir data/ si existe (para distribuir con BD pre-poblada)
data_dir = Path('data')
if data_dir.exists():
    datas.append(('data', 'data'))

a = Analysis(
    ['main.py'],
    pathex=[],
    binaries=[],
    datas=datas,
    hiddenimports=[
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtUiTools',
        'sqlite3',
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=block_cipher,
    noarchive=False,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name='TorneoFutbol',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=False,  # No mostrar consola
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=None,  # Puedes agregar un icono aquí si tienes uno: 'app/resources/img/icon.ico'
)
