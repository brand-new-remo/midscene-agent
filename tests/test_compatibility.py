#!/usr/bin/env python3
"""
LangChain/LangGraph 1.0+ 兼容性测试脚本

此脚本将验证所有必要的组件是否已正确安装和配置。
"""

import sys
import os
import asyncio
from typing import List

# Add src to path to import modules
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..', 'src'))

# 测试结果
class TestResult:
    def __init__(self, name: str, passed: bool, message: str = ""):
        self.name = name
        self.passed = passed
        self.message = message

    def __str__(self):
        status = "✅" if self.passed else "❌"
        result = f"{status} {self.name}"
        if self.message:
            result += f"\n   {self.message}"
        return result


def get_package_version(package_name: str) -> str:
    """安全地获取包版本"""
    try:
        # Python 3.8+
        from importlib.metadata import version
        return version(package_name)
    except Exception:
        try:
            # Try to get from the module directly
            module = __import__(package_name)
            if hasattr(module, '__version__'):
                return module.__version__
        except Exception:
            pass
        return "未知版本"


def test_python_version() -> TestResult:
    """测试 Python 版本"""
    version = sys.version_info
    if version.major == 3 and version.minor >= 10:
        return TestResult(
            "Python 版本检查",
            True,
            f"Python {version.major}.{version.minor}.{version.micro}"
        )
    else:
        return TestResult(
            "Python 版本检查",
            False,
            f"需要 Python >= 3.10，当前版本: {version.major}.{version.minor}.{version.micro}"
        )


def test_imports() -> List[TestResult]:
    """测试必要的包导入"""
    results = []

    # 测试 LangChain
    try:
        import langchain
        version = get_package_version('langchain')
        results.append(TestResult(
            "LangChain 导入",
            True,
            f"版本: {version}"
        ))
    except ImportError as e:
        results.append(TestResult(
            "LangChain 导入",
            False,
            str(e)
        ))

    # 测试 LangChain Core
    try:
        import langchain_core
        version = get_package_version('langchain-core')
        results.append(TestResult(
            "LangChain Core 导入",
            True,
            f"版本: {version}"
        ))
    except ImportError as e:
        results.append(TestResult(
            "LangChain Core 导入",
            False,
            str(e)
        ))

    # 测试 LangGraph
    try:
        import langgraph
        version = get_package_version('langgraph')
        results.append(TestResult(
            "LangGraph 导入",
            True,
            f"版本: {version}"
        ))
    except ImportError as e:
        results.append(TestResult(
            "LangGraph 导入",
            False,
            str(e)
        ))

    # 测试 LangChain OpenAI
    try:
        import langchain_openai
        version = get_package_version('langchain-openai')
        results.append(TestResult(
            "LangChain OpenAI 导入",
            True,
            f"版本: {version}"
        ))
    except ImportError as e:
        results.append(TestResult(
            "LangChain OpenAI 导入",
            False,
            str(e)
        ))

    # 测试 MCP
    try:
        import mcp
        version = get_package_version('mcp')
        results.append(TestResult(
            "MCP 导入",
            True,
            f"版本: {version}"
        ))
    except ImportError as e:
        results.append(TestResult(
            "MCP 导入",
            False,
            str(e)
        ))

    # 测试 Pydantic
    try:
        import pydantic
        version = get_package_version('pydantic')
        results.append(TestResult(
            "Pydantic 导入",
            True,
            f"版本: {version}"
        ))
    except ImportError as e:
        results.append(TestResult(
            "Pydantic 导入",
            False,
            str(e)
        ))

    return results


def test_langchain_api() -> List[TestResult]:
    """测试 LangChain 1.0+ API"""
    results = []

    # 测试 HumanMessage
    try:
        from langchain_core.messages import HumanMessage
        msg = HumanMessage(content="test")
        if hasattr(msg, "content"):
            results.append(TestResult(
                "HumanMessage API",
                True,
                "消息格式正确"
            ))
        else:
            results.append(TestResult(
                "HumanMessage API",
                False,
                "缺少 content 属性"
            ))
    except Exception as e:
        results.append(TestResult(
            "HumanMessage API",
            False,
            str(e)
        ))

    # 测试 ChatDeepSeek
    try:
        from langchain_deepseek import ChatDeepSeek
        # 注意：不初始化实际连接，只测试类是否存在
        results.append(TestResult(
            "ChatDeepSeek 类",
            True,
            "类存在且可导入"
        ))
    except Exception as e:
        results.append(TestResult(
            "ChatDeepSeek 类",
            False,
            str(e)
        ))

    # 测试工具装饰器
    try:
        from langchain_core.tools import tool

        @tool
        async def test_tool(x: str) -> str:
            """A test tool for validation purposes"""
            return x

        results.append(TestResult(
            "@tool 装饰器",
            True,
            "装饰器工作正常"
        ))
    except Exception as e:
        results.append(TestResult(
            "@tool 装饰器",
            False,
            str(e)
        ))

    return results


def test_langgraph_api() -> List[TestResult]:
    """测试 LangGraph API"""
    results = []

    # 测试 create_react_agent
    try:
        from langgraph.prebuilt import create_react_agent
        results.append(TestResult(
            "create_react_agent",
            True,
            "函数可导入"
        ))
    except Exception as e:
        results.append(TestResult(
            "create_react_agent",
            False,
            str(e)
        ))

    return results


async def test_agent_creation() -> TestResult:
    """测试智能体创建（不实际运行）"""
    try:
        from agent import MidsceneAgent
        # 测试实例化（不初始化连接）
        agent = MidsceneAgent(
            deepseek_api_key="test-key",
            deepseek_base_url="https://api.deepseek.com",
            deepseek_model="deepseek-chat"
        )
        return TestResult(
            "MidsceneAgent 实例化",
            True,
            "Agent 类可正常实例化"
        )
    except Exception as e:
        return TestResult(
            "MidsceneAgent 实例化",
            False,
            str(e)
        )


async def run_all_tests():
    """运行所有测试"""
    print("🧪 Midscene LangGraph Agent - 兼容性测试")
    print("=" * 60)
    print()

    all_results = []

    # 测试 Python 版本
    print("1. 系统环境检查")
    print("-" * 60)
    result = test_python_version()
    all_results.append(result)
    print(result)
    print()

    # 测试包导入
    print("2. 包导入检查")
    print("-" * 60)
    import_results = test_imports()
    for result in import_results:
        all_results.append(result)
        print(result)
    print()

    # 测试 LangChain API
    print("3. LangChain API 检查")
    print("-" * 60)
    api_results = test_langchain_api()
    for result in api_results:
        all_results.append(result)
        print(result)
    print()

    # 测试 LangGraph API
    print("4. LangGraph API 检查")
    print("-" * 60)
    graph_results = test_langgraph_api()
    for result in graph_results:
        all_results.append(result)
        print(result)
    print()

    # 测试 Agent 创建
    print("5. Agent 类检查")
    print("-" * 60)
    agent_result = await test_agent_creation()
    all_results.append(agent_result)
    print(agent_result)
    print()

    # 汇总结果
    print("=" * 60)
    print("📊 测试汇总")
    print("=" * 60)

    passed = sum(1 for r in all_results if r.passed)
    total = len(all_results)

    print(f"\n总测试数: {total}")
    print(f"通过: {passed}")
    print(f"失败: {total - passed}")

    if passed == total:
        print("\n🎉 所有测试通过！系统已准备好使用 Midscene LangGraph Agent")
        return True
    else:
        print(f"\n⚠️  有 {total - passed} 项测试失败，请检查上述错误信息")
        return False


if __name__ == "__main__":
    try:
        result = asyncio.run(run_all_tests())
        sys.exit(0 if result else 1)
    except KeyboardInterrupt:
        print("\n\n👋 测试已取消")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试过程中发生错误: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
