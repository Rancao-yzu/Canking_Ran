"""
CAN 报文展示面板 - 支持按 CAN ID 折叠分组
DBC 解析为懒加载: 点击展开时解码, 默认不解析以减少性能开销
"""
import time
import tkinter as tk
from tkinter import ttk

import gui_style

MAX_MESSAGES = 200


class ReceivePanel(ttk.LabelFrame):
    """报文展示面板 (DBC 解析为懒加载, 点击展开时解码)"""

    def __init__(self, parent):
        super().__init__(parent, text="实时报文", style="Card.TLabelframe", padding=4)
        self._dbc_loader = None
        self._msg_count = 0
        self._auto_scroll = True
        self._group_enabled = True         # 默认按 CAN ID 折叠
        self._paused = False              # 界面更新是否暂停
        self._group_data = {}              # {can_id: {"item": iid, "count": N, "data": dict}}
        self._decoded_items = set()        # 已解码的 item iid, 避免重复解码
        self._setup_ui()

    def set_dbc_loader(self, dbc_loader):
        """设置 DBC 加载器, 供懒解码使用"""
        self._dbc_loader = dbc_loader

    def _setup_ui(self):
        # ---- 工具栏 ----
        toolbar = ttk.Frame(self)
        toolbar.pack(fill=tk.X, pady=(0, 4))

        self.clear_btn = ttk.Button(toolbar, text="清空全部", style="Secondary.TButton")
        self.clear_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.group_btn = ttk.Button(toolbar, text="逐条显示", style="Secondary.TButton")
        self.group_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.record_btn = ttk.Button(toolbar, text="开启报文记录器", style="Primary.TButton")
        self.record_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.pause_btn = ttk.Button(toolbar, text="暂停", style="Secondary.TButton")
        self.pause_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.replay_btn = ttk.Button(toolbar, text="导入回放", style="Secondary.TButton")
        self.replay_btn.pack(side=tk.LEFT, padx=(0, 6))

        self.msg_count_label = ttk.Label(toolbar, text="报文: 0 条",
                                         style="Secondary.TLabel")
        self.msg_count_label.pack(side=tk.LEFT)

        # ---- Treeview 容器 ----
        tree_frame = ttk.Frame(self)
        tree_frame.pack(fill=tk.BOTH, expand=True)
        tree_frame.rowconfigure(0, weight=1)
        tree_frame.columnconfigure(0, weight=1)

        columns = ("id", "time", "dlc", "raw")
        self.msg_tree = ttk.Treeview(tree_frame, columns=columns,
                                     show="tree headings", selectmode="browse")
        self.msg_tree.heading("#0", text="")
        self.msg_tree.heading("id", text="CAN ID")
        self.msg_tree.heading("time", text="时间")
        self.msg_tree.heading("dlc", text="DLC")
        self.msg_tree.heading("raw", text="原始数据 (Hex) / 解析信号")

        self.msg_tree.column("#0", width=30, stretch=False)
        self.msg_tree.column("id", width=110, anchor=tk.CENTER)
        self.msg_tree.column("time", width=120, anchor=tk.CENTER)
        self.msg_tree.column("dlc", width=46, anchor=tk.CENTER)
        self.msg_tree.column("raw", width=520)

        self.v_scroll = ttk.Scrollbar(tree_frame, orient=tk.VERTICAL, command=self._on_scroll)
        h_scroll = ttk.Scrollbar(tree_frame, orient=tk.HORIZONTAL, command=self.msg_tree.xview)
        self.msg_tree.configure(yscrollcommand=self._on_tree_yscroll, xscrollcommand=h_scroll.set)
        self.msg_tree.grid(row=0, column=0, sticky="nsew")
        self.v_scroll.grid(row=0, column=1, sticky="ns")
        h_scroll.grid(row=1, column=0, sticky="ew")

        gui_style.configure_tree_tags(self.msg_tree)

        self.msg_tree.bind("<Double-1>", self._on_double_click)
        self.msg_tree.bind("<<TreeviewOpen>>", self._on_tree_open)

    # ---- 滚动控制 ----

    def _on_tree_yscroll(self, first, last):
        """树视图滚动时更新自动滚动状态 (覆盖鼠标滚轮和拖动滚动条)"""
        try:
            self._auto_scroll = (float(last) >= 1.0)
        except (ValueError, TypeError):
            pass
        self.v_scroll.set(first, last)

    def _on_scroll(self, *args):
        if args[1]:
            try:
                self._auto_scroll = (float(args[1]) >= 1.0)
            except ValueError:
                pass
        self.msg_tree.yview(*args[:2])

    # ==================== 懒解码 ====================

    def _decode_data(self, data: dict):
        """根据原始字节懒解码 DBC 信号, 返回信号列表"""
        if self._dbc_loader is None or not self._dbc_loader.is_loaded:
            return []
        raw_bytes = data.get("data")
        if not raw_bytes:
            return []
        decoded = self._dbc_loader.decode_message(data["id"], bytes(raw_bytes))
        if decoded:
            return [(name, val) for name, val in decoded.items()]
        return []

    def _add_placeholder_child(self, parent, data: dict):
        """添加占位子行: 展开前显示 '点击展开查看 DBC 解析'"""
        self.msg_tree.insert(parent, tk.END,
                             values=("", "", "", "    点击展开查看 DBC 解析"),
                             tags=("placeholder",))

    def _rebuild_placeholder(self, parent, data: dict):
        """重建占位子行 (用于折叠模式下更新)"""
        for child in self.msg_tree.get_children(parent):
            self.msg_tree.delete(child)
        self._add_placeholder_child(parent, data)

    def _lazy_decode_and_fill(self, parent, data: dict):
        """懒解码并填充信号子行"""
        # 清除占位行
        for child in self.msg_tree.get_children(parent):
            self.msg_tree.delete(child)
        # 解码并填充
        signals = self._decode_data(data)
        if signals:
            for sig_name, sig_val in signals:
                display_val = f"{sig_val:.6g}" if isinstance(sig_val, float) else str(sig_val)
                self.msg_tree.insert(parent, tk.END,
                                     values=("", "", "", f"    {sig_name} = {display_val}"),
                                     tags=("signal",))
        else:
            self.msg_tree.insert(parent, tk.END,
                                 values=("", "", "", "    (无 DBC 或解析失败)"),
                                 tags=("no_signal",))
        self._decoded_items.add(parent)

    def _rebuild_signal_children(self, parent, data: dict):
        """重建信号子行 (用于折叠模式下更新)"""
        for child in self.msg_tree.get_children(parent):
            self.msg_tree.delete(child)
        signals = self._decode_data(data)
        if signals:
            for sig_name, sig_val in signals:
                display_val = f"{sig_val:.6g}" if isinstance(sig_val, float) else str(sig_val)
                self.msg_tree.insert(parent, tk.END,
                                     values=("", "", "", f"    {sig_name} = {display_val}"),
                                     tags=("signal",))
        else:
            self.msg_tree.insert(parent, tk.END,
                                 values=("", "", "", "    (无 DBC 或解析失败)"),
                                 tags=("no_signal",))
        self._decoded_items.add(parent)

    # ==================== 添加报文 ====================

    def add_message(self, data: dict):
        if self._group_enabled:
            self._add_grouped(data)
        else:
            self._add_individual(data)

    def _add_individual(self, data: dict):
        """逐条模式：每条报文独立一行, 信号子行点击展开时懒解码"""
        children = self.msg_tree.get_children("")
        if len(children) >= MAX_MESSAGES:
            oldest = children[0]
            self._decoded_items.discard(oldest)
            self.msg_tree.delete(oldest)
            self._msg_count -= 1

        is_fd = data.get("is_fd", False)
        bitrate_switch = data.get("bitrate_switch", False)
        is_extended = data.get("is_extended", False)
        
        # 构建前缀
        prefix_parts = []
        if is_fd and bitrate_switch:
            prefix_parts.append("[FDB]")
        elif is_fd:
            prefix_parts.append("[FD]")
            
        if is_extended:
            prefix_parts.append("[EXT]")
        else:
            prefix_parts.append("[STD]")
            
        prefix = " ".join(prefix_parts) + " " if prefix_parts else ""
        
        msg_id_hex = f"{prefix}0x{data['id']:X}"
        iid = f"msg_{self._msg_count}_{data['id']}_{time.time()}"
        parent = self.msg_tree.insert("", tk.END, iid=iid,
                                      values=(msg_id_hex, data["time"], data["dlc"], data["raw"]),
                                      open=False)
        # 加占位行, 点击展开时才解码
        self._add_placeholder_child(parent, data)

        self._msg_count += 1
        self._update_count_label()
        self._maybe_scroll()

    def _add_grouped(self, data: dict):
        """折叠模式：相同 CAN ID 合并为一行, 信号子行点击展开时懒解码"""
        can_id = data["id"]
        is_fd = data.get("is_fd", False)
        bitrate_switch = data.get("bitrate_switch", False)
        is_extended = data.get("is_extended", False)
        
        # 构建前缀：帧类型 + FD/BRS信息
        frame_type = "[EXT]" if is_extended else "[STD]"
        if is_fd and bitrate_switch:
            fd_prefix = f"{frame_type}[FDB] "
        elif is_fd:
            fd_prefix = f"{frame_type}[FD] "
        else:
            fd_prefix = f"{frame_type} "
        
        msg_id_hex = f"{fd_prefix}0x{can_id:X}"

        if can_id in self._group_data:
            group = self._group_data[can_id]
            group["count"] += 1
            group["data"] = data

            self.msg_tree.item(group["item"],
                               values=(msg_id_hex, data["time"], data["dlc"], data["raw"]))

            # 若已展开显示真实信号, 重新懒解码; 否则只更新占位行
            if group["item"] in self._decoded_items:
                self._decoded_items.discard(group["item"])
                self._rebuild_signal_children(group["item"], data)
            else:
                self._rebuild_placeholder(group["item"], data)

        else:
            children = self.msg_tree.get_children("")
            if len(children) >= MAX_MESSAGES:
                oldest_iid = children[0]
                self._decoded_items.discard(oldest_iid)
                for cid, g in list(self._group_data.items()):
                    if g["item"] == oldest_iid:
                        self._msg_count -= g["count"]
                        del self._group_data[cid]
                        break
                self.msg_tree.delete(oldest_iid)

            iid = f"grp_{can_id}_{time.time()}"
            parent = self.msg_tree.insert("", tk.END, iid=iid,
                                          values=(msg_id_hex, data["time"], data["dlc"], data["raw"]),
                                          open=False)
            self._add_placeholder_child(parent, data)
            self._group_data[can_id] = {"item": parent, "count": 1, "data": data}

        self._msg_count += 1
        self._update_count_label()
        self._maybe_scroll()

    def _update_count_label(self):
        if self._group_enabled:
            unique = len(self._group_data)
            self.msg_count_label.configure(
                text=f"报文: {self._msg_count} 条 | 分组: {unique} 类")
        else:
            self.msg_count_label.configure(text=f"报文: {self._msg_count} 条")

    def _maybe_scroll(self):
        if self._auto_scroll:
            self.msg_tree.yview_moveto(1.0)

    # ==================== 清空 ====================

    def clear(self):
        for item in self.msg_tree.get_children(""):
            self.msg_tree.delete(item)
        self._group_data.clear()
        self._decoded_items.clear()
        self._msg_count = 0
        self._update_count_label()
        self._auto_scroll = True

    # ==================== 折叠开关 ====================

    def toggle_grouping(self):
        """切换折叠模式"""
        self._group_enabled = not self._group_enabled
        self.clear()
        if self._group_enabled:
            self.group_btn.configure(text="逐条显示")
        else:
            self.group_btn.configure(text="折叠相同ID")

    @property
    def group_enabled(self):
        return self._group_enabled

    # ==================== 暂停界面更新 ====================

    def toggle_pause(self):
        """切换暂停更新"""
        self._paused = not self._paused
        if self._paused:
            self.pause_btn.configure(text="恢复")
        else:
            self.pause_btn.configure(text="暂停")

    @property
    def paused(self):
        return self._paused

    @property
    def count(self):
        return self._msg_count

    # ==================== 展开事件 (懒解码入口) ====================

    def _on_tree_open(self, event):
        """用户点击展开 → 触发懒解码"""
        sel = self.msg_tree.selection()
        if not sel:
            return
        item = sel[0]
        # 只处理父行 (报文行), 忽略子行
        if self.msg_tree.parent(item):
            return
        # 已解码则跳过
        if item in self._decoded_items:
            return
        # 从存储中查找对应的原始数据
        data = self._find_data_by_iid(item)
        if data:
            self._lazy_decode_and_fill(item, data)

    def _find_data_by_iid(self, iid):
        """根据 item iid 查找原始报文数据"""
        # 先从普通行的 parent 查找 (需要遍历)
        for parent in self.msg_tree.get_children(""):
            if parent == iid:
                values = self.msg_tree.item(parent, "values")
                if not values or len(values) < 4:
                    return None
                # 从 raw hex 重建 data
                raw_text = values[3]
                raw_hex = raw_text.strip()
                if raw_hex:
                    parts = raw_hex.split()
                    data_bytes = [int(b, 16) for b in parts]
                else:
                    data_bytes = []
                # 从 id 列解析 can_id — 去掉所有 [TAG] 前缀
                id_text = (values[0] or "")
                for tag in ("[FDB]", "[FD]", "[EXT]", "[STD]"):
                    id_text = id_text.replace(tag, "")
                id_text = id_text.replace("0x", "").replace(" ", "").strip()
                try:
                    can_id = int(id_text, 16)
                except ValueError:
                    can_id = 0
                return {"id": can_id, "data": data_bytes}
        return None

    # ==================== 双击交互 ====================

    def _on_double_click(self, event):
        sel = self.msg_tree.selection()
        if not sel:
            return
        item = sel[0]
        parent = self.msg_tree.parent(item)
        values = self.msg_tree.item(item, "values")
        if parent:
            # 信号行：复制值
            text = values[3].strip() if values else ""
            if text:
                root = self.msg_tree.winfo_toplevel()
                root.clipboard_clear()
                root.clipboard_append(text)
        else:
            # 报文行：切换展开/折叠
            if self.msg_tree.item(item, "open"):
                self.msg_tree.item(item, open=False)
            else:
                self.msg_tree.item(item, open=True)
