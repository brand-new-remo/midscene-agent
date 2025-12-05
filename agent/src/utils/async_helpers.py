"""
异步辅助工具
"""

import asyncio
from typing import Callable, Any, Optional


async def create_task_with_timeout(
    coro: Callable,
    timeout: Optional[float] = None,
    *args,
    **kwargs
) -> Any:
    """
    创建并等待带超时的任务。

    Args:
        coro: 要执行的协程函数
        timeout: 超时时间（秒）（可选）
        *args: 协程的位置参数
        **kwargs: 协程的关键字参数

    Returns:
        协程的结果

    Raises:
        asyncio.TimeoutError: 如果超过超时时间
    """
    task = asyncio.create_task(coro(*args, **kwargs))

    try:
        if timeout:
            return await asyncio.wait_for(task, timeout=timeout)
        else:
            return await task
    except asyncio.TimeoutError:
        task.cancel()
        raise


async def run_with_timeout(
    func: Callable,
    timeout: Optional[float] = None,
    *args,
    **kwargs
) -> Any:
    """
    在执行器中运行同步函数并设置超时。

    Args:
        func: 要执行的同步函数
        timeout: 超时时间（秒）（可选）
        *args: 函数的位置参数
        **kwargs: 函数的关键字参数

    Returns:
        函数的结果

    Raises:
        asyncio.TimeoutError: 如果超过超时时间
    """
    loop = asyncio.get_event_loop()

    try:
        if timeout:
            return await asyncio.wait_for(
                loop.run_in_executor(None, func, *args, **kwargs),
                timeout=timeout
            )
        else:
            return await loop.run_in_executor(None, func, *args, **kwargs)
    except asyncio.TimeoutError:
        raise
