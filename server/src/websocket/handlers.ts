/**
 * WebSocket 消息处理器
 */
import { WebSocket } from 'ws';
import type { ActionParams, ActionType, WsMessage } from '../types/index';
import type MidsceneOrchestrator from '../orchestrator/index';
import { WebSocketConnectionManager } from './connectionManager';

/**
 * 发送 WebSocket 错误消息
 */
function sendWebSocketError(ws: WebSocket, message: string, type = 'error'): void {
  ws.send(
    JSON.stringify({
      type,
      message,
      timestamp: Date.now(),
    })
  );
}

/**
 * 创建 WebSocket 消息处理器
 */
export function createWebSocketHandlers(
  orchestrator: MidsceneOrchestrator,
  connectionManager: WebSocketConnectionManager
): {
  handleSubscribe: (ws: WebSocket, sessionId: string) => void;
  handleAction: (
    ws: WebSocket,
    sessionId: string,
    action: ActionType,
    params: ActionParams
  ) => Promise<void>;
  handleUnsubscribe: (sessionId: string | null) => void;
  handleMessage: (
    ws: WebSocket,
    data: WsMessage,
    currentSessionId: string | null,
    setSessionId: (id: string | null) => void
  ) => Promise<void>;
} {
  /**
   * 处理订阅
   */
  const handleSubscribe = (ws: WebSocket, sessionId: string): void => {
    if (!sessionId) {
      sendWebSocketError(ws, 'Session ID is required for subscribe');
      return;
    }
    connectionManager.addConnection(sessionId, ws);

    ws.send(
      JSON.stringify({
        type: 'subscribed',
        sessionId,
        timestamp: Date.now(),
      })
    );
  };

  /**
   * 处理动作执行
   */
  const handleAction = async (
    ws: WebSocket,
    sessionId: string,
    action: ActionType,
    params: ActionParams
  ): Promise<void> => {
    try {
      await orchestrator.executeAction(sessionId, action, params, {
        stream: true,
        websocket: ws,
      });
    } catch (error) {
      const err = error as Error;
      ws.send(
        JSON.stringify({
          type: 'action_error',
          sessionId,
          action,
          error: err.message,
          timestamp: Date.now(),
        })
      );
    }
  };

  /**
   * 处理取消订阅
   */
  const handleUnsubscribe = (sessionId: string | null): void => {
    if (sessionId) {
      connectionManager.removeConnection(sessionId);
    }
  };

  /**
   * 处理 WebSocket 消息
   */
  const handleMessage = async (
    ws: WebSocket,
    data: WsMessage,
    currentSessionId: string | null,
    setSessionId: (id: string | null) => void
  ): Promise<void> => {
    const { type, sessionId, action, params } = data;

    switch (type) {
      case 'subscribe': {
        if (!sessionId) {
          sendWebSocketError(ws, 'Session ID is required for subscribe');
          setSessionId(null);
          break;
        }
        setSessionId(sessionId);
        handleSubscribe(ws, sessionId);
        break;
      }
      case 'action': {
        if (!currentSessionId) {
          sendWebSocketError(ws, 'No active session');
          return;
        }
        await handleAction(ws, currentSessionId, action as ActionType, params as ActionParams);
        break;
      }
      case 'unsubscribe': {
        handleUnsubscribe(currentSessionId);
        setSessionId(null);
        break;
      }
      default: {
        sendWebSocketError(ws, `Unknown message type: ${type}`);
      }
    }
  };

  return {
    handleSubscribe,
    handleAction,
    handleUnsubscribe,
    handleMessage,
  };
}
