/**
 * @fileoverview Session 相关类型定义
 * @description 定义 Midscene 会话管理的所有类型，包括会话配置、会话对象和会话信息
 */

import type { Browser, Page } from 'playwright'
import { MidscenePlaywrightAgent } from '../midscene-playwright-agent'

/**
 * 会话配置接口
 * @description 用于创建新 Midscene 会话的配置参数
 */
export interface SessionConfig {
  /** 是否以无头模式启动浏览器（默认：true） */
  headless?: boolean

  /** 浏览器视口宽度（默认：1920px） */
  viewport_width?: number

  /** 浏览器视口高度（默认：1080px） */
  viewport_height?: number

  /** Midscene 使用的 AI 模型名称（默认：从环境变量 MIDSCENE_MODEL_NAME 获取） */
  model?: string

  /** AI API 的基础 URL（默认：从环境变量 OPENAI_BASE_URL 获取） */
  baseURL?: string

  /** AI API 的密钥（默认：从环境变量 OPENAI_API_KEY 获取） */
  apiKey?: string

  /** 网络空闲等待超时时间（默认：2000ms） */
  waitForNetworkIdleTimeout?: number

  /** 动作执行超时时间（默认：30000ms） */
  actionTimeout?: number
}

/**
 * Midscene 配置接口
 * @description 会话内部使用的 Midscene 运行时配置
 */
export interface MidsceneConfig {
  /** AI 模型名称，必填 */
  model: string

  /** AI API 基础 URL，可选 */
  baseURL?: string

  /** AI API 密钥，可选 */
  apiKey?: string

  /** 网络空闲等待超时时间，默认 2000ms */
  waitForNetworkIdleTimeout: number

  /** 动作执行超时时间，默认 30000ms */
  actionTimeout: number
}

/**
 * 会话对象接口
 * @description 表示一个活跃的 Midscene 会话，包含其所有相关状态和资源
 */
export interface Session {
  /** MidscenePlaywrightAgent 实例，用于执行网页自动化操作 */
  agent: MidscenePlaywrightAgent

  /** Playwright 浏览器实例 */
  browser: Browser

  /** Playwright 页面实例，原始的 Page 对象 */
  page: Page

  /** Midscene 运行时配置 */
  config: MidsceneConfig

  /** 会话当前状态：
   * - 'ready': 会话已就绪，可以执行操作
   * - 'busy': 会话正在执行操作中
   * - 'error': 会话遇到错误，需要重建
   */
  state: 'ready' | 'busy' | 'error'

  /** 会话创建时间戳（Unix 毫秒时间戳） */
  createdAt: number

  /** 会话最后活动时间戳（Unix 毫秒时间戳） */
  lastActivity: number
}

/**
 * 会话信息接口
 * @description 用于 API 响应中展示会话概要信息的轻量级类型
 */
export interface SessionInfo {
  /** 会话唯一标识符 */
  sessionId: string

  /** 会话创建时间戳 */
  createdAt: number

  /** 会话最后活动时间戳 */
  lastActivity: number

  /** 会话当前状态（字符串格式） */
  state: string
}
