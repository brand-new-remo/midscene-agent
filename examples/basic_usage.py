"""
基础使用示例

此示例演示如何使用 MidsceneAgent 自动化网页任务。
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 将 src 添加到路径 - 使用绝对路径以提高可靠性
current_dir = os.path.dirname(os.path.abspath(__file__))
src_path = os.path.join(current_dir, "..", "src")
sys.path.insert(0, os.path.abspath(src_path))

# 直接导入智能体模块
from agent import MidsceneAgent  # pyright: ignore

# 加载环境变量
load_dotenv()


async def basic_example():
    """
    使用 MidsceneAgent 进行网页自动化的基础示例。
    """
    # 从环境获取配置
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 在环境中未找到 DEEPSEEK_API_KEY")
        print("请在 .env 文件中设置或将其导出为环境变量")
        return

    # 为 Midscene MCP 服务器准备环境变量
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    # 初始化智能体
    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        deepseek_model=os.getenv("DEEPSEEK_MODEL", "deepseek-chat"),
        temperature=0,
        env=midscene_env,
    )

    try:
        # 将智能体用作异步上下文管理器
        async with agent_instance:
            # 定义任务
            task = """
            请完成以下网页自动化任务：
            1. 导航到 https://www.bing.com
            2. 在搜索框中输入 "LangGraph DeepSeek Midscene"
            3. 点击搜索按钮
            4. 等待结果加载
            5. 告诉我第一个搜索结果的标题

            请逐步进行并报告你在每一步看到的内容。
            """

            # 执行任务
            async for event in agent_instance.execute(task):
                if "messages" in event:
                    # 打印最新消息
                    last_message = event["messages"][-1]
                    # LangChain 1.0+ 兼容输出
                    if hasattr(last_message, "content"):
                        print(last_message.content)
                    else:
                        print(last_message)
                elif "error" in event:
                    print(f"❌ 错误: {event['error']}")

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback

        traceback.print_exc()


async def interactive_example():
    """
    交互式示例 - 允许在一个会话中执行多个任务。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        return

    # 为 Midscene MCP 服务器准备环境变量
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        env=midscene_env,
    )

    try:
        # 初始化一次
        await agent_instance.initialize()

        # 按顺序执行多个任务
        tasks = [
            "导航到 https://news.ycombinator.com 并告诉我页面标题",
            "查找 'submit' 按钮或链接并描述它的位置",
            "向下滚动查看页面上更多内容",
        ]

        for i, task in enumerate(tasks, 1):
            print(f"\n{'='*60}")
            print(f"任务 {i}/{len(tasks)}")
            print(f"{'='*60}\n")

            async for event in agent_instance.execute(task):
                if "messages" in event:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, "content"):
                        print(last_message.content)
                    else:
                        print(last_message)

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await agent_instance.cleanup()


async def query_example():
    """
    专注于从页面查询信息的示例。
    """
    api_key = os.getenv("DEEPSEEK_API_KEY")
    if not api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        return

    # 为 Midscene MCP 服务器准备环境变量
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent_instance = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        env=midscene_env,
    )

    try:
        await agent_instance.initialize()

        # 首先，导航到页面
        print("📄 正在导航到 https://example.com...")
        async for event in agent_instance.execute("导航到 https://example.com"):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content"):
                    print(msg.content)
                else:
                    print(msg)

        # 现在查询页面
        print("\n🔍 正在查询页面信息...")
        async for event in agent_instance.execute(
            "这个页面是关于什么的？提取所有可见文本并列出主要部分。"
        ):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content"):
                    print(msg.content)
                else:
                    print(msg)

    except Exception as e:
        print(f"❌ 错误: {e}")
    finally:
        await agent_instance.cleanup()


if __name__ == "__main__":
    print("MidsceneAgent 基础使用示例\n")
    print("选择要运行的示例:")
    print("1. 基础网页自动化任务")
    print("2. 交互式多任务示例")
    print("3. 页面查询示例")
    print("\n按 Ctrl+C 退出\n")

    try:
        choice = input("输入你的选择 (1-3): ").strip()
        print()

        if choice == "1":
            asyncio.run(basic_example())
        elif choice == "2":
            asyncio.run(interactive_example())
        elif choice == "3":
            asyncio.run(query_example())
        else:
            print("无效选择。正在运行基础示例...")
            asyncio.run(basic_example())

    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback

        traceback.print_exc()
