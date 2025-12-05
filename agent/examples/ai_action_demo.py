#!/usr/bin/env python3
"""
演示 Midscene Agent 的 aiAction 功能

aiAction 是 Midscene.js 的核心 API，允许 AI 自动规划并执行一系列 UI 动作。
这比手动调用各个 API 更智能、更方便。
"""

import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
# 相对于当前示例文件的路径
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)

# 添加 src 到路径
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))

from src.agent import MidsceneAgent


async def demo_ai_action():
    """演示 aiAction 功能"""
    print("\n" + "=" * 70)
    print("🤖 Midscene Agent - aiAction 演示")
    print("=" * 70)
    print("\naiAction 允许 AI 自动规划并执行一系列 UI 动作")
    print("比手动调用各个 API 更智能、更方便！\n")

    # 检查 API 密钥
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        print("请在 .env 文件中设置")
        return

    # 创建 Agent
    agent = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config={
            "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL"),
            "headless": False,  # 显示浏览器以便观察
        },
        tool_set="full",
        enable_websocket=True
    )

    try:
        async with agent:
            print("✅ Agent 初始化成功\n")

            # 示例任务 1: 简单导航和查询
            print("📝 示例 1: 访问 GitHub 并搜索")
            print("-" * 70)

            task1 = """
访问 https://github.com，然后执行以下操作：
1. 在页面顶部的搜索框中输入 "midscene"
2. 点击搜索按钮
3. 等待搜索结果加载完成
4. 告诉我搜索结果的数量
"""

            print(f"任务描述: {task1.strip()}\n")

            results = []
            async for event in agent.execute(task1, stream=True):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if hasattr(latest_msg, "content") and latest_msg.content:
                        print(f"💬 {latest_msg.content}")
                        results.append(latest_msg.content)

            print("\n" + "=" * 70)
            print("📝 示例 2: 复杂的多步骤任务")
            print("-" * 70)

            task2 = """
在当前页面（GitHub 搜索结果页）执行以下操作：
1. 找到第一个搜索结果并点击进入
2. 查看该仓库的描述信息
3. 截取一张屏幕截图保存为 "github_repo"
4. 告诉我该仓库的主要编程语言是什么
"""

            print(f"任务描述: {task2.strip()}\n")

            results2 = []
            async for event in agent.execute(task2, stream=True):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if hasattr(latest_msg, "content") and latest_msg.content:
                        print(f"💬 {latest_msg.content}")
                        results2.append(latest_msg.content)

            print("\n" + "=" * 70)
            print("📝 示例 3: 使用 aiAction 的高级特性")
            print("-" * 70)

            # 设置 AI 上下文（让 AI 知道背景知识）
            print("\n🔧 设置 AI 上下文...")
            await agent.http_client.execute_action(
                "setAIActionContext",
                {"context": "如果遇到 Cookie 同意对话框，请先关闭它"}
            )
            print("✅ 上下文设置完成")

            task3 = """
访问 https://example.com，然后：
1. 查看页面内容
2. 使用 aiQuery 提取页面标题和描述
3. 记录一张截图，标题为 "Example 页面"
4. 告诉我页面是否包含 "Example Domain" 文本
"""

            print(f"\n任务描述: {task3.strip()}\n")

            results3 = []
            async for event in agent.execute(task3, stream=True):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if hasattr(latest_msg, "content") and latest_msg.content:
                        print(f"💬 {latest_msg.content}")
                        results3.append(latest_msg.content)

            print("\n" + "=" * 70)
            print("🎉 演示完成！")
            print("=" * 70)
            print("\n💡 aiAction 的优势:")
            print("  • 智能规划: AI 自动分解复杂任务")
            print("  • 灵活执行: 可以包含多个步骤和操作")
            print("  • 上下文感知: 可以设置背景知识")
            print("  • 错误处理: AI 可以处理意外情况")
            print("\n✨ 现在你已经掌握了 Midscene.js 的核心功能！")

    except Exception as e:
        print(f"❌ 演示失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_ai_action())
