/**
 * Midscene Node.js 服务器
 *
 * 提供 HTTP API 和 WebSocket 接口，
 * 集成 Midscene.js + Playwright 实现网页自动化
 */
import 'dotenv/config';

import { createApp, errorHandler } from './middleware/index';
import { registerRoutes } from './routes/index';
import { createWebSocketServer } from './websocket/index';
import { startServer } from './server/start';
import MidsceneOrchestrator from './orchestrator/index';

// 过滤掉 Midscene 的报告日志
const originalConsoleLog = console.log;
console.log = (...args: unknown[]) => {
  const message = args.join(' ');
  if (message.includes('Midscene - report file updated')) {
    return; // 跳过这个日志
  }
  originalConsoleLog(...args);
};

// 创建 Express 应用
const app = createApp();

// 初始化 orchestrator
const orchestrator = new MidsceneOrchestrator();

// 注册路由
registerRoutes(app, orchestrator);

// 全局错误处理
app.use(errorHandler);

// 启动服务器
const { httpServer, gracefulShutdown } = await startServer(app);

// 初始化 WebSocket 服务器
const { server: wsServer, connectionManager } = createWebSocketServer(httpServer, orchestrator);

// 设置信号处理器
gracefulShutdown.setupSignalHandlers(httpServer, wsServer, orchestrator);

export { app, httpServer, wsServer, connectionManager, orchestrator };
