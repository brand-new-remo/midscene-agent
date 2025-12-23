"""
路径工具函数
提供智能的路径检测功能
"""

import os


def get_project_root() -> str:
    """
    获取项目根目录

    Returns:
        项目根目录的绝对路径
    """
    return os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))


def get_tests_dir() -> str:
    """
    获取测试文件目录 (tests/)

    Returns:
        测试目录的绝对路径

    Raises:
        FileNotFoundError: 当找不到测试目录时抛出
    """
    # 从 runner/utils 向上查找 2 级到项目根目录
    current_dir = os.path.dirname(__file__)  # runner/utils
    runner_parent = os.path.dirname(current_dir)  # runner
    project_root = os.path.dirname(runner_parent)  # midscene-agent

    tests_dir = os.path.join(project_root, "tests")

    if os.path.exists(tests_dir):
        return tests_dir

    raise FileNotFoundError(f"找不到测试目录: {tests_dir}")
