"""
XMind 文件解析器
"""

import json
import re
from pathlib import Path
from typing import Any, Dict, List, Optional

from .exceptions import ValidationError, XMindParseError
from .models import (
    Module,
    NodeType,
    ParsedDocument,
    Step,
    TestCase,
    WebConfig,
    XMindNode,
)
from .utils import extract_xmind_content


class XMindParser:
    """XMind 文件解析器"""

    def __init__(self):
        self.current_module: Optional[Module] = None
        self.current_testcase: Optional[TestCase] = None

    def parse_file(self, xmind_path: Path) -> ParsedDocument:
        """解析 XMind 文件"""
        content, content_type = extract_xmind_content(xmind_path)

        if content_type == "json":
            return self._parse_json_content(content, xmind_path)
        else:
            raise XMindParseError(f"暂不支持 content.xml 格式: {xmind_path}")

    def _parse_json_content(self, content: str, xmind_path: Path) -> ParsedDocument:
        """解析 JSON 格式内容"""
        try:
            data = json.loads(content)
        except json.JSONDecodeError as e:
            raise XMindParseError(f"JSON 解析失败: {e}", xmind_path.name)

        if not isinstance(data, list) or len(data) == 0:
            raise XMindParseError(
                "无效的 XMind 格式: content.json 不是数组或为空", xmind_path.name
            )

        sheet = data[0]
        if "rootTopic" not in sheet:
            raise XMindParseError("无效的 XMind 格式: 缺少 rootTopic", xmind_path.name)

        document = ParsedDocument()
        root_topic = sheet["rootTopic"]
        self._parse_topic_tree(root_topic, document, level=0)

        return document

    def _parse_topic_tree(
        self, topic: Dict[str, Any], document: ParsedDocument, level: int
    ):
        """递归解析主题树"""
        title = topic.get("title", "").strip()
        topic_id = topic.get("id", "")

        if level == 0:
            document.version = title
        else:
            node_type = self._identify_node_type(title, level)

            if node_type == NodeType.MODULE:
                self._parse_module(topic, document, level)
            elif node_type == NodeType.TESTCASE:
                self._parse_testcase(topic, level)
            elif node_type == NodeType.STEP:
                self._parse_steps(topic, level)
            elif node_type == NodeType.VERIFICATION:
                self._parse_verifications(topic, level)

        children = topic.get("children", {})
        attached = children.get("attached", [])

        for child in attached:
            self._parse_topic_tree(child, document, level + 1)

    def _identify_node_type(self, title: str, level: int) -> NodeType:
        """识别节点类型"""
        title = title.strip()

        if level == 1 and title.startswith("#"):
            return NodeType.MODULE

        if level == 2 and not title.startswith("#"):
            return NodeType.TESTCASE

        if level == 3:
            if self._is_step_title(title):
                return NodeType.STEP

        if level == 4:
            if self._is_verification_title(title):
                return NodeType.VERIFICATION

        return NodeType.UNKNOWN

    def _is_step_title(self, title: str) -> bool:
        """判断是否为步骤标题"""
        lines = title.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r"^\d+\.", line):
                return True
        return False

    def _is_verification_title(self, title: str) -> bool:
        """判断是否为验证标题"""
        lines = title.split("\n")
        for line in lines:
            line = line.strip()
            if not line:
                continue
            if re.match(r"^\d+\.", line):
                return True
        return False

    def _parse_module(
        self, topic: Dict[str, Any], document: ParsedDocument, level: int
    ):
        """解析模块节点"""
        title = topic.get("title", "").strip()
        if title.startswith("#"):
            module_name = title[1:].strip()
        else:
            module_name = title

        self.current_module = Module(name=module_name)
        document.modules.append(self.current_module)

    def _parse_testcase(self, topic: Dict[str, Any], level: int):
        """解析测试用例节点"""
        if self.current_module is None:
            raise ValidationError("测试用例必须在模块下")

        title = topic.get("title", "").strip()
        self.current_testcase = TestCase(name=title)
        self.current_module.testcases.append(self.current_testcase)

    def _parse_steps(self, topic: Dict[str, Any], level: int):
        """解析步骤节点"""
        if self.current_testcase is None:
            raise ValidationError("步骤必须在测试用例下")

        title = topic.get("title", "").strip()
        steps = self._parse_step_lines(title)

        for step in steps:
            self.current_testcase.steps.append(step)

    def _parse_verifications(self, topic: Dict[str, Any], level: int):
        """解析验证节点"""
        if self.current_testcase is None:
            raise ValidationError("验证步骤必须在测试用例下")

        title = topic.get("title", "").strip()
        verifications = self._parse_step_lines(title, is_verification=True)

        for step in verifications:
            self.current_testcase.steps.append(step)

    def _parse_step_lines(
        self, content: str, is_verification: bool = False
    ) -> List[Step]:
        """解析步骤行"""
        steps = []
        lines = content.split("\n")

        for line in lines:
            line = line.strip()
            if not line:
                continue

            match = re.match(r"^(\d+)\.\s*(.*)", line)
            if match:
                number = int(match.group(1))
                step_content = match.group(2).strip()

                if step_content:
                    steps.append(
                        Step(
                            number=number,
                            content=step_content,
                            is_verification=is_verification,
                        )
                    )

        return steps
