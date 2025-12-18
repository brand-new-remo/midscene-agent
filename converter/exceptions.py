"""
XMind 转换工具的异常定义
"""


class ConverterError(Exception):
    """转换工具基础异常"""

    pass


class XMindParseError(ConverterError):
    """XMind 文件解析错误"""

    def __init__(self, message: str, node_id: str | None = None):
        self.node_id = node_id
        super().__init__(message)


class ValidationError(ConverterError):
    """验证错误"""

    pass


class ConverterFileNotFoundError(ConverterError):
    """文件未找到错误"""

    pass


class BuildError(ConverterError):
    """构建文件错误"""

    pass
