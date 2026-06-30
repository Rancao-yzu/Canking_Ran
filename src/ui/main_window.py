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
        self.root.geometry("1280x880")
        self.root.configure(bg=gui_style.BG_BASE)
        gui_style.apply_style(self.root)

        # ---- 核心组件 ----
        self.bus_manager = KvaserBusManager()
        self.dbc_loader = DbcLoader()
        self.can_filter = CanFilter()
        self.receiver = MessageReceiver(self.bus_manager, self.dbc_loader)
        self.sender = MessageSender(self.bus_manager, self.dbc_loader)
        self.recording_path = None

        # ---- UI ----
        self._setup_ui()
        self._poll_queue()

    # ==================== UI 布局 ====================

    def _setup_ui(self):
        # 顶部标题栏
        self._setup_titlebar()

        # 左右分割主区域 (可拖拽)
        self._main_pane = ttk.PanedWindow(self.root, orient=tk.HORIZONTAL)
        self._main_pane.pack(fill=tk.BOTH, expand=True)

        # 左侧边栏
        self._setup_sidebar()

        # 右侧 Notebook
        self._setup_notebook()

        # 底部状态栏
        status_frame = tk.Frame(self.root, bg=gui_style.BG_CARD, highlightbackground=gui_style.BORDER_LIGHT, highlightthickness=1)
        status_frame.pack(fill=tk.X, side=tk.BOTTOM)
        self.statusbar = tk.Label(status_frame,
                                   text="  就绪  |  先加载 DBC 文件并连接 Kvaser 设备",
                                   font=("Microsoft YaHei", 8),
                                   fg=gui_style.TEXT_SECONDARY, bg=gui_style.BG_CARD,
                                   anchor=tk.W, padx=10, pady=5)
        self.statusbar.pack(fill=tk.X)

    def _setup_titlebar(self):
        """顶部标题栏 - 品牌感设计（浅橙色渐变背景）"""
        # 外层 Frame 用于边框（无边距，贴边）
        outer = tk.Frame(self.root, bg=gui_style.BORDER_LIGHT)
        outer.pack(fill=tk.X)

        # Canvas 作为标题栏主体，可绘制渐变
        self._title_canvas = tk.Canvas(outer, height=44, bg=gui_style.BG_CARD,
                                        highlightthickness=0, borderwidth=0)
        self._title_canvas.pack(fill=tk.X, expand=True)
        # 绑定 resize 重绘渐变
        self._title_canvas.bind("<Configure>", self._on_titlebar_resize)

        # --- 使用 Canvas 内嵌窗口放置所有控件 ---
        # 渐变起止色（与 _draw_gradient 保持一致）
        title_gradient_start = "#FFC992"  # 左侧微暖橙
        title_gradient_est   = "#FFCF9E"  # 右侧浅暖橙
        title_gradient_end   = "#FFE9D2"  # 右侧

        # 左侧品牌色块
        self._brand_canvas = tk.Canvas(self._title_canvas, width=4, height=32,
                                        bg=title_gradient_start, highlightthickness=0, borderwidth=0)
        self._brand_canvas.create_rectangle(0, 0, 4, 32, fill=gui_style.BLUE, outline="")
        self._title_canvas.create_window(14, 22, window=self._brand_canvas, anchor=tk.W)

        # 标题文字（融入左侧渐变起始色）
        title_frame = tk.Frame(self._title_canvas, bg=title_gradient_start)
        tk.Label(title_frame, text="Canking @Ran", font=("Microsoft YaHei", 14, "bold"),
                 fg=gui_style.TEXT_PRIMARY, bg=title_gradient_start).pack(side=tk.LEFT)
        tk.Label(title_frame, text="CAN Tool on linux with Kvaser ", font=("Microsoft YaHei", 12),
                 fg=gui_style.TEXT_SECONDARY, bg=title_gradient_est).pack(side=tk.LEFT, padx=(6, 0), pady=(4, 0))
        self._title_canvas.create_window(30, 22, window=title_frame, anchor=tk.W)

        # 右侧状态区（融入右侧渐变末色）
        right_frame = tk.Frame(self._title_canvas, bg=title_gradient_end)

        self.connection_indicator = tk.Canvas(right_frame, width=10, height=10,
                                              bg=title_gradient_end, highlightthickness=0, borderwidth=0)
        self.connection_indicator.pack(side=tk.LEFT, padx=(0, 5))
        self._draw_indicator("#B0B0BB")

        self.connection_label = tk.Label(right_frame, text="未连接",
                                          font=("Microsoft YaHei", 8),
                                          fg=gui_style.TEXT_SECONDARY, bg=title_gradient_end)
        self.connection_label.pack(side=tk.LEFT)

        # 记录状态指示器
        self.record_indicator = tk.Canvas(right_frame, width=10, height=10,
                                           bg=title_gradient_end, highlightthickness=0, borderwidth=0)
        self.record_indicator.pack(side=tk.LEFT, padx=(15, 5))
        self._draw_record_indicator("gray")
        
        self.record_label = tk.Label(right_frame, text="未记录",
                                     font=("Microsoft YaHei", 8),
                                     fg=gui_style.TEXT_SECONDARY, bg=title_gradient_end)
        self.record_label.pack(side=tk.LEFT)

        self.msg_counter_label = tk.Label(right_frame, text="",
                                           font=("Microsoft YaHei", 8),
                                           fg=gui_style.TEXT_SECONDARY, bg=title_gradient_end)
        self.msg_counter_label.pack(side=tk.RIGHT, padx=(20, 0))
        # 右侧区域靠右放置 (在 resize 时重新定位)
        self._title_right_frame = right_frame
        self._title_canvas.create_window(0, 22, window=right_frame, anchor=tk.E, tags=("right",))

    def _on_titlebar_resize(self, event):
        """标题栏 resize 时重绘渐变并重新定位右侧控件"""
        self._draw_gradient(self._title_canvas)
        # 右侧区域贴右边缘
        self._title_canvas.coords("right", event.width - 12, 22)

    def _draw_gradient(self, canvas: tk.Canvas):
        """在 Canvas 上绘制左到右的浅橙色渐变"""
        canvas.delete("gradient")
        width = canvas.winfo_width()
        height = canvas.winfo_height()
        if width < 10 or height < 4:
            return

        # 渐变: 左侧微暖橙 → 右侧浅暖橙
        start_r, start_g, start_b = 255, 201, 146   # #FFC992
        end_r, end_g, end_b   = 255, 233, 210       # #FFE9D2

        step = 2
        for x in range(0, width, step):
            ratio = x / max(width - 1, 1)
            r = int(start_r + (end_r - start_r) * ratio)
            g = int(start_g + (end_g - start_g) * ratio)
            b = int(start_b + (end_b - start_b) * ratio)
            color = f"#{r:02X}{g:02X}{b:02X}"
            canvas.create_rectangle(x, 0, x + step, height, fill=color, outline="", tags="gradient")

    def _draw_indicator(self, color):
        c = self.connection_indicator
        c.delete("all")
        c.create_oval(2, 2, 10, 10, fill=color, outline="")

    def _draw_record_indicator(self, color):
        c = self.record_indicator
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
        self.receive_panel.record_btn.configure(command=self._on_toggle_record)
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

    def _on_browse_record(self):
        """浏览选择报文记录文件"""
        filepath = filedialog.asksaveasfilename(
            title="选择报文记录文件",
            defaultextension=".asc",
            filetypes=[("ASC 文件", "*.asc"), ("所有文件", "*.*")]
        )
        if filepath:
            self.config_panel.record_path_var.set(filepath)
            self.recording_path = filepath

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
                can_filters=self.can_filter.to_can_filters(),  # 移除硬件过滤器，使用软件过滤
            )

            print( self.can_filter.to_can_filters() )
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
                                        fg=gui_style.GREEN)
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
                                        fg=gui_style.TEXT_SECONDARY)
        self.statusbar.configure(text="已断开连接")

    def _on_mode_changed(self, event=None):
        cp = self.config_panel
        if cp.is_fd_mode():
            cp.fd_bitrate_combo.configure(state="readonly")
        else:
            cp.fd_bitrate_combo.configure(state=tk.DISABLED)

    # ==================== 发送回调 ====================

    def _add_sent_message(self, can_id, data, is_fd, is_extended=False):
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
            "bitrate_switch": is_fd,     # 添加BRS标志，与发送时的设置一致
            "is_extended": is_extended,
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
                        self._add_sent_message(can_id, data, is_fd, is_extended)
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
                cb = lambda cid, d, fd=is_fd, ext=is_extended: self._add_sent_message(cid, d, fd, ext)
                self.sender.start_cyclic(can_id, data, sp.get_period_ms(),
                                         is_extended, is_fd, on_send=cb)
                sp.send_status_var.set(f"循环中 0x{can_id:X} @{sp.get_period_ms()}ms")
                sp.send_btn.configure(state=tk.DISABLED)
                sp.stop_send_btn.configure(state=tk.NORMAL)
                self.statusbar.configure(text=f"DBC 循环发送: 0x{can_id:X}")

            elif mode == "循环随机":
                msg_obj = self.dbc_loader.db.get_message_by_frame_id(can_id)
                dlc = msg_obj.length if msg_obj else 8
                cb = lambda cid, d, fd=is_fd, ext=is_extended: self._add_sent_message(cid, d, fd, ext)
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
                    self._add_sent_message(can_id, data, is_fd, is_extended)
                    sp.send_status_var.set(f"已发送 0x{can_id:X}")
                    self.statusbar.configure(text=f"发送: 0x{can_id:X}")
                except Exception as e:
                    sp.send_status_var.set(f"失败: {e}")

            elif mode == "循环":
                data = sp.get_raw_data_bytes()
                if data is None:
                    messagebox.showwarning("提示", "数据格式无效")
                    return
                cb = lambda cid, d, fd=is_fd, ext=is_extended: self._add_sent_message(cid, d, fd, ext)
                self.sender.start_cyclic(can_id, data, sp.get_period_ms(),
                                         is_extended, is_fd, on_send=cb)
                sp.send_status_var.set(f"循环中 0x{can_id:X} @{sp.get_period_ms()}ms")
                sp.send_btn.configure(state=tk.DISABLED)
                sp.stop_send_btn.configure(state=tk.NORMAL)
                self.statusbar.configure(text=f"循环发送: 0x{can_id:X}")

            elif mode == "循环随机":
                dlc = sp.get_raw_dlc()
                cb = lambda cid, d, fd=is_fd, ext=is_extended: self._add_sent_message(cid, d, fd, ext)
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

    def _on_toggle_record(self):
        """切换报文记录状态"""
        if self.bus_manager.is_recording():
            # 停止记录
            self.bus_manager.stop_recording()
            self._draw_record_indicator("gray")
            self.record_label.configure(text="未记录", fg=gui_style.TEXT_SECONDARY)
            self.receive_panel.record_btn.configure(text="开启报文记录器")
            self.statusbar.configure(text="已停止报文记录")
        else:
            # 开始记录
            if not self.bus_manager.is_connected:
                messagebox.showwarning("提示", "请先连接 CAN 总线")
                return
                
            # 始终使用自动生成的默认路径
            from datetime import datetime
            timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
            record_path = f"can_log_{timestamp}.asc"
            
            try:
                self.bus_manager.start_recording(record_path)
                self._draw_record_indicator(gui_style.GREEN)
                self.record_label.configure(text="记录中", fg=gui_style.GREEN)
                self.receive_panel.record_btn.configure(text="关闭报文记录器")
                self.statusbar.configure(text=f"开始记录到文件: {record_path}")
            except Exception as e:
                messagebox.showerror("记录失败", str(e))
                self._draw_record_indicator("gray")
                self.record_label.configure(text="未记录", fg=gui_style.TEXT_SECONDARY)
                self.receive_panel.record_btn.configure(text="开启报文记录器")
                self.statusbar.configure(text="报文记录启动失败")

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
                    
                    # 记录功能由 BusRecorder 透明代理处理，无需手动写入
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
