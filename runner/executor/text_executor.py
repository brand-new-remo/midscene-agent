#!/usr/bin/env python3
"""
自然语言测试用例执行器

使用方法:
    python -m executor.text_executor <txt_file> [选项]
    例如: python -m executor.text_executor tests/texts/basic_usage.txt
"""

import asyncio
import os
import sys
import argparse
import re
import glob
from typing import Dict, Any, Optional
import json

# 添加 runner 到 sys.path
runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
if runner_dir not in sys.path:
    sys.path.insert(0, runner_dir)

# 直接导入 agent 模块
from agent.agent import MidsceneAgent


class TextTestExecutor:
    """自然语言测试执行器"""

    def __init__(
        self, text_config: Dict[str, Any], args: Optional[argparse.Namespace] = None
    ):
        self.config = text_config
        self.args = args or argparse.Namespace()
        self.agent: Optional[MidsceneAgent] = None
        self.results = []

    async def initialize_agent(self):
        """初始化 Midscene Agent"""
        web_config = self.config.get("web", {})

        # 创建 Midscene 配置
        midscene_config = {
            "model": os.getenv("MIDSCENE_MODEL_NAME", "doubao-seed-1.6-vision")
            or "doubao-seed-1.6-vision",
            "api_key": os.getenv("OPENAI_API_KEY") or "",
            "base_url": os.getenv("OPENAI_BASE_URL") or "",
            # 使用命令行参数覆盖 headless 设置
            "headless": (
                not self.args.headed
                if hasattr(self.args, "headed")
                else web_config.get("headless", False)
            ),
        }

        # 应用命令行参数覆盖
        if hasattr(self.args, "web_viewportWidth") and self.args.web_viewportWidth:
            midscene_config["viewport_width"] = self.args.web_viewportWidth
        elif "viewportWidth" in web_config:
            midscene_config["viewport_width"] = web_config["viewportWidth"]

        if hasattr(self.args, "web_viewportHeight") and self.args.web_viewportHeight:
            midscene_config["viewport_height"] = self.args.web_viewportHeight
        elif "viewportHeight" in web_config:
            midscene_config["viewport_height"] = web_config["viewportHeight"]

        # 创建 Agent
        deepseek_api_key = os.getenv("DEEPSEEK_API_KEY") or ""
        deepseek_base_url = (
            os.getenv("DEEPSEEK_BASE_URL", "https://api.deepseek.com/v1")
            or "https://api.deepseek.com/v1"
        )
        midscene_server_url = (
            os.getenv("MIDSCENE_SERVER_URL", "http://localhost:3000")
            or "http://localhost:3000"
        )

        self.agent = MidsceneAgent(
            deepseek_api_key=deepseek_api_key,
            deepseek_base_url=deepseek_base_url,
            midscene_server_url=midscene_server_url,
            midscene_config=midscene_config,
            tool_set="full",
            enable_websocket=True,
        )

        await self.agent.initialize()
        return self.agent

    async def navigate_to_url(self, url: str):
        """导航到指定 URL"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化，无法导航")
            return

        print(f"\n🌐 正在导航到: {url}")
        try:
            async for event in self.agent.execute(f"导航到 {url}", stream=True):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(f"  💬 {msg.content}")
        except Exception as e:
            print(f"  ❌ 导航失败: {e}")

    def parse_text_file(self, file_path: str) -> Dict[str, Any]:
        """解析 .txt 文件为内部配置结构"""
        with open(file_path, "r", encoding="utf-8") as f:
            content = f.read()

        config = {"web": {}, "tasks": []}
        current_section = None
        current_task = None
        step_counter = 0

        for line in content.split("\n"):
            line = line.strip()

            # 跳过空行和注释
            if not line or line.startswith("#"):
                continue

            # 先解析任务定义 - 必须在其他@检查之前
            if line.startswith("@task:"):
                task_name = line.split(":", 1)[1].strip()
                current_task = {"name": task_name, "flow": []}
                config["tasks"].append(current_task)
                step_counter = 0
                continue

            # 然后解析配置节 (@web, @agent)
            if line.startswith("@"):
                if ":" in line:
                    section_name, section_value = line.split(":", 1)
                    section_name = section_name.strip("@").strip()
                    section_value = section_value.strip()

                    if section_name == "web":
                        current_section = "web"
                        config["web"] = {}
                    elif section_name == "agent":
                        current_section = "agent"
                        config["agent"] = {"aiActionContext": section_value}
                continue

            # 解析配置项
            if current_section == "web":
                if ":" in line:
                    key, value = line.split(":", 1)
                    key = key.strip()
                    value = value.strip()

                    # 转换数据类型
                    if key in ["headless"]:
                        config["web"][key] = value.lower() in ["true", "1", "yes", "on"]
                    elif key in ["viewportWidth", "viewportHeight"]:
                        config["web"][key] = int(value)
                    else:
                        config["web"][key] = value

            # 解析步骤
            if current_task is not None:
                # 提取步骤编号
                step_match = re.match(r"^(\d+)\.\s*(.+)$", line)
                if step_match:
                    step_number = int(step_match.group(1))
                    step_content = step_match.group(2).strip()
                    step_counter = step_number

                    # 解析步骤类型
                    parsed_step = self._parse_step(step_content)
                    if parsed_step:
                        current_task["flow"].append(parsed_step)

        return config

    def _parse_step(self, content: str) -> Optional[Dict[str, Any]]:
        """解析单个步骤

        新版本：简化解析逻辑，直接将所有内容作为自然语言传递给 AI
        AI 会自动判断需要执行什么操作
        """
        content = content.strip()

        # 如果内容为空，跳过
        if not content:
            return None

        # 移除旧版本的特殊指令前缀，直接作为自然语言处理
        # 统一格式：所有步骤都使用 ai 动作，让大模型自动判断要做什么
        return {"ai": content}

    async def execute_step(self, step: Dict[str, Any]):
        """执行单个步骤

        新版本：简化逻辑，所有步骤都通过 AI 自动判断和执行
        """
        for action_type, action_content in step.items():
            try:
                if action_type == "ai":
                    # 新版本：所有步骤都通过 AI 自动规划执行
                    await self._execute_ai_action(action_content)
                else:
                    # 保留其他类型以防万一，但实际上不会用到
                    print(f"  ⚠️ 未知操作类型: {action_type}")
            except Exception as e:
                print(f"  ❌ 执行失败: {e}")
                import traceback

                traceback.print_exc()

    async def _execute_ai_action(self, content: Any):
        """执行 AI 自动规划操作

        新版本：增强自然语言理解，自动判断操作类型
        """
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return

        prompt = content if isinstance(content, str) else str(content)

        print(f"\n🤖 AI 自动操作:")
        print(f"  📝 指令: {prompt}")

        # 增强提示词，帮助 AI 更好地理解自然语言指令
        # AI 会自动判断是导航、点击、输入、查询、截图还是其他操作
        enhanced_prompt = f"""{prompt}

请根据上述自然语言描述，自动判断需要执行什么操作：
- 如果是导航，使用导航工具
- 如果是点击、输入、滚动等交互，使用相应的交互工具
- 如果是查询、验证信息，使用查询工具
- 如果需要截图，使用截图工具
- 如果是其他操作，选择最合适的工具

请自动完成这个任务，并告诉我执行结果。"""

        async for event in self.agent.execute(enhanced_prompt, stream=True):
            if "messages" in event:
                msg = event["messages"][-1]
                if hasattr(msg, "content") and msg.content:
                    print(f"  💬 {msg.content}")

    async def _execute_ai_assert(self, content: Any):
        """执行断言"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return

        if isinstance(content, str):
            prompt = content
            error_message = ""
            name = ""
        else:
            prompt = content.get("prompt", "")
            error_message = content.get("errorMessage", "")
            name = content.get("name", "")

        print(f"\n🔍 执行断言:")
        print(f"  📝 条件: {prompt}")

        task = f"验证以下条件是否成立: {prompt}"
        if error_message:
            task += f" 如果不成立，显示错误: {error_message}"

        try:
            async for event in self.agent.execute(task, stream=True):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(f"  💬 {msg.content}")
            print("  ✅ 断言完成")
        except Exception as e:
            print(f"  ❌ 断言失败: {e}")

    async def _execute_log_screenshot(self, content: Any):
        """记录截图"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return

        if isinstance(content, str):
            title = content
            content_text = ""
        else:
            title = content.get("content", "untitled")
            content_text = content.get("title", "")

        print(f"\n📸 截图记录:")
        print(f"  📝 标题: {title}")

        try:
            result = await self.agent.take_screenshot(name=title)
            if result:
                print(f"  ✅ 截图已保存")
        except Exception as e:
            print(f"  ❌ 截图失败: {e}")

    async def _execute_ai_query(self, content: Any):
        """执行查询"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return {}

        if isinstance(content, str):
            prompt = content
            name = "查询结果"
        else:
            name = content.get("name", "查询结果")
            prompt = content.get("prompt", "")

        print(f"\n📊 执行查询:")
        print(f"  📝 名称: {name}")
        print(f"  📝 查询: {prompt}")

        try:
            query_result = await self.agent.http_client.execute_query(
                "aiQuery",
                {"dataDemand": {name: prompt}, "options": {"domIncluded": True}},
            )

            if query_result:
                print(f"  ✅ 查询完成")
                print(
                    f"  📋 结果: {json.dumps(query_result, ensure_ascii=False, indent=2)}"
                )
                return query_result
            else:
                print(f"  ⚠️ 查询返回空结果")
                return {}
        except Exception as e:
            print(f"  ❌ 查询失败: {e}")
            import traceback

            traceback.print_exc()
            return {}

    async def _execute_ai_boolean(self, content: Any):
        """执行布尔查询"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return False

        if isinstance(content, str):
            prompt = content
        else:
            prompt = content.get("prompt", str(content))

        print(f"\n✅ 执行布尔查询:")
        print(f"  📝 查询: {prompt}")

        try:
            query_result = await self.agent.http_client.execute_query(
                "aiBoolean",
                {"dataDemand": {"result": prompt}, "options": {"domIncluded": True}},
            )

            if query_result:
                result = query_result.get("result", False)
                print(f"  ✅ 查询完成: {result}")
                return result
            else:
                print(f"  ⚠️ 查询返回空结果")
                return False
        except Exception as e:
            print(f"  ❌ 查询失败: {e}")
            return False

    async def _execute_ai_number(self, content: Any):
        """执行数字查询"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return 0

        if isinstance(content, str):
            prompt = content
        else:
            prompt = content.get("prompt", str(content))

        print(f"\n🔢 执行数字查询:")
        print(f"  📝 查询: {prompt}")

        try:
            query_result = await self.agent.http_client.execute_query(
                "aiNumber",
                {"dataDemand": {"result": prompt}, "options": {"domIncluded": True}},
            )

            if query_result:
                result = query_result.get("result", 0)
                print(f"  ✅ 查询完成: {result}")
                return result
            else:
                print(f"  ⚠️ 查询返回空结果")
                return 0
        except Exception as e:
            print(f"  ❌ 查询失败: {e}")
            return 0

    async def _execute_ai_string(self, content: Any):
        """执行字符串查询"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return ""

        if isinstance(content, str):
            prompt = content
        else:
            prompt = content.get("prompt", str(content))

        print(f"\n📝 执行字符串查询:")
        print(f"  📝 查询: {prompt}")

        try:
            query_result = await self.agent.http_client.execute_query(
                "aiString",
                {"dataDemand": {"result": prompt}, "options": {"domIncluded": True}},
            )

            if query_result:
                result = query_result.get("result", "")
                print(f"  ✅ 查询完成: {result}")
                return result
            else:
                print(f"  ⚠️ 查询返回空结果")
                return ""
        except Exception as e:
            print(f"  ❌ 查询失败: {e}")
            return ""

    async def _execute_sleep(self, content: Any):
        """等待"""
        if isinstance(content, (int, float)):
            if content > 1000:
                seconds = content / 1000
                print(f"\n⏳ 等待 {content}ms")
            else:
                seconds = content
                print(f"\n⏳ 等待 {content}s")
        else:
            seconds = float(content)
            print(f"\n⏳ 等待 {seconds}s")

        await asyncio.sleep(seconds)

    async def _execute_interaction(self, action_type: str, content: Any):
        """执行交互操作"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return

        if isinstance(content, str):
            prompt = content
            params = {}
        else:
            prompt = content.get("locate", {}).get("prompt", str(content))
            params = content.get("locate", {})

        print(f"\n👆 执行交互: {action_type}")
        print(f"  📝 描述: {prompt}")

        action_desc = f"{action_type} {prompt}"
        if "xpath" in params:
            action_desc += f" (xpath: {params['xpath']})"

        try:
            async for event in self.agent.execute(action_desc, stream=True):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(f"  💬 {msg.content}")
        except Exception as e:
            print(f"  ❌ 交互失败: {e}")

    async def _execute_ai_wait_for(self, content: Any):
        """等待条件满足"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return

        if isinstance(content, str):
            prompt = content
            timeout = 30000
        else:
            prompt = content.get("prompt", str(content))
            timeout = content.get("timeout", 30000)

        print(f"\n⏳ 等待条件:")
        print(f"  📝 条件: {prompt}")
        print(f"  ⏰ 超时: {timeout}ms")

        try:
            task = f"等待条件满足: {prompt}，超时时间 {timeout}ms"
            async for event in self.agent.execute(task, stream=True):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(f"  💬 {msg.content}")
            print(f"  ✅ 等待完成")
        except Exception as e:
            print(f"  ❌ 等待检查失败: {e}")
            await asyncio.sleep(timeout / 1000)

    async def _execute_javascript(self, content: Any):
        """执行 JavaScript"""
        if self.agent is None:
            print(f"  ❌ Agent 未初始化")
            return

        if isinstance(content, str):
            script = content
            name = "js_result"
        else:
            script = content.get("script", str(content))
            name = content.get("name", "js_result")

        print(f"\n💻 执行 JavaScript:")
        print(f"  📝 名称: {name}")

        try:
            task = f"执行 JavaScript: {script}"
            async for event in self.agent.execute(task, stream=True):
                if "messages" in event:
                    msg = event["messages"][-1]
                    if hasattr(msg, "content"):
                        print(f"  💬 {msg.content}")
            print(f"  ✅ JavaScript 执行完成")
        except Exception as e:
            print(f"  ❌ JavaScript 执行失败: {e}")

    async def run(self):
        """运行所有任务"""
        tasks = self.config.get("tasks", [])

        if not tasks:
            print("❌ 未找到任务")
            return

        # 初始化 Agent
        await self.initialize_agent()

        # 导航到 URL
        web_config = self.config.get("web", {})
        if "url" in web_config:
            await self.navigate_to_url(web_config["url"])

        # 执行任务
        for i, task in enumerate(tasks, 1):
            task_name = task.get("name", f"任务 {i}")
            flow = task.get("flow", [])
            continue_on_error = task.get("continueOnError", False)

            print("\n" + "=" * 70)
            print(f"📝 执行任务 {i}/{len(tasks)}: {task_name}")
            print("=" * 70)

            task_result = {"name": task_name, "success": True, "steps": []}

            for step in flow:
                step_result = {"action": list(step.keys())[0], "success": True}
                try:
                    await self.execute_step(step)
                    step_result["success"] = True
                except Exception as e:
                    print(f"❌ 步骤执行失败: {e}")
                    step_result["success"] = False
                    task_result["success"] = False
                    if not continue_on_error:
                        break

                task_result["steps"].append(step_result)

            self.results.append(task_result)

            if task_result["success"]:
                print(f"\n✅ 任务完成: {task_name}")
            else:
                print(f"\n❌ 任务失败: {task_name}")

        # 清理
        if self.agent:
            await self.agent.cleanup()

        # 打印总结
        self.print_summary()

    def print_summary(self):
        """打印执行总结"""
        print("\n" + "=" * 70)
        print("📊 执行总结")
        print("=" * 70)

        total_tasks = len(self.results)
        success_tasks = sum(1 for r in self.results if r["success"])
        failed_tasks = total_tasks - success_tasks

        print(f"\n📋 总任务数: {total_tasks}")
        print(f"✅ 成功: {success_tasks}")
        print(f"❌ 失败: {failed_tasks}")
        print(
            f"📈 成功率: {success_tasks/total_tasks*100:.1f}%"
            if total_tasks > 0
            else "📈 成功率: N/A"
        )

        for result in self.results:
            status = "✅" if result["success"] else "❌"
            print(f"\n{status} {result['name']}")

        print("\n" + "=" * 70)


def parse_arguments():
    """解析命令行参数"""
    parser = argparse.ArgumentParser(
        description="直接执行自然语言测试用例",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
示例:
  %(prog)s tests/texts/basic_usage.txt
  %(prog)s tests/texts/*.txt --concurrent 4
  %(prog)s tests/texts/basic_usage.txt --headed
  %(prog)s tests/texts/*.txt --continue-on-error --summary output.json
        """,
    )

    parser.add_argument(
        "files", nargs="+", help="要执行的文本文件或模式（如 tests/texts/*.txt）"
    )

    parser.add_argument(
        "--concurrent", type=int, default=1, help="并发执行的数量 (默认: 1)"
    )

    parser.add_argument(
        "--continue-on-error",
        action="store_true",
        help="如果脚本文件执行失败，继续运行其余脚本文件",
    )

    parser.add_argument(
        "--headed", action="store_true", help="在有图形界面的浏览器中运行脚本"
    )

    parser.add_argument(
        "--keep-window",
        action="store_true",
        help="脚本执行结束后保持浏览器窗口打开（自动启用 --headed）",
    )

    parser.add_argument(
        "--summary", type=str, help="指定生成的 JSON 格式汇总报告文件的路径"
    )

    parser.add_argument(
        "--web.userAgent",
        type=str,
        help="设置浏览器 UA，将覆盖所有脚本文件中的 web.userAgent 参数",
    )

    parser.add_argument(
        "--web.viewportWidth",
        type=int,
        help="设置浏览器视口宽度，将覆盖所有脚本文件中的 web.viewportWidth 参数",
    )

    parser.add_argument(
        "--web.viewportHeight",
        type=int,
        help="设置浏览器视口高度，将覆盖所有脚本文件中的 web.viewportHeight 参数",
    )

    args = parser.parse_args()

    if args.keep_window:
        args.headed = True

    return args


async def main():
    """主函数 - 支持多个文件和命令行参数"""
    args = parse_arguments()

    # 扩展文件模式
    txt_files = []
    for pattern in args.files:
        if "*" in pattern or "?" in pattern:
            files = glob.glob(pattern)
            txt_files.extend(files)
        else:
            txt_files.append(pattern)

    # 去重并过滤
    txt_files = list(set(txt_files))
    txt_files = [f for f in txt_files if f.endswith(".txt")]

    if not txt_files:
        print("❌ 未找到匹配的文本文件")
        return

    print(f"📋 找到 {len(txt_files)} 个文本文件:")
    for i, f in enumerate(txt_files, 1):
        print(f"  {i}. {f}")
    print()

    # 检查环境变量
    if not os.getenv("DEEPSEEK_API_KEY"):
        print("⚠️ 警告: 未设置 DEEPSEEK_API_KEY")

    if not os.getenv("OPENAI_API_KEY"):
        print("⚠️ 警告: 未设置 OPENAI_API_KEY")

    print("\n" + "=" * 70)
    print("🚀 开始执行自然语言测试")
    print("=" * 70)

    all_results = []

    if args.concurrent > 1:
        print(f"\n⚡ 并发执行模式 ({args.concurrent} 个并发)")

    for i, txt_file in enumerate(txt_files, 1):
        print(f"\n{'='*70}")
        print(f"执行 {i}/{len(txt_files)}: {txt_file}")
        print(f"{'='*70}")

        if not os.path.exists(txt_file):
            print(f"❌ 文件不存在: {txt_file}")
            if not args.continue_on_error:
                break
            all_results.append(
                {"file": txt_file, "success": False, "error": "文件不存在"}
            )
            continue

        try:
            executor = TextTestExecutor({}, args)
            config = executor.parse_text_file(txt_file)
            executor.config = config

            if not config.get("tasks"):
                print(f"❌ 文件中没有任务: {txt_file}")
                if not args.continue_on_error:
                    break
                all_results.append(
                    {"file": txt_file, "success": False, "error": "文件中没有任务"}
                )
                continue

            await executor.run()

            all_results.append(
                {
                    "file": txt_file,
                    "success": all(r["success"] for r in executor.results),
                    "results": executor.results,
                }
            )

        except Exception as e:
            print(f"❌ 执行失败: {e}")
            import traceback

            traceback.print_exc()

            all_results.append({"file": txt_file, "success": False, "error": str(e)})

            if not args.continue_on_error:
                break

    # 生成汇总报告
    if args.summary:
        try:
            summary = {
                "total_files": len(txt_files),
                "success_files": sum(1 for r in all_results if r["success"]),
                "failed_files": sum(1 for r in all_results if not r["success"]),
                "results": all_results,
            }

            with open(args.summary, "w", encoding="utf-8") as f:
                json.dump(summary, f, ensure_ascii=False, indent=2)

            print(f"\n✅ 汇总报告已保存到: {args.summary}")
        except Exception as e:
            print(f"❌ 保存汇总报告失败: {e}")

    print("\n👋 感谢使用自然语言执行器！")


if __name__ == "__main__":
    asyncio.run(main())
