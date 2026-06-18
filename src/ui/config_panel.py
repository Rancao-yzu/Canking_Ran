"""
Kvaser 连接配置面板 - 扁平暗色风格
"""
import tkinter as tk
from tkinter import ttk

import gui_style


class ConfigPanel(ttk.LabelFrame):
    """Kvaser CAN 配置面板"""

    def __init__(self, parent):
        super().__init__(parent, text="  设备配置", style="Card.TLabelframe", padding=10)
        self.columnconfigure(0, weight=1)
        self._setup_fields()
        self._setup_buttons()

    def _setup_fields(self):
        # DBC 文件
        ttk.Label(self, text="DBC 文件").pack(anchor=tk.W, pady=(0, 2))
        dbc_row = ttk.Frame(self)
        dbc_row.pack(fill=tk.X, pady=(0, 8))
        self.dbc_path_var = tk.StringVar()
        ttk.Entry(dbc_row, textvariable=self.dbc_path_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.browse_btn = ttk.Button(dbc_row, text="浏览", style="LightOrange.TButton")
        self.browse_btn.pack(side=tk.RIGHT)

        # CAN 通道
        ttk.Label(self, text="CAN 通道").pack(anchor=tk.W, pady=(0, 2))
        ch_row = ttk.Frame(self)
        ch_row.pack(fill=tk.X, pady=(0, 8))
        self.channel_var = tk.StringVar()
        self.channel_combo = ttk.Combobox(ch_row, textvariable=self.channel_var)
        self.channel_combo.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.refresh_btn = ttk.Button(ch_row, text="刷新", style="LightOrange.TButton")
        self.refresh_btn.pack(side=tk.RIGHT)

        # CAN 模式
        ttk.Label(self, text="CAN 模式").pack(anchor=tk.W, pady=(0, 2))
        self.mode_var = tk.StringVar(value="CAN FD")
        self.mode_combo = ttk.Combobox(self, textvariable=self.mode_var,
                                       state="readonly", values=["CAN", "CAN FD"])
        self.mode_combo.pack(fill=tk.X, pady=(0, 8))

        # 仲裁域比特率
        ttk.Label(self, text="仲裁域比特率 (bps)").pack(anchor=tk.W, pady=(0, 2))
        self.bitrate_var = tk.StringVar(value="500000")
        ttk.Combobox(self, textvariable=self.bitrate_var,
                     values=["125000", "250000", "500000", "1000000"]).pack(fill=tk.X, pady=(0, 8))

        # FD 数据比特率
        ttk.Label(self, text="FD 数据比特率 (bps)").pack(anchor=tk.W, pady=(0, 2))
        self.fd_bitrate_var = tk.StringVar(value="2000000")
        self.fd_bitrate_combo = ttk.Combobox(self, textvariable=self.fd_bitrate_var,
                                             values=["500000", "1000000", "2000000",
                                                     "4000000", "5000000"])
        self.fd_bitrate_combo.pack(fill=tk.X, pady=(0, 8))

    def _setup_buttons(self):
        # 连接/断开按钮
        btn_row = ttk.Frame(self)
        btn_row.pack(fill=tk.X, pady=(4, 0))
        self.connect_btn = ttk.Button(btn_row, text="连接设备", style="Primary.TButton")
        self.connect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))
        self.disconnect_btn = ttk.Button(btn_row, text="断开", style="Danger.TButton", state=tk.DISABLED)
        self.disconnect_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        self.status_var = tk.StringVar(value="等待连接...")
        ttk.Label(self, textvariable=self.status_var,
                  style="Secondary.TLabel").pack(fill=tk.X, pady=(6, 0))

    # ---- 对外接口 ----
    def get_channel_number(self):
        full = self.channel_var.get().strip()
        return full.split(" - ")[0] if " - " in full else full

    def get_bitrate(self):
        return self.bitrate_var.get().strip()

    def get_fd_bitrate(self):
        return self.fd_bitrate_var.get().strip()

    def is_fd_mode(self):
        return self.mode_var.get() == "CAN FD"


    def set_status(self, text):
        self.status_var.set(text)
