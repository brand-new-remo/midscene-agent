"""
HTTP 客户端用于与 Node.js Midscene 服务通信

提供与 Node.js Midscene 服务的异步通信接口，
支持 HTTP REST API 和 WebSocket 流式响应。
"""

import asyncio
import aiohttp
import json
import logging
from typing import Dict, Any, Optional, AsyncGenerator, List
from dataclasses import dataclass, asdict
from contextlib import asynccontextmanager

# 配置日志
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)


@dataclass
class SessionConfig:
    """
    会话配置 - 浏览器参数

    注意：视觉模型相关配置（model, api_key, base_url 等）
    应在 Node.js server 端通过环境变量配置，
    以实现架构分离。
    """
    headless: bool = True
    viewport_width: int = 1920
    viewport_height: int = 1080


@dataclass
class ActionResult:
    """动作执行结果"""
    success: bool
    result: Optional[Dict[str, Any]] = None
    error: Optional[str] = None
    timestamp: Optional[int] = None


class MidsceneHTTPClient:
    """
    HTTP 客户端包装器

    提供与 Node.js Midscene 服务的异步通信接口
    """

    def __init__(self, base_url: str = "http://localhost:3000"):
        """
        初始化 HTTP 客户端

        Args:
            base_url: Node.js 服务器地址
        """
        self.base_url = base_url.rstrip('/')
        self.session: Optional[aiohttp.ClientSession] = None
        self.session_id: Optional[str] = None
        self.websocket: Optional[aiohttp.ClientWebSocketResponse] = None
        self.connector: Optional[aiohttp.TCPConnector] = None

    @asynccontextmanager
    async def connection(self):
        """异步上下文管理器"""
        await self.connect()
        try:
            yield self
        finally:
            await self.disconnect()

    async def connect(self) -> None:
        """建立 HTTP 连接"""
        if self.session:
            return

        # 配置连接池
        self.connector = aiohttp.TCPConnector(
            limit=100,  # 连接池大小
            limit_per_host=30,  # 每个主机连接数
            ttl_dns_cache=300,  # DNS 缓存时间
            use_dns_cache=True,
        )

        self.session = aiohttp.ClientSession(
            connector=self.connector,
            timeout=aiohttp.ClientTimeout(total=300)
        )

        logger.info(f"HTTP 客户端已连接到 {self.base_url}")

    async def disconnect(self) -> None:
        """断开 HTTP 连接"""
        await self.cleanup()

    async def create_session(self, config: Optional[SessionConfig] = None) -> str:
        """
        创建新的 Midscene 会话

        Args:
            config: 会话配置

        Returns:
            会话 ID

        Raises:
            RuntimeError: 如果创建会话失败
        """
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        config = config or SessionConfig()

        try:
            async with self.session.post(
                f"{self.base_url}/api/sessions",
                json=asdict(config)
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    session_id = data["sessionId"]
                    self.session_id = session_id
                    logger.info(f"✅ 创建会话成功: {session_id}")
                    return session_id
                else:
                    error_text = await response.text()
                    error_msg = f"创建会话失败 ({response.status}): {error_text}"
                    logger.error(error_msg)
                    raise RuntimeError(error_msg)
        except Exception as e:
            error_msg = f"创建会话时出错: {str(e)}"
            logger.error(error_msg)
            raise RuntimeError(error_msg)

    async def execute_action(
        self,
        action: str,
        params: Optional[Dict[str, Any]] = None,
        stream: bool = False
    ) -> AsyncGenerator[Dict[str, Any], None]:
        """
        执行网页动作

        Args:
            action: 动作名称
            params: 动作参数
            stream: 是否使用流式响应

        Yields:
            执行结果或进度事件
        """
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        if not self.session_id:
            raise RuntimeError("未创建会话")

        try:
            if stream and self.websocket:
                # WebSocket 流式传输
                await self._send_websocket_action(action, params)
                async for event in self._listen_websocket():
                    yield event
            else:
                # HTTP 请求
                async with self.session.post(
                    f"{self.base_url}/api/sessions/{self.session_id}/action",
                    json={
                        "action": action,
                        "params": params or {}
                    }
                ) as response:
                    if response.status == 200:
                        result = await response.json()
                        yield result
                    else:
                        error_text = await response.text()
                        yield {
                            "success": False,
                            "error": f"HTTP {response.status}: {error_text}",
                            "timestamp": int(asyncio.get_event_loop().time() * 1000)
                        }

        except Exception as e:
            error_msg = str(e)
            logger.error(f"执行动作失败: {error_msg}")
            yield {
                "success": False,
                "error": error_msg,
                "timestamp": int(asyncio.get_event_loop().time() * 1000)
            }

    async def _send_websocket_action(self, action: str, params: Optional[Dict[str, Any]]) -> None:
        """通过 WebSocket 发送动作"""
        if not self.websocket:
            raise RuntimeError("WebSocket 未连接")

        # 类型断言：告诉 Pylance 这里 websocket 不是 None
        assert self.websocket is not None
        await self.websocket.send_json({
            "type": "action",
            "sessionId": self.session_id,
            "action": action,
            "params": params or {}
        })

    async def _listen_websocket(self) -> AsyncGenerator[Dict[str, Any], None]:
        """监听 WebSocket 消息"""
        if not self.websocket:
            return

        # 类型断言：告诉 Pylance 这里 websocket 不是 None
        assert self.websocket is not None
        try:
            async for msg in self.websocket:
                if msg.type == aiohttp.WSMsgType.TEXT:
                    data = json.loads(msg.data)
                    yield data
                elif msg.type == aiohttp.WSMsgType.ERROR:
                    # 类型断言：告诉 Pylance 这里 websocket 不是 None
                    assert self.websocket is not None
                    logger.error(f"WebSocket error: {self.websocket.exception()}")
                    break
        except Exception as e:
            logger.error(f"WebSocket listen error: {e}")
        finally:
            logger.info("WebSocket listener closed")

    async def execute_query(
        self,
        query: str,
        params: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        查询页面信息

        Args:
            query: 查询类型
            params: 查询参数

        Returns:
            查询结果
        """
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        if not self.session_id:
            raise RuntimeError("未创建会话")

        try:
            async with self.session.post(
                f"{self.base_url}/api/sessions/{self.session_id}/query",
                json={
                    "query": query,
                    "params": params or {}
                }
            ) as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info(f"✅ 查询成功: {query}")
                    return result
                else:
                    error_text = await response.text()
                    error_msg = f"查询失败 ({response.status}): {error_text}"
                    logger.error(error_msg)
                    return {
                        "success": False,
                        "error": error_msg,
                        "timestamp": int(asyncio.get_event_loop().time() * 1000)
                    }
        except Exception as e:
            error_msg = f"查询时出错: {str(e)}"
            logger.error(error_msg)
            return {
                "success": False,
                "error": error_msg,
                "timestamp": int(asyncio.get_event_loop().time() * 1000)
            }

    async def get_sessions(self) -> List[Dict[str, Any]]:
        """获取活跃会话列表"""
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        try:
            async with self.session.get(f"{self.base_url}/api/sessions") as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("sessions", [])
                else:
                    logger.error(f"获取会话列表失败: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"获取会话列表时出错: {e}")
            return []

    async def get_session_history(self) -> List[Dict[str, Any]]:
        """获取会话历史"""
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        if not self.session_id:
            raise RuntimeError("未创建会话")

        try:
            async with self.session.get(
                f"{self.base_url}/api/sessions/{self.session_id}/history"
            ) as response:
                if response.status == 200:
                    data = await response.json()
                    return data.get("history", [])
                else:
                    logger.error(f"获取会话历史失败: {response.status}")
                    return []
        except Exception as e:
            logger.error(f"获取会话历史时出错: {e}")
            return []

    async def connect_websocket(self) -> bool:
        """连接 WebSocket 以支持流式响应"""
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        if not self.session_id:
            raise RuntimeError("未创建会话")

        try:
            ws_url = self.base_url.replace("http", "ws") + "/ws"
            self.websocket = await self.session.ws_connect(ws_url)

            # 类型断言：告诉 Pylance 这里 websocket 不是 None
            assert self.websocket is not None
            # 订阅会话
            await self.websocket.send_json({
                "type": "subscribe",
                "sessionId": self.session_id
            })

            logger.info("✅ WebSocket 连接成功")
            return True

        except Exception as e:
            logger.warning(f"⚠️ WebSocket 连接失败: {e}")
            # 确保在失败时重置 websocket 状态
            self.websocket = None
            return False

    async def disconnect_websocket(self) -> None:
        """断开 WebSocket 连接"""
        if self.websocket:
            try:
                # 类型断言：告诉 Pylance 这里 websocket 不是 None
                assert self.websocket is not None
                await self.websocket.send_json({
                    "type": "unsubscribe",
                    "sessionId": self.session_id
                })
                await self.websocket.close()
                self.websocket = None
                logger.info("🔌 WebSocket 连接已断开")
            except Exception as e:
                logger.error(f"断开 WebSocket 连接时出错: {e}")

    async def health_check(self) -> Dict[str, Any]:
        """健康检查"""
        if not self.session:
            await self.connect()

        assert self.session is not None, "HTTP session should be initialized"

        try:
            async with self.session.get(f"{self.base_url}/api/health") as response:
                if response.status == 200:
                    result = await response.json()
                    logger.info("✅ 健康检查通过")
                    return result
                else:
                    error_msg = f"健康检查失败: {response.status}"
                    logger.error(error_msg)
                    return {
                        "status": "unhealthy",
                        "error": error_msg,
                        "timestamp": int(asyncio.get_event_loop().time() * 1000)
                    }
        except Exception as e:
            error_msg = f"健康检查时出错: {str(e)}"
            logger.error(error_msg)
            return {
                "status": "error",
                "error": error_msg,
                "timestamp": int(asyncio.get_event_loop().time() * 1000)
            }

    async def cleanup(self) -> None:
        """清理资源"""
        try:
            # 断开 WebSocket 连接
            if self.websocket:
                await self.disconnect_websocket()

            # 销毁会话
            if self.session_id and self.session:
                try:
                    await self.session.delete(
                        f"{self.base_url}/api/sessions/{self.session_id}"
                    )
                    logger.info(f"🗑️ 会话 {self.session_id} 已销毁")
                except Exception as e:
                    logger.warning(f"销毁会话时出错: {e}")

            # 关闭 HTTP 会话
            if self.session:
                await self.session.close()
                self.session = None

            # 关闭连接器
            if self.connector:
                await self.connector.close()
                self.connector = None

            self.session_id = None

            logger.info("🔌 HTTP 客户端已清理")

        except Exception as e:
            logger.error(f"清理资源时出错: {e}")

    async def __aenter__(self):
        """异步上下文管理器入口"""
        await self.connect()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        """异步上下文管理器出口"""
        await self.cleanup()


class MidsceneConnectionError(Exception):
    """当连接到 Midscene 服务器失败时抛出"""
    pass


class MidsceneActionError(Exception):
    """当执行动作失败时抛出"""
    pass