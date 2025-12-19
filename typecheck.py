#!/usr/bin/env python3
"""
typecheck.py

使用 npx 调用 Pyright 对当前项目进行 Python 类型检查（Pylance simple 模式）。
- 不允许自动安装 pyright
- 执行前检查是否已全局安装 pyright
- 所有输出均为机器可读 JSON（适合给 Claude 使用）

前置条件：
- 已安装 Node.js（包含 npm）
- 已全局安装 pyright：
    npm install -g pyright
"""

import subprocess
import sys
import json


def exit_with_json(payload: dict, code: int = 0) -> None:
    print(json.dumps(payload, ensure_ascii=False))
    sys.exit(code)


def main() -> None:
    check: subprocess.CompletedProcess[str] | None = None
    result: subprocess.CompletedProcess[str] | None = None
    # 1. 检查 npm 是否存在，以及是否全局安装了 pyright
    try:
        check = subprocess.run(
            ["npm", "ls", "-g", "pyright", "--depth=0", "--json"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        exit_with_json(
            {
                "tool": "pyright",
                "status": "error",
                "reason": "npm_not_found",
                "message": "未找到 npm，请先安装 Node.js（包含 npm）。",
            },
            code=1,
        )

    if check is None or check.returncode != 0 or '"pyright"' not in check.stdout:
        exit_with_json(
            {
                "tool": "pyright",
                "status": "error",
                "reason": "pyright_not_installed",
                "message": "未检测到全局安装的 pyright。",
                "hint": "请执行：npm install -g pyright",
            },
            code=1,
        )

    # 2. 执行 pyright（禁止隐式安装）
    try:
        result = subprocess.run(
            ["npx", "--no-install", "pyright", "--outputjson"],
            capture_output=True,
            text=True,
        )
    except FileNotFoundError:
        exit_with_json(
            {
                "tool": "pyright",
                "status": "error",
                "reason": "npx_not_found",
                "message": "未找到 npx，请确认 Node.js/npm 安装完整。",
            },
            code=1,
        )

    # 3. 正常情况下，pyright 的 stdout 就是 JSON
    if result is not None and result.stdout:
        # 原样透传 pyright 的 JSON
        print(result.stdout.strip())
        sys.exit(result.returncode)

    # 4. 极端异常兜底
    exit_with_json(
        {
            "tool": "pyright",
            "status": "error",
            "reason": "unknown_error",
            "stderr": result.stderr.strip() if result else "",
        },
        code=1,
    )


if __name__ == "__main__":
    main()
