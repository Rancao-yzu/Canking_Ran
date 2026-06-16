"""
CAN 报文发送器
支持单次发送、循环发送、随机数据发送、DBC 变量发送。
"""

import random
import time
import threading

import can

from core.can_bus import KvaserBusManager
from core.dbc_loader import DbcLoader


class MessageSender:
    """CAN 报文发送器"""

    def __init__(self, bus_manager: KvaserBusManager, dbc_loader: DbcLoader = None):
        self._bus_mgr = bus_manager
        self._dbc = dbc_loader
        self._send_worker = None

    # ==================== 单次发送 ====================

    def send_once(self, can_id: int, data: bytes, is_extended=False, is_fd=False):
        """发送单条 CAN 报文
        
        Args:
            can_id: CAN ID (整型)
            data: 数据载荷 (bytes)
            is_extended: 是否为扩展帧
            is_fd: 是否为 CAN FD 帧
        """
        msg = can.Message(
            arbitration_id=can_id,
            data=data,
            is_extended_id=is_extended,
            is_fd=is_fd,
        )
        self._bus_mgr.send(msg)

    def send_by_dbc(self, can_id: int, signals_dict: dict, is_extended=False, is_fd=False):
        """根据 DBC 信号名和值编码并发送 CAN 报文
        
        Args:
            can_id: CAN ID
            signals_dict: {信号名: 信号值}
            is_extended: 是否为扩展帧
            is_fd: 是否为 CAN FD 帧
        """
        if self._dbc is None or not self._dbc.is_loaded:
            raise RuntimeError("DBC 未加载，无法按 DBC 变量发送")
        data = self._dbc.encode_message(can_id, signals_dict)
        if data is None:
            raise ValueError(f"无法编码 CAN ID=0x{can_id:X} 的信号: {signals_dict}")
        self.send_once(can_id, data, is_extended, is_fd)

    def send_random(self, can_id: int, dlc: int, is_extended=False, is_fd=False):
        """发送随机数据的 CAN 报文
        
        Args:
            can_id: CAN ID
            dlc: 数据长度 (0-64 for FD, 0-8 for non-FD)
            is_extended: 是否为扩展帧
            is_fd: 是否为 CAN FD 帧
        """
        data = bytes(random.randint(0, 255) for _ in range(dlc))
        self.send_once(can_id, data, is_extended, is_fd)

    # ==================== 循环发送 ====================

    def start_cyclic(self, can_id: int, data: bytes, period_ms: float,
                     is_extended=False, is_fd=False, on_send=None):
        """启动循环发送
        
        Args:
            can_id: CAN ID
            data: 数据载荷
            period_ms: 发送周期（毫秒）
            is_extended: 是否为扩展帧
            is_fd: 是否为 CAN FD 帧
            on_send: 每次发送后的回调 func(can_id, data)
        """
        self.stop_cyclic()
        self._send_worker = SendWorker(
            bus_mgr=self._bus_mgr,
            can_id=can_id,
            data=data,
            period_ms=period_ms,
            is_extended=is_extended,
            is_fd=is_fd,
            on_send=on_send,
        )
        self._send_worker.start()

    def start_cyclic_random(self, can_id: int, dlc: int, period_ms: float,
                            is_extended=False, is_fd=False, on_send=None):
        """启动循环随机数据发送
        
        每个周期生成新的随机数据。
        """
        self.stop_cyclic()
        self._send_worker = SendWorker(
            bus_mgr=self._bus_mgr,
            can_id=can_id,
            data=None,          # None 表示每次随机生成
            dlc=dlc,
            period_ms=period_ms,
            is_extended=is_extended,
            is_fd=is_fd,
            random_data=True,
            on_send=on_send,
        )
        self._send_worker.start()

    def stop_cyclic(self):
        """停止循环发送"""
        if self._send_worker is not None:
            self._send_worker.stop()
            self._send_worker = None

    @property
    def is_sending_cyclic(self):
        """是否正在循环发送"""
        return self._send_worker is not None and self._send_worker.running


class SendWorker:
    """循环发送工作线程"""

    def __init__(self, bus_mgr, can_id, data, period_ms,
                 is_extended=False, is_fd=False, dlc=None, random_data=False,
                 on_send=None):
        self._bus_mgr = bus_mgr
        self._can_id = can_id
        self._data = data
        self._period_s = period_ms / 1000.0
        self._is_extended = is_extended
        self._is_fd = is_fd
        self._dlc = dlc
        self._random_data = random_data
        self._on_send = on_send      # 发送回调: func(can_id, data)
        self._running = False
        self._thread = None

    def start(self):
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    @property
    def running(self):
        return self._running

    def _run(self):
        while self._running:
            data = self._data
            if self._random_data:
                data = bytes(random.randint(0, 255) for _ in range(self._dlc))
            msg = can.Message(
                arbitration_id=self._can_id,
                data=data,
                is_extended_id=self._is_extended,
                is_fd=self._is_fd,
            )
            try:
                self._bus_mgr.send(msg)
                if self._on_send:
                    self._on_send(self._can_id, data)
            except Exception:
                pass
            time.sleep(self._period_s)
