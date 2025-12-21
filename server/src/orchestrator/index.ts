/**
 * Midscene Orchestrator
 *
 * 负责管理多个 Midscene PlaywrightAgent 会话，
 * 执行网页自动化动作，并提供查询功能。
 */
import type {
  ActionOptions,
  ActionParams,
  ActionRecord,
  ActionResult,
  ActionType,
  HealthCheckResult,
  LocationResult,
  OrchestratorInterface,
  QueryParams,
  QueryType,
  Session,
  SessionConfig,
  SessionInfo,
  TabInfo,
} from './types.js';
import winston from 'winston';

// 导入各个功能模块
import { initializeLogger, ensureLogDirectory } from './config.js';
import { createSession, validateSession, destroySession, getActiveSessions } from './session.js';
import { executeAction } from './actions/execute.js';
import { executeQuery } from './queries/execute.js';
import { getSessionHistory, healthCheck, shutdown } from './system.js';
import { ActionDeduplicator, type DeduplicationConfig } from './middleware/deduplication.js';

class MidsceneOrchestrator implements OrchestratorInterface {
  sessions: Map<string, Session>;

  actionHistory: Map<string, ActionRecord[]>;

  logger: winston.Logger;

  deduplicator: ActionDeduplicator;

  constructor() {
    this.sessions = new Map();
    this.actionHistory = new Map();
    this.logger = initializeLogger();
    ensureLogDirectory();

    // 初始化去重中间件
    this.deduplicator = new ActionDeduplicator(this.logger, {
      timeWindow: 5000, // 5秒内不重复执行相同操作
      maxCacheSize: 1000, // 最大缓存1000个操作
      enableLogging: true, // 启用日志记录
    });
  }

  /**
   * 创建新的 Midscene 会话
   */
  async createSession(config: SessionConfig = {}): Promise<string> {
    return createSession(this.sessions, this.logger, config);
  }

  /**
   * 验证会话是否存在
   */
  private validateSession(sessionId: string): Session {
    return validateSession(this.sessions, sessionId, this.logger);
  }

  /**
   * 执行网页动作
   */
  async executeAction(
    sessionId: string,
    action: ActionType,
    params: ActionParams = {},
    options: ActionOptions = {}
  ): Promise<ActionResult> {
    const session = this.validateSession(sessionId);

    // 1. 检查是否应该执行操作（去重检查）
    if (!this.deduplicator.shouldExecute(sessionId, action, params)) {
      // 如果是重复操作，返回缓存的结果
      const cachedResult = this.deduplicator.getCachedResult(sessionId, action, params);
      if (cachedResult) {
        this.logger.info('跳过重复操作，返回缓存结果', {
          sessionId,
          action,
          params,
          cachedResult,
        });
        return cachedResult;
      }
    }

    // 2. 执行操作
    const startTime = Date.now();
    const result = await executeAction(
      session,
      sessionId,
      action,
      params,
      options,
      this.actionHistory,
      this.logger
    );

    // 3. 记录操作结果到去重缓存
    const duration = Date.now() - startTime;
    const resultWithDuration: ActionResult = {
      ...result,
      duration,
    };

    this.deduplicator.record(sessionId, action, params, resultWithDuration);

    return resultWithDuration;
  }

  /**
   * 查询页面信息 - 函数重载，提供精确的类型返回
   */

  // aiAssert 查询：返回断言结果对象
  async executeQuery(
    sessionId: string,
    query: 'aiAssert',
    params?: QueryParams
  ): Promise<{ success: true; assertion: string }>;

  // aiBoolean 查询：返回布尔值
  async executeQuery(sessionId: string, query: 'aiBoolean', params?: QueryParams): Promise<boolean>;

  // aiNumber 查询：返回数值
  async executeQuery(sessionId: string, query: 'aiNumber', params?: QueryParams): Promise<number>;

  // aiString 查询：返回字符串
  async executeQuery(sessionId: string, query: 'aiString', params?: QueryParams): Promise<string>;

  // aiAsk 查询：返回字符串或对象
  async executeQuery(
    sessionId: string,
    query: 'aiAsk',
    params?: QueryParams
  ): Promise<string | Record<string, unknown>>;

  // aiQuery 查询：返回结构化数据
  async executeQuery(
    sessionId: string,
    query: 'aiQuery',
    params?: QueryParams
  ): Promise<Record<string, unknown> | string>;

  // aiLocate 查询：返回位置信息
  async executeQuery(
    sessionId: string,
    query: 'aiLocate',
    params?: QueryParams
  ): Promise<{ x: number; y: number; width: number; height: number }>;

  // location 查询：返回位置信息结果
  async executeQuery(
    sessionId: string,
    query: 'location',
    params?: QueryParams
  ): Promise<LocationResult>;

  // getTabs 查询：返回标签页信息列表
  async executeQuery(sessionId: string, query: 'getTabs', params?: QueryParams): Promise<TabInfo[]>;

  // 通用重载：返回 unknown（用于动态查询类型）
  async executeQuery(sessionId: string, query: QueryType, params?: QueryParams): Promise<unknown>;

  // 方法实现
  async executeQuery(
    sessionId: string,
    query: QueryType,
    params: QueryParams = {}
  ): Promise<unknown> {
    return executeQuery(this.sessions, sessionId, query, params, this.logger);
  }

  /**
   * 销毁会话
   */
  async destroySession(sessionId: string): Promise<void> {
    return destroySession(this.sessions, this.actionHistory, sessionId, this.logger);
  }

  /**
   * 获取活跃会话列表
   */
  getActiveSessions(): SessionInfo[] {
    return getActiveSessions(this.sessions);
  }

  /**
   * 获取会话历史
   */
  getSessionHistory(sessionId: string): ActionRecord[] {
    return getSessionHistory(this.actionHistory, sessionId);
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<HealthCheckResult> {
    return healthCheck(this.sessions, this.actionHistory);
  }

  /**
   * 获取去重中间件统计信息
   */
  getDeduplicationStats(): {
    cacheSize: number;
    maxCacheSize: number;
    timeWindow: number;
    config: DeduplicationConfig;
  } {
    return this.deduplicator.getStats();
  }

  /**
   * 清理去重缓存中的过期项
   */
  cleanExpiredDeduplicationCache(): number {
    return this.deduplicator.cleanExpired();
  }

  /**
   * 清空去重缓存
   */
  clearDeduplicationCache(): void {
    this.deduplicator.clear();
  }

  /**
   * 优雅关闭
   */
  async shutdown(): Promise<void> {
    // 在关闭前清理去重缓存
    this.logger.info('正在清理去重缓存...');
    this.clearDeduplicationCache();

    return shutdown(this.sessions, this.actionHistory, this.logger, (sessionId: string) =>
      destroySession(this.sessions, this.actionHistory, sessionId, this.logger)
    );
  }
}

export default MidsceneOrchestrator;
