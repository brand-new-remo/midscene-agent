"""
XMind 转换工具的数据模型
"""

from dataclasses import dataclass, field
from typing import List, Optional, Dict, Any
from enum import Enum


class NodeType(Enum):
    """XMind 节点类型"""
    ROOT = "root"
    MODULE = "module"
    TESTCASE = "testcase"
    STEP = "step"
    VERIFICATION = "verification"
    UNKNOWN = "unknown"


@dataclass
class XMindNode:
    """XMind 节点"""
    id: str
    title: str
    node_type: NodeType
    level: int
    children: List['XMindNode'] = field(default_factory=list)
    parent: Optional['XMindNode'] = None


@dataclass
class Step:
    """测试步骤"""
    number: int
    content: str
    is_verification: bool = False


@dataclass
class WebConfig:
    """Web 配置"""
    url: str = "https://example.com"
    headless: bool = False
    viewport_width: int = 1280
    viewport_height: int = 768


@dataclass
class TestCase:
    """测试用例"""
    name: str
    web_config: Optional[WebConfig] = None
    steps: List[Step] = field(default_factory=list)


@dataclass
class Module:
    """测试模块"""
    name: str
    description: Optional[str] = None
    testcases: List[TestCase] = field(default_factory=list)


@dataclass
class ParsedDocument:
    """解析后的文档"""
    modules: List[Module] = field(default_factory=list)
    version: str = "1.0.0"
