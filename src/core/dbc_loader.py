"""
DBC 文件加载与解析
"""

import cantools


class DbcLoader:
    """DBC 数据库加载器"""

    def __init__(self):
        self._db = None
        self._filepath = None

    def load(self, filepath: str):
        """加载 DBC 文件
        
        Args:
            filepath: DBC 文件路径
        """
        self._db = cantools.database.load_file(filepath)
        self._filepath = filepath

    @property
    def db(self):
        """获取 cantools 数据库对象"""
        return self._db

    @property
    def is_loaded(self):
        """DBC 是否已加载"""
        return self._db is not None

    @property
    def filepath(self):
        """当前加载的 DBC 文件路径"""
        return self._filepath

    @property
    def message_count(self):
        """DBC 中定义的报文数量"""
        if self._db is not None:
            return len(self._db.messages)
        return 0

    def decode_message(self, arbitration_id, data):
        """解码 CAN 报文数据
        
        Returns:
            dict: {信号名: 信号值} 或 None（解析失败）
        """
        if self._db is not None:
            try:
                return self._db.decode_message(arbitration_id, data)
            except Exception:
                return None
        return None

    def get_message_by_id(self, can_id):
        """根据 CAN ID 查找 DBC 中的报文定义"""
        if self._db is not None:
            try:
                return self._db.get_message_by_frame_id(can_id)
            except Exception:
                return None
        return None

    def encode_message(self, can_id, signals_dict):
        """根据 DBC 定义编码信号值为 CAN 报文数据
        
        Args:
            can_id: CAN ID
            signals_dict: {信号名: 信号值}
        Returns:
            bytes: 编码后的数据，失败返回 None
        """
        if self._db is not None:
            try:
                return self._db.encode_message(can_id, signals_dict)
            except Exception:
                return None
        return None
