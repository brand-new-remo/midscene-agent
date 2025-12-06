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

# 移除示例导入 - agent文件夹现在只包含核心代码


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
    print("  3. 自定义任务模式")
    print("\n其他:")
    print("  4. 检查配置")
    print("  0. 退出")
    print()


async def run_yaml_tests():
    """运行 YAML 测试用例"""
    print("\n" + "=" * 70)
    print("📝 YAML 测试用例")
    print("=" * 70 + "\n")

    # 显示可用的 YAML 文件
    tests_dir = os.path.join(os.path.dirname(__file__), "tests")
    if not os.path.exists(tests_dir):
        print("❌ tests 目录不存在")
        return

    yaml_files = [f for f in os.listdir(tests_dir) if f.endswith('.yaml')]

    if not yaml_files:
        print("❌ 未找到 YAML 测试文件")
        return

    print("📋 可用的 YAML 测试文件:")
    for i, file in enumerate(yaml_files, 1):
        print(f"  {i}. {file}")
    print()

    await _run_yaml_tests(yaml_files, tests_dir)


async def _run_yaml_tests(yaml_files, tests_dir):
    """使用 Python 直接执行 YAML"""
    print("\n🐍 使用 Python 直接执行 YAML 测试用例")
    print("=" * 70 + "\n")

    # 选择要运行的文件
    print("选择要运行的测试 (输入数字，多个用逗号分隔):")
    print("输入 'all' 运行所有测试")
    print("输入 'a' 运行单个测试")

    choice = input("\n你的选择: ").strip()

    try:
        if choice.lower() == 'all':
            # 运行所有测试
            print(f"\n🚀 运行所有 YAML 测试用例...\n")
            for file in yaml_files:
                yaml_path = os.path.join(tests_dir, file)
                print(f"\n{'='*70}")
                print(f"运行: {file}")
                print(f"{'='*70}")
                os.system(f"python run_yaml_direct.py '{yaml_path}'")
                print(f"\n✅ {file} 执行完成\n")
        elif choice.lower() == 'a':
            # 运行单个测试
            idx = input(f"输入测试编号 (1-{len(yaml_files)}): ").strip()
            idx = int(idx) - 1
            if 0 <= idx < len(yaml_files):
                yaml_path = os.path.join(tests_dir, yaml_files[idx])
                print(f"\n{'='*70}")
                print(f"运行: {yaml_files[idx]}")
                print(f"{'='*70}")
                os.system(f"python run_yaml_direct.py '{yaml_path}'")
                print(f"\n✅ {yaml_files[idx]} 执行完成\n")
            else:
                print("❌ 无效编号")
        else:
            # 解析多个编号
            selected_indices = [int(x.strip()) - 1 for x in choice.split(',')]
            for idx in selected_indices:
                if 0 <= idx < len(yaml_files):
                    yaml_path = os.path.join(tests_dir, yaml_files[idx])
                    print(f"\n{'='*70}")
                    print(f"运行: {yaml_files[idx]}")
                    print(f"{'='*70}")
                    os.system(f"python run_yaml_direct.py '{yaml_path}'")
                    print(f"\n✅ {yaml_files[idx]} 执行完成\n")

        print("\n" + "=" * 70)
        print("✨ 所有测试执行完成")
        print("=" * 70)

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback
        traceback.print_exc()


async def run_custom_task():
    """运行用户提供的自定义任务。"""
    from agent.agent import MidsceneAgent

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

    # 获取当前脚本目录下的 .env 文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")

    # 检查 .env 文件
    if not os.path.exists(env_path):
        print("⚠️ 警告: 未找到 .env 文件")
        print("   复制 .env.example 到 .env 并添加你的 API 密钥\n")
        return

    # 读取 .env 文件
    with open(env_path, "r") as f:
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
                    timeout = aiohttp.ClientTimeout(total=2)
                    async with session.get("http://localhost:3000/api/health", timeout=timeout) as response:
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
    """运行所有 YAML 测试"""
    print("\n" + "=" * 70)
    print("🧪 运行所有 YAML 测试")
    print("=" * 70 + "\n")

    try:
        tests_dir = os.path.join(os.path.dirname(__file__), "tests")
        if not os.path.exists(tests_dir):
            print("❌ tests 目录不存在")
            return

        yaml_files = [f for f in os.listdir(tests_dir) if f.endswith('.yaml')]

        if not yaml_files:
            print("❌ 未找到 YAML 测试文件")
            return

        print(f"📋 找到 {len(yaml_files)} 个 YAML 测试文件")
        print("🚀 开始运行所有测试...\n")

        # 使用 Python 直接执行所有测试
        for i, file in enumerate(yaml_files, 1):
            yaml_path = os.path.join(tests_dir, file)
            print(f"\n{'='*70}")
            print(f"运行 {i}/{len(yaml_files)}: {file}")
            print(f"{'='*70}")
            os.system(f"python run_yaml_direct.py '{yaml_path}'")
            print(f"\n✅ {file} 执行完成\n")
            await asyncio.sleep(1)  # 任务间隔

        print("\n" + "=" * 70)
        print("✅ 所有测试执行完成")
        print("=" * 70)

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback
        traceback.print_exc()


async def main():
    """主入口点。"""
    print_banner()

    # 获取当前脚本目录下的 .env 文件路径
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(script_dir, ".env")

    # 检查 .env 是否存在
    if not os.path.exists(env_path):
        print("⚠️ 警告: 未找到 .env 文件")
        print("   复制 .env.example 到 .env 并添加你的 DEEPSEEK_API_KEY\n")

    while True:
        print_menu()

        try:
            choice = input("输入你的选择 (0-4): ").strip()
            print()

            if choice == "0":
                print("👋 感谢使用 Midscene Agent ！\n")
                sys.exit(0)

            elif choice == "1":
                print("📝 正在运行 YAML 测试用例...\n")
                await run_yaml_tests()

            elif choice == "2":
                print("🧪 正在运行所有 YAML 测试...\n")
                await run_all_tests()

            elif choice == "3":
                print("🎯 启动自定义任务模式...\n")
                await run_custom_task()

            elif choice == "4":
                check_config()

            else:
                print("❌ 无效选择。请重试。\n")
                continue

            # 再次显示菜单前暂停
            if choice in ["1", "2", "3"]:
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
