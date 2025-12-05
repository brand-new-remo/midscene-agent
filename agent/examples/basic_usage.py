"""
Midscene Agent 使用示例

演示如何使用基于 HTTP 的 Midscene Agent，
包括基础网页自动化、查询和流式响应功能。
"""

import asyncio
import os
from dotenv import load_dotenv
import sys
sys.path.insert(0, os.path.join(os.path.dirname(__file__), '..'))
from src.agent import MidsceneAgent

# 加载环境变量
# 相对于当前示例文件的路径
env_path = os.path.join(os.path.dirname(__file__), '..', '.env')
load_dotenv(env_path)


async def basic_example():
    """
    基础网页自动化示例

    演示如何使用 Midscene Agent 执行基本的网页操作
    """
    print("\n" + "=" * 70)
    print("🚀 Midscene Agent - 基础示例")
    print("=" * 70)

    # 获取 API 密钥
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        print("请在 .env 文件中设置 DEEPSEEK_API_KEY")
        return

    # 准备 Midscene 配置
    midscene_config = {
        "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
        "api_key": os.getenv("OPENAI_API_KEY"),
        "base_url": os.getenv("OPENAI_BASE_URL"),
        "headless": False,  # 显示浏览器窗口以便观察
        "viewport_width": 1280,
        "viewport_height": 768,
    }

    # 创建 Agent
    agent = MidsceneAgent(
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config=midscene_config,
        tool_set="full",  # 使用完整工具集
        enable_websocket=True,  # 启用 WebSocket 流式响应
    )

    try:
        # 使用异步上下文管理器
        async with agent:
            print("\n✅ Agent 初始化成功")

            # 示例任务：访问 GitHub 并执行操作
            task = """请完成以下网页自动化任务：
            1. 导航到 https://midscenejs.com/zh/index.html
            2. 等待页面完全加载
            3. 点击左侧导航菜单中的"MCP 服务"菜单项
            4. 检查是否显示了“使用场景”部分
            """

            print(f"\n📝 执行任务: {task}")
            print("\n" + "-" * 70)

            # 执行任务并流式显示结果
            async for event in agent.execute(task, stream=True):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if hasattr(latest_msg, "content") and latest_msg.content:
                        print(f"💬 {latest_msg.content}")
                elif "error" in event:
                    print(f"❌ 错误: {event['error']}")

            print("\n" + "-" * 70)

            # 额外的交互示例
            print("\n🔍 执行额外查询...")

            # 获取当前页面位置
            location_result = await agent.http_client.execute_query("location")
            print(f"📍 当前页面位置: {location_result}")

            # 截取屏幕截图
            screenshot_result = await agent.take_screenshot(name="example_screenshot")
            print(f"📸 截图完成: {screenshot_result.get('screenshot', {})}")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()


async def query_example():
    """
    页面查询示例

    演示如何使用Agent 查询页面信息
    """
    print("\n" + "=" * 70)
    print("🔍 Midscene Agent - 查询示例")
    print("=" * 70)

    # 获取 API 密钥
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        return

    # 创建 Agent
    agent = MidsceneAgent(
        deepseek_api_key=deepseek_api_key,
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config={
            "headless": False,
            "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
        },
        tool_set="full",
        enable_websocket=True,
    )

    try:
        async with agent:
            print("\n✅ Agent 初始化成功")

            # 访问百度首页并查询信息
            task = """访问 https://www.baidu.com 并：
            1. 导航到百度首页
            2. 等待页面加载完成
            3. 查询页面标题是什么
            4. 验证是否有搜索输入框
            5. 提取页面上显示的主要文本内容
            """

            print(f"\n📝 执行任务: {task}")
            print("\n" + "-" * 70)

            async for event in agent.execute(task, stream=True):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if hasattr(latest_msg, "content") and latest_msg.content:
                        print(f"💬 {latest_msg.content}")

            print("\n" + "-" * 70)

            # 使用 aiQuery 提取结构化数据
            print("\n📊 使用 aiQuery 提取结构化数据...")
            query_result = await agent.http_client.execute_query(
                "aiQuery",
                {
                    "dataDemand": {
                        "title": "页面标题",
                        "searchBoxExists": "是否存在搜索输入框",
                        "mainLinks": "页面上主要链接的文本, string[]",
                    },
                    "options": {"domIncluded": True},
                },
            )
            print(f"📋 查询结果: {query_result}")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()


async def interactive_example():
    """
    交互式多任务示例

    演示如何连续执行多个相关任务
    """
    print("\n" + "=" * 70)
    print("🔄 Midscene Agent - 交互式示例")
    print("=" * 70)

    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        return

    agent = MidsceneAgent(
        deepseek_api_key=deepseek_api_key,
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config={
            "headless": False,
            "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
        },
        tool_set="full",
        enable_websocket=True,
    )

    try:
        async with agent:
            print("\n✅ Agent 初始化成功")

            # 任务列表
            tasks = [
                "访问 https://httpbin.org 并导航到首页",
                "找到页面上的输入框并输入测试数据",
                "截取当前页面的屏幕截图",
                "验证输入是否成功",
                "获取页面的控制台日志",
            ]

            for i, task in enumerate(tasks, 1):
                print(f"\n📝 任务 {i}/{len(tasks)}: {task}")
                print("-" * 50)

                async for event in agent.execute(task, stream=True):
                    if "messages" in event:
                        latest_msg = event["messages"][-1]
                        if hasattr(latest_msg, "content") and latest_msg.content:
                            print(f"💬 {latest_msg.content}")

                # 任务间隔
                if i < len(tasks):
                    print("\n⏳ 等待 2 秒...")
                    await asyncio.sleep(2)

            print("\n✅ 所有任务执行完成")

            # 获取会话信息
            session_info = await agent.get_session_info()
            print(f"\n📊 会话统计:")
            print(f"  - 活跃会话数: {len(session_info['active_sessions'])}")
            print(f"  - 动作历史数: {len(session_info['session_history'])}")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()


async def test_new_features():
    """
    测试新功能示例

    演示Agent 的新特性
    """
    print("\n" + "=" * 70)
    print("🆕 Midscene Agent - 新功能测试")
    print("=" * 70)

    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ 错误: 未找到 DEEPSEEK_API_KEY")
        return

    agent = MidsceneAgent(
        deepseek_api_key=deepseek_api_key,
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config={
            "headless": False,
            "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
        },
        tool_set="full",
        enable_websocket=True,
    )

    try:
        async with agent:
            print("\n✅ Agent 初始化成功")

            # 测试 WebSocket 流式响应
            print("\n🔌 测试 WebSocket 流式响应...")
            task_with_progress = """访问 https://example.com 并执行以下操作：
            1. 导航到页面
            2. 等待页面完全加载
            3. 悬停在页面标题上
            4. 滚动页面到底部
            5. 滚动回到顶部
            """

            async for event in agent.execute(task_with_progress, stream=True):
                if "messages" in event:
                    latest_msg = event["messages"][-1]
                    if hasattr(latest_msg, "content") and latest_msg.content:
                        print(f"📡 [流式] {latest_msg.content}")

            # 测试健康检查
            print("\n🏥 测试健康检查...")
            health = await agent.health_check()
            print(f"健康状态: {health}")

            # 测试会话管理
            print("\n📋 测试会话信息...")
            sessions = await agent.http_client.get_sessions()
            print(f"活跃会话: {sessions}")

    except Exception as e:
        print(f"\n❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()


async def main():
    """主函数"""
    print("\n" + "=" * 70)
    print("🎉 欢迎使用Midscene Agent！")
    print("本示例展示了基于 HTTP + WebSocket 的新架构")
    print("=" * 70)

    # 检查 Node.js 服务是否运行
    import aiohttp

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get("http://localhost:3000/api/health") as response:
                if response.status == 200:
                    print("\n✅ Node.js Midscene 服务运行正常")
                else:
                    print(f"\n⚠️ Node.js 服务返回状态: {response.status}")
    except Exception as e:
        print(f"\n❌ 无法连接到 Node.js 服务: {e}")
        print("请确保已启动 Node.js 服务: cd server && npm install && npm start")
        return

    # 运行示例
    print("\n选择要运行的示例:")
    print("1. 基础网页自动化示例")
    print("2. 页面查询示例")
    print("3. 交互式多任务示例")
    print("4. 新功能测试示例")
    print("0. 退出")

    choice = input("\n请输入选择 (0-4): ").strip()

    if choice == "1":
        await basic_example()
    elif choice == "2":
        await query_example()
    elif choice == "3":
        await interactive_example()
    elif choice == "4":
        await test_new_features()
    elif choice == "0":
        print("\n👋 再见！")
    else:
        print("\n❌ 无效选择")


if __name__ == "__main__":
    try:
        asyncio.run(main())
    except KeyboardInterrupt:
        print("\n\n👋 再见！\n")
    except Exception as e:
        print(f"\n❌ 发生错误: {e}")
        import traceback

        traceback.print_exc()
