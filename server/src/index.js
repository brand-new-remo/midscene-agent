/**
 * Midscene Node.js 服务器
 *
 * 提供 HTTP API 和 WebSocket 接口，
 * 集成 Midscene.js + Playwright 实现网页自动化
 */

require('dotenv').config();
const express = require('express');
const http = require('http');
const WebSocket = require('ws');
const cors = require('cors');
const { MidsceneOrchestrator } = require('./orchestrator');
const {
  httpMetricsMiddleware,
  getMetrics,
  startMetricsCollection
} = require('./metrics');

const app = express();
const server = http.createServer(app);
const wss = new WebSocket.Server({ server });

// 中间件
app.use(cors());
app.use(express.json({ limit: '10mb' }));
app.use(httpMetricsMiddleware());

// 初始化 orchestrator
const orchestrator = new MidsceneOrchestrator();

// WebSocket 连接管理
const wsConnections = new Map(); // sessionId -> ws

/**
 * WebSocket 消息处理
 */
wss.on('connection', (ws, req) => {
  let currentSessionId = null;

  console.log('🔌 WebSocket client connected');

  ws.on('message', async (message) => {
    try {
      const data = JSON.parse(message);
      const { type, sessionId, action, params } = data;

      switch (type) {
        case 'subscribe':
          currentSessionId = sessionId;
          wsConnections.set(sessionId, ws);
          console.log(`📡 Client subscribed to session: ${sessionId}`);

          ws.send(JSON.stringify({
            type: 'subscribed',
            sessionId,
            timestamp: Date.now()
          }));
          break;

        case 'action':
          if (currentSessionId) {
            try {
              const result = await orchestrator.executeAction(
                currentSessionId,
                action,
                params,
                { stream: true, websocket: ws }
              );
            } catch (error) {
              ws.send(JSON.stringify({
                type: 'action_error',
                sessionId: currentSessionId,
                action,
                error: error.message,
                timestamp: Date.now()
              }));
            }
          }
          break;

        case 'unsubscribe':
          if (currentSessionId) {
            wsConnections.delete(currentSessionId);
            console.log(`📡 Client unsubscribed from session: ${currentSessionId}`);
            currentSessionId = null;
          }
          break;

        default:
          ws.send(JSON.stringify({
            type: 'error',
            message: `Unknown message type: ${type}`,
            timestamp: Date.now()
          }));
      }
    } catch (error) {
      console.error('WebSocket message error:', error);
      ws.send(JSON.stringify({
        type: 'error',
        message: error.message,
        timestamp: Date.now()
      }));
    }
  });

  ws.on('close', () => {
    if (currentSessionId) {
      wsConnections.delete(currentSessionId);
      console.log(`📡 WebSocket client disconnected from session: ${currentSessionId}`);
    }
  });

  ws.on('error', (error) => {
    console.error('WebSocket error:', error);
  });
});

/**
 * HTTP 路由
 */

// 健康检查
app.get('/api/health', async (req, res) => {
  try {
    const health = await orchestrator.healthCheck();
    res.json({
      status: 'ok',
      timestamp: Date.now(),
      ...health
    });
  } catch (error) {
    res.status(500).json({
      status: 'error',
      message: error.message,
      timestamp: Date.now()
    });
  }
});

// 创建会话
app.post('/api/sessions', async (req, res) => {
  try {
    const sessionId = await orchestrator.createSession(req.body);
    res.json({
      success: true,
      sessionId,
      timestamp: Date.now()
    });
    console.log(`✅ Session created: ${sessionId}`);
  } catch (error) {
    console.error('Failed to create session:', error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// 执行动作
app.post('/api/sessions/:sessionId/action', async (req, res) => {
  const { sessionId } = req.params;
  const { action, params } = req.body;

  try {
    const result = await orchestrator.executeAction(sessionId, action, params);
    res.json({
      success: true,
      result,
      timestamp: Date.now()
    });
  } catch (error) {
    console.error(`Failed to execute action ${action} for session ${sessionId}:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// 查询页面信息
app.post('/api/sessions/:sessionId/query', async (req, res) => {
  const { sessionId } = req.params;
  const { query, params } = req.body;

  try {
    const result = await orchestrator.executeQuery(sessionId, query, params);
    res.json({
      success: true,
      result,
      timestamp: Date.now()
    });
  } catch (error) {
    console.error(`Failed to execute query ${query} for session ${sessionId}:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// 截取屏幕截图
app.get('/api/sessions/:sessionId/screenshot', async (req, res) => {
  const { sessionId } = req.params;

  try {
    const screenshot = await orchestrator.takeScreenshot(sessionId, req.query);
    res.json({
      success: true,
      screenshot,
      timestamp: Date.now()
    });
  } catch (error) {
    console.error(`Failed to take screenshot for session ${sessionId}:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// 获取活跃会话列表
app.get('/api/sessions', (req, res) => {
  try {
    const sessions = orchestrator.getActiveSessions();
    res.json({
      success: true,
      sessions,
      timestamp: Date.now()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// 获取会话历史
app.get('/api/sessions/:sessionId/history', (req, res) => {
  const { sessionId } = req.params;

  try {
    const history = orchestrator.getSessionHistory(sessionId);
    res.json({
      success: true,
      history,
      timestamp: Date.now()
    });
  } catch (error) {
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// 销毁会话
app.delete('/api/sessions/:sessionId', async (req, res) => {
  const { sessionId } = req.params;

  try {
    await orchestrator.destroySession(sessionId);
    res.json({
      success: true,
      message: `Session ${sessionId} destroyed`,
      timestamp: Date.now()
    });
    console.log(`🗑️ Session destroyed: ${sessionId}`);
  } catch (error) {
    console.error(`Failed to destroy session ${sessionId}:`, error);
    res.status(500).json({
      success: false,
      error: error.message,
      timestamp: Date.now()
    });
  }
});

// Prometheus 指标端点
app.get('/metrics', async (req, res) => {
  try {
    const metrics = await getMetrics();
    res.set('Content-Type', register.contentType);
    res.end(metrics);
  } catch (error) {
    res.status(500).json({
      error: error.message
    });
  }
});

// 根路径
app.get('/', (req, res) => {
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
      'GET /api/sessions/:sessionId/screenshot - Take screenshot',
      'GET /api/sessions/:sessionId/history - Get session history',
      'DELETE /api/sessions/:sessionId - Destroy session',
      'GET /metrics - Prometheus metrics',
      'WebSocket /ws - WebSocket connection'
    ],
    timestamp: Date.now()
  });
});

// 全局错误处理
app.use((err, req, res, next) => {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: err.message,
    timestamp: Date.now()
  });
});

// 启动服务器
const PORT = process.env.PORT || 3000;

async function startServer() {
  try {
    // 启动指标收集
    startMetricsCollection(orchestrator);

    server.listen(PORT, () => {
      console.log('\n' + '='.repeat(70));
      console.log('🚀 Midscene Node.js Server v2.0.0');
      console.log('='.repeat(70));
      console.log(`✅ HTTP Server running on port ${PORT}`);
      console.log(`✅ WebSocket server ready`);
      console.log(`✅ Orchestrator initialized`);
      console.log(`📊 Health check: http://localhost:${PORT}/api/health`);
      console.log(`📈 Metrics: http://localhost:${PORT}/metrics`);
      console.log('='.repeat(70) + '\n');
    });

    // 优雅关闭处理
    const gracefulShutdown = async (signal) => {
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

    process.on('uncaughtException', (error) => {
      console.error('Uncaught Exception:', error);
      gracefulShutdown('UNCAUGHT_EXCEPTION');
    });

    process.on('unhandledRejection', (reason, promise) => {
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

module.exports = { app, server, orchestrator };