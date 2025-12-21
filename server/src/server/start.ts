/**
 * 服务器启动逻辑
 */
import http from 'http';
import type { Application } from 'express';
import { SERVER_CONFIG } from '../config/server';
import { GracefulShutdown } from './shutdown';

/**
 * 启动服务器
 */
export async function startServer(app: Application): Promise<{
  httpServer: http.Server;
  gracefulShutdown: GracefulShutdown;
}> {
  // 创建 HTTP 服务器
  const httpServer = http.createServer(app);

  // 创建优雅关闭处理器
  const gracefulShutdown = new GracefulShutdown();

  try {
    // 启动服务器
    await new Promise<void>((resolve, reject) => {
      httpServer.listen(SERVER_CONFIG.PORT, (error?: Error) => {
        if (error) {
          reject(error);
          return;
        }

        console.log(`\n${'='.repeat(70)}`);
        console.log('🚀 Midscene Node.js Server v2.0.0');
        console.log('='.repeat(70));
        console.log(`✅ HTTP Server running on port ${SERVER_CONFIG.PORT}`);
        console.log(`📊 Health check: http://localhost:${SERVER_CONFIG.PORT}/api/health`);
        console.log(`${'='.repeat(70)}\n`);

        resolve();
      });
    });

    return {
      httpServer,
      gracefulShutdown,
    };
  } catch (error) {
    console.error('Failed to start server:', error);
    throw error;
  }
}
