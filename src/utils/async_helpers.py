"""
Async helper utilities
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
    Create and await a task with timeout.

    Args:
        coro: Coroutine function to execute
        timeout: Timeout in seconds (optional)
        *args: Positional arguments for the coroutine
        **kwargs: Keyword arguments for the coroutine

    Returns:
        Result from the coroutine

    Raises:
        asyncio.TimeoutError: If timeout is exceeded
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
    Run a synchronous function in an executor with timeout.

    Args:
        func: Synchronous function to execute
        timeout: Timeout in seconds (optional)
        *args: Positional arguments for the function
        **kwargs: Keyword arguments for the function

    Returns:
        Result from the function

    Raises:
        asyncio.TimeoutError: If timeout is exceeded
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
