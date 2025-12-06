/**
 * Midscene Node.js 服务器
 *
 * 提供 HTTP API 和 WebSocket 接口，
 * 集成 Midscene.js + Playwright 实现网页自动化
 */
import 'dotenv/config';
import http from 'http';

import cors from 'cors';
import express, { type NextFunction, type Request, type Response } from 'express';
import { WebSocket, WebSocketServer } from 'ws';

import MidsceneOrchestrator from './orchestrator.js';

import type { ActionParams, ActionType, QueryParams, QueryType, WsMessage } from './types/index.js';

const app = express();
const server = http.createServer(app);
const wss = new WebSocketServer({
  server,
});

// 中间件
app.use(cors());
app.use(
  express.json({
    limit: '10mb',
  })
);

// 初始化 orchestrator
const orchestrator = new MidsceneOrchestrator();

// WebSocket 连接管理
const wsConnections = new Map<string, WebSocket>();

/**
 * 处理 WebSocket 订阅
 */
function handleWebSocketSubscribe(ws: WebSocket, sessionId: string): void {
  wsConnections.set(sessionId, ws);
  console.log(`📡 Client subscribed to session: ${sessionId}`);

  ws.send(
    JSON.stringify({
      type: 'subscribed',
      sessionId,
      timestamp: Date.now(),
    })
  );
}

/**
 * 处理 WebSocket 动作执行
 */
async function handleWebSocketAction(
  ws: WebSocket,
  currentSessionId: string,
  action: ActionType,
  params: ActionParams
): Promise<void> {
  try {
    await orchestrator.executeAction(currentSessionId, action, params, {
      stream: true,
      websocket: ws,
    });
  } catch (error) {
    const err = error as Error;
    ws.send(
      JSON.stringify({
        type: 'action_error',
        sessionId: currentSessionId,
        action,
        error: err.message,
        timestamp: Date.now(),
      })
    );
  }
}

/**
 * 处理 WebSocket 取消订阅
 */
function handleWebSocketUnsubscribe(currentSessionId: string | null): void {
  if (currentSessionId) {
    wsConnections.delete(currentSessionId);
    console.log(`📡 Client unsubscribed from session: ${currentSessionId}`);
  }
}

/**
 * 发送 WebSocket 错误消息
 */
function sendWebSocketError(ws: WebSocket, message: string, type = 'error'): void {
  ws.send(
    JSON.stringify({
      type,
      message,
      timestamp: Date.now(),
    })
  );
}

/**
 * 处理 WebSocket 消息
 */
async function handleWebSocketMessage(
  ws: WebSocket,
  data: WsMessage,
  currentSessionId: string | null,
  setSessionId: (id: string | null) => void
): Promise<void> {
  const { type, sessionId, action, params } = data;

  switch (type) {
    case 'subscribe': {
      const newSessionId = sessionId;
      if (!newSessionId) {
        sendWebSocketError(ws, 'Session ID is required for subscribe');
        return;
      }
      setSessionId(newSessionId);
      handleWebSocketSubscribe(ws, newSessionId);
      break;
    }
    case 'action': {
      if (!currentSessionId) {
        sendWebSocketError(ws, 'No active session');
        return;
      }
      await handleWebSocketAction(
        ws,
        currentSessionId,
        action as ActionType,
        params as ActionParams
      );
      break;
    }
    case 'unsubscribe': {
      handleWebSocketUnsubscribe(currentSessionId);
      setSessionId(null);
      break;
    }
    default: {
      sendWebSocketError(ws, `Unknown message type: ${type}`);
    }
  }
}

/**
 * WebSocket 消息处理
 */
wss.on('connection', (ws: WebSocket) => {
  let currentSessionId: string | null = null;

  console.log('🔌 WebSocket client connected');

  ws.on('message', async (message: Buffer) => {
    try {
      const data = JSON.parse(message.toString()) as WsMessage;
      await handleWebSocketMessage(ws, data, currentSessionId, (id) => {
        currentSessionId = id;
      });
    } catch (error) {
      const err = error as Error;
      console.error('WebSocket message error:', err);
      sendWebSocketError(ws, err.message);
    }
  });

  ws.on('close', () => {
    if (currentSessionId) {
      wsConnections.delete(currentSessionId);
      console.log(`📡 WebSocket client disconnected from session: ${currentSessionId}`);
    }
  });

  ws.on('error', (error: Error) => {
    console.error('WebSocket error:', error);
  });
});

/**
 * HTTP 路由
 */

// 健康检查
app.get('/api/health', async (req: Request, res: Response) => {
  try {
    const health = await orchestrator.healthCheck();
    res.json({
      timestamp: Date.now(),
      ...health,
    });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({
      status: 'error',
      message: err.message,
      timestamp: Date.now(),
    });
  }
});

// 创建会话
app.post('/api/sessions', async (req: Request, res: Response) => {
  try {
    const sessionId = await orchestrator.createSession(req.body);
    res.json({
      success: true,
      sessionId,
      timestamp: Date.now(),
    });
    console.log(`✅ Session created: ${sessionId}`);
  } catch (error) {
    const err = error as Error;
    console.error('Failed to create session:', err);
    res.status(500).json({
      success: false,
      error: err.message,
      timestamp: Date.now(),
    });
  }
});

// 执行动作
app.post('/api/sessions/:sessionId/action', async (req: Request, res: Response) => {
  const { sessionId } = req.params;
  const { action, params } = req.body as { action: ActionType; params: ActionParams };

  try {
    const result = await orchestrator.executeAction(sessionId, action, params);
    res.json({
      success: true,
      result,
      timestamp: Date.now(),
    });
  } catch (error) {
    const err = error as Error;
    console.error(`Failed to execute action ${action} for session ${sessionId}:`, err);
    res.status(500).json({
      success: false,
      error: err.message,
      timestamp: Date.now(),
    });
  }
});

// 查询页面信息
app.post('/api/sessions/:sessionId/query', async (req: Request, res: Response) => {
  const { sessionId } = req.params;
  const { query, params } = req.body as { query: QueryType; params: QueryParams };

  try {
    const result = await orchestrator.executeQuery(sessionId, query, params);
    res.json({
      success: true,
      result,
      timestamp: Date.now(),
    });
  } catch (error) {
    const err = error as Error;
    console.error(`Failed to execute query ${query} for session ${sessionId}:`, err);
    res.status(500).json({
      success: false,
      error: err.message,
      timestamp: Date.now(),
    });
  }
});

// 获取活跃会话列表
app.get('/api/sessions', (req: Request, res: Response) => {
  try {
    const sessions = orchestrator.getActiveSessions();
    res.json({
      success: true,
      sessions,
      timestamp: Date.now(),
    });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({
      success: false,
      error: err.message,
      timestamp: Date.now(),
    });
  }
});

// 获取会话历史
app.get('/api/sessions/:sessionId/history', (req: Request, res: Response) => {
  const { sessionId } = req.params;

  try {
    const history = orchestrator.getSessionHistory(sessionId);
    res.json({
      success: true,
      history,
      timestamp: Date.now(),
    });
  } catch (error) {
    const err = error as Error;
    res.status(500).json({
      success: false,
      error: err.message,
      timestamp: Date.now(),
    });
  }
});

// 销毁会话
app.delete('/api/sessions/:sessionId', async (req: Request, res: Response) => {
  const { sessionId } = req.params;

  try {
    await orchestrator.destroySession(sessionId);
    res.json({
      success: true,
      message: `Session ${sessionId} destroyed`,
      timestamp: Date.now(),
    });
    console.log(`🗑️ Session destroyed: ${sessionId}`);
  } catch (error) {
    const err = error as Error;
    console.error(`Failed to destroy session ${sessionId}:`, err);
    res.status(500).json({
      success: false,
      error: err.message,
      timestamp: Date.now(),
    });
  }
});

// 根路径
app.get('/', (req: Request, res: Response) => {
  res.json({
    name: 'Midscene Server',
    version: '2.0.0',
    description: 'Node.js server for Midscene.js + Playwright integration',
    endpoints: [
      'GET /api/health - Health check',
      'POST /api/sessions - Create session',
      'GET /api/sessions - List sessions',
      'POST /api/sessions/:sessionId/action - Execute action',
      'POST /api/sessions/:sessionId/query - Query page',
      'GET /api/sessions/:sessionId/history - Get session history',
      'DELETE /api/sessions/:sessionId - Destroy session',
      'WebSocket /ws - WebSocket connection',
    ],
    timestamp: Date.now(),
  });
});

// 全局错误处理
app.use((err: Error, _req: Request, res: Response, _next: NextFunction) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: err.message,
    timestamp: Date.now(),
  });
});

// 启动服务器
const PORT = process.env.PORT || 3000;

async function startServer(): Promise<void> {
  try {
    server.listen(PORT, () => {
      console.log(`\n${'='.repeat(70)}`);
      console.log('🚀 Midscene Node.js Server v2.0.0');
      console.log('='.repeat(70));
      console.log(`✅ HTTP Server running on port ${PORT}`);
      console.log(`✅ WebSocket server ready`);
      console.log(`✅ Orchestrator initialized`);
      console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
      console.log(`${'='.repeat(70)}\n`);
    });

    // 优雅关闭处理
    const gracefulShutdown = async (signal: string): Promise<void> => {
      console.log(`\n🛑 Received ${signal}. Starting graceful shutdown...`);

      // 关闭 HTTP 服务器
      server.close(() => {
        console.log('✅ HTTP server closed');
      });

      // 关闭 WebSocket 连接
      wss.clients.forEach((ws) => {
        ws.close();
      });

      // 关闭 orchestrator
      await orchestrator.shutdown();

      console.log('✅ Graceful shutdown complete');
      process.exit(0);
    };

    // 监听关闭信号
    process.on('SIGTERM', () => gracefulShutdown('SIGTERM'));
    process.on('SIGINT', () => gracefulShutdown('SIGINT'));

    process.on('uncaughtException', (error: Error) => {
      console.error('Uncaught Exception:', error);
      gracefulShutdown('UNCAUGHT_EXCEPTION');
    });

    process.on('unhandledRejection', (reason: unknown, promise: Promise<unknown>) => {
      console.error('Unhandled Rejection at:', promise, 'reason:', reason);
      gracefulShutdown('UNHANDLED_REJECTION');
    });
  } catch (error) {
    console.error('Failed to start server:', error);
    process.exit(1);
  }
}

// 启动服务器
startServer();

export { app, server, orchestrator };
