#!/usr/bin/env python3
"""
Midscene Agent 测试脚本

验证 Node.js 服务、HTTP 客户端和 Agent 的功能
"""

import asyncio
import os
import sys
import json
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()

# 添加 src 到路径
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

from src.http_client import MidsceneHTTPClient, SessionConfig
from src.agent import MidsceneAgent


async def test_http_client():
    """测试 HTTP 客户端"""
    print("\n" + "=" * 70)
    print("🔍 测试 1: HTTP 客户端")
    print("=" * 70)

    client = MidsceneHTTPClient(base_url="http://localhost:3000")

    try:
        # 连接
        await client.connect()
        print("✅ HTTP 客户端连接成功")

        # 健康检查
        health = await client.health_check()
        if health.get("status") == "ok":
            print("✅ 服务器健康检查通过")
            print(f"   活跃会话: {health.get('activeSessions', 0)}")
        else:
            print(f"⚠️ 服务器状态: {health}")
            return False

        # 创建会话
        config = SessionConfig(
            model=os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
            headless=True
        )

        session_id = await client.create_session(config)
        print(f"✅ 会话创建成功: {session_id[:20]}...")

        # 测试动作执行
        print("\n📝 测试动作执行...")
        async for event in client.execute_action("navigate", {"url": "https://example.com"}):
            if event.get("success"):
                print("✅ 导航动作执行成功")
                break
            elif event.get("error"):
                print(f"❌ 导航失败: {event['error']}")
                return False

        # 测试查询
        print("\n🔍 测试查询执行...")
        query_result = await client.execute_query("location")
        if query_result.get("success"):
            print("✅ 查询执行成功")
            print(f"   结果: {query_result.get('result', {})}")
        else:
            print(f"❌ 查询失败: {query_result}")
            return False

        # 清理
        await client.cleanup()
        print("✅ HTTP 客户端测试完成")

        return True

    except Exception as e:
        print(f"❌ HTTP 客户端测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_agent():
    """测试 Agent"""
    print("\n" + "=" * 70)
    print("🤖 测试 2: Agent")
    print("=" * 70)

    # 检查 API 密钥
    deepseek_api_key = os.getenv("DEEPSEEK_API_KEY")
    if not deepseek_api_key:
        print("❌ 未找到 DEEPSEEK_API_KEY，跳过 Agent 测试")
        return True

    # 创建 Agent
    agent = MidsceneAgent(
        deepseek_api_key=deepseek_api_key,
        deepseek_base_url=os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"),
        midscene_server_url=os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000"),
        midscene_config={
            "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"),
            "headless": True,
            "api_key": os.getenv("OPENAI_API_KEY"),
            "base_url": os.getenv("OPENAI_BASE_URL")
        },
        tool_set="basic",
        enable_websocket=True
    )

    try:
        # 初始化
        await agent.initialize()
        print("✅ Agent 初始化成功")

        # 简单任务
        print("\n📝 执行简单任务...")
        task = "访问 https://example.com 并验证页面加载"

        results = []
        async for event in agent.execute(task, stream=True):
            if "messages" in event:
                latest_msg = event["messages"][-1]
                if hasattr(latest_msg, "content") and latest_msg.content:
                    content = latest_msg.content[:100] + "..." if len(latest_msg.content) > 100 else latest_msg.content
                    print(f"   💬 {content}")
                    results.append(latest_msg.content)

        if results:
            print("✅ Agent 执行成功")
        else:
            print("⚠️ Agent 未返回结果")

        # 健康检查
        health = await agent.health_check()
        if health.get("status") == "ok":
            print("✅ Agent 健康检查通过")

        # 会话信息
        session_info = await agent.get_session_info()
        print(f"✅ 会话信息: {len(session_info['active_sessions'])} 活跃会话")

        # 清理
        await agent.cleanup()
        print("✅ Agent 测试完成")

        return True

    except Exception as e:
        print(f"❌ Agent 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return False


async def test_node_server():
    """测试 Node.js 服务器直接访问"""
    print("\n" + "=" * 70)
    print("🌐 测试 3: Node.js 服务器")
    print("=" * 70)

    try:
        import aiohttp

        async with aiohttp.ClientSession() as session:
            # 健康检查
            async with session.get("http://localhost:3000/api/health") as response:
                if response.status == 200:
                    health = await response.json()
                    print("✅ Node.js 服务器运行正常")
                    print(f"   状态: {health.get('status')}")
                    print(f"   活跃会话: {health.get('activeSessions', 0)}")
                    print(f"   运行时间: {health.get('uptime', 0):.2f} 秒")
                else:
                    print(f"⚠️ 服务器返回状态: {response.status}")
                    return False

            # 测试会话创建
            async with session.post(
                "http://localhost:3000/api/sessions",
                json={"headless": True}
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data["session_id"]
                    print(f"✅ 会话创建成功: {session_id[:20]}...")

                    # 清理会话
                    async with session.delete(
                        f"http://localhost:3000/api/sessions/{session_id}"
                    ) as delete_response:
                        if delete_response.status == 200:
                            print("✅ 会话清理成功")
                        else:
                            print(f"⚠️ 会话清理失败: {delete_response.status}")

                else:
                    error = await response.text()
                    print(f"❌ 会话创建失败: {error}")
                    return False

            # 测试指标端点
            async with session.get("http://localhost:3000/metrics") as response:
                if response.status == 200:
                    metrics_text = await response.text()
                    if "midscene_actions_total" in metrics_text:
                        print("✅ Prometheus 指标端点正常")
                    else:
                        print("⚠️ 指标格式异常")
                else:
                    print(f"⚠️ 指标端点返回状态: {response.status}")

            print("✅ Node.js 服务器测试完成")
            return True

    except Exception as e:
        print(f"❌ Node.js 服务器测试失败: {e}")
        print("请确保 Node.js 服务正在运行: cd server && npm start")
        return False


async def run_all_tests():
    """运行所有测试"""
    print("\n" + "=" * 70)
    print("🧪 Midscene Agent 架构测试")
    print("=" * 70)

    tests = [
        ("Node.js 服务器", test_node_server),
        ("HTTP 客户端", test_http_client),
        ("Agent", test_agent)
    ]

    results = {}

    for test_name, test_func in tests:
        try:
            result = await test_func()
            results[test_name] = result
        except Exception as e:
            print(f"\n❌ {test_name} 测试异常: {e}")
            results[test_name] = False

    # 输出总结
    print("\n" + "=" * 70)
    print("📊 测试总结")
    print("=" * 70)

    for test_name, result in results.items():
        status = "✅ 通过" if result else "❌ 失败"
        print(f"{test_name}: {status}")

    total_tests = len(results)
    passed_tests = sum(1 for r in results.values() if r)

    print(f"\n总计: {passed_tests}/{total_tests} 测试通过")

    if passed_tests == total_tests:
        print("\n🎉 所有测试通过！架构运行正常")
        return 0
    else:
        print(f"\n⚠️ {total_tests - passed_tests} 项测试失败")
        print("请检查失败的测试并修复问题")
        return 1


async def main():
    """主函数"""
    try:
        exit_code = await run_all_tests()
        sys.exit(exit_code)
    except KeyboardInterrupt:
        print("\n\n👋 测试被用户中断")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ 测试异常: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)


if __name__ == "__main__":
    asyncio.run(main())