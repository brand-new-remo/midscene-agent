"""
模板系统异常定义

定义模板系统中可能出现的各种异常类型。
"""

from typing import Any


class TemplateError(Exception):
    """模板系统基础异常"""

    pass


class TemplateNotFoundError(TemplateError):
    """模板未找到异常"""

    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"Template '{template_name}' not found")


class TemplateValidationError(TemplateError):
    """模板验证失败异常"""

    def __init__(self, template_name: str, errors: list):
        self.template_name = template_name
        self.errors = errors
        error_msg = f"Template '{template_name}' validation failed:\n" + "\n".join(
            f"  - {e}" for e in errors
        )
        super().__init__(error_msg)


class TemplateCompilationError(TemplateError):
    """模板编译失败异常"""

    def __init__(self, template_name: str, error_msg: str):
        self.template_name = template_name
        self.error_msg = error_msg
        super().__init__(f"Failed to compile template '{template_name}': {error_msg}")


class TemplateExecutionError(TemplateError):
    """模板执行失败异常"""

    def __init__(self, template_name: str, step_id: str, error_msg: str):
        self.template_name = template_name
        self.step_id = step_id
        self.error_msg = error_msg
        super().__init__(
            f"Failed to execute step '{step_id}' in template '{template_name}': {error_msg}"
        )


class TemplateParameterError(TemplateError):
    """模板参数错误异常"""

    def __init__(self, template_name: str, param_name: str, error_msg: str):
        self.template_name = template_name
        self.param_name = param_name
        self.error_msg = error_msg
        super().__init__(
            f"Parameter error in template '{template_name}': {param_name} - {error_msg}"
        )


class ContextError(TemplateError):
    """上下文管理错误异常"""

    pass


class ContextNotFoundError(ContextError):
    """上下文变量未找到异常"""

    def __init__(self, key: str, scope: str):
        self.key = key
        self.scope = scope
        super().__init__(f"Context variable '{key}' not found in scope '{scope}'")


class ContextAccessError(ContextError):
    """上下文访问错误异常"""

    def __init__(self, key: str, scope: str, error_msg: str):
        self.key = key
        self.scope = scope
        self.error_msg = error_msg
        super().__init__(
            f"Failed to access context variable '{key}' in scope '{scope}': {error_msg}"
        )


class ParameterError(TemplateError):
    """参数错误异常"""

    def __init__(self, error_msg: str):
        self.error_msg = error_msg
        super().__init__(error_msg)


class ParameterValidationError(ParameterError):
    """参数验证失败异常"""

    def __init__(self, param_name: str, value: Any, expected_type: str):
        self.param_name = param_name
        self.value = value
        self.expected_type = expected_type
        super().__init__(
            f"Parameter '{param_name}' validation failed: got {type(value).__name__}, expected {expected_type}"
        )


class ParameterConversionError(ParameterError):
    """参数类型转换失败异常"""

    def __init__(self, param_name: str, value: Any, target_type: str):
        self.param_name = param_name
        self.value = value
        self.target_type = target_type
        super().__init__(
            f"Failed to convert parameter '{param_name}' from {type(value).__name__} to {target_type}"
        )


class RegistryError(TemplateError):
    """模板注册表错误异常"""

    pass


class RegistryLoadError(RegistryError):
    """注册表加载失败异常"""

    def __init__(self, registry_path: str, error_msg: str):
        self.registry_path = registry_path
        self.error_msg = error_msg
        super().__init__(
            f"Failed to load template registry from '{registry_path}': {error_msg}"
        )


class TemplateAlreadyExistsError(RegistryError):
    """模板已存在异常"""

    def __init__(self, template_name: str):
        self.template_name = template_name
        super().__init__(f"Template '{template_name}' already exists in registry")


class InvalidTemplateFormatError(RegistryError):
    """模板格式无效异常"""

    def __init__(self, template_path: str, error_msg: str):
        self.template_path = template_path
        self.error_msg = error_msg
        super().__init__(f"Invalid template format in '{template_path}': {error_msg}")


class EngineError(TemplateError):
    """模板引擎错误异常"""

    pass


class EngineCompilationError(EngineError):
    """引擎编译错误异常"""

    def __init__(self, template_name: str, error_msg: str):
        self.template_name = template_name
        self.error_msg = error_msg
        super().__init__(
            f"Engine compilation error for template '{template_name}': {error_msg}"
        )


class EngineExecutionError(EngineError):
    """引擎执行错误异常"""

    def __init__(self, template_name: str, error_msg: str):
        self.template_name = template_name
        self.error_msg = error_msg
        super().__init__(
            f"Engine execution error for template '{template_name}': {error_msg}"
        )


class CircularTemplateReferenceError(EngineError):
    """循环模板引用异常"""

    def __init__(self, template_name: str, reference_chain: list):
        self.template_name = template_name
        self.reference_chain = reference_chain
        chain_str = " -> ".join(reference_chain)
        super().__init__(f"Circular template reference detected: {chain_str}")
