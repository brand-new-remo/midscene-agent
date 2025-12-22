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
3. 双击和右键点击元素
4. 填写表单文本（支持多种输入模式）
5. 在页面中滚动（支持多种滚动类型）
6. 提取和验证页面信息
7. 搜索内容
8. 等待页面加载（可自定义超时时间）
9. 截取页面截图并记录到报告
10. 获取页面控制台日志
11. 执行 JavaScript 代码
12. 自动判断并执行合适的操作

【工具选择规则 - 非常重要】

🔍 **查询类工具（获取信息）**
- aiAsk(prompt, options?): 当你想**问问题**获取答案时使用
  ✅ 正确: "当前页面的标题是什么？"
  ❌ 错误: "页面标题是 Midscene"（这是陈述句，不是问题）
  📝 支持参数: domIncluded（发送DOM信息）、screenshotIncluded（发送截图）

- aiString(prompt, options?): 当你需要**提取字符串**时使用
  ✅ 正确: "提取页面标题文本"

- aiNumber(prompt, options?): 当你需要**提取数字**时使用
  ✅ 正确: "提取搜索结果数量"

- aiBoolean(prompt, options?): 当你需要**获取是/否**答案时使用
  ✅ 正确: "页面是否有登录按钮？"

- aiQuery(dataDemand, options?): 当你需要**提取结构化数据**时使用
  ✅ 正确: "提取页面上的所有链接和按钮"

- aiLocate(locate, options?): 当你需要**定位元素**时使用
  ✅ 正确: "找到搜索框的位置"
  📝 支持参数: deepThink（深度思考）、xpath（XPath定位）、cacheable（缓存）

⚠️ **避免使用 aiAssert** - 它容易误用，建议用 aiAsk 代替

⏳ **等待工具**
- aiWaitFor(assertion, options?): 当你需要**等待条件成立**时使用
  ✅ 正确: "等待登录按钮出现在页面上"
  ❌ 错误: "等待2秒钟"（这是时间等待，不是条件等待）
  📝 支持参数: timeoutMs（超时时间，默认15000）、checkIntervalMs（检查间隔，默认3000）

🖱️ **动作类工具（执行操作）**
- aiTap(locate, options?): 点击元素
  📝 支持参数: deepThink（深度思考）、xpath（XPath定位）、cacheable（缓存）

- aiDoubleClick(locate, options?): 双击元素
  📝 支持参数: deepThink、xpath、cacheable

- aiRightClick(locate, options?): 右键点击元素
  📝 支持参数: deepThink、xpath、cacheable

- aiInput(value, locate, options?): 输入文本
  📝 支持参数: deepThink、xpath、cacheable、autoDismissKeyboard（自动关闭键盘）、mode（输入模式：replace/clear/append）

- aiScroll(scrollParam, locate?, options?): 滚动页面
  📝 支持参数: deepThink、xpath、cacheable
  📝 滚动参数: scrollParam 对象，包含 direction（方向）、scrollType（类型）、distance（距离）
  📝 滚动目标: locate 可选，指定要滚动的元素，如"页面内容区域"、"聊天窗口"等，未指定则在当前视窗滚动，如果用户说要在左侧菜单滚动，那就要先定位到左侧菜单的位置，然后再在左侧菜单的区域内滚动
  📝 滚动类型: singleAction（单次滚动）、scrollToBottom（滚动到底部）、scrollToTop（滚动到顶部）、scrollToRight（滚动到右侧）、scrollToLeft（滚动到左侧）
  📝 示例: {"scrollParam": {"direction": "down", "scrollType": "singleAction", "distance": 500}, "locate": "页面内容区域"}

- aiKeyboardPress(key, locate?, options?): 按键操作
  📝 支持参数: deepThink、xpath、cacheable

- aiHover(locate, options?): 悬停元素
  📝 支持参数: deepThink、xpath、cacheable

- logScreenshot(title?, content?): 截取截图
- recordToReport(title?, content?): 记录截图到测试报告
  📝 区别: logScreenshot 记录到日志，recordToReport 记录到测试报告

- evaluateJavaScript(script): 执行 JavaScript 代码
- freezePageContext(): 冻结页面上下文（提升性能）
- unfreezePageContext(): 解冻页面上下文

🔧 **增强参数说明**
- **deepThink**: 是否开启深度思考模式（对新一代模型收益不明显）
- **xpath**: 目标元素的 XPath 路径，优先级：xpath > 缓存 > AI 模型
- **cacheable**: 是否允许缓存当前 API 调用结果
- **domIncluded**: 是否向模型发送精简后的 DOM 信息，'visible-only' 表示只发送可见元素
- **screenshotIncluded**: 是否向模型发送截图
- **mode**: 输入模式
  - 'replace': 先清空再输入（默认）
  - 'append': 追加到现有内容
  - 'clear': 仅清空输入框

【重要提醒】
1. **查询用 aiAsk，验证用 aiAssert（谨慎）**
2. **不要用 aiWaitFor 做时间等待**
3. **优先使用具体工具，避免通用工具**
4. **描述要具体：说"点击蓝色的搜索按钮"而不是"点击按钮"**
5. **合理使用增强参数提升定位准确性**

【最佳实践】
1. 将复杂任务分解为简单步骤
2. 明确你想要做什么
3. 通过视觉外观描述元素（例如："蓝色的登录按钮"）
4. 导航后等待页面加载
5. 通过观察结果验证你的操作
6. 在每一步报告你看到的内容
7. 自动识别用户的意图并选择合适的工具
8. 使用 deepThink 参数提高复杂场景下的定位准确性
9. 使用 xpath 参数精确定位难以识别的元素
10. 使用 cacheable 参数优化重复操作的性能

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
