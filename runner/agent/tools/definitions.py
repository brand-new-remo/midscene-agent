"""
MCP 工具定义

本模块提供声明式的 Midscene MCP 工具定义，将所有可用的工具
集中管理，简化工具创建和管理流程。
"""

from typing import Dict, List, Literal

# 工具分类常量
TOOL_CATEGORY_NAVIGATION = "navigation"
TOOL_CATEGORY_INTERACTION = "interaction"
TOOL_CATEGORY_QUERY = "query"
TOOL_CATEGORY_TEST = "test"

# 完整的工具定义
TOOL_DEFINITIONS = {
    # ========== 导航工具 ==========
    "midscene_navigate": {
        "description": "导航到指定的 URL 地址",
        "params": {"url": "要导航到的完整 URL 地址"},
        "category": TOOL_CATEGORY_NAVIGATION,
        "required": True,
    },
    # ========== 核心交互工具 ==========
    "midscene_aiTap": {
        "description": "使用 AI 智能定位并点击页面元素。可以通过自然语言描述要点击的元素，如'点击登录按钮'、'点击搜索框'等",
        "params": {
            "locate": "要点击元素的自然语言描述，支持中文和英文，如'搜索按钮'、'登录链接'、'确认按钮'等",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_aiInput": {
        "description": "使用 AI 智能定位输入框并输入文本。可以同时指定输入的文本内容和目标元素",
        "params": {
            "value": "要输入的文本内容",
            "locate": "输入框的自然语言描述，如'搜索框'、'邮箱输入框'、'密码框'等",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
            "autoDismissKeyboard?": "键盘是否在输入文本后自动关闭，仅在 Android/iOS 中有效，默认 true",
            "mode?": "输入模式：'replace'(先清空再输入) | 'clear'(仅清空) | 'append'(追加到现有内容)，默认 'replace'",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_aiScroll": {
        "description": "使用 AI 执行页面滚动操作，可以指定滚动方向、距离和滚动目标元素",
        "params": {
            "scrollParam": '滚动参数对象，必须是字典格式，包含 direction、scrollType、distance 属性。示例：{"direction": "down", "scrollType": "singleAction", "distance": 500}',
            "locate?": "可选，用自然语言描述的要滚动的元素定位，如'页面内容区域'、'聊天窗口'等，未指定则在当前视窗滚动",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_aiKeyboardPress": {
        "description": "使用 AI 执行键盘按键操作，如按 Enter、Tab、空格、Escape 等",
        "params": {
            "key": "按键名称，如 'Enter'、'Tab'、'Escape'、' '（空格）等",
            "locate?": "可选，指定按键操作的目标元素",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_aiHover": {
        "description": "使用 AI 智能悬停在页面元素上，触发 hover 事件。常用于显示隐藏菜单、工具提示等",
        "params": {
            "locate": "要悬停元素的自然语言描述，如'用户头像'、'菜单项'、'产品图片'等",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    # ========== 标签页管理工具 ==========
    "midscene_setActiveTab": {
        "description": "切换到指定的浏览器标签页",
        "params": {"tabId": "要切换到的标签页 ID"},
        "category": TOOL_CATEGORY_NAVIGATION,
        "required": True,
    },
    # ========== 查询和验证工具 ==========
    "midscene_aiAssert": {
        "description": "使用 AI 智能分析当前页面状态，提取信息或验证条件。可以询问页面内容、提取数据、验证元素等",
        "params": {
            "assertion": "关于页面内容的问题或验证条件，如'页面标题是什么？'、'显示的价格是多少？'、'是否有登录按钮？'等",
            "domIncluded?": "是否向模型发送精简后的 DOM 信息，用于提取 UI 中不可见的属性，默认 false，'visible-only' 表示只发送可见元素",
            "screenshotIncluded?": "是否向模型发送截图，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_location": {
        "description": "通过自然语言定位页面元素，获取元素的坐标和大小信息",
        "params": {"locate": "用自然语言描述的元素定位", "options?": "可选配置项"},
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_getTabs": {
        "description": "获取所有浏览器标签页的信息，包括标签页 ID、标题和 URL",
        "params": {},
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },
    "midscene_getConsoleLogs": {
        "description": "获取浏览器控制台日志，包括错误信息和调试信息",
        "params": {"msgType?": "日志类型过滤，如 'error'、'warn'、'info' 等"},
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },
    "midscene_aiAsk": {
        "description": "使用 AI 模型对当前页面发起提问，获得字符串形式的回答",
        "params": {
            "prompt": "用自然语言描述的询问内容",
            "domIncluded?": "是否向模型发送精简后的 DOM 信息，用于提取 UI 中不可见的属性，默认 false，'visible-only' 表示只发送可见元素",
            "screenshotIncluded?": "是否向模型发送截图，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_aiQuery": {
        "description": "直接从 UI 提取结构化数据，支持字符串、数字、JSON、数组等格式",
        "params": {
            "dataDemand": "描述预期的返回值和格式",
            "domIncluded?": "是否向模型发送精简后的 DOM 信息，用于提取 UI 中不可见的属性，默认 false，'visible-only' 表示只发送可见元素",
            "screenshotIncluded?": "是否向模型发送截图，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_aiBoolean": {
        "description": "从 UI 中提取一个布尔值",
        "params": {
            "prompt": "用自然语言描述的期望值",
            "domIncluded?": "是否向模型发送精简后的 DOM 信息，用于提取 UI 中不可见的属性，默认 false，'visible-only' 表示只发送可见元素",
            "screenshotIncluded?": "是否向模型发送截图，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_aiNumber": {
        "description": "从 UI 中提取一个数字",
        "params": {
            "prompt": "用自然语言描述的期望值",
            "domIncluded?": "是否向模型发送精简后的 DOM 信息，用于提取 UI 中不可见的属性，默认 false，'visible-only' 表示只发送可见元素",
            "screenshotIncluded?": "是否向模型发送截图，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_aiString": {
        "description": "从 UI 中提取一个字符串",
        "params": {
            "prompt": "用自然语言描述的期望值",
            "domIncluded?": "是否向模型发送精简后的 DOM 信息，用于提取 UI 中不可见的属性，默认 false，'visible-only' 表示只发送可见元素",
            "screenshotIncluded?": "是否向模型发送截图，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_aiLocate": {
        "description": "通过自然语言定位页面元素，获取元素的坐标和大小信息",
        "params": {
            "locate": "用自然语言描述的元素定位",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_aiDoubleClick": {
        "description": "使用 AI 智能定位并双击页面元素",
        "params": {
            "locate": "要双击元素的自然语言描述",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_aiRightClick": {
        "description": "使用 AI 智能定位并右键点击页面元素",
        "params": {
            "locate": "要右键点击元素的自然语言描述",
            "deepThink?": "是否开启深度思考模式，如果为 true，AI 会调用模型两次以精确定位元素，默认 false",
            "xpath?": "目标元素的 xpath 路径，如果提供，优先级：xpath > 缓存 > AI 模型",
            "cacheable?": "当启用缓存功能时，是否允许缓存当前 API 调用结果，默认 true",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_aiWaitFor": {
        "description": "等待某个条件达成，支持自定义超时时间和检查间隔",
        "params": {
            "assertion": "用自然语言描述的断言条件",
            "timeoutMs?": "超时时间（毫秒），默认为 15000",
            "checkIntervalMs?": "检查间隔（毫秒），默认为 3000",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    # ========== 测试和调试工具 ==========
    "midscene_playwright_example": {
        "description": "获取 Playwright 使用示例，帮助了解如何编写网页自动化测试",
        "params": {},
        "category": TOOL_CATEGORY_TEST,
        "required": False,
    },
    # ========== AI 自动规划工具 ==========
    "midscene_aiAction": {
        "description": "使用 AI 自动规划并执行一系列 UI 动作。通过自然语言描述任务，AI 会自动分解并执行多个步骤。这是 Midscene 的核心 API，适用于复杂的自动化任务",
        "params": {
            "prompt": "要执行的 UI 动作描述，可以使用自然语言，如'在搜索框中输入 JavaScript，然后点击搜索按钮'",
            "cacheable?": "是否启用缓存，默认 True",
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },
    "midscene_evaluateJavaScript": {
        "description": "在当前页面上下文中执行 JavaScript 表达式，并返回结果",
        "params": {
            "script": "要执行的 JavaScript 代码，如'document.title'、'window.innerWidth' 等"
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },
    "midscene_logScreenshot": {
        "description": "截取当前页面的屏幕截图并在报告中记录，支持添加标题和描述",
        "params": {
            "title?": "截图的标题，如'登录页面'、'搜索结果'等",
            "content?": "截图的描述信息，如'用户 A 的操作截图'",
        },
        "category": TOOL_CATEGORY_TEST,
        "required": False,
    },
    "midscene_recordToReport": {
        "description": "记录截图到测试报告中",
        "params": {
            "title?": "截图标题，默认为 'untitled'",
            "content?": "截图描述",
        },
        "category": TOOL_CATEGORY_TEST,
        "required": False,
    },
    "midscene_getLogContent": {
        "description": "获取页面控制台日志内容",
        "params": {
            "msgType?": "日志类型过滤，如 'error'、'warn'、'info' 等",
            "level?": "日志级别过滤",
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },
    "midscene_freezePageContext": {
        "description": "冻结当前页面上下文，使后续操作复用相同的页面快照，提高大量并发操作的性能",
        "params": {},
        "category": TOOL_CATEGORY_TEST,
        "required": False,
    },
    "midscene_unfreezePageContext": {
        "description": "解冻页面上下文，恢复使用实时页面状态",
        "params": {},
        "category": TOOL_CATEGORY_TEST,
        "required": False,
    },
    "midscene_runYaml": {
        "description": "执行 YAML 格式的自动化脚本，返回所有 .aiQuery 调用的结果",
        "params": {"yaml_script": "YAML 格式的自动化脚本内容，包含 tasks 和 flow 配置"},
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },
    "midscene_setAIActionContext": {
        "description": "设置 AI 动作上下文背景知识，会在调用 agent.aiAction() 时发送给 AI 模型",
        "params": {
            "context": "背景知识描述，如'如果存在 Cookie 同意对话框，请先关闭它'"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },
}

# 工具分类配置
TOOL_CATEGORIES = {
    TOOL_CATEGORY_NAVIGATION: {
        "name": "导航工具",
        "description": "页面导航和标签页操作",
        "tools": ["midscene_navigate", "midscene_setActiveTab"],
    },
    TOOL_CATEGORY_INTERACTION: {
        "name": "交互工具",
        "description": "页面元素交互：点击、输入、滚动、按键、悬停、等待、AI自动规划",
        "tools": [
            "midscene_aiAction",
            "midscene_aiTap",
            "midscene_aiDoubleClick",
            "midscene_aiRightClick",
            "midscene_aiInput",
            "midscene_aiScroll",
            "midscene_aiKeyboardPress",
            "midscene_aiHover",
            "midscene_aiWaitFor",
        ],
    },
    TOOL_CATEGORY_QUERY: {
        "name": "查询工具",
        "description": "页面信息提取、验证和数据查询",
        "tools": [
            "midscene_aiAssert",
            "midscene_aiAsk",
            "midscene_aiQuery",
            "midscene_aiBoolean",
            "midscene_aiNumber",
            "midscene_aiString",
            "midscene_aiLocate",
            "midscene_getTabs",
            "midscene_getConsoleLogs",
            "midscene_getLogContent",
            "midscene_playwright_example",
        ],
    },
    TOOL_CATEGORY_TEST: {
        "name": "测试工具",
        "description": "自动化测试和调试",
        "tools": [
            "midscene_playwright_example",
            "midscene_evaluateJavaScript",
            "midscene_logScreenshot",
            "midscene_recordToReport",
            "midscene_freezePageContext",
            "midscene_unfreezePageContext",
            "midscene_runYaml",
            "midscene_setAIActionContext",
        ],
    },
}

# 推荐的工具组合
RECOMMENDED_TOOL_SETS = {
    "basic": {
        "name": "基础工具集",
        "description": "日常网页自动化所需的基础工具",
        "tools": [
            "midscene_navigate",
            "midscene_aiTap",
            "midscene_aiInput",
            "midscene_aiAssert",
        ],
    },
    "full": {
        "name": "完整工具集",
        "description": "包含所有功能工具的完整集合",
        "tools": list(TOOL_DEFINITIONS.keys()),
    },
    "advanced": {
        "name": "高级工具集",
        "description": "包含基础工具 + 高级交互工具（hover、waitFor 等）+ AI自动规划",
        "tools": [
            "midscene_navigate",
            "midscene_aiAction",
            "midscene_aiTap",
            "midscene_aiDoubleClick",
            "midscene_aiRightClick",
            "midscene_aiInput",
            "midscene_aiScroll",
            "midscene_aiKeyboardPress",
            "midscene_aiHover",
            "midscene_aiWaitFor",
            "midscene_aiAssert",
            "midscene_aiLocate",
            "midscene_logScreenshot",
            "midscene_getTabs",
            "midscene_setActiveTab",
            "midscene_aiQuery",
            "midscene_aiAsk",
        ],
    },
}


def get_tools_by_category(category: str) -> List[str]:
    """根据分类获取工具名称列表"""
    return TOOL_CATEGORIES.get(category, {}).get("tools", [])


def get_tool_definition(tool_name: str) -> Dict:
    """获取指定工具的定义"""
    return TOOL_DEFINITIONS.get(tool_name, {})


def get_all_tool_names() -> List[str]:
    """获取所有工具名称"""
    return list(TOOL_DEFINITIONS.keys())


def get_recommended_tool_set(set_name: str) -> List[str]:
    """获取推荐的工具组合"""
    return RECOMMENDED_TOOL_SETS.get(set_name, {}).get("tools", [])
