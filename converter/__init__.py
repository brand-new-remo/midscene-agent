"""
XMind 转换工具

将 XMind 思维导图格式的测试用例转换为自然语言测试文件。
"""

from .exceptions import (
    BuildError,
    ConverterError,
    ConverterFileNotFoundError,
    ValidationError,
    XMindParseError,
)
from .models import (
    Module,
    NodeType,
    ParsedDocument,
    Step,
    TestCase,
    WebConfig,
    XMindNode,
)
from .text_generator import TextGenerator
from .xmind_parser import XMindParser

__version__ = "1.0.0"
__author__ = "Claude Code"

__all__ = [
    "XMindParser",
    "TextGenerator",
    "XMindNode",
    "NodeType",
    "Step",
    "WebConfig",
    "TestCase",
    "Module",
    "ParsedDocument",
    "ConverterError",
    "XMindParseError",
    "ValidationError",
    "ConverterFileNotFoundError",
    "BuildError",
]
