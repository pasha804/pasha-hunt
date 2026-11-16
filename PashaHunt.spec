# -*- mode: python ; coding: utf-8 -*-
import os

ffmpeg_dll = r"C:\Users\USER\AppData\Local\Programs\Python\Python314\Lib\site-packages\cv2\opencv_videoio_ffmpeg500_64.dll"
binaries = []
if os.path.exists(ffmpeg_dll):
    binaries.append((ffmpeg_dll, '.'))

datas = [
    ('installer/icon.ico', '.'),
    ('installer/icon.ico', 'installer'),
    ('logo.png', '.'),
    ('intro.mp4', '.'),
    ('desktop_ui', 'desktop_ui'),
    ('jobs.json', '.'),
    ('profile.json', '.'),
    ('config.json', '.'),
    ('cv_history.json', '.'),
    ('tracker.csv', '.'),
    ('desktop_app.py', '.'),
    ('desktop_server.py', '.'),
    ('scrapling_adapter.py', '.'),
]

a = Analysis(
    ['jobhunter.py'],
    pathex=[],
    binaries=binaries,
    datas=datas,
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
        'fitz',
        'pymupdf',
        'imaplib',
        'smtplib',
        'email',
        'dns',
        'dns.resolver',
        'desktop_app',
        'desktop_server',
        'scrapling_adapter',
        'bot',
        'cv',
        'docx'
    ],
    hookspath=[],
    hooksconfig={},
    runtimehooks=[],
    excludes=['pyarrow', 'scipy', 'psycopg2', 'matplotlib', 'tkinter'],
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
