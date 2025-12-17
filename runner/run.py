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

# 将当前目录添加到路径
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))

# 导入配置检查函数
from runner.check_config import check_config

# 导入模式模块
from runner.modes import yaml_mode, text_mode, custom_mode


def print_banner():
    """打印应用程序横幅。"""
    print("\n" + "=" * 70)
    print("  🕷️  Midscene LangGraph Agent - 快速启动器")
    print("=" * 70)
    print("\n基于 HTTP + WebSocket 的现代化架构")
    print("更稳定、更强大、更智能！\n")


def print_menu():
    """打印主菜单。"""
    print("选择功能:\n")
    print("📝 YAML 测试用例:")
    print("  1. 运行单个 YAML 测试")
    print("  2. 运行所有 YAML 测试")
    print("\n📄 自然语言测试用例:")
    print("  3. 运行单个自然语言测试")
    print("  4. 运行所有自然语言测试")
    print("\n其他:")
    print("  5. 自定义任务模式")
    print("  6. 检查配置")
    print("  0. 退出")
    print()


async def main():
    """主入口点。"""
    print_banner()

    # 获取当前脚本目录下的 .env 文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(os.path.dirname(script_dir), ".env")

    # 检查 .env 是否存在
    if not os.path.exists(env_path):
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
                print("📝 正在运行 YAML 测试用例...\n")
                await yaml_mode.run_yaml_tests()

            elif choice == "2":
                print("🧪 正在运行所有 YAML 测试...\n")
                await yaml_mode.run_all_tests()

            elif choice == "3":
                print("📄 正在运行自然语言测试用例...\n")
                await text_mode.run_text_tests()

            elif choice == "4":
                print("🧪 正在运行所有自然语言测试...\n")
                await text_mode.run_all_text_tests()

            elif choice == "5":
                print("🎯 启动自定义任务模式...\n")
                await custom_mode.run_custom_task()

            elif choice == "6":
                check_config()

            else:
                print("❌ 无效选择。请重试。\n")
                continue

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



def main_wrapper():
    """同步包装函数，用于CLI入口点"""
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n👋 感谢使用 Midscene Agent ！\n")
        sys.exit(0)


if __name__ == "__main__":
    main_wrapper()
