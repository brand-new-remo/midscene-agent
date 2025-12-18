"""
MidsceneAgent 配置管理

本模块提供 MidsceneAgent 的配置管理功能，包括环境变量加载、
配置验证和默认参数设置。
"""

import os
from typing import Any, Dict, Optional

from dotenv import load_dotenv

# 从 .env 文件加载环境变量
# 相对于当前文件的路径
env_path = os.path.join(os.path.dirname(os.path.dirname(__file__)), ".env")
load_dotenv(env_path)


class Config:
    """MidsceneAgent 配置类"""

    # DeepSeek API 配置
    DEEPSEEK_API_KEY: str = os.getenv("DEEPSEEK_API_KEY", "")
    DEEPSEEK_BASE_URL: str = os.getenv(
        "DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1"
    )
    DEEPSEEK_MODEL: str = os.getenv("DEEPSEEK_MODEL", "deepseek-chat")
    DEEPSEEK_TEMPERATURE: float = float(os.getenv("DEEPSEEK_TEMPERATURE", "0"))

    # Midscene 配置
    MIDSCENE_MODEL_NAME: str = os.getenv(
        "MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision"
    )
    MIDSCENE_COMMAND: str = os.getenv("MIDSCENE_COMMAND", "npx")
    MIDSCENE_ARGS: list = os.getenv("MIDSCENE_ARGS", "-y @midscene/mcp").split()
    MIDSCENE_SERVER_URL: str = os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000")

    # 浏览器配置
    CHROME_PATH: Optional[str] = os.getenv("CHROME_PATH")
    HEADLESS: bool = os.getenv("HEADLESS", "false").lower() == "true"

    # 额外环境变量
    OPENAI_API_KEY: str = os.getenv("OPENAI_API_KEY", "")
    OPENAI_BASE_URL: str = os.getenv("OPENAI_BASE_URL", "")

    @classmethod
    def validate(cls) -> bool:
        """
        验证配置。

        Returns:
            如果配置有效返回 True，否则返回 False
        """
        if not cls.DEEPSEEK_API_KEY:
            print("⚠️  警告: DEEPSEEK_API_KEY 未设置")
            return False
        return True

    @classmethod
    def to_dict(cls) -> Dict[str, Any]:
        """
        将配置转换为字典。

        Returns:
            配置的字典表示
        """
        return {
            "deepseek": {
                "api_key": (
                    cls.DEEPSEEK_API_KEY[:10] + "..." if cls.DEEPSEEK_API_KEY else ""
                ),
                "base_url": cls.DEEPSEEK_BASE_URL,
                "model": cls.DEEPSEEK_MODEL,
                "temperature": cls.DEEPSEEK_TEMPERATURE,
            },
            "midscene": {
                "model": cls.MIDSCENE_MODEL_NAME,
                "command": cls.MIDSCENE_COMMAND,
                "args": cls.MIDSCENE_ARGS,
                "api_key": (
                    cls.OPENAI_API_KEY[:10] + "..." if cls.OPENAI_API_KEY else ""
                ),
                "base_url": cls.OPENAI_BASE_URL,
            },
            "browser": {
                "headless": cls.HEADLESS,
                "chrome_path": cls.CHROME_PATH,
            },
        }

    @classmethod
    def print_config(cls):
        """打印当前配置（敏感数据已隐藏）。"""
        import json

        print("\n📋 配置:")
        print(json.dumps(cls.to_dict(), indent=2))


# 智能体的默认提示词
SYSTEM_PROMPT = """你是一个专业的 AI 驱动网页自动化智能体。你可以通过自然语言指令与网页进行交互。

你的能力：
1. 导航到任何网站
2. 点击元素（按钮、链接、图片等）
3. 填写表单文本
4. 在页面中滚动
5. 提取和验证页面信息
6. 搜索内容
7. 等待页面加载
8. 截取页面截图
9. 自动判断并执行合适的操作

可用工具：
- midscene_action: 在网页上执行操作
- midscene_query: 从网页查询信息

自然语言模式支持：
- 你可以直接理解纯粹的自然语言描述
- 无需使用特殊指令（如 ASSERT:、QUERY:、SCREENSHOT:）
- 用户可以用自然语言描述你想要的操作
- 你会自动判断需要执行什么操作（导航、点击、输入、查询、截图等）

最佳实践：
1. 将复杂任务分解为简单步骤
2. 明确你想要做什么
3. 通过视觉外观描述元素（例如："蓝色的登录按钮"）
4. 导航后等待页面加载
5. 通过观察结果验证你的操作
6. 在每一步报告你看到的内容
7. 自动识别用户的意图并选择合适的工具

当你需要与页面交互时：
1. 清楚描述操作（例如："点击右上角的 '搜索' 按钮"）
2. 等待操作完成
3. 观察结果
4. 进行下一步

记住：你能像人类一样看到页面。描述你看到的内容并相应地采取行动。
"""

EXAMPLE_TASKS = [
    {
        "name": "搜索测试",
        "description": "导航到搜索引擎并执行搜索",
        "instruction": """
        1. 导航到 https://www.google.com
        2. 在搜索框中输入 "artificial intelligence"
        3. 点击搜索按钮
        4. 告诉我第一个结果的标题
        """,
    },
    {
        "name": "表单填写",
        "description": "填写并提交联系表单",
        "instruction": """
        1. 导航到 https://httpbin.org/forms/post
        2. 在姓名字段填入 "Test User"
        3. 在邮箱字段填入 "test@example.com"
        4. 在评论字段填入 "This is a test"
        5. 提交表单
        6. 显示响应结果
        """,
    },
    {
        "name": "电商浏览",
        "description": "在电商网站上浏览产品",
        "instruction": """
        1. 导航到 https://www.amazon.com
        2. 搜索 "laptop"
        3. 列出你看到的前 3 个产品及其价格
        4. 点击第一个产品
        5. 告诉我产品评分和评论数量
        """,
    },
]
