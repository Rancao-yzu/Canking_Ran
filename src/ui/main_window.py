"""
主窗口 - Canking_Ran
Kvaser CAN 工具主界面
布局: 左侧边栏(配置+筛选) | 右侧 Notebook 页签(接收 | 发送)
"""
import tkinter as tk
from tkinter import ttk, filedialog, messagebox

import gui_style

from ui.config_panel import ConfigPanel
from ui.send_panel import SendPanel
from ui.receive_panel import ReceivePanel
from ui.filter_panel import FilterPanel

from core.can_bus import KvaserBusManager
from core.dbc_loader import DbcLoader
from receiver.message_receiver import MessageReceiver
from sender.message_sender import MessageSender
from filter.can_filter import CanFilter


class MainWindow:
    """Canking_Ran 主窗口"""

    def __init__(self, root: tk.Tk):
        self.root = root
        self.root.title("Canking_Ran - Kvaser CAN 工具")
        self.root.geometry("1280x800")
        self.root.configure(bg=gui_style.BG_BASE)
        gui_style.apply_style(self.root)

        # ---- 核心组件 ----
        self.bus_manager = KvaserBusManager()
        self.dbc_loader = DbcLoader()
        self.can_filter = CanFilter()
        self.receiver = MessageReceiver(self.bus_manager, self.dbc_loader)
        self.sender = MessageSender(self.bus_manager, self.dbc_loader)

        # ---- UI ----
        self._setup_ui()
        self._poll_queue()

    # ==================== UI 布局 ====================

    def _setup_ui(self):
        # 顶部标题栏
        self._setup_titlebar()

        # 左右分割主区域 (可拖拽)
        self._main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self._main_pane.pack(fill=tk.BOTH, expand=True, padx=5, pady=(0, 5))

        # 左侧边栏
        self._setup_sidebar()

        # 右侧 Notebook
        self._setup_notebook()

        # 底部状态栏
        self.statusbar = ttk.Label(self.root,
                                   text="就绪 | 先加载 DBC 文件并连接 Kvaser 设备",
                                   style="Status.TLabel")
        self.statusbar.pack(fill=tk.X, side=tk.BOTTOM)

    def _setup_titlebar(self):
        """顶部标题栏 - 连接状态指示"""
        bar = ttk.Frame(self.root)
        bar.pack(fill=tk.X, padx=8, pady=(6, 0))

        ttk.Label(bar, text="Canking_Ran", font=("Microsoft YaHei", 13, "bold"),
                  foreground=gui_style.BLUE).pack(side=tk.LEFT)

        self.connection_indicator = tk.Canvas(bar, width=12, height=12,
                                              bg=gui_style.BG_BASE, highlightthickness=0)
        self.connection_indicator.pack(side=tk.LEFT, padx=(12, 4))
        self._draw_indicator("gray")

        self.connection_label = ttk.Label(bar, text="未连接",
                                          style="Secondary.TLabel")
        self.connection_label.pack(side=tk.LEFT)

        self.msg_counter_label = ttk.Label(bar, text="",
                                           style="Secondary.TLabel")
        self.msg_counter_label.pack(side=tk.RIGHT)

    def _draw_indicator(self, color):
        c = self.connection_indicator
        c.delete("all")
        c.create_oval(2, 2, 10, 10, fill=color, outline="")

    def _setup_sidebar(self):
        """左侧边栏 - 配置 + 筛选"""
        sidebar = ttk.Frame(self._main_pane)
        sidebar.columnconfigure(0, weight=1)
        sidebar.rowconfigure(1, weight=1)

        # 1. 配置面板
        self.config_panel = ConfigPanel(sidebar)
        self.config_panel.grid(row=0, column=0, sticky="ew", pady=(0, 4))
        self._bind_config_events()

        # 2. 筛选面板
        self.filter_panel = FilterPanel(sidebar)
        self.filter_panel.grid(row=1, column=0, sticky="nsew")
        self._bind_filter_events()

        self._main_pane.add(sidebar, weight=0)

    def _setup_notebook(self):
        """右侧 Notebook 页签"""
        self.notebook = ttk.Notebook(self._main_pane)

        # ---- 接收 Tab ----
        self.receive_panel = ReceivePanel(self.notebook)
        self.receive_panel.clear_btn.configure(command=self._on_clear_messages)
        self.receive_panel.group_btn.configure(command=self._on_toggle_grouping)
        self.notebook.add(self.receive_panel, text="  接收  ")

        # ---- 发送 Tab ----
        self.send_panel = SendPanel(self.notebook)
        self.notebook.add(self.send_panel, text="  发送  ")
        self._bind_send_events()

        self._main_pane.add(self.notebook, weight=1)

    # ==================== 事件绑定 ====================

    def _bind_config_events(self):
        cp = self.config_panel
        cp.browse_btn.configure(command=self._on_browse_dbc)
        cp.refresh_btn.configure(command=self._on_refresh_channels)
        cp.connect_btn.configure(command=self._on_connect)
        cp.disconnect_btn.configure(command=self._on_disconnect)
        cp.mode_combo.bind("<<ComboboxSelected>>", self._on_mode_changed)

    def _bind_send_events(self):
        sp = self.send_panel
        sp.send_btn.configure(command=self._on_send)
        sp.stop_send_btn.configure(command=self._on_stop_send)

    def _bind_filter_events(self):
        fp = self.filter_panel
        fp.add_btn.configure(command=self._on_add_filter_id)
        fp.remove_btn.configure(command=self._on_remove_filter_id)
        fp.clear_btn.configure(command=self._on_clear_filter)
        fp.filter_enabled_var.trace_add("write", self._on_filter_toggle)

    # ==================== 配置回调 ====================

    def _on_browse_dbc(self):
        filepath = filedialog.askopenfilename(
            title="选择 DBC 文件",
            filetypes=[("DBC 文件", "*.dbc"), ("所有文件", "*.*")]
        )
        if not filepath:
            return
        try:
            self.dbc_loader.load(filepath)
            self.config_panel.dbc_path_var.set(filepath)
            self.config_panel.set_status(
                f"DBC 已加载: {self.dbc_loader.message_count} 条报文")
            # 刷新发送面板的 DBC 报文列表
            self.send_panel.set_dbc_loader(self.dbc_loader)
            # 注入给接收面板, 供懒解码使用
            self.receive_panel.set_dbc_loader(self.dbc_loader)
            self.statusbar.configure(text=f"DBC 文件: {filepath}")
        except Exception as e:
            messagebox.showerror("错误", f"加载 DBC 失败:\n{e}")

    def _on_refresh_channels(self):
        try:
            from can.interfaces.kvaser import KvaserBus
            ch_list = KvaserBus._detect_available_configs()
            channels = []
            for i, c in enumerate(ch_list):
                ch_num = c.get("channel", i)
                serial = c.get("device_name", "")
                label = f"{ch_num} - {serial}" if serial else str(ch_num)
                channels.append(label)
            if channels:
                self.config_panel.channel_combo["values"] = channels
                self.config_panel.channel_var.set(channels[0])
                self.config_panel.set_status(f"检测到 {len(channels)} 个通道")
            else:
                self.config_panel.channel_combo["values"] = ["0", "1"]
                self.config_panel.set_status("未检测到设备")
        except Exception as e:
            self.config_panel.channel_combo["values"] = ["0", "1"]
            self.config_panel.set_status(f"扫描失败: {e}")

    def _on_connect(self):
        cp = self.config_panel
        channel = cp.get_channel_number()
        if not channel:
            messagebox.showwarning("提示", "请选择 CAN 通道")
            return
        try:
            bitrate = int(cp.get_bitrate())
        except ValueError:
            messagebox.showerror("错误", "比特率格式无效")
            return

        data_bitrate = None
        is_fd = cp.is_fd_mode()
        if is_fd:
            try:
                data_bitrate = int(cp.get_fd_bitrate())
            except ValueError:
                messagebox.showerror("错误", "FD 数据比特率格式无效")
                return

        try:
            self.bus_manager.connect(
                channel=channel,
                bitrate=bitrate,
                data_bitrate=data_bitrate,
                fd=is_fd,
                can_filters=self.can_filter.to_can_filters(),
            )
        except Exception as e:
            messagebox.showerror("连接失败", str(e))
            return

        self.receiver.start()
        cp.connect_btn.configure(state=tk.DISABLED)
        cp.disconnect_btn.configure(state=tk.NORMAL)
        fd_str = " CAN FD" if is_fd else ""
        cp.set_status(f"已连接{fd_str}: 通道{channel}")
        self._draw_indicator(gui_style.GREEN)
        self.connection_label.configure(text=f"已连接 | 通道 {channel}{fd_str}",
                                        foreground=gui_style.GREEN)
        self.statusbar.configure(text=f"已连接 Kvaser 通道 {channel}")

    def _on_disconnect(self):
        cp = self.config_panel
        self.receiver.stop()
        self.sender.stop_cyclic()
        self.bus_manager.disconnect()
        cp.connect_btn.configure(state=tk.NORMAL)
        cp.disconnect_btn.configure(state=tk.DISABLED)
        cp.set_status("已断开")
        self._draw_indicator("gray")
        self.connection_label.configure(text="未连接",
                                        foreground=gui_style.TEXT_SECONDARY)
        self.statusbar.configure(text="已断开连接")

    def _on_mode_changed(self, event=None):
        cp = self.config_panel
        if cp.is_fd_mode():
            cp.fd_bitrate_combo.configure(state="readonly")
        else:
            cp.fd_bitrate_combo.configure(state=tk.DISABLED)

    # ==================== 发送回调 ====================

    def _add_sent_message(self, can_id, data, is_fd):
        """将发送的报文也加入到接收面板展示 (不预解码)"""
        from datetime import datetime
        raw_hex = " ".join(f"{b:02X}" for b in data)

        entry = {
            "id": can_id,
            "time": datetime.now().strftime("%H:%M:%S.%f")[:-3],
            "dlc": len(data),
            "raw": raw_hex,
            "data": list(data),          # 原始字节, 供懒解码
            "signals": [],               # 点击展开时懒解码
            "is_fd": is_fd,
        }
        self.receive_panel.add_message(entry)

    def _on_send(self):
        sp = self.send_panel
        if not self.bus_manager.is_connected:
            messagebox.showwarning("提示", "请先连接 CAN 总线")
            return

        mode = sp.get_send_mode()
        is_extended = sp.is_extended()
        is_fd = self.config_panel.is_fd_mode()

        # 根据当前编辑器模式选择数据源
        if sp.current_editor == "dbc":
            # DBC 变量发送: 先验证信号值
            valid, errors = sp.validate_signals()
            if not valid:
                err_msg = "以下信号值超出允许范围:\n\n" + "\n".join("  • " + e for e in errors)
                messagebox.showwarning("信号值越界", err_msg)
                return

            can_id, signals = sp.get_dbc_signals_dict()
            if can_id is None or signals is None:
                messagebox.showwarning("提示", "信号值格式无效，请检查输入")
                return

            if mode == "单次":
                try:
                    self.sender.send_by_dbc(can_id, signals, is_extended, is_fd)
                    # 收集发送的报文
                    data = self.dbc_loader.encode_message(can_id, signals)
                    if data:
                        self._add_sent_message(can_id, data, is_fd)
                    sp.send_status_var.set(f"DBC 发送 0x{can_id:X}")
                    self.statusbar.configure(text=f"DBC 发送: 0x{can_id:X}")
                except Exception as e:
                    sp.send_status_var.set(f"失败: {e}")

            elif mode == "循环":
                # 先编码一次获取 data
                try:
                    data = self.dbc_loader.encode_message(can_id, signals)
                    if data is None:
                        messagebox.showwarning("提示", "DBC 编码失败")
                        return
                except Exception as e:
                    messagebox.showwarning("提示", f"DBC 编码失败: {e}")
                    return
                cb = lambda cid, d, fd=is_fd: self._add_sent_message(cid, d, fd)
                self.sender.start_cyclic(can_id, data, sp.get_period_ms(),
                                         is_extended, is_fd, on_send=cb)
                sp.send_status_var.set(f"循环中 0x{can_id:X} @{sp.get_period_ms()}ms")
                sp.send_btn.configure(state=tk.DISABLED)
                sp.stop_send_btn.configure(state=tk.NORMAL)
                self.statusbar.configure(text=f"DBC 循环发送: 0x{can_id:X}")

            elif mode == "循环随机":
                dlc = len(self.dbc_loader.db.get_message_by_frame_id(can_id).length)
                cb = lambda cid, d, fd=is_fd: self._add_sent_message(cid, d, fd)
                self.sender.start_cyclic_random(can_id, dlc, sp.get_period_ms(),
                                                is_extended, is_fd, on_send=cb)
                sp.send_status_var.set(f"随机循环中 0x{can_id:X}")
                sp.send_btn.configure(state=tk.DISABLED)
                sp.stop_send_btn.configure(state=tk.NORMAL)
                self.statusbar.configure(text=f"随机循环发送: 0x{can_id:X}")

        else:
            # 原始 Hex 发送
            can_id = sp.get_raw_can_id()
            if can_id is None:
                messagebox.showwarning("提示", "CAN ID 格式无效")
                return

            if mode == "单次":
                data = sp.get_raw_data_bytes()
                if data is None:
                    messagebox.showwarning("提示", "数据格式无效")
                    return
                try:
                    self.sender.send_once(can_id, data, is_extended, is_fd)
                    self._add_sent_message(can_id, data, is_fd)
                    sp.send_status_var.set(f"已发送 0x{can_id:X}")
                    self.statusbar.configure(text=f"发送: 0x{can_id:X}")
                except Exception as e:
                    sp.send_status_var.set(f"失败: {e}")

            elif mode == "循环":
                data = sp.get_raw_data_bytes()
                if data is None:
                    messagebox.showwarning("提示", "数据格式无效")
                    return
                cb = lambda cid, d, fd=is_fd: self._add_sent_message(cid, d, fd)
                self.sender.start_cyclic(can_id, data, sp.get_period_ms(),
                                         is_extended, is_fd, on_send=cb)
                sp.send_status_var.set(f"循环中 0x{can_id:X} @{sp.get_period_ms()}ms")
                sp.send_btn.configure(state=tk.DISABLED)
                sp.stop_send_btn.configure(state=tk.NORMAL)
                self.statusbar.configure(text=f"循环发送: 0x{can_id:X}")

            elif mode == "循环随机":
                dlc = sp.get_raw_dlc()
                cb = lambda cid, d, fd=is_fd: self._add_sent_message(cid, d, fd)
                self.sender.start_cyclic_random(can_id, dlc, sp.get_period_ms(),
                                                is_extended, is_fd, on_send=cb)
                sp.send_status_var.set(f"随机循环中 0x{can_id:X}")
                sp.send_btn.configure(state=tk.DISABLED)
                sp.stop_send_btn.configure(state=tk.NORMAL)
                self.statusbar.configure(text=f"随机循环发送: 0x{can_id:X}")

    def _on_stop_send(self):
        sp = self.send_panel
        self.sender.stop_cyclic()
        sp.send_status_var.set("")
        sp.send_btn.configure(state=tk.NORMAL)
        sp.stop_send_btn.configure(state=tk.DISABLED)
        self.statusbar.configure(text="已停止循环发送")

    # ==================== 筛选回调 ====================

    def _on_add_filter_id(self):
        fp = self.filter_panel
        raw = fp.get_id_string()
        if not raw:
            return
        try:
            cid = int(raw, 16) if raw.lower().startswith("0x") else int(raw)
        except ValueError:
            messagebox.showwarning("提示", "CAN ID 格式无效")
            return
        self.can_filter.add_id(cid)
        fp.add_id_to_list(f"0x{cid:X}")
        self.statusbar.configure(text=f"添加筛选: 0x{cid:X}")

    def _on_remove_filter_id(self):
        self.filter_panel.remove_selected()
        self._rebuild_filter()

    def _on_clear_messages(self):
        """清空报文列表"""
        self.receive_panel.clear()
        self.statusbar.configure(text="报文列表已清空")

    def _on_toggle_grouping(self):
        """切换折叠/逐条显示模式"""
        self.receive_panel.toggle_grouping()
        mode = "折叠" if self.receive_panel.group_enabled else "逐条"
        self.statusbar.configure(text=f"显示模式: {mode}")

    def _on_clear_filter(self):
        self.filter_panel.clear_all()
        self.can_filter.clear()

    def _on_filter_toggle(self, *args):
        if self.filter_panel.is_enabled():
            self.can_filter.enable()
        else:
            self.can_filter.disable()
        self._rebuild_filter()

    def _rebuild_filter(self):
        self.can_filter.clear()
        for cid in self.filter_panel.get_all_ids():
            self.can_filter.add_id(cid)
        if self.filter_panel.is_enabled():
            self.can_filter.enable()

    # ==================== 接收队列轮询 ====================

    def _poll_queue(self):
        import queue
        try:
            while True:
                data = self.receiver.msg_queue.get_nowait()
                if self.can_filter.match(data["id"]):
                    self.receive_panel.add_message(data)
        except queue.Empty:
            pass

        count = self.receive_panel.count
        self.msg_counter_label.configure(
            text=f"报文: {count} 条" if count > 0 else "")

        self.root.after(50, self._poll_queue)

    def on_close(self):
        self.sender.stop_cyclic()
        self.receiver.stop()
        self.bus_manager.disconnect()
        self.root.destroy()
