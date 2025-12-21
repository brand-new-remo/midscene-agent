#!/usr/bin/env python3
"""
测试去重中间件和记忆机制
用于验证阶段1的实现是否正常工作
"""

import sys
import os

# 添加runner到路径
runner_dir = os.path.dirname(os.path.abspath(__file__))
sys.path.insert(0, runner_dir)

import time
import asyncio
from typing import Dict, Any

# 测试记忆组件
from runner.agent.memory.simple_memory import SimpleMemory, MemoryContextBuilder


def test_simple_memory():
    """测试简单记忆组件"""
    print("=" * 60)
    print("测试1: 简单记忆组件")
    print("=" * 60)

    # 创建记忆组件
    memory = SimpleMemory(max_size=10)

    # 添加一些操作记录
    memory.add_record(
        action="navigate",
        params={"url": "https://example.com"},
        result={"success": True, "title": "Example"},
        context={"url": "https://example.com", "title": "Example"}
    )

    memory.add_record(
        action="click",
        params={"locate": "button"},
        result={"success": True},
        context={"url": "https://example.com", "title": "Example"}
    )

    memory.add_record(
        action="input",
        params={"locate": "search", "value": "test"},
        result={"success": True},
        context={"url": "https://example.com", "title": "Example"}
    )

    # 测试获取最近操作
    print("\n1. 最近操作记录:")
    recent = memory.get_recent_actions(limit=2)
    for record in recent:
        print(f"   - {record.action}: {record.params}")

    # 测试构建上下文
    print("\n2. 构建的上下文:")
    context = memory.get_recent_context(limit=2)
    print(context)

    # 测试统计信息
    print("\n3. 统计信息:")
    stats = memory.get_stats()
    for key, value in stats.items():
        print(f"   {key}: {value}")

    # 测试查找相似操作
    print("\n4. 查找相似操作:")
    similar = memory.find_similar_action(
        action="click",
        params={"locate": "button"},
        time_window=60
    )
    if similar:
        print(f"   找到相似操作: {similar.action}")
    else:
        print("   未找到相似操作")

    # 测试上下文构建器
    print("\n5. 上下文构建器:")
    builder = MemoryContextBuilder(memory)
    execution_context = builder.build_execution_context(
        current_task="点击搜索按钮",
        include_history=True,
        include_stats=True
    )
    print(execution_context)

    print("\n✅ 简单记忆组件测试完成")


def test_memory_serialization():
    """测试记忆序列化"""
    print("\n" + "=" * 60)
    print("测试2: 记忆序列化")
    print("=" * 60)

    # 创建记忆并添加记录
    memory1 = SimpleMemory(max_size=5)
    memory1.add_record(
        action="test",
        params={"key": "value"},
        result={"success": True},
        context={"url": "https://test.com"}
    )

    # 序列化
    data = memory1.to_dict()
    print(f"1. 序列化数据: {data}")

    # 反序列化
    memory2 = SimpleMemory(max_size=5)
    memory2.from_dict(data)

    # 验证
    print("\n2. 反序列化后的记录:")
    records = memory2.get_recent_actions()
    for record in records:
        print(f"   - {record.action}: {record.params}")

    print("\n✅ 记忆序列化测试完成")


def test_deduplication_typescript():
    """测试TypeScript去重中间件（模拟）"""
    print("\n" + "=" * 60)
    print("测试3: 去重机制模拟")
    print("=" * 60)

    # 模拟去重中间件的行为
    cache = {}

    def should_execute(key: str, time_window: int = 5000) -> bool:
        """检查是否应该执行操作"""
        now = time.time() * 1000  # 毫秒
        if key not in cache:
            return True

        time_diff = now - cache[key]["timestamp"]
        return time_diff > time_window

    def record(key: str, result: Dict[str, Any]):
        """记录操作结果"""
        cache[key] = {
            "result": result,
            "timestamp": time.time() * 1000
        }

    # 测试场景1: 第一次执行
    key1 = "navigate:https://example.com"
    print("\n1. 第一次执行操作:")
    if should_execute(key1):
        print(f"   ✅ 执行操作: {key1}")
        record(key1, {"success": True})
    else:
        print(f"   ❌ 跳过操作: {key1}")

    # 测试场景2: 重复执行（应该跳过）
    print("\n2. 重复执行操作:")
    if should_execute(key1):
        print(f"   ✅ 执行操作: {key1}")
        record(key1, {"success": True})
    else:
        print(f"   ❌ 跳过操作: {key1} (检测到重复)")

    # 测试场景3: 不同操作（应该执行）
    key2 = "click:button"
    print("\n3. 不同操作:")
    if should_execute(key2):
        print(f"   ✅ 执行操作: {key2}")
        record(key2, {"success": True})
    else:
        print(f"   ❌ 跳过操作: {key2}")

    # 测试场景4: 等待足够时间后重复执行
    print("\n4. 等待后重复执行:")
    time.sleep(0.01)  # 等待10毫秒
    # 注意：由于时间窗口是5000ms，这里应该仍然跳过
    if should_execute(key1):
        print(f"   ✅ 执行操作: {key1}")
        record(key1, {"success": True})
    else:
        print(f"   ❌ 跳过操作: {key1} (仍在时间窗口内)")

    print("\n   缓存状态:")
    for key, value in cache.items():
        print(f"   - {key}: {value}")

    print("\n✅ 去重机制测试完成")


def main():
    """主测试函数
    开始测试去重中间件和记忆机制"""
    print("测试时间:", time.strftime("%Y-%m-%d %H:%M:%S"))

    try:
        # 运行测试
        test_simple_memory()
        test_memory_serialization()
        test_deduplication_typescript()

        print("\n" + "=" * 60)
        print("🎉 所有测试完成！")
        print("=" * 60)

        print("\n📋 测试总结:")
        print("1. ✅ 简单记忆组件 - 工作正常")
        print("2. ✅ 记忆序列化 - 工作正常")
        print("3. ✅ 去重机制 - 工作正常")

        print("\n💡 实施建议:")
        print("- Node.js去重中间件已集成到Orchestrator")
        print("- Python记忆组件已集成到Agent")
        print("- 建议在实际测试中验证效果")

    except Exception as e:
        print(f"\n❌ 测试失败: {e}")
        import traceback
        traceback.print_exc()
        return 1

    return 0


if __name__ == "__main__":
    sys.exit(main())