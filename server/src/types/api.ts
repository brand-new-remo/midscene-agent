/**
 * @fileoverview API 相关类型定义
 * @description 定义 HTTP API 的所有响应类型和结果类型
 */

import type { Logger } from 'winston'
import type { Session, SessionConfig, SessionInfo, ActionType, ActionParams, ActionResult, ActionRecord, ActionOptions, QueryType, QueryParams } from './index.js'

/**
 * API 响应基接口
 * @description 所有 HTTP API 响应的标准格式
 */
export interface ApiResponse<T = unknown> {
  /** 请求是否成功执行 */
  success: boolean

  /** 响应时间戳（Unix 毫秒时间戳） */
  timestamp: number

  /** 响应数据（可选） */
  result?: T

  /** 错误信息（可选，请求失败时包含） */
  error?: string

  /** 成功消息（可选） */
  message?: string
}

/**
 * 创建会话响应接口
 * @description POST /api/sessions 接口的响应格式
 */
export interface CreateSessionResponse extends ApiResponse {
  /** 成功创建后会话 ID（仅在 success=true 时存在） */
  sessionId?: string
}

/**
 * 执行动作响应接口
 * @description POST /api/sessions/:id/action 接口的响应格式
 */
export interface ExecuteActionResponse extends ApiResponse {
  /** 动作执行结果（仅在 success=true 时存在） */
  result?: ActionResult
}

/**
 * 执行查询响应接口
 * @description POST /api/sessions/:id/query 接口的响应格式
 */
export interface ExecuteQueryResponse extends ApiResponse {
  /** 查询执行结果（仅在 success=true 时存在） */
  result?: unknown
}

/**
 * 获取会话列表响应接口
 * @description GET /api/sessions 接口的响应格式
 */
export interface GetSessionsResponse extends ApiResponse {
  /** 活跃会话列表（仅在 success=true 时存在） */
  sessions?: SessionInfo[]
}

/**
 * 获取会话历史响应接口
 * @description GET /api/sessions/:id/history 接口的响应格式
 */
export interface GetSessionHistoryResponse extends ApiResponse {
  /** 会话动作历史记录（仅在 success=true 时存在） */
  history?: ActionRecord[]
}

/**
 * 销毁会话响应接口
 * @description DELETE /api/sessions/:id 接口的响应格式
 */
export interface DestroySessionResponse extends ApiResponse {
  /** 成功消息（仅在 success=true 时存在） */
  message?: string
}

/**
 * 健康检查结果接口
 * @description GET /api/health 接口的响应数据格式
 */
export interface HealthCheckResult {
  /** 服务状态标识 */
  status: string

  /** 当前活跃的会话数量 */
  activeSessions: number

  /** 自服务启动以来的累计动作执行次数 */
  totalActions: number

  /** 服务运行时长（秒） */
  uptime: number

  /** 当前进程的内存使用情况 */
  memory: NodeJS.MemoryUsage
}

/**
 * 健康检查响应接口
 * @description GET /api/health 接口的完整响应格式
 */
export interface HealthCheckResponse extends ApiResponse<HealthCheckResult> {
  /** 健康检查结果数据（包含服务状态统计信息） */
  result?: HealthCheckResult
}

/**
 * 根路径响应接口
 * @description GET / 接口的响应格式，提供服务信息
 */
export interface RootResponse {
  /** 服务名称 */
  name: string

  /** 服务版本号 */
  version: string

  /** 服务描述 */
  description: string

  /** 支持的所有 API 端点列表 */
  endpoints: string[]

  /** 响应时间戳 */
  timestamp: number
}

/**
 * Orchestrator 接口定义
 * @description 定义 MidsceneOrchestrator 类的公开方法规范
 */
export interface OrchestratorInterface {
  /** 所有活跃会话的映射表 */
  sessions: Map<string, Session>

  /** 所有会话的动作历史记录映射表 */
  actionHistory: Map<string, ActionRecord[]>

  /** Winston 日志实例 */
  logger: Logger

  /**
   * 创建新的 Midscene 会话
   * @param config - 会话配置参数
   * @returns 创建的会话唯一 ID
   */
  createSession(config?: SessionConfig): Promise<string>

  /**
   * 执行网页动作
   * @param sessionId - 会话 ID
   * @param action - 动作类型
   * @param params - 动作参数
   * @param options - 执行选项（如流式响应）
   * @returns 动作执行结果
   */
  executeAction(sessionId: string, action: ActionType, params?: ActionParams, options?: ActionOptions): Promise<ActionResult>

  /**
   * 查询页面信息
   * @param sessionId - 会话 ID
   * @param query - 查询类型
   * @param params - 查询参数
   * @returns 查询结果
   */
  executeQuery(sessionId: string, query: QueryType, params?: QueryParams): Promise<unknown>

  /**
   * 销毁指定会话
   * @param sessionId - 要销毁的会话 ID
   */
  destroySession(sessionId: string): Promise<void>

  /**
   * 获取所有活跃会话列表
   * @returns 会话信息数组
   */
  getActiveSessions(): SessionInfo[]

  /**
   * 获取指定会话的动作历史记录
   * @param sessionId - 会话 ID
   * @returns 动作记录数组
   */
  getSessionHistory(sessionId: string): ActionRecord[]

  /**
   * 执行服务健康检查
   * @returns 健康检查结果
   */
  healthCheck(): Promise<HealthCheckResult>

  /**
   * 优雅关闭 Orchestrator
   */
  shutdown(): Promise<void>
}
