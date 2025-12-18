"""
路径工具函数
提供智能的路径检测功能，支持新旧两种目录结构
"""

import os


def get_project_root() -> str:
    """
    获取项目根目录

    Returns:
        项目根目录的绝对路径
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_tests_dir(test_type: str) -> str:
    """
    获取测试目录 - 支持新旧两种结构

    此函数会智能检测测试文件的位置：
    1. 首先尝试新的路径结构：tests/{test_type}/
    2. 如果新路径不存在，回退到旧路径：runner/{test_type}/
    3. 如果旧路径也不存在，抛出 FileNotFoundError

    Args:
        test_type: 测试类型，应为 'yamls' 或 'texts'

    Returns:
        测试目录的绝对路径

    Raises:
        FileNotFoundError: 当找不到测试目录时抛出
    """
    if test_type not in ("yamls", "texts"):
        raise ValueError(f"test_type 必须是 'yamls' 或 'texts'，不能是 '{test_type}'")

    # 方法1: 使用当前文件位置向上查找3级到项目根目录
    current_dir = os.path.dirname(__file__)  # runner/utils
    runner_parent = os.path.dirname(current_dir)  # runner
    project_root = os.path.dirname(runner_parent)  # midscene-agent

    new_path = os.path.join(project_root, "tests", test_type)

    # 检查新路径是否存在
    if os.path.exists(new_path):
        return new_path

    # 回退到旧路径（向后兼容）
    old_path = os.path.join(runner_parent, test_type)
    if os.path.exists(old_path):
        print(f"⚠️ 警告: 仍在使用旧路径 {old_path}")
        print(f"   建议将测试文件移动到 {new_path}")
        return old_path

    raise FileNotFoundError(f"找不到测试目录: {new_path} 或 {old_path}")
