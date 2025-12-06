/**
 * 优雅关闭逻辑
 */
import http from 'http';
import { WebSocketServer } from 'ws';
import type MidsceneOrchestrator from '../orchestrator/index';

/**
 * 优雅关闭处理器
 */
export class GracefulShutdown {
  private isShuttingDown = false;

  /**
   * 执行优雅关闭
   */
  async shutdown(
    signal: string,
    httpServer: http.Server,
    wss: WebSocketServer,
    orchestrator: MidsceneOrchestrator
  ): Promise<void> {
    if (this.isShuttingDown) {
      console.log('Shutdown already in progress...');
      return;
    }

    this.isShuttingDown = true;
    console.log(`\n🛑 Received ${signal}. Starting graceful shutdown...`);

    // 关闭 HTTP 服务器
    httpServer.close(() => {
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
  }

  /**
   * 注册关闭信号监听
   */
  setupSignalHandlers(
    httpServer: http.Server,
    wss: WebSocketServer,
    orchestrator: MidsceneOrchestrator
  ): void {
    // 监听关闭信号
    process.on('SIGTERM', () => {
      this.shutdown('SIGTERM', httpServer, wss, orchestrator);
    });

    process.on('SIGINT', () => {
      this.shutdown('SIGINT', httpServer, wss, orchestrator);
    });

    process.on('uncaughtException', (error: Error) => {
      console.error('Uncaught Exception:', error);
      this.shutdown('UNCAUGHT_EXCEPTION', httpServer, wss, orchestrator);
    });

    process.on('unhandledRejection', (reason: unknown, promise: Promise<unknown>) => {
      console.error('Unhandled Rejection at:', promise, 'reason:', reason);
      this.shutdown('UNHANDLED_REJECTION', httpServer, wss, orchestrator);
    });
  }
}
