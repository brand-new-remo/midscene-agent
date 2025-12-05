/**
 * @fileoverview WebSocket 相关类型定义
 * @description 定义 WebSocket 通信的所有类型，包括消息格式和响应类型
 */

import type { ActionParams } from './action.js'

/**
 * WebSocket 消息基接口
 * @description 所有 WebSocket 消息的基础结构
 */
export interface WsMessage {
  /** 消息类型，用于区分不同类型的操作 */
  type: string

  /** 相关的会话 ID（某些消息类型需要） */
  sessionId?: string

  /** 动作类型（action 类型消息需要） */
  action?: string

  /** 动作参数（action 类型消息需要） */
  params?: ActionParams

  /** 消息时间戳（Unix 毫秒时间戳） */
  timestamp?: number
}

/**
 * WebSocket 订阅消息接口
 * @description 客户端订阅会话的消息格式
 */
export interface WsSubscribeMessage extends WsMessage {
  /** 消息类型 */
  type: 'subscribe'

  /** 要订阅的会话 ID（必需） */
  sessionId: string
}

/**
 * WebSocket 动作消息接口
 * @description 客户端执行动作的消息格式
 */
export interface WsActionMessage extends WsMessage {
  /** 消息类型 */
  type: 'action'

  /** 要执行的动作类型 */
  action: string

  /** 动作执行参数 */
  params: ActionParams
}

/**
 * WebSocket 取消订阅消息接口
 * @description 客户端取消订阅的消息格式
 */
export interface WsUnsubscribeMessage extends WsMessage {
  /** 消息类型 */
  type: 'unsubscribe'
}

/**
 * WebSocket 响应消息接口
 * @description 服务器向客户端发送的响应消息格式
 */
export interface WsResponse {
  /** 响应类型，用于区分不同类型的响应 */
  type: string

  /** 相关的会话 ID */
  sessionId?: string

  /** 执行的动作类型 */
  action?: string

  /** 响应数据或动作执行结果 */
  result?: unknown

  /** 错误信息（发生错误时） */
  error?: string

  /** 响应时间戳（Unix 毫秒时间戳） */
  timestamp: number
}

/**
 * WebSocket 动作开始响应接口
 * @description 当动作开始执行时发送的响应
 */
export interface WsActionStartResponse extends WsResponse {
  /** 响应类型 */
  type: 'action_start'

  /** 会话 ID */
  sessionId: string

  /** 开始执行的动作类型 */
  action: string

  /** 响应时间戳 */
  timestamp: number
}

/**
 * WebSocket 动作完成响应接口
 * @description 当动作完成执行时发送的响应
 */
export interface WsActionCompleteResponse extends WsResponse {
  /** 响应类型 */
  type: 'action_complete'

  /** 会话 ID */
  sessionId: string

  /** 完成执行的动作类型 */
  action: string

  /** 动作执行结果 */
  result: unknown

  /** 响应时间戳 */
  timestamp: number
}

/**
 * WebSocket 动作错误响应接口
 * @description 当动作执行失败时发送的响应
 */
export interface WsActionErrorResponse extends WsResponse {
  /** 响应类型 */
  type: 'action_error'

  /** 会话 ID */
  sessionId: string

  /** 执行失败的动作类型 */
  action?: string

  /** 错误信息 */
  error: string

  /** 响应时间戳 */
  timestamp: number
}

/**
 * WebSocket 订阅确认响应接口
 * @description 当订阅成功时发送的确认响应
 */
export interface WsSubscribedResponse extends WsResponse {
  /** 响应类型 */
  type: 'subscribed'

  /** 成功订阅的会话 ID */
  sessionId: string

  /** 响应时间戳 */
  timestamp: number
}
