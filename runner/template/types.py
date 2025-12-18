"""
模板系统类型定义

定义模板系统中使用的所有数据类型和接口。
"""

from dataclasses import dataclass, field
from enum import Enum
from typing import Any, Dict, List, Optional, Union


class ContextScope(Enum):
    """上下文作用域枚举"""

    GLOBAL = "global"  # 全局上下文 - 所有测试共享
    SESSION = "session"  # 会话上下文 - 当前测试会话
    TEMPLATE = "template"  # 模板上下文 - 当前模板执行
    STEP = "step"  # 步骤上下文 - 当前步骤


@dataclass
class TemplateParameter:
    """模板参数定义"""

    name: str
    type: str  # "string", "number", "boolean", "url", "selector"
    required: bool = False
    description: str = ""
    default: Any = None
    choices: Optional[List[Any]] = None  # 可选值列表

    def validate(self, value: Any) -> bool:
        """验证参数值是否符合类型要求"""
        if value is None:
            return not self.required

        if self.choices and value not in self.choices:
            return False

        # 简单类型检查
        if self.type == "string" and not isinstance(value, str):
            return False
        elif self.type == "number" and not isinstance(value, (int, float)):
            return False
        elif self.type == "boolean" and not isinstance(value, bool):
            return False
        elif self.type == "url" and not isinstance(value, str):
            return False
        elif self.type == "selector" and not isinstance(value, str):
            return False

        return True

    def convert(self, value: Any) -> Any:
        """转换参数值到正确类型"""
        if value is None:
            return None

        if self.type == "number":
            try:
                return float(value) if "." in str(value) else int(value)
            except (ValueError, TypeError):
                return value
        elif self.type == "boolean":
            if isinstance(value, bool):
                return value
            return str(value).lower() in ("true", "1", "yes", "on")

        return value


@dataclass
class TemplateStep:
    """模板步骤定义"""

    id: str
    action: str  # 操作类型，如 "ai", "aiInput", "aiTap" 等
    params: Dict[str, Any] = field(default_factory=dict)
    description: Optional[str] = None
    condition: Optional[str] = None  # 条件表达式
    continue_on_error: bool = False  # 错误时是否继续


@dataclass
class Template:
    """模板数据类"""

    name: str
    version: str = "1.0.0"
    description: str = ""
    category: str = "general"
    tags: List[str] = field(default_factory=list)
    author: str = "user"

    # 参数定义
    parameters: Dict[str, TemplateParameter] = field(default_factory=dict)

    # 默认上下文
    default_context: Dict[str, Any] = field(default_factory=dict)

    # 步骤定义
    steps: List[TemplateStep] = field(default_factory=list)
    post_steps: List[TemplateStep] = field(default_factory=list)

    # 条件步骤
    conditional_steps: List[Dict[str, Any]] = field(default_factory=list)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "Template":
        """从字典创建模板"""
        template_data = data.get("template", {})

        # 解析参数
        parameters = {}
        for param_name, param_config in template_data.get("parameters", {}).items():
            parameters[param_name] = TemplateParameter(
                name=param_name,
                type=param_config.get("type", "string"),
                required=param_config.get("required", False),
                description=param_config.get("description", ""),
                default=param_config.get("default"),
                choices=param_config.get("choices"),
            )

        # 解析步骤
        steps = []
        for step_data in template_data.get("steps", []):
            steps.append(
                TemplateStep(
                    id=step_data.get("id", ""),
                    action=step_data.get("action", ""),
                    params=step_data.get("params", {}),
                    description=step_data.get("description"),
                    condition=step_data.get("condition"),
                    continue_on_error=step_data.get("continue_on_error", False),
                )
            )

        # 解析后置步骤
        post_steps = []
        for step_data in template_data.get("post_steps", []):
            post_steps.append(
                TemplateStep(
                    id=step_data.get("id", ""),
                    action=step_data.get("action", ""),
                    params=step_data.get("params", {}),
                    description=step_data.get("description"),
                    condition=step_data.get("condition"),
                    continue_on_error=step_data.get("continue_on_error", False),
                )
            )

        return cls(
            name=template_data.get("name", ""),
            version=template_data.get("version", "1.0.0"),
            description=template_data.get("description", ""),
            category=template_data.get("category", "general"),
            tags=template_data.get("tags", []),
            author=template_data.get("author", "user"),
            parameters=parameters,
            default_context=template_data.get("context", {}),
            steps=steps,
            post_steps=post_steps,
            conditional_steps=template_data.get("conditional_steps", []),
        )

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "template": {
                "name": self.name,
                "version": self.version,
                "description": self.description,
                "category": self.category,
                "tags": self.tags,
                "author": self.author,
                "parameters": {
                    name: {
                        "type": param.type,
                        "required": param.required,
                        "description": param.description,
                        "default": param.default,
                        "choices": param.choices,
                    }
                    for name, param in self.parameters.items()
                },
                "context": self.default_context,
                "steps": [
                    {
                        "id": step.id,
                        "action": step.action,
                        "params": step.params,
                        "description": step.description,
                        "condition": step.condition,
                        "continue_on_error": step.continue_on_error,
                    }
                    for step in self.steps
                ],
                "post_steps": [
                    {
                        "id": step.id,
                        "action": step.action,
                        "params": step.params,
                        "description": step.description,
                        "condition": step.condition,
                        "continue_on_error": step.continue_on_error,
                    }
                    for step in self.post_steps
                ],
                "conditional_steps": self.conditional_steps,
            }
        }

    def validate_parameters(self, parameters: Dict[str, Any]) -> List[str]:
        """验证参数，返回错误列表"""
        errors = []

        for param_name, param in self.parameters.items():
            value = parameters.get(param_name, param.default)

            if param.required and value is None:
                errors.append(f"Required parameter '{param_name}' is missing")
                continue

            if value is not None and not param.validate(value):
                errors.append(f"Parameter '{param_name}' has invalid value: {value}")

        return errors

    def get_parameter(self, name: str, default: Any = None) -> Any:
        """获取参数值（带默认值）"""
        return self.parameters.get(name, default)


@dataclass
class TemplateCall:
    """模板调用定义"""

    name: str
    parameters: Dict[str, Any] = field(default_factory=dict)
    context: Dict[str, Any] = field(default_factory=dict)
    condition: Optional[str] = None
    continue_on_error: bool = False

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        result = {
            "name": self.name,
            "parameters": self.parameters,
            "context": self.context,
        }
        if self.condition:
            result["condition"] = self.condition
        if self.continue_on_error:
            result["continue_on_error"] = self.continue_on_error
        return result

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "TemplateCall":
        """从字典创建模板调用"""
        return cls(
            name=data.get("name", ""),
            parameters=data.get("parameters", {}),
            context=data.get("context", {}),
            condition=data.get("condition"),
            continue_on_error=data.get("continue_on_error", False),
        )


@dataclass
class CompiledTemplate:
    """编译后的模板（已展开参数）"""

    name: str
    steps: List[Dict[str, Any]]
    context: Dict[str, Any]

    def to_dict(self) -> Dict[str, Any]:
        """转换为字典"""
        return {
            "name": self.name,
            "steps": self.steps,
            "context": self.context,
        }
