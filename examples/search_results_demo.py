#!/usr/bin/env python3
"""
演示如何使用新的搜索结果提取工具

此脚本展示了如何在执行搜索后，使用专门的工具提取第一个搜索结果的标题。
"""
import asyncio
import os
from dotenv import load_dotenv

# 加载环境变量
load_dotenv()


async def demo_search_results_extraction():
    """演示搜索结果提取功能"""
    from src.agent import MidsceneAgent

    print("=" * 60)
    print("🔍 搜索结果提取演示")
    print("=" * 60)

    # 从环境变量获取配置
    api_key = os.getenv("DEEPSEEK_API_KEY")
    base_url = os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")

    if not api_key:
        print("❌ 错误：未找到 DEEPSEEK_API_KEY")
        return

    # 创建智能体
    agent = MidsceneAgent(
        deepseek_api_key=api_key,
        deepseek_base_url=base_url,
        deepseek_model="deepseek-chat"
    )

    print("\n🚀 初始化智能体...")
    try:
        async with agent:
            print("✅ 智能体初始化成功")

            # 任务1：导航到 Bing 并搜索
            print("\n" + "="*60)
            print("📝 任务1：导航到 Bing 并搜索")
            print("="*60)

            task1 = "导航到 bing.com，然后在搜索框中输入 'LangGraph DeepSeek Midscene' 并执行搜索"

            async for event in agent.execute(task1):
                if "error" in event:
                    print(f"❌ 错误: {event['error']}")
                elif "messages" in event and event["messages"]:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, 'content'):
                        content = last_message.content
                        if content and content.strip():
                            print(f"\n💬 {content}")

            # 等待页面加载
            await asyncio.sleep(3)

            # 任务2：提取第一个搜索结果的标题
            print("\n" + "="*60)
            print("📝 任务2：提取第一个搜索结果的标题")
            print("="*60)

            task2 = "使用 extract_search_results 工具提取当前页面上第一个搜索结果的标题"

            async for event in agent.execute(task2):
                if "error" in event:
                    print(f"❌ 错误: {event['error']}")
                elif "messages" in event and event["messages"]:
                    last_message = event["messages"][-1]
                    if hasattr(last_message, 'content'):
                        content = last_message.content
                        if content and content.strip():
                            print(f"\n✅ 提取结果:")
                            print(f"{content}")

            print("\n" + "="*60)
            print("✨ 演示完成")
            print("="*60)
            print("\n💡 使用说明:")
            print("   1. 现在可以使用 'extract_search_results' 工具专门提取搜索结果")
            print("   2. 该工具会尝试多种查询策略以提高准确性")
            print("   3. 如果失败会自动截图并重新分析")
            print("   4. 可以在任务中使用这个工具名称来提取搜索结果")

    except Exception as e:
        print(f"❌ 演示执行失败: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(demo_search_results_extraction())
