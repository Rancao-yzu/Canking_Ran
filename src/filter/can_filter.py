"""
CAN ID 筛选器
"""

import can


class CanFilter:
    """CAN ID 筛选器"""

    def __init__(self):
        self._ids = set()         # 允许的 CAN ID 集合（int）
        self._enabled = False     # 筛选是否启用

    # ==================== 添加/移除 ====================

    def add_id(self, can_id: int):
        """添加单个 CAN ID
        
        Args:
            can_id: CAN ID (整型)
        """
        self._ids.add(can_id)

    def remove_id(self, can_id: int):
        """移除单个 CAN ID"""
        self._ids.discard(can_id)

    def clear(self):
        """清空所有筛选条件"""
        self._ids.clear()

    # ==================== 启用/禁用 ====================

    def enable(self):
        """启用筛选"""
        self._enabled = True

    def disable(self):
        """禁用筛选"""
        self._enabled = False

    @property
    def enabled(self):
        return self._enabled

    # ==================== 匹配 ====================

    def match(self, can_id: int) -> bool:
        """检查 CAN ID 是否通过筛选
        
        Returns:
            True 表示通过（或筛选未启用时全部通过）
        """
        if not self._enabled:
            return True
        return can_id in self._ids

    def matches(self, msg) -> bool:
        """检查 can.Message 是否通过筛选"""
        if not self._enabled:
            return True
        return self.match(msg.arbitration_id)

    # ==================== 导出 python-can 格式 ====================

    def to_can_filters(self):
        """导出为 python-can 的 can_filters 格式
        
        用于 Bus 初始化时设置硬件过滤。
        """
        if not self._enabled or not self._ids:
            return None
        filters = []
        for cid in self._ids:
            filters.append({"can_id": cid, "can_mask": 0x7FF, "extended": False})
            filters.append({"can_id": cid, "can_mask": 0x7FF, "extended": True})
        return filters

    # ==================== 查询 ====================

    @property
    def ids(self):
        """当前筛选的 ID 集合"""
        return self._ids.copy()

    @property
    def count(self):
        """筛选条件数量"""
        return len(self._ids)

    def __str__(self):
        parts = [f"0x{cid:X}" for cid in sorted(self._ids)]
        return f"CAN ID 筛选 [{', '.join(parts)}]" if parts else "CAN ID 筛选 (无)"
