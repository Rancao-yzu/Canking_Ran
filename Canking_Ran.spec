# -*- mode: python ; coding: utf-8 -*-
"""
Canking_Ran PyInstaller 打包规格
================================
打包方式: 单文件 (onefile)
运行环境: Linux x86_64

打包命令:
  pyinstaller Canking_Ran.spec

或指定输出目录:
  pyinstaller --distpath ./dist --workpath ./build Canking_Ran.spec
"""

import sys
from pathlib import Path
from PyInstaller.utils.hooks import collect_submodules

# ---------- 路径定义 ----------
ROOT = Path(SPECPATH)      # SPECPATH: spec 文件所在目录
SRC = ROOT / "src"
RESOURCES = ROOT / "Resources"

# ---------- 隐藏导入 ----------
# python-can: 只显式导入实际使用的接口和模块，避免与 excludes 冲突
# 项目实际使用: can.interfaces.kvaser (can_bus.py), can.interfaces.virtual (开发/测试)
# can.io / can.io.player: ASC 日志记录器 (can.ASCWriter)

# 项目内部包 (确保子模块都被打包)
project_hidden = (
    collect_submodules("core", str(SRC))
    + collect_submodules("ui", str(SRC))
    + collect_submodules("receiver", str(SRC))
    + collect_submodules("sender", str(SRC))
    + collect_submodules("filter", str(SRC))
)

# ---------- 元数据文件 ----------
datas = []
# 若需要在打包后随程序分发 DBC 文件，取消下面的注释:
# datas += [(str(RESOURCES), "Resources")]

a = Analysis(
    scripts=[str(SRC / "main.py")],
    pathex=[str(SRC)],  # 让项目包内 import 能正常解析
    binaries=[],
    datas=datas,
    hiddenimports=[
        # python-can
        "can",
        "can.interfaces.kvaser",
        "can.interfaces.virtual",
        "can.io",
        "can.io.player",
        # cantools
        "cantools",
        "cantools.database",
        "cantools.database.can",
        "cantools.database.can.formats",
        "cantools.database.can.formats.dbc",
        # tkinter (标准库, 但部分分发版需要显式声明)
        "tkinter",
        "tkinter.ttk",
        "tkinter.filedialog",
        "tkinter.messagebox",
        "tkinter.scrolledtext",
        # 项目内部
        "gui_style",
    ] + project_hidden,
    hookspath=[],
    hooksconfig={},
    runtime_hooks=[],
    excludes=[
        # 标准库中不用的模块
        "tkinter.test",
        "unittest",
        "test",
        "pydoc",
        "distutils",
        "setuptools",
        "pip",
        "pkg_resources",
        "http",
        "xmlrpc",
        "wsgiref",
        "curses",
        "ensurepip",
        "lib2to3",
        # 已确认可安全排除的无关模块
        "multiprocessing",
        "netrc",
        "ftplib",
        "smtplib",
        "poplib",
        "imaplib",
        "nntplib",
        "telnetlib",
        "webbrowser",
        "turtle",
        "venv",
        "zipapp",
        "doctest",
        "statistics",
        # 第三方库排除（已安装但项目完全不使用）
        "numpy",
        "pandas",
        "matplotlib",
        "contourpy",
        "cycler",
        "fonttools",
        "kiwisolver",
        "pyparsing",
        "Flask",
        "Flask-Cors",
        "canlib",
        "qt-gui",
        "jupyter-events",
        "jupyter-lsp",
        "PyPDF2",

        "rosbag",
        "roslib",
        "rqt-bag-plugins",

    ],
    win_no_prefer_redirects=False,
    win_private_assemblies=False,
    cipher=None,
    noarchive=False,
)

pyz = PYZ(
    a.pure,
    a.zipped_data,
    cipher=None,
)

exe = EXE(
    pyz,
    a.scripts,
    a.binaries,
    a.zipfiles,
    a.datas,
    [],
    name="Canking_Ran",
    debug=False,
    bootloader_ignore_signals=False,
    strip=False,
    upx=True,          # 启用 UPX 压缩 (需系统安装 upx)
    upx_exclude=[],    # 排除某些库, 避免 upx 压缩后启动异常
    runtime_tmpdir=None,
    console=False,          # 不显示终端窗口 (GUI 程序)
    disable_windowed_traceback=False,
    target_arch=None,
    codesign_identity=None,
    entitlements_file=None,
)
