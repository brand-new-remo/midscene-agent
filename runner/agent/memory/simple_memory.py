"""
简单记忆组件
用于存储和管理AI执行过程中的操作历史和上下文信息
"""

from dataclasses import dataclass, asdict
from typing import Any, Dict, List, Optional
import json
import time
import logging

# 配置日志
logger = logging.getLogger(__name__)


@dataclass
class MemoryRecord:
    """记忆记录"""
    timestamp: float
    action: str
    params: Dict[str, Any]
    result: Any
    context: Dict[str, Any]  # 页面上下文
    success: bool = True     # 操作是否成功
    error_message: Optional[str] = None  # 错误信息（如果有）


class SimpleMemory:
    """简单记忆组件

    用于在AI执行过程中存储和检索操作历史，
    帮助AI记住之前执行过的操作和结果，避免重复执行。
    """

    def __init__(self, max_size: int = 100):
        """初始化记忆组件

        Args:
            max_size: 最大记忆记录数量，超过时会删除最旧的记录
        """
        self.max_size = max_size
        self.records: List[MemoryRecord] = []
        self.page_context: Dict[str, Any] = {}

    def add_record(
        self,
        action: str,
        params: Dict[str, Any],
        result: Any,
        context: Optional[Dict[str, Any]] = None,
        success: bool = True,
        error_message: Optional[str] = None
    ) -> None:
        """添加记忆记录

        Args:
            action: 操作类型（如 'navigate', 'click', 'input'）
            params: 操作参数
            result: 操作结果
            context: 页面上下文（如 URL、标题等）
            success: 操作是否成功
            error_message: 错误信息（如果操作失败）
        """
        record = MemoryRecord(
            timestamp=time.time(),
            action=action,
            params=params,
            result=result,
            context=context or self.page_context,
            success=success,
            error_message=error_message
        )

        self.records.append(record)

        # 保持最大大小限制
        if len(self.records) > self.max_size:
            removed_record = self.records.pop(0)
            logger.debug(f"移除最旧的记忆记录: {removed_record.action}")

    def update_context(self, context: Dict[str, Any]) -> None:
        """更新页面上下文

        Args:
            context: 新的页面上下文信息
        """
        self.page_context.update(context)
        logger.debug(f"更新页面上下文: {context}")

    def get_recent_actions(self, limit: int = 10) -> List[MemoryRecord]:
        """获取最近的操作记录

        Args:
            limit: 返回记录的最大数量

        Returns:
            最近的记忆记录列表
        """
        return self.records[-limit:] if self.records else []

    def get_successful_actions(self, limit: int = 10) -> List[MemoryRecord]:
        """获取最近成功的操作记录

        Args:
            limit: 返回记录的最大数量

        Returns:
            最近成功的记忆记录列表
        """
        successful_records = [r for r in self.records if r.success]
        return successful_records[-limit:] if successful_records else []

    def find_similar_action(
        self,
        action: str,
        params: Dict[str, Any],
        time_window: float = 300  # 5分钟
    ) -> Optional[MemoryRecord]:
        """查找相似的历史操作

        Args:
            action: 操作类型
            params: 操作参数
            time_window: 时间窗口（秒）

        Returns:
            找到的相似记录，如果没有则返回None
        """
        current_time = time.time()

        # 从最新的记录开始查找
        for record in reversed(self.records):
            # 检查时间窗口
            if current_time - record.timestamp > time_window:
                break

            # 检查操作类型和参数
            if record.action == action and self._params_similar(record.params, params):
                logger.debug(f"找到相似操作: {action}, 参数: {params}")
                return record

        return None

    def _params_similar(self, params1: Dict[str, Any], params2: Dict[str, Any]) -> bool:
        """检查两个参数字典是否相似

        Args:
            params1: 参数字典1
            params2: 参数字典2

        Returns:
            如果参数相似返回True，否则返回False
        """
        # 简单实现：检查JSON序列化后是否相等
        # 未来可以扩展为更智能的相似度匹配
        try:
            return json.dumps(params1, sort_keys=True) == json.dumps(params2, sort_keys=True)
        except (TypeError, ValueError):
            return False

    def get_action_history(self, action_type: Optional[str] = None) -> List[MemoryRecord]:
        """获取操作历史

        Args:
            action_type: 如果指定，只返回该类型的操作记录

        Returns:
            操作历史记录列表
        """
        if action_type:
            return [r for r in self.records if r.action == action_type]
        return self.records.copy()

    def get_last_action(self) -> Optional[MemoryRecord]:
        """获取最后一个操作记录

        Returns:
            最后一个操作记录，如果没有记录则返回None
        """
        return self.records[-1] if self.records else None

    def get_success_rate(self, action_type: Optional[str] = None) -> float:
        """计算操作成功率

        Args:
            action_type: 如果指定，只计算该类型的操作成功率

        Returns:
            成功率（0.0 到 1.0）
        """
        if action_type:
            records = [r for r in self.records if r.action == action_type]
        else:
            records = self.records

        if not records:
            return 1.0  # 没有记录时返回100%成功率

        successful_count = sum(1 for r in records if r.success)
        return successful_count / len(records)

    def get_recent_context(self, limit: int = 5) -> str:
        """构建最近操作的上下文描述

        Args:
            limit: 包含的最近操作数量

        Returns:
            格式化的上下文描述字符串
        """
        recent_actions = self.get_recent_actions(limit)

        if not recent_actions:
            return "无历史操作记录"

        lines = ["=== 最近操作历史 ==="]
        for record in recent_actions:
            status = "✅" if record.success else "❌"
            lines.append(
                f"{status} [{record.action}] "
                f"参数: {record.params}, "
                f"结果: {self._format_result(record.result)}, "
                f"页面: {record.context.get('url', 'unknown')}"
            )

        return "\n".join(lines)

    def _format_result(self, result: Any) -> str:
        """格式化操作结果

        Args:
            result: 操作结果

        Returns:
            格式化的结果字符串
        """
        if isinstance(result, dict):
            # 如果是字典，只显示关键字段
            key_fields = ['success', 'message', 'title', 'url']
            formatted = {k: v for k, v in result.items() if k in key_fields}
            return str(formatted) if formatted else str(result)[:100]
        elif isinstance(result, str) and len(result) > 100:
            return result[:100] + "..."
        return str(result)

    def to_dict(self) -> Dict[str, Any]:
        """序列化记忆到字典

        Returns:
            包含所有记忆数据的字典
        """
        return {
            "records": [asdict(r) for r in self.records],
            "page_context": self.page_context,
            "max_size": self.max_size,
            "created_at": time.time()
        }

    def from_dict(self, data: Dict[str, Any]) -> None:
        """从字典反序列化记忆

        Args:
            data: 包含记忆数据的字典
        """
        try:
            self.records = [MemoryRecord(**r) for r in data.get("records", [])]
            self.page_context = data.get("page_context", {})
            logger.info(f"从字典恢复记忆: {len(self.records)} 条记录")
        except Exception as e:
            logger.error(f"从字典恢复记忆失败: {e}")

    def clear(self) -> None:
        """清空所有记忆记录"""
        record_count = len(self.records)
        self.records.clear()
        self.page_context.clear()
        logger.info(f"清空记忆记录: {record_count} 条")

    def get_stats(self) -> Dict[str, Any]:
        """获取记忆统计信息

        Returns:
            包含统计信息的字典
        """
        total_count = len(self.records)
        successful_count = sum(1 for r in self.records if r.success)
        failed_count = total_count - successful_count

        # 统计各操作类型的数量
        action_counts: Dict[str, int] = {}
        for record in self.records:
            action_counts[record.action] = action_counts.get(record.action, 0) + 1

        return {
            "total_records": total_count,
            "successful_records": successful_count,
            "failed_records": failed_count,
            "success_rate": self.get_success_rate(),
            "max_size": self.max_size,
            "current_size": total_count,
            "action_counts": action_counts,
            "page_context": self.page_context.copy()
        }

    def cleanup_old_records(self, max_age: float = 3600) -> int:
        """清理过旧的记录

        Args:
            max_age: 最大年龄（秒），默认1小时

        Returns:
            清理的记录数量
        """
        current_time = time.time()
        old_records = [r for r in self.records if current_time - r.timestamp > max_age]

        for record in old_records:
            self.records.remove(record)

        if old_records:
            logger.info(f"清理过旧记录: {len(old_records)} 条")

        return len(old_records)


class MemoryContextBuilder:
    """记忆上下文构建器

    用于构建包含历史信息的上下文字符串，
    帮助AI了解之前的操作和当前状态。
    """

    def __init__(self, memory: SimpleMemory):
        self.memory = memory

    def build_execution_context(
        self,
        current_task: str,
        include_history: bool = True,
        include_stats: bool = False
    ) -> str:
        """构建执行上下文

        Args:
            current_task: 当前任务描述
            include_history: 是否包含历史操作
            include_stats: 是否包含统计信息

        Returns:
            格式化的执行上下文字符串
        """
        parts = []

        # 当前任务
        parts.append(f"=== 当前任务 ===")
        parts.append(f"{current_task}")

        # 历史操作
        if include_history:
            history = self.memory.get_recent_context(limit=5)
            parts.append(f"\n{history}")

        # 统计信息
        if include_stats:
            stats = self.memory.get_stats()
            parts.append(f"\n=== 统计信息 ===")
            parts.append(f"总操作数: {stats['total_records']}")
            parts.append(f"成功率: {stats['success_rate']:.2%}")

        return "\n".join(parts)

    def build_action_guidance(
        self,
        current_action: str,
        params: Dict[str, Any]
    ) -> str:
        """构建操作指导

        Args:
            current_action: 当前要执行的操作
            params: 操作参数

        Returns:
            包含操作指导的字符串
        """
        # 查找相似的历史操作
        similar_action = self.memory.find_similar_action(current_action, params)

        parts = []
        parts.append(f"=== 操作指导 ===")
        parts.append(f"当前操作: {current_action}")
        parts.append(f"操作参数: {params}")

        if similar_action:
            parts.append(f"\n💡 提示: 之前执行过类似操作")
            parts.append(f"  上次结果: {similar_action.result}")
            if similar_action.success:
                parts.append(f"  上次成功，可以参考之前的做法")
            else:
                parts.append(f"  上次失败，注意避免同样的错误")

        return "\n".join(parts)