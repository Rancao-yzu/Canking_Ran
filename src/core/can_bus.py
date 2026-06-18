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
            cls._instance._logger = None  # ASC记录器
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
        if self._logger is not None:
            self._logger.stop()
            self._logger = None
        if self._bus is not None:
            try:
                self._bus.shutdown()
            except Exception:
                pass
            self._bus = None

    @property
    def is_connected(self):
        """是否已连接"""
        return self._bus is not None and self._running

    def start_recording(self, asc_path):
        """开始记录报文到ASC文件"""
        if self._bus is None:
            raise RuntimeError("总线未连接")
        # 创建ASC记录器
        self._logger = can.ASCWriter(asc_path)

    def stop_recording(self):
        """停止记录报文"""
        if self._logger is not None:
            self._logger.stop()
            self._logger = None

    def is_recording(self):
        """是否正在记录"""
        return self._logger is not None

    def recv(self, timeout=0.5):
        """接收一条 CAN 报文（阻塞）"""
        if self._bus is not None:
            msg = self._bus.recv(timeout=timeout)
            if msg is not None:
                # 如果启用了记录，自动记录报文
                if self._logger is not None:
                    # 确保报文有正确的时间戳
                    import time
                    if msg.timestamp == 0 or msg.timestamp is None:
                        msg.timestamp = time.time()
                        msg.is_rx = True    
                    self._logger(msg)
                return msg
        return None

    def send(self, msg, timeout=None):
        """发送一条 CAN 报文"""
        if self._bus is not None:
            # 如果启用了记录，自动记录报文
            if self._logger is not None:
                import time
                if msg.timestamp == 0 or msg.timestamp is None:
                    msg.timestamp = time.time()
                    msg.is_rx = False    
                self._logger(msg)
            self._bus.send(msg, timeout=timeout)