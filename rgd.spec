# -*- mode: python ; coding: utf-8 -*-

# Build con:
#   pyinstaller rgd.spec

block_cipher = None

a = Analysis(
    ['run.py'],              # 👈 PRIMA DIFFERENZA: entrypoint
    pathex=['.', 'src'],     # 👈 SECONDA DIFFERENZA: includiamo root + src
    binaries=[],
    datas=[],
    hiddenimports=[],
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[],
    noarchive=False,
    optimize=0,
)

pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.datas,
    [],
    name='rgd',        # 👈 nome exe
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    upx_exclude=[],
    runtime_tmpdir=None,
    console=True,
    disable_windowed_traceback=False,
    argv_emulation=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
    icon=['assets\\windows\\openrgd.ico'],  # 👈 tieni l’icona
)
