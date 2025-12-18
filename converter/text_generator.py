"""
自然语言测试文件生成器
"""

from pathlib import Path
from typing import List

from .models import Module, ParsedDocument, Step, TestCase
from .utils import sanitize_filename


class TextGenerator:
    """自然语言测试文件生成器"""

    def __init__(self):
        pass

    def generate(self, document: ParsedDocument, output_dir: Path) -> List[Path]:
        """生成测试文件"""
        output_dir = Path(output_dir)
        output_dir.mkdir(parents=True, exist_ok=True)

        generated_files = []

        for module in document.modules:
            output_file = output_dir / f"{sanitize_filename(module.name)}.txt"
            content = self._generate_module_file(module)
            output_file.write_text(content, encoding="utf-8")
            generated_files.append(output_file)

        return generated_files

    def _generate_module_file(self, module: Module) -> str:
        """生成单个模块文件"""
        lines = []

        lines.append(f"# {module.name}")
        lines.append("")
        lines.append("@web:")
        lines.append("  url: https://example.com  # TODO: 请填写实际 URL")
        lines.append("  headless: false")
        lines.append("  viewportWidth: 1280")
        lines.append("  viewportHeight: 768")
        lines.append("")

        for i, testcase in enumerate(module.testcases):
            lines.append(f"@task: {testcase.name}")
            lines.append("")

            all_steps = self._merge_steps(testcase.steps)

            for step in all_steps:
                lines.append(f"{step.number}. {step.content}")

            lines.append("")
            lines.append("")

        return "\n".join(lines)

    def _merge_steps(self, steps: List[Step]) -> List[Step]:
        """合并并重新编号步骤"""
        all_steps = []
        current_number = 1

        for step in steps:
            step.number = current_number
            all_steps.append(step)
            current_number += 1

        return all_steps
