import type { HealthCheckResult, ActionRecord } from './types.js';
import type { Session } from './types.js';
import winston from 'winston';

/**
 * 获取指定会话的动作历史记录
 * @param actionHistory 动作历史存储 Map
 * @param sessionId 会话 ID
 * @returns 该会话的动作历史记录数组
 * @description 从历史记录中获取指定会话的所有动作执行记录，如果没有记录则返回空数组
 */
export const getSessionHistory = (
  actionHistory: Map<string, ActionRecord[]>,
  sessionId: string
): ActionRecord[] => {
  return actionHistory.get(sessionId) || [];
};

/**
 * 执行健康检查
 * @param sessions 会话存储 Map
 * @param actionHistory 动作历史存储 Map
 * @returns 健康检查结果对象
 * @description 检查 Orchestrator 的运行状态，包括：
 * - 活跃会话数量
 * - 总动作执行次数
 * - 系统运行时间
 * - 内存使用情况
 * 用于监控和诊断系统状态
 */
export const healthCheck = (
  sessions: Map<string, Session>,
  actionHistory: Map<string, ActionRecord[]>
): HealthCheckResult => {
  const activeSessions = sessions.size;
  const totalActions = Array.from(actionHistory.values()).reduce(
    (sum, history) => sum + history.length,
    0
  );

  return {
    status: 'healthy',
    activeSessions,
    totalActions,
    uptime: process.uptime(),
    memory: process.memoryUsage(),
  };
};

/**
 * 优雅关闭 Orchestrator
 * @param sessions 会话存储 Map
 * @param actionHistory 动作历史存储 Map
 * @param logger 日志记录器
 * @param destroySessionFn 销毁会话的回调函数
 * @description 安全地关闭 Orchestrator 服务：
 * 1. 记录关闭开始日志
 * 2. 并行销毁所有活跃的会话
 * 3. 等待所有会话销毁完成
 * 4. 记录关闭完成日志
 * 确保所有资源被正确清理
 */
export const shutdown = async (
  sessions: Map<string, Session>,
  actionHistory: Map<string, ActionRecord[]>,
  logger: winston.Logger,
  destroySessionFn: (sessionId: string) => Promise<void>
): Promise<void> => {
  logger.info('Shutting down orchestrator...');

  const destroyPromises = Array.from(sessions.keys()).map((sessionId) =>
    destroySessionFn(sessionId)
  );

  await Promise.all(destroyPromises);

  logger.info('Orchestrator shutdown complete');
};
