"""
CAN 报文接收器
后台线程接收 CAN 报文并通过 DBC 解析后放入队列。
"""

import threading
import queue
import traceback
from datetime import datetime

from core.can_bus import KvaserBusManager
from core.dbc_loader import DbcLoader


class MessageReceiver:
    """CAN 报文接收器"""

    def __init__(self, bus_manager: KvaserBusManager, dbc_loader: DbcLoader = None):
        self._bus_mgr = bus_manager
        self._dbc = dbc_loader
        self._running = False
        self._thread = None
        self._queue = queue.Queue()        # 存放解析后的报文，供 UI 消费

    def start(self):
        """启动接收线程"""
        if self._running:
            return
        self._running = True
        self._thread = threading.Thread(target=self._run, daemon=True)
        self._thread.start()

    def stop(self):
        """停止接收线程"""
        self._running = False
        if self._thread is not None:
            self._thread.join(timeout=2.0)
            self._thread = None

    @property
    def is_running(self):
        return self._running

    @property
    def msg_queue(self):
        """消息队列，供 UI 轮询"""
        return self._queue

    def _run(self):
        """接收循环"""
        while self._running:
            msg = self._bus_mgr.recv(timeout=0.5)
            if msg is not None:
                self._decode_and_enqueue(msg)

    def _decode_and_enqueue(self, msg):
        """将 CAN 报文原始数据放入队列 (不解析, 点击展开时懒解码)"""
        timestamp = datetime.now().strftime("%H:%M:%S.%f")[:-3]
        raw_hex = " ".join(f"{b:02X}" for b in msg.data)
        is_fd = bool(msg.is_fd) if hasattr(msg, "is_fd") else False
        bitrate_switch = bool(msg.bitrate_switch) if hasattr(msg, "bitrate_switch") else False

        self._queue.put({
            "id": msg.arbitration_id,
            "time": timestamp,
            "dlc": msg.dlc,
            "raw": raw_hex,
            "data": list(msg.data),      # 原始字节, 供 UI 懒解码
            "signals": [],               # 不再预解码
            "is_fd": is_fd,
            "bitrate_switch": bitrate_switch,
        })