#!/usr/bin/env python3
"""
配置检查模块

提供配置检查功能。
"""

import os
import asyncio
import aiohttp


def check_config():
    """检查并显示配置。"""
    print("\n" + "=" * 70)
    print("配置检查")
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