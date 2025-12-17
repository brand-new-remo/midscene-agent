"""
Midscene Agent 模板系统

这个模块提供了操作模板/宏系统，用于简化生产环境中的通用操作。
通过预定义的模板，用户可以轻松调用复杂的工作流程，如登录、搜索等。

主要组件：
- TemplateEngine: 模板解析和展开引擎
- ContextManager: 上下文管理系统
- TemplateRegistry: 模板注册和检索
- Template: 模板数据类
"""

from .types import (
    Template,
    TemplateParameter,
    TemplateStep,
    ContextScope,
    TemplateCall,
)

from .context import ContextManager

from .registry import TemplateRegistry

from .engine import TemplateEngine

from .exceptions import (
    TemplateError,
    TemplateNotFoundError,
    TemplateValidationError,
    ContextError,
    ParameterError,
)

__all__ = [
    # 核心类
    "TemplateEngine",
    "ContextManager",
    "TemplateRegistry",

    # 数据类
    "Template",
    "TemplateParameter",
    "TemplateStep",
    "TemplateCall",

    # 枚举
    "ContextScope",

    # 异常
    "TemplateError",
    "TemplateNotFoundError",
    "TemplateValidationError",
    "ContextError",
    "ParameterError",
]

__version__ = "1.0.0"
