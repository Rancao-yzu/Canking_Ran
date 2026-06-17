"""
CAN ID 筛选面板 - 扁平暗色风格
"""
import tkinter as tk
from tkinter import ttk

import gui_style


class FilterPanel(ttk.LabelFrame):
    """CAN ID 筛选面板"""

    def __init__(self, parent):
        super().__init__(parent, text="CAN ID 筛选", style="Card.TLabelframe", padding=10)
        self._setup_ui()

    def _setup_ui(self):
        # 启用开关
        self.filter_enabled_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(self, text="启用筛选", variable=self.filter_enabled_var).pack(anchor=tk.W, pady=(0, 6))

        # 输入 + 添加
        ttk.Label(self, text="添加 CAN ID (Hex)").pack(anchor=tk.W, pady=(0, 2))
        add_row = ttk.Frame(self)
        add_row.pack(fill=tk.X, pady=(0, 6))
        self.add_id_var = tk.StringVar()
        ttk.Entry(add_row, textvariable=self.add_id_var).pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 4))
        self.add_btn = ttk.Button(add_row, text="添加", style="Primary.TButton")
        self.add_btn.pack(side=tk.RIGHT)

        # 操作按钮
        btn_row = ttk.Frame(self)
        btn_row.pack(fill=tk.X, pady=(0, 6))
        self.remove_btn = ttk.Button(btn_row, text="移除选中", style="LightOrange.TButton")
        self.remove_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(0, 3))

        self.clear_btn = ttk.Button(btn_row, text="清空", style="LightOrange.TButton")
        self.clear_btn.pack(side=tk.LEFT, fill=tk.X, expand=True, padx=(3, 0))

        # ID 列表
        list_frame = ttk.Frame(self)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.id_listbox = tk.Listbox(list_frame, height=4,
                                     font=gui_style.FONT_MONO,
                                     borderwidth=0,
                                     highlightthickness=0)
        gui_style.style_native_widget(self.id_listbox)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.id_listbox.yview)
        self.id_listbox.configure(yscrollcommand=scrollbar.set)
        self.id_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")

    # ---- 对外接口 ----
    def is_enabled(self):
        return self.filter_enabled_var.get()

    def get_id_string(self):
        return self.add_id_var.get().strip()

    def add_id_to_list(self, can_id_str):
        self.id_listbox.insert(tk.END, can_id_str)
        self.add_id_var.set("")

    def remove_selected(self):
        for index in reversed(self.id_listbox.curselection()):
            self.id_listbox.delete(index)

    def clear_all(self):
        self.id_listbox.delete(0, tk.END)

    def get_all_ids(self):
        ids = []
        for i in range(self.id_listbox.size()):
            raw = self.id_listbox.get(i)
            try:
                cid = int(raw, 16) if raw.lower().startswith("0x") else int(raw)
                ids.append(cid)
            except ValueError:
                pass
        return ids
