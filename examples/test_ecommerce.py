"""
电商测试示例

此示例演示使用自然语言测试电商网站。
"""

import asyncio
import os
import sys
from dotenv import load_dotenv

# 将父目录添加到路径，使其可以导入 src 包
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)
sys.path.insert(0, parent_dir)

# 导入智能体模块
from src.agent import MidsceneAgent

load_dotenv()


async def test_product_search():
    """
    测试电商网站上的产品搜索功能。
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

    # 在 Amazon 上测试产品搜索
    task = """
    让我们测试产品搜索功能：

    1. 导航到 https://www.amazon.com
    2. 搜索 "wireless headphones"
    3. 等待搜索结果加载
    4. 报告显示了多少个搜索结果
    5. 显示的第一个产品的价格和评分是多少？
    6. 点击第一个产品查看详情
    7. 此产品列出的主要特性有哪些？

    请慢慢来，并在进行下一步之前验证每一步。
    """

    print("🛒 电商产品搜索测试")
    print("=" * 60)

    try:
        async with agent_instance:
            async for event in agent_instance.execute(task):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(msg.content)
                    else:
                        print(msg)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()


async def test_form_filling():
    """
    测试表单填写功能。
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

        # 测试表单填写
        task = """
        让我们测试表单填写：

        1. 导航到 https://httpbin.org/forms/post（这是一个测试表单）
        2. 用以下信息填写表单：
           - Custname: "John Doe"
           - Custtel: "123-456-7890"
           - Custemail: "john.doe@example.com"
           - Comments: "This is a test submission"
        3. 提交表单
        4. 报告服务器的响应

        描述你在每一步看到的内容，并确认表单字段填写正确。
        """

        print("📝 表单填写测试")
        print("=" * 60)

        async for event in agent_instance.execute(task):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content"):
                    print(msg.content)
                else:
                    print(msg)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent_instance.cleanup()


async def test_navigation():
    """
        测试导航和页面状态验证。
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

        # 测试导航
        task = """
        让我们测试网站导航：

        1. 导航到 https://news.ycombinator.com
        2. 页面的标题是什么？
        3. 列出页眉中的所有导航链接
        4. 点击 "new" 链接（或类似的）
        5. 等待页面加载并描述可见内容
        6. 返回上一页
        7. 验证你回到了主页

        注意页面结构并报告任何变化。
        """

        print("🧭 导航测试")
        print("=" * 60)

        async for event in agent_instance.execute(task):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content"):
                    print(msg.content)
                else:
                    print(msg)

    except Exception as e:
        print(f"❌ 错误: {e}")
        import traceback
        traceback.print_exc()
    finally:
        await agent_instance.cleanup()


async def run_all_tests():
    """
    按顺序运行所有电商测试。
    """
    print("🧪 电商测试套件")
    print("=" * 60)
    print("\n这将运行多个测试场景:")
    print("1. 产品搜索测试")
    print("2. 表单填写测试")
    print("3. 导航测试")
    print("\n每个测试将按顺序运行。按 Ctrl+C 跳过剩余测试。\n")

    tests = [
        ("产品搜索", test_product_search),
        ("表单填写", test_form_filling),
        ("导航", test_navigation),
    ]

    for name, test_func in tests:
        print(f"\n{'='*60}")
        print(f"正在运行: {name}")
        print(f"{'='*60}\n")

        try:
            await test_func()
            print(f"\n✅ {name} 已成功完成")
        except KeyboardInterrupt:
            print(f"\n⚠️  跳过剩余测试")
            break
        except Exception as e:
            print(f"\n❌ {name} 失败: {e}")
            import traceback
            traceback.print_exc()

        print("\n" + "=" * 60)
        input("按 Enter 键继续下一个测试...")
        print()

    print("\n🎉 所有测试完成！")


if __name__ == "__main__":
    print("电商测试示例\n")

    try:
        choice = input(
            "选择要运行的测试:\n"
            "1. 产品搜索测试\n"
            "2. 表单填写测试\n"
            "3. 导航测试\n"
            "4. 运行所有测试\n\n"
            "输入选择 (1-4): "
        ).strip()

        print()

        if choice == "1":
            asyncio.run(test_product_search())
        elif choice == "2":
            asyncio.run(test_form_filling())
        elif choice == "3":
            asyncio.run(test_navigation())
        elif choice == "4":
            asyncio.run(run_all_tests())
        else:
            print("正在运行产品搜索测试...")
            asyncio.run(test_product_search())

    except KeyboardInterrupt:
        print("\n\n👋 再见！")
    except Exception as e:
        print(f"\n❌ 错误: {e}")
        import traceback
        traceback.print_exc()
