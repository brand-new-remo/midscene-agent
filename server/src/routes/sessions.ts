/**
 * 会话管理路由
 */
import { type Request, type Response } from 'express';
import type { ActionParams, ActionType, QueryParams, QueryType } from '../types/index';
import type MidsceneOrchestrator from '../orchestrator/index';

export function createSessionRoutes(orchestrator: MidsceneOrchestrator): {
  create: (req: Request, res: Response) => Promise<void>;
  executeAction: (req: Request, res: Response) => Promise<void>;
  executeQuery: (req: Request, res: Response) => Promise<void>;
  list: (req: Request, res: Response) => void;
  getHistory: (req: Request, res: Response) => void;
  destroy: (req: Request, res: Response) => Promise<void>;
} {
  return {
    /**
     * 创建会话
     */
    create: async (req: Request, res: Response) => {
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
    },

    /**
     * 执行动作
     */
    executeAction: async (req: Request, res: Response) => {
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
    },

    /**
     * 查询页面信息
     */
    executeQuery: async (req: Request, res: Response) => {
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
    },

    /**
     * 获取活跃会话列表
     */
    list: (req: Request, res: Response) => {
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
    },

    /**
     * 获取会话历史
     */
    getHistory: (req: Request, res: Response) => {
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
    },

    /**
     * 销毁会话
     */
    destroy: async (req: Request, res: Response) => {
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
    },
  };
}
