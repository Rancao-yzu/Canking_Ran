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

def main():

    root = tk.Tk()
    app = MainWindow(root)

    # 窗口关闭回调
    root.protocol("WM_DELETE_WINDOW", app.on_close)

    root.mainloop()


if __name__ == "__main__":
    main()
