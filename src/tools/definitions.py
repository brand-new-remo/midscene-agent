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
TOOL_CATEGORY_DATA = "data"
TOOL_CATEGORY_TEST = "test"

# 完整的工具定义
TOOL_DEFINITIONS = {
    # ========== 导航工具 ==========
    "midscene_navigate": {
        "description": "导航到指定的 URL 地址",
        "params": {
            "url": "要导航到的完整 URL 地址"
        },
        "category": TOOL_CATEGORY_NAVIGATION,
        "required": True,
    },

    # ========== 核心交互工具 ==========
    "midscene_aiTap": {
        "description": "使用 AI 智能定位并点击页面元素。可以通过自然语言描述要点击的元素，如'点击登录按钮'、'点击搜索框'等",
        "params": {
            "locate": "要点击元素的自然语言描述，支持中文和英文，如'搜索按钮'、'登录链接'、'确认按钮'等"
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },

    "midscene_aiInput": {
        "description": "使用 AI 智能定位输入框并输入文本。可以同时指定输入的文本内容和目标元素",
        "params": {
            "value": "要输入的文本内容",
            "locate": "输入框的自然语言描述，如'搜索框'、'邮箱输入框'、'密码框'等"
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },

    "midscene_aiScroll": {
        "description": "使用 AI 执行页面滚动操作，可以指定滚动方向和距离",
        "params": {
            "direction": "滚动方向，向上或向下滚动",
            "scrollType": "滚动类型：'once'表示固定距离，'untilBottom'表示滚动到底部",
            "distance?": "滚动距离（像素），默认 500"
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },

    "midscene_aiKeyboardPress": {
        "description": "使用 AI 执行键盘按键操作，如按 Enter、Tab、空格、Escape 等",
        "params": {
            "key": "按键名称，如 'Enter'、'Tab'、'Escape'、' '（空格）等",
            "locate?": "可选，指定按键操作的目标元素"
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },

    "midscene_aiHover": {
        "description": "使用 AI 智能悬停在页面元素上，触发 hover 事件。常用于显示隐藏菜单、工具提示等",
        "params": {
            "locate": "要悬停元素的自然语言描述，如'用户头像'、'菜单项'、'产品图片'等"
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },

    "midscene_aiWaitFor": {
        "description": "使用 AI 智能等待页面满足指定条件，如等待元素出现、等待文本可见、等待页面加载完成等",
        "params": {
            "assertion": "等待条件的自然语言描述，如'等待登录按钮出现'、'等待页面加载完成'、'等待错误提示消失'等",
            "timeoutMs?": "最大等待时间（毫秒），默认 30000（30 秒）",
            "checkIntervalMs?": "检查间隔时间（毫秒），默认 1000（1 秒）"
        },
        "category": TOOL_CATEGORY_INTERACTION,
        "required": True,
    },

    # ========== 查询和验证工具 ==========
    "midscene_aiAssert": {
        "description": "使用 AI 智能分析当前页面状态，提取信息或验证条件。可以询问页面内容、提取数据、验证元素等",
        "params": {
            "assertion": "关于页面内容的问题或验证条件，如'页面标题是什么？'、'显示的价格是多少？'、'是否有登录按钮？'等"
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },

    "midscene_location": {
        "description": "获取当前页面的 URL 地址和页面标题",
        "params": {},
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },

    "midscene_screenshot": {
        "description": "截取当前页面的屏幕截图，支持全页面截图或指定元素截图",
        "params": {
            "name?": "截图名称，用于标识截图文件",
            "element?": "可选，指定要截图的页面元素",
            "fullPage?": "是否截取完整页面，默认 False"
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },

    "midscene_get_tabs": {
        "description": "获取所有浏览器标签页的信息，包括标签页 ID、标题和 URL",
        "params": {},
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },

    "midscene_get_screenshot": {
        "description": "获取已保存的截图文件",
        "params": {
            "name": "截图名称"
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": True,
    },

    "midscene_get_console_logs": {
        "description": "获取浏览器控制台日志，包括错误信息和调试信息",
        "params": {
            "msgType?": "日志类型过滤，如 'error'、'warn'、'info' 等"
        },
        "category": TOOL_CATEGORY_QUERY,
        "required": False,
    },

    # ========== 数据获取工具 ==========
    "midscene_get": {
        "description": "获取页面指定元素的属性值，如文本内容、链接地址、图片源等",
        "params": {
            "locate": "要获取数据的元素描述",
            "attribute?": "可选，指定要获取的属性名，默认获取文本内容"
        },
        "category": TOOL_CATEGORY_DATA,
        "required": True,
    },

    "midscene_element": {
        "description": "获取页面元素的详细信息，包括位置、大小、属性等",
        "params": {
            "locate": "要获取信息的元素描述"
        },
        "category": TOOL_CATEGORY_DATA,
        "required": True,
    },

    "midscene_set": {
        "description": "设置页面指定元素的值，比 aiInput 更精细的控制",
        "params": {
            "locate": "要设置的元素描述",
            "value": "要设置的值"
        },
        "category": TOOL_CATEGORY_DATA,
        "required": True,
    },

    # ========== 测试和调试工具 ==========
    "midscene_playwright": {
        "description": "直接执行 Playwright 代码，用于高级用户进行底层浏览器控制",
        "params": {
            "code": "要执行的 Playwright JavaScript 代码"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },

    "midscene_define": {
        "description": "定义测试场景，用于创建可重复执行的自动化测试",
        "params": {
            "definition": "测试场景的定义描述"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },

    "midscene_run": {
        "description": "运行指定的测试场景",
        "params": {
            "testName": "要运行的测试名称"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },

    "midscene_retrieve": {
        "description": "检索测试执行的结果",
        "params": {
            "query": "查询条件或测试名称"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },

    "midscene_replay": {
        "description": "回放测试执行的完整过程",
        "params": {
            "sessionId": "测试会话 ID"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": True,
    },

    "midscene_report": {
        "description": "生成测试报告",
        "params": {
            "format?": "报告格式，如 'html'、'json' 等"
        },
        "category": TOOL_CATEGORY_TEST,
        "required": False,
    },
}

# 工具分类配置
TOOL_CATEGORIES = {
    TOOL_CATEGORY_NAVIGATION: {
        "name": "导航工具",
        "description": "页面导航和 URL 操作",
        "tools": ["midscene_navigate"]
    },
    TOOL_CATEGORY_INTERACTION: {
        "name": "交互工具",
        "description": "页面元素交互：点击、输入、滚动、按键、悬停、等待",
        "tools": [
            "midscene_aiTap",
            "midscene_aiInput",
            "midscene_aiScroll",
            "midscene_aiKeyboardPress",
            "midscene_aiHover",
            "midscene_aiWaitFor"
        ]
    },
    TOOL_CATEGORY_QUERY: {
        "name": "查询工具",
        "description": "页面信息提取、验证和截图",
        "tools": [
            "midscene_aiAssert",
            "midscene_location",
            "midscene_screenshot",
            "midscene_get_tabs",
            "midscene_get_screenshot",
            "midscene_get_console_logs"
        ]
    },
    TOOL_CATEGORY_DATA: {
        "name": "数据工具",
        "description": "获取和设置页面元素数据",
        "tools": [
            "midscene_get",
            "midscene_element",
            "midscene_set"
        ]
    },
    TOOL_CATEGORY_TEST: {
        "name": "测试工具",
        "description": "自动化测试和调试",
        "tools": [
            "midscene_playwright",
            "midscene_define",
            "midscene_run",
            "midscene_retrieve",
            "midscene_replay",
            "midscene_report"
        ]
    }
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
        ]
    },
    "full": {
        "name": "完整工具集",
        "description": "包含所有功能工具的完整集合",
        "tools": list(TOOL_DEFINITIONS.keys())
    },
    "advanced": {
        "name": "高级工具集",
        "description": "包含基础工具 + 高级交互工具（hover、waitFor 等）",
        "tools": [
            "midscene_navigate",
            "midscene_aiTap",
            "midscene_aiInput",
            "midscene_aiScroll",
            "midscene_aiKeyboardPress",
            "midscene_aiHover",
            "midscene_aiWaitFor",
            "midscene_aiAssert",
            "midscene_location",
            "midscene_get",
            "midscene_element",
        ]
    }
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
