/**
 * Midscene Orchestrator
 *
 * 负责管理多个 Midscene PlaywrightAgent 会话，
 * 执行网页自动化动作，并提供查询功能。
 */
import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';

import { PlaywrightAgent } from '@midscene/web';
import { chromium, type Page } from 'playwright';
import { v4 as uuidv4 } from 'uuid';
import winston from 'winston';
import type {
  ActionOptions,
  ActionParams,
  ActionRecord,
  ActionResult,
  ActionType,
  HealthCheckResult,
  LocationResult,
  MidsceneConfig,
  OrchestratorInterface,
  QueryParams,
  QueryType,
  Session,
  SessionConfig,
  SessionInfo,
  TabInfo,
} from './types/index.js';
import type WebSocket from 'ws';

const filename = fileURLToPath(import.meta.url);
const dirname = path.dirname(filename);

class MidsceneOrchestrator implements OrchestratorInterface {
  sessions: Map<string, Session>;

  actionHistory: Map<string, ActionRecord[]>;

  logger: winston.Logger;

  constructor() {
    this.sessions = new Map();
    this.actionHistory = new Map();
    this.logger = winston.createLogger({
      level: 'info',
      format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
      transports: [
        new winston.transports.File({ filename: 'logs/error.log', level: 'error' }),
        new winston.transports.File({ filename: 'logs/combined.log' }),
        new winston.transports.Console({
          format: winston.format.simple(),
        }),
      ],
    });

    // 确保日志目录存在
    const logDir = path.join(dirname, '../logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
  }

  /**
   * 创建新的 Midscene 会话
   */
  async createSession(config: SessionConfig = {}): Promise<string> {
    const sessionId = uuidv4();
    const startTime = Date.now();

    this.logger.info('Creating new session', { sessionId, config });

    try {
      // 构建 Playwright 配置
      const playwrightConfig = {
        headless: config.headless !== false,
        viewport: {
          width: config.viewport_width || 1920,
          height: config.viewport_height || 1080,
        },
      };

      // 创建 Playwright 浏览器实例
      const browser = await chromium.launch({ headless: playwrightConfig.headless });

      // 创建新页面
      const page = await browser.newPage({
        viewport: playwrightConfig.viewport,
      });

      // 构建 Midscene 配置
      const midsceneConfig: MidsceneConfig = {
        model: config.model || process.env.MIDSCENE_MODEL_NAME || 'doubao-seed-1.6-vision',
        baseURL: config.baseURL || process.env.OPENAI_BASE_URL,
        apiKey: config.apiKey || process.env.OPENAI_API_KEY,
        waitForNetworkIdleTimeout: config.waitForNetworkIdleTimeout || 2000,
        actionTimeout: config.actionTimeout || 30000,
      };

      // 创建 PlaywrightAgent 实例
      const agent = new PlaywrightAgent(page, midsceneConfig);

      // 存储会话信息
      this.sessions.set(sessionId, {
        agent,
        browser,
        page, // 保存原始的 Playwright Page 引用
        config: midsceneConfig,
        state: 'ready',
        createdAt: Date.now(),
        lastActivity: Date.now(),
      });

      this.actionHistory.set(sessionId, []);

      this.logger.info('Session created successfully', {
        sessionId,
        duration: Date.now() - startTime,
      });

      return sessionId;
    } catch (error) {
      const err = error as Error;
      this.logger.error('Failed to create session', {
        sessionId,
        error: err.message,
        stack: err.stack,
      });

      throw new Error(`Failed to create session: ${err.message}`);
    }
  }

  /**
   * 验证会话是否存在
   */
  private validateSession(sessionId: string): Session {
    const session = this.sessions.get(sessionId);
    if (!session) {
      const error = new Error(`Session ${sessionId} not found`);
      this.logger.error('Session not found', { sessionId });
      throw error;
    }
    return session;
  }

  /**
   * 记录动作历史 - 使用配置对象减少参数
   */
  // eslint-disable-next-line max-params
  private recordActionHistory(config: {
    sessionId: string;
    action: ActionType;
    params: ActionParams;
    result: ActionResult | undefined;
    error: string | undefined;
    duration: number;
    timestamp: number;
  }): void {
    const { sessionId, action, params, result, error, duration, timestamp } = config;
    const actionRecord: ActionRecord = {
      action,
      params,
      result,
      error,
      duration,
      timestamp,
    };
    const history = this.actionHistory.get(sessionId);
    if (history) {
      history.push(actionRecord);
    }
  }

  /**
   * 执行动作并记录结果 - 使用配置对象减少参数
   */
  // eslint-disable-next-line max-params
  private async executeAndRecord(config: {
    sessionId: string;
    action: ActionType;
    params: ActionParams;
    startTime: number;
    executeFn: () => Promise<ActionResult>;
  }): Promise<ActionResult> {
    const { sessionId, action, params, startTime, executeFn } = config;
    const result = await executeFn();
    const duration = Date.now() - startTime;

    this.recordActionHistory({
      sessionId,
      action,
      params,
      result,
      error: undefined,
      duration,
      timestamp: startTime,
    });

    this.logger.info('Action completed', {
      sessionId,
      action,
      duration,
    });

    return result;
  }

  /**
   * 处理动作执行错误 - 使用配置对象减少参数
   */
  // eslint-disable-next-line max-params
  private handleActionError(config: {
    sessionId: string;
    action: ActionType;
    params: ActionParams;
    startTime: number;
    error: Error;
    options: ActionOptions;
  }): void {
    const { sessionId, action, params, startTime, error, options } = config;
    const duration = Date.now() - startTime;

    this.recordActionHistory({
      sessionId,
      action,
      params,
      result: undefined,
      error: error.message,
      duration,
      timestamp: startTime,
    });

    this.logger.error('Action failed', {
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
    const { agent, page } = session;
    const startTime = Date.now();

    session.lastActivity = Date.now();

    this.logger.info('Executing action', {
      sessionId,
      action,
      params: JSON.stringify(params),
    });

    try {
      // 支持流式响应
      if (options.stream && options.websocket) {
        return await this.executeActionWithProgress({
          agent,
          page,
          action,
          params,
          ws: options.websocket,
          sessionId,
        });
      }

      // 执行动作并记录结果
      return await this.executeAndRecord({
        sessionId,
        action,
        params,
        startTime,
        executeFn: () => this.executeActionDirect(agent, page, action, params),
      });
    } catch (error) {
      const err = error as Error;
      this.handleActionError({
        sessionId,
        action,
        params,
        startTime,
        error: err,
        options,
      });
      throw error;
    }
  }

  /**
   * 处理导航动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleNavigate(page: Page, params: ActionParams): Promise<ActionResult> {
    const { url } = params;
    if (!url) {
      throw new Error('navigate requires "url" parameter');
    }
    await page.goto(url, { waitUntil: 'networkidle' });
    return { success: true, url };
  }

  /**
   * 处理点击动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleTap(agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> {
    const { locate } = params;
    if (!locate) {
      throw new Error('aiTap requires "locate" parameter');
    }
    await agent.aiTap(locate, params.options);
    return { success: true, action: 'tap', target: locate };
  }

  /**
   * 处理输入动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleInput(agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> {
    const { locate } = params;
    const { value } = params;
    if (!locate) {
      throw new Error('aiInput requires "locate" parameter');
    }
    if (!value) {
      throw new Error('aiInput requires "value" parameter');
    }
    await agent.aiInput(locate, { ...params.options, value });
    return { success: true, action: 'input', value };
  }

  /**
   * 处理滚动动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleScroll(agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> {
    const { direction } = params;
    if (!direction) {
      throw new Error('aiScroll requires "direction" parameter');
    }
    await agent.aiScroll(params.locate, {
      direction,
      scrollType: params.scrollType || 'once',
      distance:
        typeof params.distance === 'string'
          ? parseInt(params.distance, 10)
          : params.distance || 500,
    });
    return { success: true, action: 'scroll', direction };
  }

  /**
   * 处理键盘按键动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleKeyboardPress(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const { key } = params;
    if (!key) {
      throw new Error('aiKeyboardPress requires "key" parameter');
    }
    await agent.aiKeyboardPress(key, params.locate, params.options);
    return { success: true, action: 'keypress', key };
  }

  /**
   * 处理悬停动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleHover(agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> {
    const { locate } = params;
    if (!locate) {
      throw new Error('aiHover requires "locate" parameter');
    }
    await agent.aiHover(locate, params.options);
    return { success: true, action: 'hover', target: locate };
  }

  /**
   * 处理等待动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleWaitFor(agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> {
    const { assertion } = params;
    if (!assertion) {
      throw new Error('aiWaitFor requires "assertion" parameter');
    }
    await agent.aiWaitFor(assertion, {
      timeoutMs: params.timeoutMs || 30000,
      checkIntervalMs: params.checkIntervalMs || 3000,
    });
    return { success: true, action: 'wait', assertion };
  }

  /**
   * 处理双击动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleDoubleClick(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const { locate } = params;
    if (!locate) {
      throw new Error('aiDoubleClick requires "locate" parameter');
    }
    await agent.aiDoubleClick(locate, params.options);
    return { success: true, action: 'doubleclick', target: locate };
  }

  /**
   * 处理右键点击动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleRightClick(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const { locate } = params;
    if (!locate) {
      throw new Error('aiRightClick requires "locate" parameter');
    }
    await agent.aiRightClick(locate, params.options);
    return { success: true, action: 'rightclick', target: locate };
  }

  /**
   * 处理 AI 动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiAction(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const { prompt } = params;
    if (!prompt) {
      throw new Error('aiAction requires "prompt" parameter');
    }
    await agent.aiAction(prompt);
    return { success: true, action: 'aiAction', prompt };
  }

  /**
   * 处理设置活动标签页动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleSetActiveTab(page: Page, params: ActionParams): Promise<ActionResult> {
    const { tabId } = params;
    if (tabId === undefined || tabId === null) {
      throw new Error('setActiveTab requires "tabId" parameter');
    }
    const browser = page.context().browser();
    if (!browser) {
      throw new Error('Browser not found');
    }
    const pages = browser.contexts()[0]?.pages() || [];
    const targetPage = pages[tabId];
    if (targetPage) {
      await targetPage.bringToFront();
      return { success: true, action: 'setActiveTab', tabId };
    }
    throw new Error(`Tab ${tabId} not found`);
  }

  /**
   * 处理执行 JavaScript 动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleEvaluateJavaScript(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const { script } = params;
    if (!script) {
      throw new Error('evaluateJavaScript requires "script" parameter');
    }
    const result = await agent.evaluateJavaScript(script);
    return { success: true, action: 'evaluateJavaScript', result };
  }

  /**
   * 处理截图动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleLogScreenshot(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const options =
      params.options && 'content' in params.options
        ? (params.options as { content: string })
        : undefined;
    const result = await agent.logScreenshot(params.title || 'screenshot', options);
    return {
      success: true,
      action: 'logScreenshot',
      title: params.title,
      result,
    };
  }

  /**
   * 处理运行 Yaml 动作
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleRunYaml(agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> {
    const { yamlScript } = params;
    if (!yamlScript) {
      throw new Error('runYaml requires "yamlScript" parameter');
    }
    const result = await agent.runYaml(yamlScript);
    return { success: true, action: 'runYaml', result };
  }

  /**
   * 处理设置 AI 动作上下文
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleSetAIActionContext(
    agent: PlaywrightAgent,
    params: ActionParams
  ): Promise<ActionResult> {
    const { context } = params;
    if (!context) {
      throw new Error('setAIActionContext requires "context" parameter');
    }
    await agent.setAIActionContext(context);
    return { success: true, action: 'setAIActionContext', context };
  }

  /**
   * 直接执行动作（无流式）
   */
  // eslint-disable-next-line complexity
  private async executeActionDirect(
    agent: PlaywrightAgent,
    page: Page,
    action: ActionType,
    params: ActionParams
  ): Promise<ActionResult> {
    switch (action) {
      case 'navigate':
        return this.handleNavigate(page, params);

      case 'aiTap':
        return this.handleTap(agent, params);

      case 'aiInput':
        return this.handleInput(agent, params);

      case 'aiScroll':
        return this.handleScroll(agent, params);

      case 'aiKeyboardPress':
        return this.handleKeyboardPress(agent, params);

      case 'aiHover':
        return this.handleHover(agent, params);

      case 'aiWaitFor':
        return this.handleWaitFor(agent, params);

      case 'aiDoubleClick':
        return this.handleDoubleClick(agent, params);

      case 'aiRightClick':
        return this.handleRightClick(agent, params);

      case 'aiAction':
        return this.handleAiAction(agent, params);

      case 'setActiveTab':
        return this.handleSetActiveTab(page, params);

      case 'evaluateJavaScript':
        return this.handleEvaluateJavaScript(agent, params);

      case 'logScreenshot':
        return this.handleLogScreenshot(agent, params);

      case 'freezePageContext':
        await agent.freezePageContext();
        return { success: true, action: 'freezePageContext' };

      case 'unfreezePageContext':
        await agent.unfreezePageContext();
        return { success: true, action: 'unfreezePageContext' };

      case 'runYaml':
        return this.handleRunYaml(agent, params);

      case 'setAIActionContext':
        return this.handleSetAIActionContext(agent, params);

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }

  /**
   * 带进度反馈的动作执行 - 使用配置对象减少参数
   */
  // eslint-disable-next-line max-lines-per-function
  private async executeActionWithProgress(config: {
    agent: PlaywrightAgent;
    page: Page;
    action: ActionType;
    params: ActionParams;
    ws: WebSocket;
    sessionId: string;
  }): Promise<ActionResult> {
    const { agent, page, action, params, ws, sessionId } = config;
    const startTime = Date.now();

    // 发送开始事件
    ws.send(
      JSON.stringify({
        type: 'action_start',
        sessionId,
        action,
        timestamp: startTime,
      })
    );

    try {
      // 执行动作
      const result = await this.executeActionDirect(agent, page, action, params);

      const duration = Date.now() - startTime;

      // 记录历史
      this.recordActionHistory({
        sessionId,
        action,
        params,
        result,
        error: undefined,
        duration,
        timestamp: startTime,
      });

      this.logger.info('Action completed', {
        sessionId,
        action,
        duration,
      });

      // 发送完成事件
      ws.send(
        JSON.stringify({
          type: 'action_complete',
          sessionId,
          action,
          result,
          timestamp: Date.now(),
        })
      );

      return result;
    } catch (error) {
      const err = error as Error;
      const duration = Date.now() - startTime;

      // 记录错误历史
      this.recordActionHistory({
        sessionId,
        action,
        params,
        result: undefined,
        error: err.message,
        duration,
        timestamp: startTime,
      });

      this.logger.error('Action failed', {
        sessionId,
        action,
        error: err.message,
        duration,
      });

      // 发送错误事件
      ws.send(
        JSON.stringify({
          type: 'action_error',
          sessionId,
          action,
          error: err.message,
          timestamp: Date.now(),
        })
      );

      throw error;
    }
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
    const session = this.sessions.get(sessionId);
    const startTime = Date.now();

    if (!session) {
      const error = new Error(`Session ${sessionId} not found`);
      this.logger.error('Session not found for query', { sessionId, query });
      throw error;
    }

    const { agent, page } = session;
    session.lastActivity = Date.now();

    this.logger.info('Executing query', { sessionId, query, params });

    try {
      const result = await this.processQuery(agent, page, query, params);
      const duration = Date.now() - startTime;
      this.logger.info('Query completed', { sessionId, query, duration });

      return result;
    } catch (error) {
      const err = error as Error;
      const duration = Date.now() - startTime;
      this.logger.error('Query failed', {
        sessionId,
        query,
        error: err.message,
        duration,
      });

      throw new Error(`Query failed: ${err.message}`);
    }
  }

  /**
   * 处理查询逻辑
   */
  private async processQuery(
    agent: PlaywrightAgent,
    page: Page,
    query: QueryType,
    params: QueryParams
  ): Promise<unknown> {
    switch (query) {
      case 'aiAssert':
        return this.handleAiAssert(agent, params);

      case 'aiAsk':
        return this.handleAiAsk(agent, params);

      case 'aiQuery':
        return this.handleAiQuery(agent, params);

      case 'aiBoolean':
        return this.handleAiBoolean(agent, params);

      case 'aiNumber':
        return this.handleAiNumber(agent, params);

      case 'aiString':
        return this.handleAiString(agent, params);

      case 'aiLocate':
        return this.handleAiLocate(agent, params);

      case 'location':
        return this.handleLocation(page);

      case 'getTabs':
        return this.handleGetTabs(page);

      default:
        throw new Error(`Unknown query: ${query}`);
    }
  }

  /**
   * 处理 aiAssert 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiAssert(
    agent: PlaywrightAgent,
    params: QueryParams
  ): Promise<{ success: true; assertion: string }> {
    const { assertion } = params;
    if (!assertion) {
      throw new Error('aiAssert requires "assertion" parameter');
    }
    await agent.aiAssert(assertion, params.errorMsg, params.options);
    return { success: true, assertion };
  }

  /**
   * 处理 aiAsk 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiAsk(
    agent: PlaywrightAgent,
    params: QueryParams
  ): Promise<string | Record<string, unknown>> {
    const { prompt } = params;
    if (!prompt) {
      throw new Error('aiAsk requires "prompt" parameter');
    }
    return agent.aiAsk(prompt, params.options);
  }

  /**
   * 处理 aiQuery 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiQuery(
    agent: PlaywrightAgent,
    params: QueryParams
  ): Promise<Record<string, unknown> | string> {
    const { dataDemand } = params;
    if (!dataDemand) {
      throw new Error('aiQuery requires "dataDemand" parameter');
    }
    return agent.aiQuery(dataDemand, params.options);
  }

  /**
   * 处理 aiBoolean 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiBoolean(agent: PlaywrightAgent, params: QueryParams): Promise<boolean> {
    const { prompt } = params;
    if (!prompt) {
      throw new Error('aiBoolean requires "prompt" parameter');
    }
    return agent.aiBoolean(prompt, params.options);
  }

  /**
   * 处理 aiNumber 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiNumber(agent: PlaywrightAgent, params: QueryParams): Promise<number> {
    const { prompt } = params;
    if (!prompt) {
      throw new Error('aiNumber requires "prompt" parameter');
    }
    return agent.aiNumber(prompt, params.options);
  }

  /**
   * 处理 aiString 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiString(agent: PlaywrightAgent, params: QueryParams): Promise<string> {
    const { prompt } = params;
    if (!prompt) {
      throw new Error('aiString requires "prompt" parameter');
    }
    return agent.aiString(prompt, params.options);
  }

  /**
   * 处理 aiLocate 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleAiLocate(
    agent: PlaywrightAgent,
    params: QueryParams
  ): Promise<{ x: number; y: number; width: number; height: number }> {
    const { locate } = params;
    if (!locate) {
      throw new Error('aiLocate requires "locate" parameter');
    }
    const result = await agent.aiLocate(locate, params.options);
    // 转换结果格式
    return {
      x: result.rect.left,
      y: result.rect.top,
      width: result.rect.width,
      height: result.rect.height,
    };
  }

  /**
   * 处理 location 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleLocation(page: Page): Promise<LocationResult> {
    const url = page.url();
    return {
      url,
      title: await page.title(),
      path: new URL(url).pathname,
    };
  }

  /**
   * 处理 getTabs 查询
   */
  // eslint-disable-next-line class-methods-use-this
  private async handleGetTabs(page: Page): Promise<TabInfo[]> {
    const browser = page.context().browser();
    if (!browser) {
      throw new Error('Browser not found');
    }
    const pages = browser.contexts()[0]?.pages() || [];
    return pages.map((p, index) => ({
      id: index,
      url: p.url(),
      title: p.title(),
    }));
  }

  /**
   * 销毁会话
   */
  async destroySession(sessionId: string): Promise<void> {
    const session = this.sessions.get(sessionId);
    if (session) {
      try {
        // 关闭 agent
        const { agent } = session;
        if (agent && typeof agent.destroy === 'function') {
          await agent.destroy();
        }

        // 关闭浏览器
        if (session.browser && typeof session.browser.close === 'function') {
          await session.browser.close();
        }

        this.logger.info('Session destroyed', { sessionId });
      } catch (error) {
        const err = error as Error;
        this.logger.error('Error destroying session', {
          sessionId,
          error: err.message,
          stack: err.stack,
        });
      } finally {
        this.sessions.delete(sessionId);
        this.actionHistory.delete(sessionId);
      }
    }
  }

  /**
   * 获取活跃会话列表
   */
  getActiveSessions(): SessionInfo[] {
    return Array.from(this.sessions.entries()).map(([sessionId, session]) => {
      return {
        sessionId,
        createdAt: session.createdAt,
        lastActivity: session.lastActivity,
        state: session.state as 'error' | 'ready' | 'busy',
      };
    });
  }

  /**
   * 获取会话历史
   */
  getSessionHistory(sessionId: string): ActionRecord[] {
    return this.actionHistory.get(sessionId) || [];
  }

  /**
   * 健康检查
   */
  async healthCheck(): Promise<HealthCheckResult> {
    const activeSessions = this.sessions.size;
    const totalActions = Array.from(this.actionHistory.values()).reduce(
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
  }

  /**
   * 优雅关闭
   */
  async shutdown(): Promise<void> {
    this.logger.info('Shutting down orchestrator...');

    const destroyPromises = Array.from(this.sessions.keys()).map((sessionId) =>
      this.destroySession(sessionId)
    );

    await Promise.all(destroyPromises);

    this.logger.info('Orchestrator shutdown complete');
  }
}

export default MidsceneOrchestrator;
