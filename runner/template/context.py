"""
上下文管理系统

负责管理模板执行过程中的各种上下文信息，包括全局上下文、
会话上下文、模板上下文等。支持上下文继承、作用域管理等。
"""

import re
from typing import Any, Dict, List, Optional, Union, Tuple
from .types import ContextScope
from .exceptions import ContextError, ContextNotFoundError, ContextAccessError


class ContextManager:
    """上下文管理器

    管理多层级的上下文信息，支持：
    - 全局上下文：所有测试共享
    - 会话上下文：当前测试会话
    - 模板上下文：当前模板执行
    - 步骤上下文：当前步骤执行
    """

    def __init__(self):
        """初始化上下文管理器"""
        # 多层级上下文存储
        self._contexts: Dict[ContextScope, Dict[str, Any]] = {
            ContextScope.GLOBAL: {},
            ContextScope.SESSION: {},
            ContextScope.TEMPLATE: {},
            ContextScope.STEP: {},
        }

        # 上下文继承链
        self._inheritance_chain = [
            ContextScope.STEP,
            ContextScope.TEMPLATE,
            ContextScope.SESSION,
            ContextScope.GLOBAL,
        ]

        # 上下文变量栈（用于作用域管理）
        self._variable_stack: List[Tuple[ContextScope, Dict[str, Any]]] = []

        # 默认全局上下文
        self._init_default_global_context()

    def _init_default_global_context(self):
        """初始化默认全局上下文"""
        self.set_global("system", {
            "name": "Midscene Test System",
            "version": "1.0.0",
            "environment": "production",
        })

        self.set_global("browser", {
            "viewportWidth": 1280,
            "viewportHeight": 768,
            "userAgent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36",
        })

    def set_global(self, key: str, value: Any):
        """设置全局上下文变量"""
        self._contexts[ContextScope.GLOBAL][key] = value

    def get_global(self, key: str, default: Any = None) -> Any:
        """获取全局上下文变量"""
        return self._contexts[ContextScope.GLOBAL].get(key, default)

    def set_session(self, session_id: str, key: str, value: Any):
        """设置会话上下文变量"""
        if ContextScope.SESSION not in self._contexts:
            self._contexts[ContextScope.SESSION] = {}
        if session_id not in self._contexts[ContextScope.SESSION]:
            self._contexts[ContextScope.SESSION][session_id] = {}
        self._contexts[ContextScope.SESSION][session_id][key] = value

    def get_session(self, session_id: str, key: str, default: Any = None) -> Any:
        """获取会话上下文变量"""
        session_context = self._contexts.get(ContextScope.SESSION, {})
        return session_context.get(session_id, {}).get(key, default)

    def set_template(self, key: str, value: Any):
        """设置模板上下文变量"""
        self._contexts[ContextScope.TEMPLATE][key] = value

    def get_template(self, key: str, default: Any = None) -> Any:
        """获取模板上下文变量"""
        return self._contexts[ContextScope.TEMPLATE].get(key, default)

    def set_step(self, key: str, value: Any):
        """设置步骤上下文变量"""
        self._contexts[ContextScope.STEP][key] = value

    def get_step(self, key: str, default: Any = None) -> Any:
        """获取步骤上下文变量"""
        return self._contexts[ContextScope.STEP].get(key, default)

    def set(self, key: str, value: Any, scope: ContextScope = ContextScope.GLOBAL):
        """设置指定作用域的上下文变量"""
        if scope not in self._contexts:
            self._contexts[scope] = {}
        self._contexts[scope][key] = value

    def get(self, key: str, scope: ContextScope = ContextScope.GLOBAL, default: Any = None) -> Any:
        """获取指定作用域的上下文变量

        如果在指定作用域未找到，会按照继承链向上查找。
        """
        # 直接从指定作用域获取
        if scope in self._contexts and key in self._contexts[scope]:
            return self._contexts[scope][key]

        # 按照继承链向上查找
        for inherited_scope in self._inheritance_chain:
            if inherited_scope == scope:
                continue
            if inherited_scope in self._contexts and key in self._contexts[inherited_scope]:
                return self._contexts[inherited_scope][key]

        return default

    def get_with_inheritance(self, key: str) -> Any:
        """获取变量值（支持继承查找）"""
        return self.get(key)

    def has(self, key: str, scope: Optional[ContextScope] = None) -> bool:
        """检查变量是否存在"""
        if scope:
            return scope in self._contexts and key in self._contexts[scope]
        else:
            # 在所有作用域中查找
            for context in self._contexts.values():
                if key in context:
                    return True
            return False

    def delete(self, key: str, scope: ContextScope):
        """删除指定作用域的变量"""
        if scope in self._contexts and key in self._contexts[scope]:
            del self._contexts[scope][key]

    def clear_scope(self, scope: ContextScope):
        """清空指定作用域的所有变量"""
        if scope in self._contexts:
            self._contexts[scope].clear()

    def clear_all(self):
        """清空所有上下文"""
        for scope in self._contexts:
            self._contexts[scope].clear()

    def push_context(self, scope: ContextScope, variables: Dict[str, Any]):
        """推送上下文变量到栈"""
        # 保存当前上下文状态
        current_state = {}
        if scope in self._contexts:
            current_state = self._contexts[scope].copy()

        self._variable_stack.append((scope, current_state))

        # 更新上下文
        if scope not in self._contexts:
            self._contexts[scope] = {}
        self._contexts[scope].update(variables)

    def pop_context(self) -> bool:
        """从栈中弹出上下文变量

        Returns:
            bool: 是否成功弹出了上下文
        """
        if not self._variable_stack:
            return False

        scope, previous_values = self._variable_stack.pop()
        self._contexts[scope] = previous_values
        return True

    def get_all_contexts(self) -> Dict[ContextScope, Dict[str, Any]]:
        """获取所有上下文（用于调试）"""
        return {
            scope: context.copy()
            for scope, context in self._contexts.items()
        }

    def merge_contexts(self, *contexts: Dict[str, Any]) -> Dict[str, Any]:
        """合并多个上下文字典

        后面的上下文会覆盖前面的同名变量。
        """
        merged = {}
        for context in contexts:
            if context:
                merged.update(context)
        return merged

    def update_global(self, variables: Dict[str, Any]):
        """批量更新全局上下文"""
        self._contexts[ContextScope.GLOBAL].update(variables)

    def update_session(self, session_id: str, variables: Dict[str, Any]):
        """批量更新会话上下文"""
        if ContextScope.SESSION not in self._contexts:
            self._contexts[ContextScope.SESSION] = {}
        if session_id not in self._contexts[ContextScope.SESSION]:
            self._contexts[ContextScope.SESSION][session_id] = {}
        self._contexts[ContextScope.SESSION][session_id].update(variables)

    def update_template(self, variables: Dict[str, Any]):
        """批量更新模板上下文"""
        self._contexts[ContextScope.TEMPLATE].update(variables)

    def update_step(self, variables: Dict[str, Any]):
        """批量更新步骤上下文"""
        self._contexts[ContextScope.STEP].update(variables)

    def get_context_for_template(self, template_context: Optional[Dict[str, Any]] = None) -> Dict[str, Any]:
        """获取模板执行时的完整上下文

        合并全局、会话和模板上下文，模板上下文优先级最高。
        """
        # 从继承链中收集所有上下文
        all_contexts = []

        # 添加全局上下文
        global_context = self._contexts.get(ContextScope.GLOBAL, {})
        if global_context:
            all_contexts.append(global_context)

        # 添加会话上下文
        session_context = self._contexts.get(ContextScope.SESSION, {})
        if session_context:
            # 如果会话上下文是嵌套的，需要展平
            flattened_session = {}
            for session_id, session_vars in session_context.items():
                for key, value in session_vars.items():
                    flattened_session[f"session.{key}"] = value
            all_contexts.append(flattened_session)

        # 添加模板上下文
        template_context_vars = self._contexts.get(ContextScope.TEMPLATE, {})
        if template_context_vars:
            all_contexts.append(template_context_vars)

        # 添加传入的模板上下文
        if template_context:
            all_contexts.append(template_context)

        # 合并所有上下文
        merged = self.merge_contexts(*all_contexts)
        return merged

    def substitute_variables(self, text: str, context: Optional[Dict[str, Any]] = None) -> str:
        """在文本中替换变量引用

        支持以下格式：
        - ${variable_name} - 简单变量引用
        - ${variable_name:default_value} - 带默认值的变量引用
        - ${nested.var.name} - 嵌套变量引用

        Args:
            text: 包含变量引用的文本
            context: 可选的上下文字典，如果不提供则使用当前上下文

        Returns:
            替换变量后的文本
        """
        if not text or "${" not in text:
            return text

        # 获取使用的上下文
        if context is None:
            context = self.get_context_for_template()

        # 变量引用模式：${var} 或 ${var:default}
        pattern = r'\$\{([^}:]+)(?::([^}]*))?\}'

        def replace_var(match):
            var_path = match.group(1).strip()
            default_value = match.group(2) if match.group(2) is not None else None

            # 支持点分隔的嵌套路径
            value = self._get_nested_value(context, var_path)

            if value is None:
                if default_value is not None:
                    return default_value
                # 如果没有默认值，保留原始引用
                return match.group(0)

            # 转换为字符串
            return str(value)

        return re.sub(pattern, replace_var, text)

    def _get_nested_value(self, context: Dict[str, Any], path: str) -> Any:
        """获取嵌套字典的值

        Args:
            context: 上下文字典
            path: 点分隔的路径，如 "user.name"

        Returns:
            嵌套的值，如果路径不存在则返回 None
        """
        keys = path.split('.')
        value = context

        try:
            for key in keys:
                value = value[key]
            return value
        except (KeyError, TypeError):
            return None

    def set_variable_from_path(self, context: Dict[str, Any], path: str, value: Any):
        """设置嵌套字典的值

        Args:
            context: 上下文字典
            path: 点分隔的路径
            value: 要设置的值
        """
        keys = path.split('.')
        target = context

        # 导航到父级字典
        for key in keys[:-1]:
            if key not in target:
                target[key] = {}
            target = target[key]

        # 设置值
        target[keys[-1]] = value

    def __repr__(self) -> str:
        """字符串表示"""
        return f"ContextManager(contexts={list(self._contexts.keys())})"
