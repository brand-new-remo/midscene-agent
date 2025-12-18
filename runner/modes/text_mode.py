#!/usr/bin/env python3
"""
自然语言测试模式模块

提供自然语言测试相关的功能。
"""

import asyncio
import os
import subprocess
import sys

from runner.utils.path_utils import get_tests_dir


async def run_text_tests() -> None:
    """运行自然语言测试用例"""
    print("\n" + "=" * 70)
    print("📄 自然语言测试用例")
    print("=" * 70 + "\n")

    # 显示可用的文本文件
    texts_dir = get_tests_dir("texts")
    if not os.path.exists(texts_dir):
        print("❌ texts 目录不存在")
        return

    txt_files = [f for f in os.listdir(texts_dir) if f.endswith(".txt")]

    if not txt_files:
        print("❌ 未找到自然语言测试文件")
        return

    print("📋 可用的自然语言测试文件:")
    for i, file in enumerate(txt_files, 1):
        print(f"  {i}. {file}")
    print()

    # 选择要运行的文件
    print("选择要运行的测试 (输入数字，多个用逗号分隔):")
    print("输入 'all' 运行所有测试")
    print("输入 'a' 运行单个测试")

    choice = input("\n你的选择: ").strip()

    try:
        if choice.lower() == "all":
            # 运行所有测试
            print(f"\n🚀 运行所有自然语言测试用例...\n")
            for file in txt_files:
                txt_path = os.path.join(texts_dir, file)
                print(f"\n{'='*70}")
                print(f"运行: {file}")
                print(f"{'='*70}")
                # 使用 subprocess 调用执行器
                runner_dir = os.path.dirname(os.path.dirname(__file__))
                result = subprocess.run(
                    [sys.executable, "-m", "executor.text_executor", txt_path],
                    cwd=runner_dir,
                )
                if result.returncode == 0:
                    print(f"\n✅ {file} 执行完成\n")
                else:
                    print(f"\n❌ {file} 执行失败\n")
        elif choice.lower() == "a":
            # 运行单个测试
            idx = input(f"输入测试编号 (1-{len(txt_files)}): ").strip()
            idx = int(idx) - 1
            if 0 <= idx < len(txt_files):
                txt_path = os.path.join(texts_dir, txt_files[idx])
                print(f"\n{'='*70}")
                print(f"运行: {txt_files[idx]}")
                print(f"{'='*70}")
                # 使用 subprocess 调用执行器
                runner_dir = os.path.dirname(os.path.dirname(__file__))
                result = subprocess.run(
                    [sys.executable, "-m", "executor.text_executor", txt_path],
                    cwd=runner_dir,
                )
                if result.returncode == 0:
                    print(f"\n✅ {txt_files[idx]} 执行完成\n")
                else:
                    print(f"\n❌ {txt_files[idx]} 执行失败\n")
            else:
                print("❌ 无效编号")
        else:
            # 解析多个编号
            selected_indices = [int(x.strip()) - 1 for x in choice.split(",")]
            for idx in selected_indices:
                if 0 <= idx < len(txt_files):
                    txt_path = os.path.join(texts_dir, txt_files[idx])
                    print(f"\n{'='*70}")
                    print(f"运行: {txt_files[idx]}")
                    print(f"{'='*70}")
                    # 使用 subprocess 调用执行器
                    result = subprocess.run(
                        [sys.executable, "-m", "executor.text_executor", txt_path],
                        cwd=os.path.dirname(__file__),
                    )
                    if result.returncode == 0:
                        print(f"\n✅ {txt_files[idx]} 执行完成\n")
                    else:
                        print(f"\n❌ {txt_files[idx]} 执行失败\n")

        print("\n" + "=" * 70)
        print("✨ 所有测试执行完成")
        print("=" * 70)

    except Exception as e:
        print(f"❌ 执行失败: {e}")
        import traceback

        traceback.print_exc()


async def run_all_text_tests() -> None:
    """运行所有自然语言测试"""
    print("\n" + "=" * 70)
    print("🧪 运行所有自然语言测试")
    print("=" * 70 + "\n")

    try:
        texts_dir = get_tests_dir("texts")
        if not os.path.exists(texts_dir):
            print("❌ texts 目录不存在")
            return

        txt_files = [f for f in os.listdir(texts_dir) if f.endswith(".txt")]

        if not txt_files:
            print("❌ 未找到自然语言测试文件")
            return

        print(f"📋 找到 {len(txt_files)} 个自然语言测试文件")
        print("🚀 开始运行所有测试...\n")

        # 使用 subprocess 调用执行器运行所有测试
        for i, file in enumerate(txt_files, 1):
            txt_path = os.path.join(texts_dir, file)
            print(f"\n{'='*70}")
            print(f"运行 {i}/{len(txt_files)}: {file}")
            print(f"{'='*70}")
            # 使用 subprocess 调用执行器
            result = subprocess.run(
                [sys.executable, "-m", "executor.text_executor", txt_path],
                cwd=os.path.dirname(__file__),
            )
            if result.returncode == 0:
                print(f"\n✅ {file} 执行完成\n")
            else:
                print(f"\n❌ {file} 执行失败\n")
            await asyncio.sleep(1)  # 任务间隔

        print("\n" + "=" * 70)
        print("✅ 所有测试执行完成")
        print("=" * 70)

    except Exception as e:
        print(f"❌ 测试执行失败: {e}")
        import traceback

        traceback.print_exc()
