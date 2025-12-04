"""
MCP 工具管理模块

本模块提供声明式的 Midscene MCP 工具定义和管理功能。
"""

from .definitions import (
    TOOL_DEFINITIONS,
    TOOL_CATEGORIES,
    RECOMMENDED_TOOL_SETS,
    get_tools_by_category,
    get_tool_definition,
    get_all_tool_names,
    get_recommended_tool_set,
    TOOL_CATEGORY_NAVIGATION,
    TOOL_CATEGORY_INTERACTION,
    TOOL_CATEGORY_QUERY,
    TOOL_CATEGORY_DATA,
    TOOL_CATEGORY_TEST,
)

__all__ = [
    "TOOL_DEFINITIONS",
    "TOOL_CATEGORIES",
    "RECOMMENDED_TOOL_SETS",
    "get_tools_by_category",
    "get_tool_definition",
    "get_all_tool_names",
    "get_recommended_tool_set",
    "TOOL_CATEGORY_NAVIGATION",
    "TOOL_CATEGORY_INTERACTION",
    "TOOL_CATEGORY_QUERY",
    "TOOL_CATEGORY_DATA",
    "TOOL_CATEGORY_TEST",
]
