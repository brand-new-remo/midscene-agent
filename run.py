#!/usr/bin/env python3
"""
MidsceneAgent 示例快速启动器

此脚本提供了一种便捷的方式来运行各种示例，
无需记住完整的 python 路径。
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

from examples.basic_usage import basic_example, interactive_example, query_example
from examples.test_ecommerce import (
    test_product_search,
    test_form_filling,
    test_navigation,
    run_all_tests,
)


def print_banner():
    """打印应用程序横幅。"""
    print("\n" + "=" * 70)
    print("  🕷️  Midscene LangGraph Agent - 快速启动器")
    print("=" * 70)
    print("\n一个强大的 AI 驱动网页自动化系统\n")


def print_menu():
    """打印主菜单。"""
    print("选择要运行的示例:\n")
    print("基础示例:")
    print("  1. 基础网页自动化任务")
    print("  2. 交互式多任务示例")
    print("  3. 页面查询示例")
    print("\n电商测试:")
    print("  4. 产品搜索测试 (Amazon)")
    print("  5. 表单填写测试 (httpbin.org)")
    print("  6. 导航测试 (Hacker News)")
    print("  7. 运行所有电商测试")
    print("\n高级:")
    print("  8. 自定义任务（输入你自己的）")
    print("\n其他:")
    print("  9. 检查配置")
    print("  0. 退出")
    print()


async def run_custom_task():
    """运行用户提供的自定义任务。"""
    from agent import MidsceneAgent

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

    # 为 Midscene MCP 服务器准备环境变量
    midscene_env = {
        "OPENAI_API_KEY": os.getenv("OPENAI_API_KEY", ""),
        "OPENAI_BASE_URL": os.getenv("OPENAI_BASE_URL", ""),
        "MIDSCENE_MODEL_NAME": os.getenv("MIDSCENE_MODEL", "doubao-seed-1.6-vision"),
    }

    agent = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com"),
        env=midscene_env,
    )

    try:
        async with agent:
            async for event in agent.execute(task):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(msg.content)
                    else:
                        print(msg)
    except Exception as e:
        print(f"❌ Error: {e}")
        import traceback
        traceback.print_exc()


def check_config():
    """检查并显示配置。"""
    from config import Config

    print("\n" + "=" * 70)
    print("配置检查")
    print("=" * 70 + "\n")

    Config.print_config()

    print("\n" + "-" * 70)
    print("\n✅ 配置状态:")
    if Config.validate():
        print("   ✓ DeepSeek API 密钥已配置")
        print("   ✓ 可以使用了！")
    else:
        print("   ⚠️  某些配置缺失")
        print("   请检查你的 .env 文件")

    print()


async def main():
    """主入口点。"""
    print_banner()

    # 检查 .env 是否存在
    if not os.path.exists(".env"):
        print("⚠️  警告: 未找到 .env 文件")
        print("   复制 .env.example 到 .env 并添加你的 DEEPSEEK_API_KEY\n")

    while True:
        print_menu()

        try:
            choice = input("输入你的选择 (0-9): ").strip()
            print()

            if choice == "0":
                print("👋 再见！\n")
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
                print("🛒 正在运行产品搜索测试...\n")
                await test_product_search()

            elif choice == "5":
                print("📝 正在运行表单填写测试...\n")
                await test_form_filling()

            elif choice == "6":
                print("🧭 正在运行导航测试...\n")
                await test_navigation()

            elif choice == "7":
                print("🧪 正在运行所有电商测试...\n")
                await run_all_tests()

            elif choice == "8":
                await run_custom_task()

            elif choice == "9":
                check_config()

            else:
                print("❌ 无效选择。请重试。\n")
                continue

            # 再次显示菜单前暂停
            if choice != "9" and choice != "0":
                input("\n" + "=" * 70)
                input("按 Enter 键返回菜单...")

            print()

        except KeyboardInterrupt:
            print("\n\n👋 再见！\n")
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
        print("\n👋 再见！\n")
        sys.exit(0)
