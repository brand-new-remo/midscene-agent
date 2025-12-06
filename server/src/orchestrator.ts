/**
 * Midscene Orchestrator
 *
 * 负责管理多个 Midscene PlaywrightAgent 会话，
 * 执行网页自动化动作，并提供查询功能。
 */

import { PlaywrightAgent } from '@midscene/web'
import { v4 as uuidv4 } from 'uuid'
import winston from 'winston'
import { chromium, type Page } from 'playwright'
import fs from 'fs'
import path from 'path'
import { fileURLToPath } from 'url'
import type WebSocket from 'ws'
import type {
  Session,
  SessionConfig,
  MidsceneConfig,
  SessionInfo,
  ActionType,
  ActionParams,
  ActionResult,
  ActionRecord,
  ActionOptions,
  QueryType,
  QueryParams,
  LocationResult,
  TabInfo,
  HealthCheckResult,
  OrchestratorInterface
} from './types/index.js'

const __filename = fileURLToPath(import.meta.url)
const __dirname = path.dirname(__filename)

export class MidsceneOrchestrator implements OrchestratorInterface {
  sessions: Map<string, Session>
  actionHistory: Map<string, ActionRecord[]>
  logger: winston.Logger

  constructor() {
    this.sessions = new Map()
    this.actionHistory = new Map()
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(
        winston.format.timestamp(),
        winston.format.json()
      ),
      transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
        new winston.transports.Console({
          format: winston.format.simple()
        })
      ]
    })

    // 确保日志目录存在
    const logDir = path.join(__dirname, '../logs')
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true })
    }
  }

  /**
   * 创建新的 Midscene 会话
   */
  async createSession(config: SessionConfig = {}): Promise<string> {
    const sessionId = uuidv4()
    const startTime = Date.now()

    this.logger.info('Creating new session', { sessionId, config })

    try {
      // 构建 Playwright 配置
      const playwrightConfig = {
        headless: config.headless !== false,
        viewport: {
          width: config.viewport_width || 1920,
          height: config.viewport_height || 1080
        }
      }

      // 创建 Playwright 浏览器实例
      const browser = await chromium.launch({ headless: playwrightConfig.headless })

      // 创建新页面
      const page = await browser.newPage({
        viewport: playwrightConfig.viewport
      })

      // 构建 Midscene 配置
      const midsceneConfig: MidsceneConfig = {
        model: config.model || process.env.MIDSCENE_MODEL_NAME || 'doubao-seed-1.6-vision',
        baseURL: config.baseURL || process.env.OPENAI_BASE_URL,
        apiKey: config.apiKey || process.env.OPENAI_API_KEY,
        waitForNetworkIdleTimeout: config.waitForNetworkIdleTimeout || 2000,
        actionTimeout: config.actionTimeout || 30000
      }

      // 创建 PlaywrightAgent 实例
      const agent = new PlaywrightAgent(page, midsceneConfig)

      // 存储会话信息
      this.sessions.set(sessionId, {
        agent,
        browser,
        page,  // 保存原始的 Playwright Page 引用
        config: midsceneConfig,
        state: 'ready',
        createdAt: Date.now(),
        lastActivity: Date.now()
      })

      this.actionHistory.set(sessionId, [])

      this.logger.info('Session created successfully', {
        sessionId,
        duration: Date.now() - startTime
      })

      return sessionId

    } catch (error) {
      const err = error as Error
      this.logger.error('Failed to create session', {
        sessionId,
        error: err.message,
        stack: err.stack
      })

      throw new Error(`Failed to create session: ${err.message}`)
    }
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
    const session = this.sessions.get(sessionId)
    const startTime = Date.now()

    if (!session) {
      const error = new Error(`Session ${sessionId} not found`)
      this.logger.error('Session not found', { sessionId, action })
      throw error
    }

    const { agent, page } = session
    session.lastActivity = Date.now()

    this.logger.info('Executing action', {
      sessionId,
      action,
      params: JSON.stringify(params)
    })

    try {
      let result: ActionResult

      // 支持流式响应
      if (options.stream && options.websocket) {
        result = await this.executeActionWithProgress(
          agent, page, action, params, options.websocket, sessionId
        )
      } else {
        result = await this.executeActionDirect(
          agent, page, action, params
        )
      }

      const duration = Date.now() - startTime

      // 记录历史
      const actionRecord: ActionRecord = {
        action,
        params,
        result,
        duration,
        timestamp: startTime
      }
      this.actionHistory.get(sessionId)!.push(actionRecord)

      this.logger.info('Action completed', {
        sessionId,
        action,
        duration
      })

      return result

    } catch (error) {
      const err = error as Error
      const duration = Date.now() - startTime

      // 记录错误历史
      const errorRecord: ActionRecord = {
        action,
        params,
        error: err.message,
        duration,
        timestamp: startTime
      }
      this.actionHistory.get(sessionId)!.push(errorRecord)

      this.logger.error('Action failed', {
        sessionId,
        action,
        error: err.message,
        duration
      })

      if (options.stream && options.websocket) {
        options.websocket.send(JSON.stringify({
          type: 'action_error',
          sessionId,
          action,
          error: err.message,
          timestamp: Date.now()
        }))
      }

      throw error
    }
  }

  /**
   * 直接执行动作（无流式）
   */
  private async executeActionDirect(
    agent: PlaywrightAgent,
    page: Page,
    action: ActionType,
    params: ActionParams
  ): Promise<ActionResult> {

    switch (action) {
      case 'navigate':
        await page.goto(params.url!, { waitUntil: 'networkidle' })
        return { success: true, url: params.url }

      case 'aiTap':
        await agent.aiTap(params.locate!, params.options)
        return { success: true, action: 'tap', target: params.locate }

      case 'aiInput':
        await agent.aiInput(params.locate!, { ...params.options, value: params.value! })
        return { success: true, action: 'input', value: params.value }

      case 'aiScroll':
        await agent.aiScroll(params.locate, {
          direction: params.direction!,
          scrollType: params.scrollType || 'once',
          distance: typeof params.distance === 'string' ? parseInt(params.distance, 10) : (params.distance || 500)
        })
        return { success: true, action: 'scroll', direction: params.direction }

      case 'aiKeyboardPress':
        if (!params.key) {
          throw new Error('aiKeyboardPress requires "key" parameter')
        }
        await agent.aiKeyboardPress(params.key, params.locate, params.options)
        return { success: true, action: 'keypress', key: params.key }

      case 'aiHover':
        await agent.aiHover(params.locate!, params.options)
        return { success: true, action: 'hover', target: params.locate }

      case 'aiWaitFor':
        await agent.aiWaitFor(params.assertion!, {
          timeoutMs: params.timeoutMs || 30000,
          checkIntervalMs: params.checkIntervalMs || 3000
        })
        return { success: true, action: 'wait', assertion: params.assertion }

      case 'aiDoubleClick':
        await agent.aiDoubleClick(params.locate!, params.options)
        return { success: true, action: 'doubleclick', target: params.locate }

      case 'aiRightClick':
        await agent.aiRightClick(params.locate!, params.options)
        return { success: true, action: 'rightclick', target: params.locate }

      case 'aiAction':
        await agent.aiAction(params.prompt!)
        return { success: true, action: 'aiAction', prompt: params.prompt }

      case 'setActiveTab': {
        // get browser from page.context().browser()
        const browser = page.context().browser()
        if (!browser) {
          throw new Error('Browser not found')
        }
        const pages = browser.contexts()[0]?.pages() || []
        const targetPage = pages[params.tabId!]
        if (targetPage) {
          await targetPage.bringToFront()
          return { success: true, action: 'setActiveTab', tabId: params.tabId }
        } else {
          throw new Error(`Tab ${params.tabId} not found`)
        }
      }

      case 'evaluateJavaScript': {
        const result = await agent.evaluateJavaScript(params.script!)
        return { success: true, action: 'evaluateJavaScript', result }
      }

      case 'logScreenshot': {
        // Only pass options if it has a content property
        const options = params.options && 'content' in params.options
          ? params.options as { content: string }
          : undefined
        const result = await agent.logScreenshot(params.title || 'screenshot', options)
        return { success: true, action: 'logScreenshot', title: params.title, result }
      }

      case 'freezePageContext':
        await agent.freezePageContext()
        return { success: true, action: 'freezePageContext' }

      case 'unfreezePageContext':
        await agent.unfreezePageContext()
        return { success: true, action: 'unfreezePageContext' }

      case 'runYaml': {
        const result = await agent.runYaml(params.yamlScript!)
        return { success: true, action: 'runYaml', result }
      }

      case 'setAIActionContext':
        await agent.setAIActionContext(params.context!)
        return { success: true, action: 'setAIActionContext', context: params.context }

      default:
        throw new Error(`Unknown action: ${action}`)
    }
  }

  /**
   * 带进度反馈的动作执行
   */
  private async executeActionWithProgress(
    agent: PlaywrightAgent,
    page: Page,
    action: ActionType,
    params: ActionParams,
    ws: WebSocket,
    sessionId: string
  ): Promise<ActionResult> {
    // 发送开始事件
    ws.send(JSON.stringify({
      type: 'action_start',
      sessionId,
      action,
      timestamp: Date.now()
    }))

    // 执行动作
    const result = await this.executeActionDirect(agent, page, action, params)

    // 发送完成事件
    ws.send(JSON.stringify({
      type: 'action_complete',
      sessionId,
      action,
      result,
      timestamp: Date.now()
    }))

    return result
  }

  /**
   * 查询页面信息 - 函数重载，提供精确的类型返回
   */

  // aiAssert 查询：返回断言结果对象
  async executeQuery(
    sessionId: string,
    query: 'aiAssert',
    params?: QueryParams
  ): Promise<{ success: true; assertion: string }>

  // aiBoolean 查询：返回布尔值
  async executeQuery(
    sessionId: string,
    query: 'aiBoolean',
    params?: QueryParams
  ): Promise<boolean>

  // aiNumber 查询：返回数值
  async executeQuery(
    sessionId: string,
    query: 'aiNumber',
    params?: QueryParams
  ): Promise<number>

  // aiString 查询：返回字符串
  async executeQuery(
    sessionId: string,
    query: 'aiString',
    params?: QueryParams
  ): Promise<string>

  // aiAsk 查询：返回字符串或对象
  async executeQuery(
    sessionId: string,
    query: 'aiAsk',
    params?: QueryParams
  ): Promise<string | Record<string, unknown>>

  // aiQuery 查询：返回结构化数据
  async executeQuery(
    sessionId: string,
    query: 'aiQuery',
    params?: QueryParams
  ): Promise<Record<string, unknown> | string>

  // aiLocate 查询：返回位置信息
  async executeQuery(
    sessionId: string,
    query: 'aiLocate',
    params?: QueryParams
  ): Promise<{ x: number; y: number; width: number; height: number }>

  // location 查询：返回位置信息结果
  async executeQuery(
    sessionId: string,
    query: 'location',
    params?: QueryParams
  ): Promise<LocationResult>

  // getTabs 查询：返回标签页信息列表
  async executeQuery(
    sessionId: string,
    query: 'getTabs',
    params?: QueryParams
  ): Promise<TabInfo[]>

  // 通用重载：返回 unknown（用于动态查询类型）
  async executeQuery(
    sessionId: string,
    query: QueryType,
    params?: QueryParams
  ): Promise<unknown>

  // 方法实现
  async executeQuery(
    sessionId: string,
    query: QueryType,
    params: QueryParams = {}
  ): Promise<unknown> {
    const session = this.sessions.get(sessionId)
    const startTime = Date.now()

    if (!session) {
      const error = new Error(`Session ${sessionId} not found`)
      this.logger.error('Session not found for query', { sessionId, query })
      throw error
    }

    const { agent, page } = session
    const extendedAgent = agent
    session.lastActivity = Date.now()

    this.logger.info('Executing query', { sessionId, query, params })

    try {
      let result: unknown

      switch (query) {
        case 'aiAssert':
          await agent.aiAssert(params.assertion!, params.errorMsg, params.options)
          result = { success: true, assertion: params.assertion }
          break

        case 'aiAsk':
          result = await extendedAgent.aiAsk(params.prompt!, params.options)
          break

        case 'aiQuery':
          result = await agent.aiQuery(params.dataDemand!, params.options)
          break

        case 'aiBoolean':
          result = await extendedAgent.aiBoolean(params.prompt!, params.options)
          break

        case 'aiNumber':
          result = await extendedAgent.aiNumber(params.prompt!, params.options)
          break

        case 'aiString':
          result = await extendedAgent.aiString(params.prompt!, params.options)
          break

        case 'aiLocate':
          result = await extendedAgent.aiLocate(params.locate!, params.options)
          break

        case 'location': {
          const url = page.url()
          result = {
            url,
            title: await page.title(),
            path: new URL(url).pathname
          } as LocationResult
          break
        }

        case 'getTabs': {
          const browser = page.context().browser()
          if (!browser) {
            throw new Error('Browser not found')
          }
          const pages = browser.contexts()[0]?.pages() || []
          result = pages.map((p, index) => ({
            id: index,
            url: p.url(),
            title: p.title()
          })) as TabInfo[]
          break
        }

        default:
          throw new Error(`Unknown query: ${query}`)
      }

      const duration = Date.now() - startTime
      this.logger.info('Query completed', { sessionId, query, duration })

      return result

    } catch (error) {
      const err = error as Error
      const duration = Date.now() - startTime
      this.logger.error('Query failed', {
        sessionId,
        query,
        error: err.message,
        duration
      })

      throw new Error(`Query failed: ${err.message}`)
    }
  }

  /**
   * 销毁会话
   */
  async destroySession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId)
    if (session) {
      try {
        // 关闭 agent
        const {agent} = session
        if (agent && typeof agent.destroy === 'function') {
          await agent.destroy()
        }

        // 关闭浏览器
        if (session.browser && typeof session.browser.close === 'function') {
          await session.browser.close()
        }

        this.logger.info('Session destroyed', { sessionId })
      } catch (error) {
        const err = error as Error
        this.logger.error('Error destroying session', {
          sessionId,
          error: err.message,
          stack: err.stack
        })
      } finally {
        this.sessions.delete(sessionId)
        this.actionHistory.delete(sessionId)
      }
    }
  }

  /**
   * 获取活跃会话列表
   */
  getActiveSessions(): SessionInfo[] {
    return Array.from(this.sessions.keys()).map(sessionId => {
      const session = this.sessions.get(sessionId)!
      return {
        sessionId,
        createdAt: session.createdAt,
        lastActivity: session.lastActivity,
        state: session.state
      }
    })
  }

  /**
   * 获取会话历史
   */
  getSessionHistory(sessionId: string): ActionRecord[] {
    return this.actionHistory.get(sessionId) || []
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<HealthCheckResult> {
    const activeSessions = this.sessions.size
    const totalActions = Array.from(this.actionHistory.values())
      .reduce((sum, history) => sum + history.length, 0)

    return {
      status: 'healthy',
      activeSessions,
      totalActions,
      uptime: process.uptime(),
      memory: process.memoryUsage()
    }
  }

  /**
   * 优雅关闭
   */
  async shutdown(): Promise<void> {
    this.logger.info('Shutting down orchestrator...')

    const destroyPromises = Array.from(this.sessions.keys())
      .map(sessionId => this.destroySession(sessionId))

    await Promise.all(destroyPromises)

    this.logger.info('Orchestrator shutdown complete')
  }
}
