/**
 * WebSocket 服务器
 */
import http from 'http';
import { WebSocketServer, type WebSocket } from 'ws';
import type { WsMessage } from '../types/index';
import type MidsceneOrchestrator from '../orchestrator/index';
import { WebSocketConnectionManager } from './connectionManager';
import { createWebSocketHandlers } from './handlers';

/**
 * 创建 WebSocket 服务器
 */
export function createWebSocketServer(
  server: http.Server,
  orchestrator: MidsceneOrchestrator
): {
  server: WebSocketServer;
  connectionManager: WebSocketConnectionManager;
  handlers: ReturnType<typeof createWebSocketHandlers>;
} {
  const wss = new WebSocketServer({ server });
  const connectionManager = new WebSocketConnectionManager();
  const handlers = createWebSocketHandlers(orchestrator, connectionManager);

  /**
   * WebSocket 连接处理
   */
  wss.on('connection', (ws: WebSocket) => {
    let currentSessionId: string | null = null;

    console.log('🔌 WebSocket client connected');

    ws.on('message', async (message: Buffer) => {
      try {
        const data = JSON.parse(message.toString()) as WsMessage;
        await handlers.handleMessage(ws, data, currentSessionId, (id) => {
          currentSessionId = id;
        });
      } catch (error) {
        const err = error as Error;
        console.error('WebSocket message error:', err);
        ws.send(
          JSON.stringify({
            type: 'error',
            message: err.message,
            timestamp: Date.now(),
          })
        );
      }
    });

    ws.on('close', () => {
      if (currentSessionId) {
        connectionManager.removeConnection(currentSessionId);
        console.log(`📡 WebSocket client disconnected from session: ${currentSessionId}`);
      }
    });

    ws.on('error', (error: Error) => {
      console.error('WebSocket error:', error);
    });
  });

  return {
    server: wss,
    connectionManager,
    handlers,
  };
}
