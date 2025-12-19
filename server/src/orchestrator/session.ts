import { PlaywrightAgent } from '@midscene/web';
import { chromium } from 'playwright';
import { v4 as uuidv4 } from 'uuid';
import winston from 'winston';
import type { MidsceneConfig, Session, SessionConfig, SessionInfo, ActionRecord } from './types.js';

/**
 * 构建 Playwright 浏览器配置
 * @param config 会话配置选项
 * @returns Playwright 浏览器配置对象
 * @description 根据会话配置生成 Playwright 浏览器的配置，包括：
 * - headless 模式设置（无头浏览器）
 * - 视口大小（宽度和高度）
 */
const buildPlaywrightConfig = (
  config: SessionConfig
): { headless: boolean; viewport: { width: number; height: number } } => {
  return {
    headless: config.headless !== false,
    viewport: {
      width: config.viewport_width || 1920,
      height: config.viewport_height || 1080,
    },
  };
};

/**
 * 构建 Midscene 配置
 * @param config 会话配置选项
 * @returns Midscene 配置对象
 * @description 生成 Midscene 所需的配置，包括：
 * - AI 模型名称
 * - API 基础 URL
 * - API 密钥
 * - 网络等待超时时间
 * - 动作执行超时时间
 */
const buildMidsceneConfig = (config: SessionConfig): MidsceneConfig => {
  return {
    model: config.model || process.env.MIDSCENE_MODEL_NAME || 'doubao-seed-1.6-vision',
    baseURL: config.baseURL || process.env.OPENAI_BASE_URL,
    apiKey: config.apiKey || process.env.OPENAI_API_KEY,
    waitForNetworkIdleTimeout: config.waitForNetworkIdleTimeout || 2000,
    actionTimeout: config.actionTimeout || 30000,
  };
};

/**
 * 创建新的 Midscene 会话
 * @param sessions 会话存储 Map
 * @param logger 日志记录器
 * @param config 会话配置选项
 * @returns 新创建会话的 ID
 * @description 创建一个新的浏览器会话，包括：
 * 1. 生成唯一会话 ID
 * 2. 启动 Playwright 浏览器
 * 3. 创建新的浏览器页面
 * 4. 初始化 Midscene PlaywrightAgent
 * 5. 将会话信息存储到 sessions Map 中
 * 6. 记录会话创建日志
 */
export const createSession = async (
  sessions: Map<string, Session>,
  logger: winston.Logger,
  config: SessionConfig = {}
): Promise<string> => {
  const sessionId = uuidv4();
  const startTime = Date.now();

  logger.info('Creating new session', { sessionId, config });

  try {
    // 构建 Playwright 配置
    const playwrightConfig = buildPlaywrightConfig(config);

    // 创建 Playwright 浏览器实例
    const browser = await chromium.launch({ headless: false });

    // 创建新页面
    const page = await browser.newPage({
      viewport: playwrightConfig.viewport,
    });

    // 构建 Midscene 配置
    const midsceneConfig = buildMidsceneConfig(config);

    // 创建 PlaywrightAgent 实例
    const agent = new PlaywrightAgent(page, midsceneConfig);

    // 存储会话信息
    sessions.set(sessionId, {
      agent,
      browser,
      page,
      config: midsceneConfig,
      state: 'ready',
      createdAt: Date.now(),
      lastActivity: Date.now(),
    });

    logger.info('Session created successfully', {
      sessionId,
      duration: Date.now() - startTime,
    });

    return sessionId;
  } catch (error) {
    const err = error as Error;
    logger.error('Failed to create session', {
      sessionId,
      error: err.message,
      stack: err.stack,
    });

    throw new Error(`Failed to create session: ${err.message}`);
  }
};

/**
 * 验证会话是否存在
 * @param sessions 会话存储 Map
 * @param sessionId 要验证的会话 ID
 * @param logger 日志记录器
 * @returns 验证通过的会话对象
 * @description 检查指定 ID 的会话是否存在，如果不存在则抛出异常
 */
export const validateSession = (
  sessions: Map<string, Session>,
  sessionId: string,
  logger: winston.Logger
): Session => {
  const session = sessions.get(sessionId);
  if (!session) {
    const error = new Error(`Session ${sessionId} not found`);
    logger.error('Session not found', { sessionId });
    throw error;
  }
  return session;
};

/**
 * 销毁会话
 * @param sessions 会话存储 Map
 * @param actionHistory 动作历史存储 Map
 * @param sessionId 要销毁的会话 ID
 * @param logger 日志记录器
 * @description 安全地关闭会话，包括：
 * 1. 销毁 PlaywrightAgent 实例
 * 2. 关闭浏览器实例
 * 3. 从 sessions Map 中删除会话
 * 4. 从 actionHistory Map 中删除历史记录
 * 5. 记录销毁日志
 */
export const destroySession = async (
  sessions: Map<string, Session>,
  actionHistory: Map<string, ActionRecord[]>,
  sessionId: string,
  logger: winston.Logger
): Promise<void> => {
  const session = sessions.get(sessionId);
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

      logger.info('Session destroyed', { sessionId });
    } catch (error) {
      const err = error as Error;
      logger.error('Error destroying session', {
        sessionId,
        error: err.message,
        stack: err.stack,
      });
    } finally {
      sessions.delete(sessionId);
      actionHistory.delete(sessionId);
    }
  }
};

/**
 * 获取所有活跃会话列表
 * @param sessions 会话存储 Map
 * @returns 活跃会话信息数组
 * @description 提取所有活跃会话的基本信息，包括：
 * - 会话 ID
 * - 创建时间
 * - 最后活动时间
 * - 当前状态
 */
export const getActiveSessions = (sessions: Map<string, Session>): SessionInfo[] => {
  return Array.from(sessions.entries()).map(([sessionId, session]) => {
    return {
      sessionId,
      createdAt: session.createdAt,
      lastActivity: session.lastActivity,
      state: session.state as 'error' | 'ready' | 'busy',
    };
  });
};
