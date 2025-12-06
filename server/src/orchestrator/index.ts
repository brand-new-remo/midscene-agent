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

class MidsceneOrchestrator implements OrchestratorInterface {
  sessions: Map<string, Session>;

  actionHistory: Map<string, ActionRecord[]>;

  logger: winston.Logger;

  constructor() {
    this.sessions = new Map();
    this.actionHistory = new Map();
    this.logger = initializeLogger();
    ensureLogDirectory();
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
    return executeAction(
      session,
      sessionId,
      action,
      params,
      options,
      this.actionHistory,
      this.logger
    );
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
   * 优雅关闭
   */
  async shutdown(): Promise<void> {
    return shutdown(this.sessions, this.actionHistory, this.logger, (sessionId: string) =>
      destroySession(this.sessions, this.actionHistory, sessionId, this.logger)
    );
  }
}

export default MidsceneOrchestrator;
