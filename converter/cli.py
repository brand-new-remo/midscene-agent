"""
命令行接口
"""

import argparse
import sys
from pathlib import Path
from typing import List

from .exceptions import ConverterError
from .text_generator import TextGenerator
from .utils import (
    ensure_output_dir,
    find_xmind_files,
    validate_input_dir,
    validate_input_file,
)
from .xmind_parser import XMindParser


def convert_single_file(
    input_path: str, output_dir: str, verbose: bool = False
) -> List[Path]:
    """转换单个 XMind 文件"""
    input_file_path = validate_input_file(input_path)
    output_dir_path = ensure_output_dir(output_dir)

    if verbose:
        print(f"解析 XMind 文件: {input_file_path}")

    parser = XMindParser()
    try:
        document = parser.parse_file(input_file_path)
    except ConverterError as e:
        print(f"解析错误: {e}", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"找到 {len(document.modules)} 个模块")

    generator = TextGenerator()
    generated_files = generator.generate(document, output_dir_path)

    if verbose:
        print(f"生成 {len(generated_files)} 个文件:")
        for file in generated_files:
            print(f"  - {file}")

    return generated_files


def convert_directory(
    input_dir: str, output_dir: str, verbose: bool = False
) -> List[Path]:
    """批量转换目录中的所有 XMind 文件"""
    input_dir_path = validate_input_dir(input_dir)
    output_dir_path = ensure_output_dir(output_dir)

    xmind_files = find_xmind_files(input_dir_path)

    if not xmind_files:
        print(f"在 {input_dir_path} 中未找到 .xmind 文件", file=sys.stderr)
        sys.exit(1)

    if verbose:
        print(f"找到 {len(xmind_files)} 个 XMind 文件")

    all_generated_files = []

    for xmind_file in xmind_files:
        if verbose:
            print(f"\n处理: {xmind_file}")

        try:
            parser = XMindParser()
            document = parser.parse_file(xmind_file)

            generator = TextGenerator()
            subdir = output_dir_path / xmind_file.stem
            generated_files = generator.generate(document, subdir)
            all_generated_files.extend(generated_files)

            if verbose:
                print(f"  生成 {len(generated_files)} 个文件")
        except ConverterError as e:
            print(f"错误 {xmind_file}: {e}", file=sys.stderr)
            continue

    if verbose:
        print(f"\n总共生成 {len(all_generated_files)} 个文件")

    return all_generated_files


def main():
    """主函数"""
    parser = argparse.ArgumentParser(description="XMind 转换为自然语言测试文件")
    parser.add_argument(
        "-i", "--input", required=True, help="输入的 XMind 文件路径或目录"
    )
    parser.add_argument("-o", "--output", required=True, help="输出目录路径")
    parser.add_argument("--verbose", action="store_true", help="显示详细输出")
    parser.add_argument("--version", action="version", version="%(prog)s 1.0.0")

    parsed_args = parser.parse_args()

    # 确保必需的参数不为 None（类型安全）
    assert parsed_args.input is not None, "input 参数不能为 None"
    assert parsed_args.output is not None, "output 参数不能为 None"

    input_path = Path(parsed_args.input)

    if input_path.is_file():
        if not input_path.suffix.lower() == ".xmind":
            print(f"错误: {input_path} 不是 .xmind 文件", file=sys.stderr)
            sys.exit(1)

        generated_files = convert_single_file(
            str(input_path), parsed_args.output, parsed_args.verbose
        )
    elif input_path.is_dir():
        generated_files = convert_directory(
            str(input_path), parsed_args.output, parsed_args.verbose
        )
    else:
        print(f"错误: {input_path} 不存在", file=sys.stderr)
        sys.exit(1)

    print(f"\n转换完成！生成了 {len(generated_files)} 个文件")


if __name__ == "__main__":
    main()
