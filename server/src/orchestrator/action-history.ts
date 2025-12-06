import type { ActionParams, ActionRecord, ActionResult, ActionType } from './types.js';
import type { ActionOptions } from './types.js';
import winston from 'winston';

/**
 * 记录动作到历史记录中
 * @param actionHistory 动作历史存储 Map
 * @param config 历史记录配置对象
 * @description 将动作执行信息添加到会话的动作历史中，包括：
 * - 会话 ID
 * - 动作类型和参数
 * - 执行结果或错误信息
 * - 执行耗时和时间戳
 */
export const recordActionHistory = (
  actionHistory: Map<string, ActionRecord[]>,
  config: {
    sessionId: string;
    action: ActionType;
    params: ActionParams;
    result: ActionResult | undefined;
    error: string | undefined;
    duration: number;
    timestamp: number;
  }
): void => {
  const { sessionId, action, params, result, error, duration, timestamp } = config;
  const actionRecord: ActionRecord = {
    action,
    params,
    result,
    error,
    duration,
    timestamp,
  };
  const history = actionHistory.get(sessionId);
  if (history) {
    history.push(actionRecord);
  }
};

/**
 * 执行动作并记录结果
 * @param actionHistory 动作历史存储 Map
 * @param logger 日志记录器
 * @param config 执行配置对象
 * @returns 动作执行结果
 * @description 执行指定的动作函数，记录执行结果到历史，并记录日志：
 * 1. 调用执行函数
 * 2. 记录执行耗时
 * 3. 保存成功结果到历史
 * 4. 记录成功日志
 */
export const executeAndRecord = async (
  actionHistory: Map<string, ActionRecord[]>,
  logger: winston.Logger,
  config: {
    sessionId: string;
    action: ActionType;
    params: ActionParams;
    startTime: number;
    executeFn: () => Promise<ActionResult>;
  }
): Promise<ActionResult> => {
  const { sessionId, action, params, startTime, executeFn } = config;
  const result = await executeFn();
  const duration = Date.now() - startTime;

  recordActionHistory(actionHistory, {
    sessionId,
    action,
    params,
    result,
    error: undefined,
    duration,
    timestamp: startTime,
  });

  logger.info('Action completed', {
    sessionId,
    action,
    duration,
  });

  return result;
};

/**
 * 处理动作执行错误
 * @param actionHistory 动作历史存储 Map
 * @param logger 日志记录器
 * @param config 错误处理配置对象
 * @description 处理动作执行过程中出现的错误：
 * 1. 记录错误信息到历史
 * 2. 记录错误日志
 * 3. 如果启用了流式传输，通过 WebSocket 发送错误消息
 */
export const handleActionError = (
  actionHistory: Map<string, ActionRecord[]>,
  logger: winston.Logger,
  config: {
    sessionId: string;
    action: ActionType;
    params: ActionParams;
    startTime: number;
    error: Error;
    options: ActionOptions;
  }
): void => {
  const { sessionId, action, params, startTime, error, options } = config;
  const duration = Date.now() - startTime;

  recordActionHistory(actionHistory, {
    sessionId,
    action,
    params,
    result: undefined,
    error: error.message,
    duration,
    timestamp: startTime,
  });

  logger.error('Action failed', {
    sessionId,
    action,
    error: error.message,
    duration,
  });

  if (options.stream && options.websocket) {
    options.websocket.send(
      JSON.stringify({
        type: 'action_error',
        sessionId,
        action,
        error: error.message,
        timestamp: Date.now(),
      })
    );
  }
};
