"""
CAN 报文发送面板 - 扁平暗色风格
支持: 原始 Hex / DBC 变量发送
"""
import tkinter as tk
from tkinter import ttk

import gui_style


class SendPanel(ttk.Frame):
    """发送控制面板"""

    def __init__(self, parent):
        super().__init__(parent)
        self.configure(style="TFrame")
        self._dbc_loader = None
        self._signal_entries = {}
        self._setup_ui()

    def set_dbc_loader(self, dbc_loader):
        self._dbc_loader = dbc_loader
        self._refresh_dbc_messages()

    # ==================== UI ====================

    def _setup_ui(self):
        # 顶部工具栏
        top = ttk.Frame(self, padding=(10, 8), style="TFrame")
        top.pack(fill=tk.X)

        ttk.Label(top, text="发送模式", font=gui_style.FONT_BODY).pack(side=tk.LEFT, padx=(0, 4))
        self.send_mode_var = tk.StringVar(value="单次")
        ttk.Combobox(top, textvariable=self.send_mode_var, width=8,
                     state="readonly", values=["单次", "循环", "循环随机"]).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(top, text="扩展帧").pack(side=tk.LEFT, padx=(0, 2))
        self.extended_var = tk.BooleanVar(value=False)
        ttk.Checkbutton(top, variable=self.extended_var).pack(side=tk.LEFT, padx=(0, 12))

        ttk.Label(top, text="周期(ms)").pack(side=tk.LEFT, padx=(0, 4))
        self.period_var = tk.StringVar(value="100")
        ttk.Entry(top, textvariable=self.period_var, width=7).pack(side=tk.LEFT, padx=(0, 12))

        self.send_btn = ttk.Button(top, text="发送", style="Primary.TButton")
        self.send_btn.pack(side=tk.LEFT, padx=(0, 4))
        self.stop_send_btn = ttk.Button(top, text="停止", style="Danger.TButton", state=tk.DISABLED)
        self.stop_send_btn.pack(side=tk.LEFT)

        self.send_status_var = tk.StringVar(value="")
        ttk.Label(top, textvariable=self.send_status_var,
                  style="Secondary.TLabel").pack(side=tk.LEFT, padx=(12, 0))

        ttk.Separator(self, orient=tk.HORIZONTAL).pack(fill=tk.X)

        # 下半部分：左右分栏
        editor = ttk.Frame(self, padding=(10, 6))
        editor.pack(fill=tk.BOTH, expand=True)
        editor.columnconfigure(1, weight=1)
        editor.rowconfigure(0, weight=1)

        # ---- 左栏：数据源 ----
        left = ttk.LabelFrame(editor, text="数据源", style="Card.TLabelframe", padding=8)
        left.grid(row=0, column=0, sticky="ns", padx=(0, 6))
        left.rowconfigure(3, weight=1)

        ttk.Label(left, text="DBC 报文").pack(anchor=tk.W, pady=(0, 2))
        self.msg_combo_var = tk.StringVar()
        self.msg_combo = ttk.Combobox(left, textvariable=self.msg_combo_var,
                                      state="readonly", width=36)
        self.msg_combo.pack(fill=tk.X, pady=(0, 6))
        self.msg_combo.bind("<<ComboboxSelected>>", self._on_dbc_msg_selected)

        list_frame = ttk.Frame(left)
        list_frame.pack(fill=tk.BOTH, expand=True)
        list_frame.rowconfigure(0, weight=1)
        list_frame.columnconfigure(0, weight=1)

        self.msg_listbox = tk.Listbox(list_frame, height=8,
                                      font=gui_style.FONT_MONO,
                                      borderwidth=0, highlightthickness=0)
        gui_style.style_native_widget(self.msg_listbox)
        scrollbar = ttk.Scrollbar(list_frame, orient=tk.VERTICAL, command=self.msg_listbox.yview)
        self.msg_listbox.configure(yscrollcommand=scrollbar.set)
        self.msg_listbox.grid(row=0, column=0, sticky="nsew")
        scrollbar.grid(row=0, column=1, sticky="ns")
        self.msg_listbox.bind("<<ListboxSelect>>", self._on_listbox_select)

        # ---- 右栏：数据编辑 ----
        right = ttk.LabelFrame(editor, text="数据编辑", style="Card.TLabelframe", padding=10)
        right.grid(row=0, column=1, sticky="nsew")
        right.columnconfigure(0, weight=1)
        right.rowconfigure(0, weight=1)

        self.edit_container = ttk.Frame(right)
        self.edit_container.grid(row=0, column=0, sticky="nsew")
        self.edit_container.columnconfigure(0, weight=1)
        self.edit_container.rowconfigure(0, weight=1)

        self._setup_raw_data_editor()

    def _setup_raw_data_editor(self):
        for w in self.edit_container.winfo_children():
            w.destroy()

        self._raw_frame = ttk.Frame(self.edit_container)
        self._raw_frame.pack(fill=tk.BOTH, expand=True)

        ttk.Label(self._raw_frame, text="CAN ID (Hex)").grid(row=0, column=0, sticky=tk.W, pady=(0, 2))
        self.can_id_var = tk.StringVar(value="0x100")
        ttk.Entry(self._raw_frame, textvariable=self.can_id_var, width=16).grid(row=0, column=1, sticky=tk.W, padx=4, pady=(0, 2))

        ttk.Label(self._raw_frame, text="DLC").grid(row=0, column=2, sticky=tk.W, padx=(12, 0), pady=(0, 2))
        self.dlc_var = tk.StringVar(value="8")
        ttk.Entry(self._raw_frame, textvariable=self.dlc_var, width=4).grid(row=0, column=3, sticky=tk.W, padx=4, pady=(0, 2))

        ttk.Label(self._raw_frame, text="数据 (Hex)").grid(row=1, column=0, sticky=tk.NW, pady=(10, 0))
        self.data_text = tk.Text(self._raw_frame, height=4, width=50,
                                 insertbackground=gui_style.TEXT_PRIMARY,
                                 font=gui_style.FONT_MONO,
                                 borderwidth=0, highlightthickness=0,
                                 padx=10, pady=8)
        gui_style.style_native_widget(self.data_text)
        self.data_text.insert("1.0", "00 00 00 00 00 00 00 00")
        self.data_text.grid(row=1, column=1, columnspan=3, sticky="nsew", padx=4, pady=(10, 0))
        self._raw_frame.columnconfigure(1, weight=1)
        self._raw_frame.rowconfigure(1, weight=1)

        self._current_editor = "raw"

    def _setup_dbc_signal_editor(self, message):
        for w in self.edit_container.winfo_children():
            w.destroy()

        frame = ttk.Frame(self.edit_container)
        frame.pack(fill=tk.BOTH, expand=True)
        frame.columnconfigure(0, weight=1)
        frame.rowconfigure(1, weight=1)

        gui_style.section_label(frame, f"{message.name}  (ID: {hex(message.frame_id)})").grid(
            row=0, column=0, sticky=tk.W, pady=(0, 10))

        canvas = tk.Canvas(frame, bg=gui_style.BG_CARD, highlightthickness=0)
        canvas.grid(row=1, column=0, sticky="nsew")

        sbar = ttk.Scrollbar(frame, orient=tk.VERTICAL, command=canvas.yview)
        sbar.grid(row=1, column=1, sticky="ns")

        sig_frame = ttk.Frame(canvas)
        canvas.create_window((0, 0), window=sig_frame, anchor="nw")
        sig_frame.bind("<Configure>", lambda e: canvas.configure(scrollregion=canvas.bbox("all")))
        canvas.configure(yscrollcommand=sbar.set)
        canvas.bind_all("<MouseWheel>", lambda e: canvas.yview_scroll(int(-1 * (e.delta / 120)), "units"))

        self._signal_entries = {}
        self._signal_meta = {}     # {name: {min, max, unit}}
        row = 0
        for signal in message.signals:
            default_val = signal.initial if signal.initial is not None else 0

            self._signal_meta[signal.name] = {
                "min": signal.minimum,
                "max": signal.maximum,
                "unit": signal.unit or "",
            }

            ttk.Label(sig_frame, text=signal.name, font=gui_style.FONT_BODY,
                      foreground=gui_style.BLUE).grid(row=row, column=0, sticky=tk.W, padx=6, pady=3)

            var = tk.StringVar(value=str(default_val))
            self._signal_entries[signal.name] = var
            ttk.Entry(sig_frame, textvariable=var, width=14).grid(row=row, column=1, padx=6, pady=3)

            info = f"{signal.unit or ''}"
            if signal.minimum is not None and signal.maximum is not None:
                info += f"  [{signal.minimum} ~ {signal.maximum}]"
            ttk.Label(sig_frame, text=info, style="Secondary.TLabel").grid(
                row=row, column=2, sticky=tk.W, padx=6, pady=3)

            row += 1

        if not message.signals:
            ttk.Label(sig_frame, text="该报文无信号定义",
                      style="Secondary.TLabel").grid(row=0, column=0, pady=20)

        self._current_editor = "dbc"

    # ==================== 事件 ====================

    def _refresh_dbc_messages(self):
        self.msg_listbox.delete(0, tk.END)
        self._all_messages = []
        if self._dbc_loader is None or not self._dbc_loader.is_loaded:
            return
        db = self._dbc_loader.db
        for msg in sorted(db.messages, key=lambda m: m.frame_id):
            label = f"0x{msg.frame_id:X}  {msg.name}"
            self._all_messages.append(label)
            self.msg_listbox.insert(tk.END, label)
        self.msg_combo["values"] = self._all_messages

    def _on_listbox_select(self, event=None):
        sel = self.msg_listbox.curselection()
        if sel:
            label = self.msg_listbox.get(sel[0])
            self.msg_combo_var.set(label)
            self._on_dbc_msg_selected()

    def _on_dbc_msg_selected(self, event=None):
        label = self.msg_combo_var.get()
        if not label or self._dbc_loader is None or not self._dbc_loader.is_loaded:
            return
        try:
            can_id = int(label.split("0x")[1].split()[0], 16)
        except (ValueError, IndexError):
            return
        try:
            msg = self._dbc_loader.db.get_message_by_frame_id(can_id)
            self._setup_dbc_signal_editor(msg)
        except Exception:
            return

    # ==================== 对外接口 ====================

    def get_send_mode(self):
        return self.send_mode_var.get()

    def is_extended(self):
        return self.extended_var.get()

    def get_period_ms(self):
        try:
            return float(self.period_var.get().strip())
        except ValueError:
            return 100.0

    def get_raw_can_id(self):
        raw = self.can_id_var.get().strip()
        try:
            return int(raw, 16) if raw.lower().startswith("0x") else int(raw)
        except ValueError:
            return None

    def get_raw_data_bytes(self):
        text = self.data_text.get("1.0", "end-1c").strip()
        try:
            return bytes.fromhex(text.replace(" ", ""))
        except ValueError:
            return None

    def get_raw_dlc(self):
        try:
            return int(self.dlc_var.get().strip())
        except ValueError:
            return 8

    def validate_signals(self):
        """验证 DBC 信号值是否在允许范围内
        
        Returns:
            (is_valid, error_list)
            is_valid: 全部合法则为 True
            error_list: ["信号名: 值 超出范围 [min ~ max]", ...]
        """
        errors = []
        for name, meta in self._signal_meta.items():
            var = self._signal_entries.get(name)
            if var is None:
                continue
            try:
                val = float(var.get())
            except ValueError:
                errors.append(f"{name}: 输入值 \"{var.get()}\" 不是有效数字")
                continue

            vmin = meta["min"]
            vmax = meta["max"]
            if vmin is not None and val < vmin:
                errors.append(
                    f"{name}: {val} 低于最小值 {vmin}{' ' + meta['unit'] if meta['unit'] else ''}")
            if vmax is not None and val > vmax:
                errors.append(
                    f"{name}: {val} 超出最大值 {vmax}{' ' + meta['unit'] if meta['unit'] else ''}")

        return (len(errors) == 0, errors)

    def get_dbc_signals_dict(self):
        label = self.msg_combo_var.get()
        if not label or self._current_editor != "dbc":
            return None, None
        try:
            can_id = int(label.split("0x")[1].split()[0], 16)
        except (ValueError, IndexError):
            return None, None
        signals = {}
        for name, var in self._signal_entries.items():
            try:
                val = float(var.get())
                if val == int(val):
                    val = int(val)
                signals[name] = val
            except ValueError:
                return None, None
        return can_id, signals

    @property
    def current_editor(self):
        return self._current_editor
