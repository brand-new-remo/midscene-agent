/**
 * Midscene Orchestrator
 *
 * 负责管理多个 Midscene PlaywrightAgent 会话，
 * 执行网页自动化动作，并提供查询功能。
 */

const { PlaywrightAgent } = require('@midscene/web');
const { v4: uuidv4 } = require('uuid');
const winston = require('winston');
const { registerMetrics, incrementActionCounter, observeActionDuration } = require('./metrics');
const { chromium } = require('playwright');

class MidsceneOrchestrator {
  constructor() {
    this.sessions = new Map(); // sessionId -> { agent, config, state, createdAt }
    this.actionHistory = new Map(); // 会话动作历史
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
    });

    // 确保日志目录存在
    const fs = require('fs');
    const path = require('path');
    const logDir = path.join(__dirname, '../logs');
    if (!fs.existsSync(logDir)) {
      fs.mkdirSync(logDir, { recursive: true });
    }
  }

  /**
   * 创建新的 Midscene 会话
   * @param {Object} config - 会话配置
   * @returns {Promise<string>} sessionId
   */
  async createSession(config = {}) {
    const sessionId = uuidv4();
    const startTime = Date.now();

    this.logger.info('Creating new session', { sessionId, config });

    try {
      // 构建 Playwright 配置
      const playwrightConfig = {
        headless: config.headless !== false,
        viewport: {
          width: config.viewport_width || 1920,
          height: config.viewport_height || 1080
        }
      };

      // 创建 Playwright 浏览器实例
      const browser = await chromium.launch(playwrightConfig);

      // 创建新页面
      const page = await browser.newPage();

      // 为页面添加popup事件监听器（兼容性修复）
      if (!page.on) {
        page.on = (event, _handler) => {
          // 简单的兼容性实现
          console.log(`Setting up listener for ${event}`);
        };
      }

      // 构建 Midscene 配置（不包含 Playwright 配置）
      const midsceneConfig = {
        model: config.model || process.env.MIDSCENE_MODEL_NAME || 'doubao-seed-1.6-vision',
        baseURL: config.baseURL || process.env.OPENAI_BASE_URL,
        apiKey: config.apiKey || process.env.OPENAI_API_KEY,
        waitForNetworkIdleTimeout: config.waitForNetworkIdleTimeout || 2000,
        actionTimeout: config.actionTimeout || 30000
      };

      // 创建 PlaywrightAgent 实例（传入页面）
      const agent = new PlaywrightAgent(page, midsceneConfig);

      // 存储会话信息
      this.sessions.set(sessionId, {
        agent,
        browser,  // 存储浏览器实例以便后续关闭
        config: midsceneConfig,
        state: 'ready',
        createdAt: Date.now(),
        lastActivity: Date.now()
      });

      this.actionHistory.set(sessionId, []);

      this.logger.info('Session created successfully', {
        sessionId,
        duration: Date.now() - startTime
      });

      incrementActionCounter('session_create', 'success');
      return sessionId;

    } catch (error) {
      this.logger.error('Failed to create session', {
        sessionId,
        error: error.message,
        stack: error.stack
      });

      incrementActionCounter('session_create', 'error');
      throw new Error(`Failed to create session: ${error.message}`);
    }
  }

  /**
   * 执行网页动作
   * @param {string} sessionId - 会话ID
   * @param {string} action - 动作类型
   * @param {Object} params - 动作参数
   * @param {Object} options - 选项
   * @returns {Promise<any>}
   */
  async executeAction(sessionId, action, params = {}, options = {}) {
    const session = this.sessions.get(sessionId);
    const startTime = Date.now();

    if (!session) {
      const error = new Error(`Session ${sessionId} not found`);
      this.logger.error('Session not found', { sessionId, action });
      incrementActionCounter('action', 'error');
      throw error;
    }

    const { agent } = session;
    session.lastActivity = Date.now();

    this.logger.info('Executing action', {
      sessionId,
      action,
      params: JSON.stringify(params)
    });

    try {
      let result;

      // 支持流式响应
      if (options.stream && options.websocket) {
        result = await this.executeActionWithProgress(
          agent, action, params, options.websocket, sessionId
        );
      } else {
        result = await this.executeActionDirect(agent, action, params);
      }

      const duration = Date.now() - startTime;

      // 记录历史
      const actionRecord = {
        action,
        params,
        result,
        duration,
        timestamp: startTime
      };
      this.actionHistory.get(sessionId).push(actionRecord);

      this.logger.info('Action completed', {
        sessionId,
        action,
        duration
      });

      incrementActionCounter(action, 'success');
      observeActionDuration(action, duration / 1000);

      return result;

    } catch (error) {
      const duration = Date.now() - startTime;

      // 记录错误历史
      const errorRecord = {
        action,
        params,
        error: error.message,
        duration,
        timestamp: startTime
      };
      this.actionHistory.get(sessionId).push(errorRecord);

      this.logger.error('Action failed', {
        sessionId,
        action,
        error: error.message,
        duration
      });

      incrementActionCounter(action, 'error');
      observeActionDuration(action, duration / 1000);

      if (options.stream && options.websocket) {
        options.websocket.send(JSON.stringify({
          type: 'action_error',
          sessionId,
          action,
          error: error.message,
          timestamp: Date.now()
        }));
      }

      throw error;
    }
  }

  /**
   * 直接执行动作（无流式）
   */
  async executeActionDirect(agent, action, params) {
    // 直接使用 Midscene 官方 API 名称，移除所有映射
    switch (action) {
      case 'navigate':
        await agent.interface.underlyingPage.goto(params.url, { waitUntil: 'networkidle' });
        return { success: true, url: params.url };

      case 'aiTap':
        await agent.aiTap(params.locate, params.options);
        return { success: true, action: 'tap', target: params.locate };

      case 'aiInput':
        await agent.aiInput(params.value, params.locate, params.options);
        return { success: true, action: 'input', value: params.value };

      case 'aiScroll':
        await agent.aiScroll({
          direction: params.direction,
          scrollType: params.scrollType || 'once',
          distance: params.distance || 500
        }, params.locate);
        return { success: true, action: 'scroll', direction: params.direction };

      case 'aiKeyboardPress':
        await agent.aiKeyboardPress(params.key, params.locate, params.options);
        return { success: true, action: 'keypress', key: params.key };

      case 'aiHover':
        await agent.aiHover(params.locate, params.options);
        return { success: true, action: 'hover', target: params.locate };

      case 'aiWaitFor':
        await agent.aiWaitFor(params.assertion, {
          timeoutMs: params.timeoutMs || 30000,
          checkIntervalMs: params.checkIntervalMs || 3000
        });
        return { success: true, action: 'wait', assertion: params.assertion };

      case 'aiDoubleClick':
        await agent.aiDoubleClick(params.locate, params.options);
        return { success: true, action: 'doubleclick', target: params.locate };

      case 'aiRightClick':
        await agent.aiRightClick(params.locate, params.options);
        return { success: true, action: 'rightclick', target: params.locate };

      case 'aiAction':
        await agent.aiAction(params.prompt, params.options);
        return { success: true, action: 'ai_action', prompt: params.prompt };

      case 'set_active_tab':
        const pages = agent.interface.underlyingPage.context().pages();
        const targetPage = pages[params.tabId];
        if (targetPage) {
          await targetPage.bringToFront();
          return { success: true, action: 'set_active_tab', tabId: params.tabId };
        } else {
          throw new Error(`Tab ${params.tabId} not found`);
        }

      case 'evaluate_javascript':
        result = await agent.evaluateJavaScript(params.script);
        return { success: true, action: 'evaluate_javascript', result };

      case 'log_screenshot':
        result = await agent.logScreenshot(params.title || 'screenshot', params.options || {});
        return { success: true, action: 'log_screenshot', title: params.title, result };

      case 'freeze_page_context':
        await agent.freezePageContext();
        return { success: true, action: 'freeze_page_context' };

      case 'unfreeze_page_context':
        await agent.unfreezePageContext();
        return { success: true, action: 'unfreeze_page_context' };

      case 'run_yaml':
        result = await agent.runYaml(params.yamlScript);
        return { success: true, action: 'run_yaml', result };

      case 'set_ai_action_context':
        agent.setAIActionContext(params.context);
        return { success: true, action: 'set_ai_action_context', context: params.context };

      default:
        throw new Error(`Unknown action: ${action}`);
    }
  }

  /**
   * 带进度反馈的动作执行
   */
  async executeActionWithProgress(agent, action, params, ws, sessionId) {
    return new Promise(async (resolve, reject) => {
      try {
        // 发送开始事件
        ws.send(JSON.stringify({
          type: 'action_start',
          sessionId,
          action,
          timestamp: Date.now()
        }));

        // 执行动作
        const result = await this.executeActionDirect(agent, action, params);

        // 发送完成事件
        ws.send(JSON.stringify({
          type: 'action_complete',
          sessionId,
          action,
          result,
          timestamp: Date.now()
        }));

        resolve(result);

      } catch (error) {
        // 发送错误事件
        ws.send(JSON.stringify({
          type: 'action_error',
          sessionId,
          action,
          error: error.message,
          timestamp: Date.now()
        }));

        reject(error);
      }
    });
  }

  /**
   * 查询页面信息
   * @param {string} sessionId - 会话ID
   * @param {string} query - 查询类型
   * @param {Object} params - 查询参数
   * @returns {Promise<any>}
   */
  async executeQuery(sessionId, query, params = {}) {
    const session = this.sessions.get(sessionId);
    const startTime = Date.now();

    if (!session) {
      const error = new Error(`Session ${sessionId} not found`);
      this.logger.error('Session not found for query', { sessionId, query });
      incrementActionCounter('query', 'error');
      throw error;
    }

    const { agent } = session;
    session.lastActivity = Date.now();

    this.logger.info('Executing query', { sessionId, query, params });

    try {
      let result;

      switch (query) {
        case 'aiAssert':
          await agent.aiAssert(params.assertion, params.errorMsg, params.options);
          result = { success: true, assertion: params.assertion };
          break;

        case 'location':
          result = await agent.aiLocate(params.locate, params.options);
          break;

        case 'screenshot':
          result = await agent.screenshot(params.name, params.fullPage);
          break;

        case 'get_tabs':
          // 使用 Playwright 的方法获取标签页
          const pages = agent.interface.underlyingPage.context().pages();
          result = pages.map((page, index) => ({
            id: index,
            url: page.url(),
            title: page.title()
          }));
          break;

        case 'get_screenshot':
          result = await agent.getScreenshot(params.name);
          break;

        case 'consoleLogs':
          result = await agent.getConsoleLogs(params.msgType);
          break;

        case 'aiQuery':
          result = await agent.aiQuery(params.dataDemand, params.options);
          break;

        case 'aiAsk':
          result = await agent.aiAsk(params.prompt, params.options);
          break;

        case 'aiBoolean':
          result = await agent.aiBoolean(params.prompt, params.options);
          break;

        case 'aiNumber':
          result = await agent.aiNumber(params.prompt, params.options);
          break;

        case 'aiString':
          result = await agent.aiString(params.prompt, params.options);
          break;

        default:
          throw new Error(`Unknown query: ${query}`);
      }

      const duration = Date.now() - startTime;
      this.logger.info('Query completed', { sessionId, query, duration });

      incrementActionCounter(`query_${query}`, 'success');
      observeActionDuration(`query_${query}`, duration / 1000);

      return result;

    } catch (error) {
      const duration = Date.now() - startTime;
      this.logger.error('Query failed', {
        sessionId,
        query,
        error: error.message,
        duration
      });

      incrementActionCounter(`query_${query}`, 'error');
      observeActionDuration(`query_${query}`, duration / 1000);

      throw new Error(`Query failed: ${error.message}`);
    }
  }

  /**
   * 截取屏幕截图
   */
  async takeScreenshot(sessionId, options = {}) {
    const session = this.sessions.get(sessionId);
    if (!session) {
      throw new Error(`Session ${sessionId} not found`);
    }

    return await session.agent.logScreenshot(options.title || 'screenshot', options);
  }

  /**
   * 销毁会话
   */
  async destroySession(sessionId) {
    const session = this.sessions.get(sessionId);
    if (session) {
      try {
        // 关闭 agent
        if (session.agent && typeof session.agent.close === 'function') {
          await session.agent.close();
        }

        // 关闭浏览器
        if (session.browser && typeof session.browser.close === 'function') {
          await session.browser.close();
        }

        this.logger.info('Session destroyed', { sessionId });
      } catch (error) {
        this.logger.error('Error destroying session', {
          sessionId,
          error: error.message,
          stack: error.stack
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
  getActiveSessions() {
    return Array.from(this.sessions.keys()).map(sessionId => {
      const session = this.sessions.get(sessionId);
      return {
        sessionId,
        createdAt: session.createdAt,
        lastActivity: session.lastActivity,
        state: session.state
      };
    });
  }

  /**
   * 获取会话历史
   */
  getSessionHistory(sessionId) {
    return this.actionHistory.get(sessionId) || [];
  }

  /**
   * 健康检查
   */
  async healthCheck() {
    const activeSessions = this.sessions.size;
    const totalActions = Array.from(this.actionHistory.values())
      .reduce((sum, history) => sum + history.length, 0);

    return {
      status: 'healthy',
      activeSessions,
      totalActions,
      uptime: process.uptime(),
      memory: process.memoryUsage()
    };
  }

  /**
   * 优雅关闭
   */
  async shutdown() {
    this.logger.info('Shutting down orchestrator...');

    const destroyPromises = Array.from(this.sessions.keys())
      .map(sessionId => this.destroySession(sessionId));

    await Promise.all(destroyPromises);

    this.logger.info('Orchestrator shutdown complete');
  }
}

module.exports = { MidsceneOrchestrator };