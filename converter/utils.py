"""
XMind 转换工具的工具函数
"""

import os
import tempfile
import zipfile
from pathlib import Path
from typing import List, Tuple

from .exceptions import ConverterError, ConverterFileNotFoundError


def ensure_output_dir(output_dir: str) -> Path:
    """确保输出目录存在"""
    path = Path(output_dir)
    path.mkdir(parents=True, exist_ok=True)
    return path


def validate_input_file(input_path: str) -> Path:
    """验证输入文件是否存在"""
    path = Path(input_path)
    if not path.exists():
        raise ConverterFileNotFoundError(f"输入文件不存在: {input_path}")
    if not path.is_file():
        raise ConverterError(f"输入路径不是文件: {input_path}")
    if not path.suffix.lower() == ".xmind":
        raise ConverterError(f"文件不是 .xmind 格式: {input_path}")
    return path


def validate_input_dir(input_dir: str) -> Path:
    """验证输入目录是否存在"""
    path = Path(input_dir)
    if not path.exists():
        raise ConverterFileNotFoundError(f"输入目录不存在: {input_dir}")
    if not path.is_dir():
        raise ConverterError(f"输入路径不是目录: {input_dir}")
    return path


def find_xmind_files(input_path: str | Path) -> List[Path]:
    """查找所有 .xmind 文件"""
    path = Path(input_path)

    if path.is_file():
        if path.suffix.lower() == ".xmind":
            return [path]
        else:
            return []

    xmind_files = list(path.glob("**/*.xmind"))
    xmind_files.extend(list(path.glob("**/*.XMind")))
    return sorted(set(xmind_files))


def sanitize_filename(filename: str) -> str:
    """清理文件名，移除非法字符"""
    invalid_chars = '<>:"/\\|?*'
    for char in invalid_chars:
        filename = filename.replace(char, "_")
    filename = filename.strip(". ")
    if not filename:
        filename = "unnamed"
    return filename


def is_xmind_file(file_path: Path) -> bool:
    """检查文件是否为有效的 XMind 文件"""
    if not file_path.suffix.lower() == ".xmind":
        return False

    try:
        with zipfile.ZipFile(file_path, "r") as zip_file:
            return (
                "content.json" in zip_file.namelist()
                or "content.xml" in zip_file.namelist()
            )
    except zipfile.BadZipFile:
        return False


def extract_xmind_content(xmind_path: Path) -> Tuple[str, str]:
    """提取 XMind 文件中的 content.json 或 content.xml 内容"""
    try:
        with zipfile.ZipFile(xmind_path, "r") as zip_file:
            if "content.json" in zip_file.namelist():
                content = zip_file.read("content.json").decode("utf-8")
                return content, "json"
            elif "content.xml" in zip_file.namelist():
                content = zip_file.read("content.xml").decode("utf-8")
                return content, "xml"
            else:
                raise ConverterError(
                    f"XMind 文件不包含 content.json 或 content.xml: {xmind_path}"
                )
    except zipfile.BadZipFile:
        raise ConverterError(f"无效的 XMind 文件: {xmind_path}")


def extract_xmind_to_temp(xmind_path: Path) -> Path:
    """将 XMind 文件提取到临时目录并返回路径"""
    import shutil

    temp_dir = Path(tempfile.mkdtemp(prefix="xmind_"))
    try:
        with zipfile.ZipFile(xmind_path, "r") as zip_file:
            zip_file.extractall(temp_dir)
        return temp_dir
    except zipfile.BadZipFile:
        shutil.rmtree(temp_dir, ignore_errors=True)
        raise ConverterError(f"无效的 XMind 文件: {xmind_path}")
