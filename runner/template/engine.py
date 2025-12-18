"""
模板引擎

负责模板的解析、编译和展开。支持参数替换、条件执行、
模板嵌套调用等功能。
"""

import copy
import re
from typing import Any, Dict, List, Optional, Set

from .context import ContextManager
from .exceptions import (
    CircularTemplateReferenceError,
    EngineError,
    ParameterError,
    ParameterValidationError,
    TemplateCompilationError,
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
)
from .registry import TemplateRegistry
from .types import CompiledTemplate, Template, TemplateCall, TemplateStep


class TemplateEngine:
    """模板引擎

    负责模板的解析、编译和展开。主要功能：
    - 参数替换：${param} 语法
    - 条件执行：基于上下文的条件判断
    - 模板嵌套：模板可以调用其他模板
    - 上下文注入：自动注入全局和局部上下文
    """

    def __init__(
        self,
        registry: TemplateRegistry,
        context_manager: Optional[ContextManager] = None,
    ):
        """初始化模板引擎

        Args:
            registry: 模板注册表
            context_manager: 可选的上下文管理器，如果不提供则创建新的
        """
        self.registry = registry
        self.context_manager = context_manager or ContextManager()

        # 编译缓存
        self._compiled_cache: Dict[str, CompiledTemplate] = {}

        # 正在编译的模板（用于检测循环引用）
        self._compiling: Set[str] = set()

        # 编译统计
        self._compile_stats = {
            "total_compilations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    async def expand_template_call(
        self,
        template_call: TemplateCall,
        session_id: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """展开模板调用为实际步骤列表

        Args:
            template_call: 模板调用定义
            session_id: 可选的会话ID，用于会话上下文

        Returns:
            展开后的步骤列表

        Raises:
            TemplateNotFoundError: 模板未找到
            TemplateValidationError: 模板验证失败
            TemplateCompilationError: 模板编译失败
        """
        template_name = template_call.name

        # 检查缓存
        cache_key = self._get_cache_key(
            template_name, template_call.parameters, template_call.context
        )
        if cache_key in self._compiled_cache:
            self._compile_stats["cache_hits"] += 1
            compiled_template = self._compiled_cache[cache_key]
        else:
            self._compile_stats["cache_misses"] += 1

            # 获取模板
            try:
                template = self.registry.get_template(template_name)
            except TemplateNotFoundError:
                raise

            # 验证参数
            param_errors = template.validate_parameters(template_call.parameters)
            if param_errors:
                raise TemplateValidationError(template_name, param_errors)

            # 编译模板
            try:
                compiled_template = await self._compile_template(
                    template,
                    template_call.parameters,
                    template_call.context,
                )
            except Exception as e:
                raise TemplateCompilationError(template_name, str(e))

            # 缓存编译结果
            self._compiled_cache[cache_key] = compiled_template

        self._compile_stats["total_compilations"] += 1

        # 设置会话上下文
        if session_id:
            # 将模板上下文设置为会话上下文
            for key, value in compiled_template.context.items():
                self.context_manager.set_session(session_id, key, value)

        return compiled_template.steps

    async def _compile_template(
        self,
        template: Template,
        parameters: Dict[str, Any],
        call_context: Dict[str, Any],
    ) -> CompiledTemplate:
        """编译模板

        Args:
            template: 模板对象
            parameters: 参数值
            call_context: 调用时提供的上下文

        Returns:
            编译后的模板
        """
        template_name = template.name

        # 检测循环引用
        if template_name in self._compiling:
            raise CircularTemplateReferenceError(
                template_name, list(self._compiling) + [template_name]
            )

        self._compiling.add(template_name)

        try:
            # 合并上下文
            merged_context = self._merge_contexts(template, parameters, call_context)

            # 展开所有步骤
            all_steps = []

            # 添加常规步骤
            for step in template.steps:
                expanded_steps = await self._expand_step(
                    step, parameters, merged_context
                )
                all_steps.extend(expanded_steps)

            # 添加后置步骤
            for step in template.post_steps:
                expanded_steps = await self._expand_step(
                    step, parameters, merged_context
                )
                all_steps.extend(expanded_steps)

            # 处理条件步骤
            for conditional_step in template.conditional_steps:
                condition = conditional_step.get("condition")
                if condition and self._evaluate_condition(condition, merged_context):
                    steps = conditional_step.get("steps", [])
                    for step_data in steps:
                        step = TemplateStep(
                            id=step_data.get("id", ""),
                            action=step_data.get("action", ""),
                            params=step_data.get("params", {}),
                            description=step_data.get("description"),
                            condition=step_data.get("condition"),
                            continue_on_error=step_data.get("continue_on_error", False),
                        )
                        expanded_steps = await self._expand_step(
                            step, parameters, merged_context
                        )
                        all_steps.extend(expanded_steps)

            # 替换步骤中的变量
            all_steps = self._substitute_variables_in_steps(all_steps, merged_context)

            # 验证编译后的步骤
            self._validate_compiled_steps(all_steps)

            return CompiledTemplate(
                name=template_name,
                steps=all_steps,
                context=merged_context,
            )

        finally:
            self._compiling.remove(template_name)

    def _merge_contexts(
        self,
        template: Template,
        parameters: Dict[str, Any],
        call_context: Dict[str, Any],
    ) -> Dict[str, Any]:
        """合并多个上下文字典

        合并顺序（后面的覆盖前面的）：
        1. 模板默认上下文
        2. 全局上下文
        3. 调用时提供的上下文
        4. 模板参数
        """
        merged = {}

        # 添加模板默认上下文
        merged.update(template.default_context)

        # 添加全局上下文
        global_context = self.context_manager.get_all_contexts()
        for scope_context in global_context.values():
            merged.update(scope_context)

        # 添加调用时提供的上下文
        merged.update(call_context)

        # 添加参数（参数优先级最高）
        merged.update(parameters)

        return merged

    async def _expand_step(
        self,
        step: TemplateStep,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """展开单个步骤

        Args:
            step: 模板步骤
            parameters: 参数值
            context: 上下文

        Returns:
            展开后的步骤列表
        """
        # 检查条件
        if step.condition and not self._evaluate_condition(step.condition, context):
            return []

        # 处理嵌套模板调用
        if step.action == "template":
            return await self._expand_nested_template(step, parameters, context)

        # 处理常规步骤
        expanded_step = {
            "id": step.id,
            "action": step.action,
            "params": copy.deepcopy(step.params),
            "description": step.description,
            "continue_on_error": step.continue_on_error,
        }

        # 替换参数和上下文变量
        expanded_step = self._substitute_variables(expanded_step, context)

        return [expanded_step]

    async def _expand_nested_template(
        self,
        step: TemplateStep,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """展开嵌套模板调用

        Args:
            step: 模板步骤
            parameters: 参数值
            context: 上下文

        Returns:
            展开后的步骤列表
        """
        template_params = step.params.get("parameters", {})
        template_context = step.params.get("context", {})

        # 创建嵌套模板调用
        nested_call = TemplateCall(
            name=step.params["name"],
            parameters=template_params,
            context=template_context,
        )

        # 递归展开嵌套模板
        return await self.expand_template_call(nested_call)

    def _substitute_variables(self, obj: Any, context: Dict[str, Any]) -> Any:
        """替换对象中的变量引用

        支持：
        - 字符串中的 ${var} 语法
        - 字典中的变量引用
        - 列表中的变量引用

        Args:
            obj: 要替换的对象
            context: 上下文字典

        Returns:
            替换后的对象
        """
        if isinstance(obj, str):
            return self.context_manager.substitute_variables(obj, context)
        elif isinstance(obj, dict):
            return {
                key: self._substitute_variables(value, context)
                for key, value in obj.items()
            }
        elif isinstance(obj, list):
            return [self._substitute_variables(item, context) for item in obj]
        else:
            return obj

    def _substitute_variables_in_steps(
        self,
        steps: List[Dict[str, Any]],
        context: Dict[str, Any],
    ) -> List[Dict[str, Any]]:
        """替换步骤列表中的变量

        Args:
            steps: 步骤列表
            context: 上下文

        Returns:
            替换后的步骤列表
        """
        return [self._substitute_variables(step, context) for step in steps]

    def _evaluate_condition(self, condition: str, context: Dict[str, Any]) -> bool:
        """评估条件表达式

        支持简单的比较运算和布尔运算。

        Args:
            condition: 条件表达式字符串
            context: 上下文

        Returns:
            条件是否成立
        """
        try:
            # 替换上下文变量
            condition = self.context_manager.substitute_variables(condition, context)

            # 安全评估（仅允许特定操作符）
            allowed_names = {
                "True": True,
                "False": False,
                "None": None,
                "and": lambda a, b: a and b,
                "or": lambda a, b: a or b,
                "not": lambda a: not a,
            }

            # 简单的条件求值（注意：实际使用中需要更严格的安全控制）
            result = eval(condition, {"__builtins__": {}}, allowed_names)
            return bool(result)

        except Exception:
            # 如果条件求值失败，返回 False
            return False

    def _validate_compiled_steps(self, steps: List[Dict[str, Any]]):
        """验证编译后的步骤

        Args:
            steps: 步骤列表

        Raises:
            TemplateCompilationError: 验证失败
        """
        errors = []

        for i, step in enumerate(steps):
            if not step.get("action"):
                errors.append(f"Step {i} is missing action")

            if step.get("action") == "template" and "name" not in step.get(
                "params", {}
            ):
                errors.append(f"Step {i} is missing template name")

        if errors:
            raise TemplateCompilationError("compiled_template", "; ".join(errors))

    def _get_cache_key(
        self,
        template_name: str,
        parameters: Dict[str, Any],
        context: Dict[str, Any],
    ) -> str:
        """生成缓存键

        Args:
            template_name: 模板名称
            parameters: 参数
            context: 上下文

        Returns:
            缓存键字符串
        """
        # 简单的缓存键生成（实际可能需要更复杂的哈希）
        params_str = str(sorted(parameters.items()))
        context_str = str(sorted(context.items()))
        return f"{template_name}:{hash(params_str)}:{hash(context_str)}"

    def clear_cache(self):
        """清空编译缓存"""
        self._compiled_cache.clear()
        self._compile_stats = {
            "total_compilations": 0,
            "cache_hits": 0,
            "cache_misses": 0,
        }

    def get_cache_info(self) -> Dict[str, Any]:
        """获取缓存信息

        Returns:
            缓存信息字典
        """
        cache_hit_rate = 0
        if self._compile_stats["total_compilations"] > 0:
            cache_hit_rate = (
                self._compile_stats["cache_hits"]
                / self._compile_stats["total_compilations"]
            )

        return {
            "cache_size": len(self._compiled_cache),
            "total_compilations": self._compile_stats["total_compilations"],
            "cache_hits": self._compile_stats["cache_hits"],
            "cache_misses": self._compile_stats["cache_misses"],
            "hit_rate": f"{cache_hit_rate:.2%}",
        }

    def get_statistics(self) -> Dict[str, Any]:
        """获取引擎统计信息

        Returns:
            统计信息字典
        """
        registry_stats = self.registry.get_statistics()

        return {
            "registry": registry_stats,
            "cache": self.get_cache_info(),
            "compiling": list(self._compiling),
        }

    def __repr__(self) -> str:
        """字符串表示"""
        return f"TemplateEngine(templates={len(self.registry)}, cache={len(self._compiled_cache)})"
