#!/usr/bin/env python3
import subprocess
import sys
from pathlib import Path


def main():
    """格式化 Python 文件的命令行入口"""
    # 默认格式化当前目录，如果传入目录参数就格式化指定目录
    target = Path(sys.argv[1]) if len(sys.argv) > 1 else Path(".")
    format_code(target)


def format_code(path: Path):
    """格式化 Python 文件"""
    # black 格式化
    subprocess.run(["black", str(path)], check=True)
    print(f"✅ Finished formatting: {path}")


if __name__ == "__main__":
    main()
