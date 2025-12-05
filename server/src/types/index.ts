/**
 * @fileoverview 类型定义汇总导出
 * @description 导出所有类型模块，方便其他文件统一导入
 */

// ====================
// Session 相关类型
// ====================
export type {
  /** 会话配置接口 */
  SessionConfig,
  /** Midscene 配置接口 */
  MidsceneConfig,
  /** 会话对象接口 */
  Session,
  /** 会话信息接口 */
  SessionInfo
} from './session.js'

// ====================
// Action 相关类型
// ====================
export type {
  /** 动作类型枚举 */
  ActionType,
  /** 动作参数接口 */
  ActionParams,
  /** 动作结果接口 */
  ActionResult,
  /** 动作记录接口 */
  ActionRecord,
  /** 动作执行选项接口 */
  ActionOptions
} from './action.js'

// ====================
// Query 相关类型
// ====================
export type {
  /** 查询类型枚举 */
  QueryType,
  /** 查询参数接口 */
  QueryParams,
  /** 页面位置信息结果接口 */
  LocationResult,
  /** 标签页信息接口 */
  TabInfo
} from './query.js'

// ====================
// WebSocket 相关类型
// ====================
export type {
  /** WebSocket 消息基接口 */
  WsMessage,
  /** WebSocket 订阅消息接口 */
  WsSubscribeMessage,
  /** WebSocket 动作消息接口 */
  WsActionMessage,
  /** WebSocket 取消订阅消息接口 */
  WsUnsubscribeMessage,
  /** WebSocket 响应消息接口 */
  WsResponse,
  /** WebSocket 动作开始响应接口 */
  WsActionStartResponse,
  /** WebSocket 动作完成响应接口 */
  WsActionCompleteResponse,
  /** WebSocket 动作错误响应接口 */
  WsActionErrorResponse,
  /** WebSocket 订阅确认响应接口 */
  WsSubscribedResponse
} from './websocket.js'

// ====================
// API 相关类型
// ====================
export type {
  /** API 响应基接口 */
  ApiResponse,
  /** 创建会话响应接口 */
  CreateSessionResponse,
  /** 执行动作响应接口 */
  ExecuteActionResponse,
  /** 执行查询响应接口 */
  ExecuteQueryResponse,
  /** 获取会话列表响应接口 */
  GetSessionsResponse,
  /** 获取会话历史响应接口 */
  GetSessionHistoryResponse,
  /** 销毁会话响应接口 */
  DestroySessionResponse,
  /** 健康检查结果接口 */
  HealthCheckResult,
  /** 健康检查响应接口 */
  HealthCheckResponse,
  /** 根路径响应接口 */
  RootResponse,
  /** Orchestrator 接口定义 */
  OrchestratorInterface
} from './api.js'

// ====================
// 重新导出的类型
// ====================

// 从子模块重新导出常用类型，方便直接引用
export type {
  SessionConfig as Config
} from './session.js'

export type {
  Session as SessionData
} from './session.js'

export type {
  ActionType as Action
} from './action.js'

export type {
  QueryType as Query
} from './query.js'

export type {
  ActionParams as Params
} from './action.js'

export type {
  WsMessage as Message
} from './websocket.js'

