#!/usr/bin/env python3
"""
Canking_Ran - Kvaser CAN 工具 (Linux)
=========================================
功能:
  1. 发送 CAN 报文 (单次/循环/随机/DBC变量, 支持扩展帧和FD模式)
  2. 接收 CAN 报文 (DBC 解析信号值)
  3. 筛选 CAN ID 查看报文

启动方式:
  python main.py
"""

import tkinter as tk
from tkinter import messagebox

from ui.main_window import MainWindow


def check_dependencies():
    """检查必要依赖"""
    missing = []
    try:
        import can
    except ImportError:
        missing.append("python-can")
    try:
        import cantools
    except ImportError:
        missing.append("cantools")
    return missing


def main():
    missing = check_dependencies()

    root = tk.Tk()
    app = MainWindow(root)

    # 窗口关闭回调
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    if missing:
        root.after(500, lambda: messagebox.showwarning(
            "缺少依赖",
            f"缺少以下 Python 库: {', '.join(missing)}\n\n"
            f"请执行: pip install {' '.join(missing)}\n\n"
            f"当前仅可查看界面布局，CAN 功能不可用。"
        ))

    root.mainloop()


if __name__ == "__main__":
    main()
