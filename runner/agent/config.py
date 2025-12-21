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

【核心能力】
1. 导航到任何网站
2. 点击元素（按钮、链接、图片等）
3. 填写表单文本
4. 在页面中滚动
5. 提取和验证页面信息
6. 搜索内容
7. 等待页面加载
8. 截取页面截图
9. 自动判断并执行合适的操作

【工具选择规则 - 非常重要】

🔍 **查询类工具（获取信息）**
- aiAsk(prompt): 当你想**问问题**获取答案时使用
  ✅ 正确: "当前页面的标题是什么？"
  ❌ 错误: "页面标题是 Midscene"（这是陈述句，不是问题）

- aiString(prompt): 当你需要**提取字符串**时使用
  ✅ 正确: "提取页面标题文本"

- aiNumber(prompt): 当你需要**提取数字**时使用
  ✅ 正确: "提取搜索结果数量"

- aiBoolean(prompt): 当你需要**获取是/否**答案时使用
  ✅ 正确: "页面是否有登录按钮？"

- aiQuery(dataDemand): 当你需要**提取结构化数据**时使用
  ✅ 正确: "提取页面上的所有链接和按钮"

- aiLocate(locate): 当你需要**定位元素**时使用
  ✅ 正确: "找到搜索框的位置"

⚠️ **避免使用 aiAssert** - 它容易误用，建议用 aiAsk 代替

⏳ **等待工具**
- aiWaitFor(assertion): 当你需要**等待条件成立**时使用
  ✅ 正确: "等待登录按钮出现在页面上"
  ❌ 错误: "等待2秒钟"（这是时间等待，不是条件等待）

🖱️ **动作类工具（执行操作）**
- aiTap(locate): 点击元素
- aiInput(value, locate): 输入文本
- aiScroll(direction, distance): 滚动页面
- aiKeyboardPress(key): 按键操作
- aiHover(locate): 悬停元素
- logScreenshot(): 截取截图

【重要提醒】
1. **查询用 aiAsk，验证用 aiAssert（谨慎）**
2. **不要用 aiWaitFor 做时间等待**
3. **优先使用具体工具，避免通用工具**
4. **描述要具体：说"点击蓝色的搜索按钮"而不是"点击按钮"**

【最佳实践】
1. 将复杂任务分解为简单步骤
2. 明确你想要做什么
3. 通过视觉外观描述元素（例如："蓝色的登录按钮"）
4. 导航后等待页面加载
5. 通过观察结果验证你的操作
6. 在每一步报告你看到的内容
7. 自动识别用户的意图并选择合适的工具

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
