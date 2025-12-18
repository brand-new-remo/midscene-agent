#!/usr/bin/env python3
"""
配置检查模块

提供配置检查功能。
"""

import asyncio
import os

import aiohttp
from dotenv import load_dotenv


def check_config():
    """检查并显示配置。"""
    print("\n" + "=" * 70)
    print("配置检查")
    print("=" * 70 + "\n")

    # 加载 .env 文件
    script_dir = os.path.dirname(os.path.abspath(__file__))
    env_path = os.path.join(os.path.dirname(script_dir), ".env")

    if os.path.exists(env_path):
        load_dotenv(env_path)
        print(f"[OK] .env 文件已加载: {env_path}\n")
    else:
        print("[WARNING] 未找到 .env 文件")
        print("   请将 .env 文件放置在项目根目录下\n")
        return

    # 检查必要的配置
    required_vars = {
        "DEEPSEEK_API_KEY": "DeepSeek API 密钥",
        "OPENAI_API_KEY": "视觉模型 API 密钥 (可选)",
        "MIDSCENE_SERVER_URL": "Node.js 服务地址 (可选)",
    }

    for var, desc in required_vars.items():
        value = os.getenv(var)
        if value:
            # 隐藏密钥的实际值
            display_value = value[:8] + "..." + value[-4:] if len(value) > 12 else "***"
            print(f"[OK] {var}: {display_value} ({desc})")
        else:
            print(f"[WARNING] {var}: 未设置 ({desc})")

    print("-" * 70)

    # 检查 Node.js 服务
    print("\n[INFO] 检查 Node.js 服务...")
    try:

        async def check_server():
            async with aiohttp.ClientSession() as session:
                try:
                    timeout = aiohttp.ClientTimeout(total=2)
                    async with session.get(
                        "http://localhost:3000/api/health", timeout=timeout
                    ) as response:
                        if response.status == 200:
                            health = await response.json()
                            print(f"[OK] Node.js 服务运行正常")
                            print(f"   活跃会话: {health.get('activeSessions', 0)}")
                            print(f"   运行时间: {health.get('uptime', 0):.1f} 秒")
                            return True
                        else:
                            print(f"[WARNING] Node.js 服务返回状态: {response.status}")
                            return False
                except Exception as e:
                    print(f"[ERROR] 无法连接到 Node.js 服务: {e}")
                    return False

        asyncio.run(check_server())
    except Exception as e:
        print(f"[WARNING] 无法检查服务状态: {e}")

    print("\n" + "=" * 70)
    print("[OK] 配置检查完成")
    print("=" * 70)
    print("\n如果所有配置正确，您可以开始使用！")
    print("\n[INFO] 更多信息:")
    print("   - README.md: 完整文档")
    print("   - docs/guides/migration.md: 迁移指南")
    print("   - docs/FINAL_SUMMARY.md: 重构详情")
    print()


if __name__ == "__main__":
    check_config()
