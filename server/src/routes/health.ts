/**
 * 健康检查路由
 */
import { type Request, type Response } from 'express';
import type MidsceneOrchestrator from '../orchestrator/index';

export function createHealthRoutes(orchestrator: MidsceneOrchestrator): {
  check: (req: Request, res: Response) => Promise<void>;
} {
  return {
    /**
     * 健康检查
     */
    check: async (req: Request, res: Response) => {
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
    },
  };
}
