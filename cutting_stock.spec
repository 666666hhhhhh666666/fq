# -*- mode: python ; coding: utf-8 -*-
import sys
from PyInstaller.utils.hooks import collect_submodules

block_cipher = None

hidden_mods = collect_submodules('ortools') + [
    'pkg_resources.py2_warn',
    'ortools.sat.python.cp_model_pb2',
    'ortools.linear_solver.pywrap_linear_solver',
]

a = Analysis(
    ['cutting_stock.py'],
    pathex=[],
    binaries=[],
    datas=[],
    hiddenimports=hidden_mods,
    hookspath=[],
    runtime_hooks=[],
    cipher=block_cipher
)
pyz = PYZ(a.pure, a.zipped_data, cipher=block_cipher)
exe = EXE(
    pyz,
    a.scripts,
    [],
    exclude_binaries=True,
    name='cutting_stock',
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,
    console=True
)
coll = COLLECT(
    exe,
    a.binaries,
    a.zipfiles,
    a.datas,
    strip=False,
    upx=True,
    name='cutting_stock'
)
