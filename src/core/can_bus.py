"""
Kvaser CAN 总线管理 - 单例模式
整个项目中唯一的 can.Bus 实例。
"""

import can


class KvaserBusManager:
    """Kvaser CAN 总线管理器，全局单例"""

    _instance = None

    def __new__(cls):
        if cls._instance is None:
            cls._instance = super().__new__(cls)
            cls._instance._bus = None
            cls._instance._running = False
        return cls._instance

    def connect(self, channel, bitrate, data_bitrate=None, fd=True, can_filters=None):
        """连接 Kvaser CAN 总线
        
        Args:
            channel: CAN 通道号
            bitrate: 仲裁域比特率
            data_bitrate: FD 数据域比特率 (CAN FD 模式时需要)
            fd: 是否启用 CAN FD
            can_filters: CAN ID 过滤列表
        """
        if self._bus is not None:
            self.disconnect()

        kwargs = {
            "interface": "kvaser",
            "channel": channel,
            "bitrate": int(bitrate),
            "fd": fd,
        }
        if fd and data_bitrate:
            kwargs["data_bitrate"] = int(data_bitrate)
        if can_filters:
            kwargs["can_filters"] = can_filters

        self._bus = can.interface.Bus(**kwargs)
        self._running = True

    def disconnect(self):
        """断开 CAN 总线连接"""
        self._running = False
        if self._bus is not None:
            try:
                self._bus.shutdown()
            except Exception:
                pass
            self._bus = None

    @property
    def bus(self):
        """获取底层 can.Bus 对象"""
        return self._bus

    @property
    def is_connected(self):
        """是否已连接"""
        return self._bus is not None and self._running

    def send(self, msg):
        """发送一条 CAN 报文"""
        if self._bus is not None:
            self._bus.send(msg)

    def recv(self, timeout=0.5):
        """接收一条 CAN 报文（阻塞）"""
        if self._bus is not None:
            return self._bus.recv(timeout=timeout)
        return None
