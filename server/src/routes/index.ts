/**
 * 路由聚合
 */
import { type Application } from 'express';
import type MidsceneOrchestrator from '../orchestrator/index';
import { createHealthRoutes } from './health';
import { createSessionRoutes } from './sessions';
import { createRootRoutes } from './root';

/**
 * 注册所有路由
 */
export function registerRoutes(app: Application, orchestrator: MidsceneOrchestrator): void {
  const healthRoutes = createHealthRoutes(orchestrator);
  const sessionRoutes = createSessionRoutes(orchestrator);
  const rootRoutes = createRootRoutes();

  // 健康检查
  app.get('/api/health', healthRoutes.check);

  // 会话管理
  app.post('/api/sessions', sessionRoutes.create);
  app.get('/api/sessions', sessionRoutes.list);
  app.post('/api/sessions/:sessionId/action', sessionRoutes.executeAction);
  app.post('/api/sessions/:sessionId/query', sessionRoutes.executeQuery);
  app.get('/api/sessions/:sessionId/history', sessionRoutes.getHistory);
  app.delete('/api/sessions/:sessionId', sessionRoutes.destroy);

  // 根路径
  app.get('/', rootRoutes.index);
}
