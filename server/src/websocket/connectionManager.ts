/**
 * WebSocket 连接管理
 */
import { WebSocket } from 'ws';

export class WebSocketConnectionManager {
  private connections = new Map<string, WebSocket>();

  /**
   * 添加连接
   */
  addConnection(sessionId: string, ws: WebSocket): void {
    // 关闭该会话的旧连接（如果存在）
    const oldConnection = this.connections.get(sessionId);
    if (oldConnection && oldConnection.readyState === WebSocket.OPEN) {
      oldConnection.close();
    }

    this.connections.set(sessionId, ws);
    console.log(`📡 Client subscribed to session: ${sessionId}`);
  }

  /**
   * 移除连接
   */
  removeConnection(sessionId: string): void {
    const removed = this.connections.delete(sessionId);
    if (removed) {
      console.log(`📡 Client unsubscribed from session: ${sessionId}`);
    }
  }

  /**
   * 根据会话 ID 获取连接
   */
  getConnection(sessionId: string): WebSocket | undefined {
    return this.connections.get(sessionId);
  }

  /**
   * 移除所有连接
   */
  removeAllConnections(): void {
    this.connections.clear();
  }

  /**
   * 获取活跃连接数
   */
  getActiveConnectionsCount(): number {
    return this.connections.size;
  }

  /**
   * 检查连接是否存在
   */
  hasConnection(sessionId: string): boolean {
    return this.connections.has(sessionId);
  }
}
