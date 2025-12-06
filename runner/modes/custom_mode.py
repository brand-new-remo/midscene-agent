#!/usr/bin/env python3
"""
自定义任务模式模块

提供自定义任务相关的功能。
"""

import os
import sys

# 添加当前目录到路径，以便能够导入 agent 包
runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if runner_dir not in sys.path:
    sys.path.insert(0, runner_dir)

from agent.agent import MidsceneAgent


async def run_custom_task():
    """运行用户提供的自定义任务。"""
    print("\n" + "=" * 70)
    print("自定义任务模式")
    print("=" * 70)
    print("\n输入你想要做的事情的自然语言描述。")
    print("例如: '前往 https://google.com 并搜索 AI 新闻'\n")

    task = input("你的任务: ").strip()

    if not task:
        print("❌ 未提供任务")
        return

    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 在环境中未找到 DEEPSEEK_API_KEY")
        print("请在 .env 文件中设置或导出它")
        return

    print("\n" + "=" * 70)
    print("正在执行你的任务...")
    print("=" * 70 + "\n")

    # 准备 Midscene 配置
    midscene_config = {
        "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "headless": False,  # 显示浏览器便于观察
    }

    agent = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config=midscene_config,
        tool_set="full",
        enable_websocket=True
    )

    try:
        async with agent:
            async for event in agent.execute(task, stream=True):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(msg.content)
                    else:
                        print(msg)
                elif "error" in event:
                    print(f"❌ 错误: {event['error']}")
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()
