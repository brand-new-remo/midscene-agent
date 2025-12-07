"""
XMind 转换工具

将 XMind 思维导图格式的测试用例转换为自然语言测试文件。
"""

from .xmind_parser import XMindParser
from .text_generator import TextGenerator
from .models import (
    XMindNode, NodeType, Step, WebConfig, TestCase, Module, ParsedDocument
)
from .exceptions import (
    ConverterError, XMindParseError, ValidationError, ConverterFileNotFoundError, BuildError
)

__version__ = "1.0.0"
__author__ = "Claude Code"

__all__ = [
    'XMindParser',
    'TextGenerator',
    'XMindNode',
    'NodeType',
    'Step',
    'WebConfig',
    'TestCase',
    'Module',
    'ParsedDocument',
    'ConverterError',
    'XMindParseError',
    'ValidationError',
    'ConverterFileNotFoundError',
    'BuildError',
]
