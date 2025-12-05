#!/usr/bin/env python3
"""
Midscene Agent 示例快速启动器

此脚本提供了一种便捷的方式来运行各种示例，
基于 HTTP + WebSocket 架构。
"""

import asyncio
import sys
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 将当前目录和 src 添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))
sys.path.insert(0, os.path.join(os.path.dirname(os.path.abspath(__file__)), 'src'))

from examples.basic_usage import (
    basic_example,
    interactive_example,
    query_example,
    test_new_features,
)


def print_banner():
    """打印应用程序横幅。"""
    print("\n" + "=" * 70)
    print("  🕷️  Midscene LangGraph Agent - 快速启动器")
    print("=" * 70)
    print("\n基于 HTTP + WebSocket 的现代化架构")
    print("更稳定、更强大、更智能！\n")


def print_menu():
    """打印主菜单。"""
    print("选择要运行的示例:\n")
    print("🎯 特性示例:")
    print("  1. 基础网页自动化任务 (流式响应)")
    print("  2. 交互式多任务示例")
    print("  3. 页面查询示例 (完整 API)")
    print("  4. 功能测试 (WebSocket + 监控)")
    print("\n其他:")
    print("  5. 运行所有测试")
    print("  6. 检查配置")
    print("  0. 退出")
    print()


async def run_custom_task():
    """运行用户提供的自定义任务。"""
    from src.agent import MidsceneAgent

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


def check_config():
    """检查并显示配置。"""
    print("\n" + "=" * 70)
    print("配置检查 ()")
    print("=" * 70 + "\n")

    # 检查 .env 文件
    if not os.path.exists(".env"):
        print("⚠️ 警告: 未找到 .env 文件")
        print("   复制 .env.example 到 .env 并添加你的 API 密钥\n")
        return

    # 读取 .env 文件
    with open(".env", "r") as f:
        env_content = f.read()

    print("📋 当前配置:")
    print("-" * 70)

    # 检查必要的配置
    required_vars = {
        "DEEPSEEK_API_KEY": "DeepSeek API 密钥",
        "OPENAI_API_KEY": "视觉模型 API 密钥 (可选)",
        "MIDSCENE_SERVER_URL": "Node.js 服务地址 (可选)"
    }

    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # 隐藏密钥的实际值
            display_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"✅ {var}: {display_value} ({desc})")
        else:
            print(f"⚠️ {var}: 未设置 ({desc})")

    print("-" * 70)

    # 检查 Node.js 服务
    print("\n🔍 检查 Node.js 服务...")
    try:
        import aiohttp
        import asyncio

        async def check_server():
            async with aiohttp.ClientSession() as session:
                try:
                    async with session.get("http://localhost:3000/api/health", timeout=2) as response:
                        if response.status == 200:
                            health = await response.json()
                            print(f"✅ Node.js 服务运行正常")
                            print(f"   活跃会话: {health.get('activeSessions', 0)}")
                            print(f"   运行时间: {health.get('uptime', 0):.1f} 秒")
                            return True
                        else:
                            print(f"⚠️ Node.js 服务返回状态: {response.status}")
                            return False
                except Exception as e:
                    print(f"❌ 无法连接到 Node.js 服务: {e}")
                    return False

        asyncio.run(check_server())
    except Exception as e:
        print(f"⚠️ 无法检查服务状态: {e}")

    print("\n" + "=" * 70)
    print("✅ 配置检查完成")
    print("=" * 70)
    print("\n如果所有配置正确，您可以开始使用 ！")
    print("\n📚 更多信息:")
    print("   - README.md: 完整文档")
    print("   - docs/guides/migration.md: 迁移指南")
    print("   - docs/FINAL_SUMMARY.md: 重构详情")
    print()


async def run_all_tests():
    """运行所有  测试"""
    print("\n" + "=" * 70)
    print("🧪 运行所有  测试")
    print("=" * 70 + "\n")

    try:
        os.system("python test_v2.py")
    except Exception as e:
        print(f"❌ 测试执行失败: {e}")


async def main():
    """主入口点。"""
    print_banner()

    # 检查 .env 是否存在
    if not os.path.exists(".env"):
        print("⚠️ 警告: 未找到 .env 文件")
        print("   复制 .env.example 到 .env 并添加你的 DEEPSEEK_API_KEY\n")

    while True:
        print_menu()

        try:
            choice = input("输入你的选择 (0-6): ").strip()
            print()

            if choice == "0":
                print("👋 感谢使用 Midscene Agent ！\n")
                sys.exit(0)

            elif choice == "1":
                print("🚀 正在运行基础网页自动化任务...\n")
                await basic_example()

            elif choice == "2":
                print("🚀 正在运行交互式多任务示例...\n")
                await interactive_example()

            elif choice == "3":
                print("🚀 正在运行页面查询示例...\n")
                await query_example()

            elif choice == "4":
                print("🚀 正在运行新功能测试...\n")
                await test_new_features()

            elif choice == "5":
                print("🧪 正在运行所有测试...\n")
                await run_all_tests()

            elif choice == "6":
                check_config()

            else:
                print("❌ 无效选择。请重试。\n")
                continue

            # 再次显示菜单前暂停
            if choice in ["1", "2", "3", "4", "5"]:
                input("\n" + "=" * 70)
                input("按 Enter 键返回菜单...")

            print()

        except KeyboardInterrupt:
            print("\n\n👋 感谢使用 Midscene Agent ！\n")
            sys.exit(0)
        except Exception as e:
            print(f"\n❌ 错误: {e}")
            import traceback
            traceback.print_exc()
            input("\n按 Enter 键继续...")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 感谢使用 Midscene Agent ！\n")
        sys.exit(0)
