# -*- mode: python ; coding: utf-8 -*-

a = Analysis(
    ['jobhunter.py'],
    pathex=[],
    binaries=[],
    datas=[
        ('installer/icon.ico', '.'),
        ('installer/icon.ico', 'installer'),
        ('logo.png', '.'),
        ('intro.mp4', '.'),
        ('desktop_ui', 'desktop_ui'),
        ('jobs.json', '.'),
        ('profile.json', '.'),
        ('tracker.csv', '.')
    ],
    hiddenimports=[
        'PySide6',
        'PySide6.QtCore',
        'PySide6.QtGui',
        'PySide6.QtWidgets',
        'PySide6.QtWebEngineWidgets',
        'PySide6.QtWebEngineCore',
        'cv2',
        'PIL',
        'PIL.Image',
        'PIL.ImageTk',
        'pypdf',
        'imaplib',
        'email',
        'dns',
        'dns.resolver'
    ],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)
pyz = PYZ(a.pure)

exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='PashaHunt',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=False,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['installer/icon.ico'],
)
coll = COLLECT(
    exe,
    a.binaries,
    a.datas,
    strip=False,
    upx=True,
    upx_exclude=[],
    name='PashaHunt',
)
