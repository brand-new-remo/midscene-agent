/**
 * 中间件配置
 */
import cors from 'cors';
import express, { type NextFunction, type Request, type Response } from 'express';
import { SERVER_CONFIG } from '../config/server';

/**
 * 创建 Express 应用实例
 */
export function createApp(): express.Application {
  const app = express();

  // 应用中间件
  app.use(cors());
  app.use(
    express.json({
      limit: SERVER_CONFIG.JSON_LIMIT,
    })
  );

  return app;
}

/**
 * 全局错误处理中间件
 */
export function errorHandler(err: Error, _req: Request, res: Response, _next: NextFunction): void {
  console.error('Unhandled error:', err);
  res.status(500).json({
    success: false,
    error: err.message,
    timestamp: Date.now(),
  });
}
