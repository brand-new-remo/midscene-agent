#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path

# 默认格式化当前目录，如果传入目录参数就格式化指定目录
target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")


def format_code(path: Path):
    """格式化 Python 文件"""
    # black 格式化
    subprocess.run(["black", str(path)], check=True)
    # isort 整理 imports
    subprocess.run(["isort", str(path)], check=True)
    print(f"✅ Finished formatting: {path}")


if __name__ == "__main__":
    format_code(target)
