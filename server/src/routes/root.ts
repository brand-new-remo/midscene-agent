/**
 * 根路径路由
 */
import { type Request, type Response } from 'express';

export function createRootRoutes(): {
  index: (req: Request, res: Response) => void;
} {
  return {
    /**
     * 根路径
     */
    index: (req: Request, res: Response) => {
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
    },
  };
}
