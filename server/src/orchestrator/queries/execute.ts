import type { QueryParams, QueryType } from '../types.js';
import type { Session } from '../types.js';
import winston from 'winston';
import { PlaywrightAgent } from '@midscene/web';
import type { Page } from 'playwright';

// aiAssert 查询处理
const handleAiAssert = async (
  agent: PlaywrightAgent,
  params: QueryParams
): Promise<{ success: true; assertion: string }> => {
  const { assertion } = params;
  if (!assertion) {
    throw new Error('aiAssert requires "assertion" parameter');
  }
  await agent.aiAssert(assertion, params.errorMsg, params.options);
  return { success: true, assertion };
};

// aiAsk 查询处理
const handleAiAsk = async (
  agent: PlaywrightAgent,
  params: QueryParams
): Promise<string | Record<string, unknown>> => {
  const { prompt } = params;
  if (!prompt) {
    throw new Error('aiAsk requires "prompt" parameter');
  }
  return agent.aiAsk(prompt, params.options);
};

// aiQuery 查询处理
const handleAiQuery = async (
  agent: PlaywrightAgent,
  params: QueryParams
): Promise<Record<string, unknown> | string> => {
  const { dataDemand } = params;
  if (!dataDemand) {
    throw new Error('aiQuery requires "dataDemand" parameter');
  }
  return agent.aiQuery(dataDemand, params.options);
};

// aiBoolean 查询处理
const handleAiBoolean = async (agent: PlaywrightAgent, params: QueryParams): Promise<boolean> => {
  const { prompt } = params;
  if (!prompt) {
    throw new Error('aiBoolean requires "prompt" parameter');
  }
  return agent.aiBoolean(prompt, params.options);
};

// aiNumber 查询处理
const handleAiNumber = async (agent: PlaywrightAgent, params: QueryParams): Promise<number> => {
  const { prompt } = params;
  if (!prompt) {
    throw new Error('aiNumber requires "prompt" parameter');
  }
  return agent.aiNumber(prompt, params.options);
};

// aiString 查询处理
const handleAiString = async (agent: PlaywrightAgent, params: QueryParams): Promise<string> => {
  const { prompt } = params;
  if (!prompt) {
    throw new Error('aiString requires "prompt" parameter');
  }
  return agent.aiString(prompt, params.options);
};

// aiLocate 查询处理
const handleAiLocate = async (
  agent: PlaywrightAgent,
  params: QueryParams
): Promise<{ x: number; y: number; width: number; height: number }> => {
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
};

// location 查询处理
const handleLocation = async (
  page: Page
): Promise<{ url: string; title: string; path: string }> => {
  const url = page.url();
  return {
    url,
    title: await page.title(),
    path: new URL(url).pathname,
  };
};

// getTabs 查询处理
const handleGetTabs = async (
  page: Page
): Promise<Array<{ id: number; url: string; title: string }>> => {
  const browser = page.context().browser();
  if (!browser) {
    throw new Error('Browser not found');
  }
  const pages = browser.contexts()[0]?.pages() || [];
  const tabPromises = pages.map(async (p, index) => ({
    id: index,
    url: p.url(),
    title: await p.title(),
  }));
  return Promise.all(tabPromises);
};

// getLogContent 查询处理
const handleGetLogContent = async (
  agent: PlaywrightAgent,
  params: QueryParams
): Promise<unknown> => {
  const { msgType, level } = params;
  return agent._unstableLogContent();
};

const processQuery = async (
  agent: PlaywrightAgent,
  page: Page,
  query: QueryType,
  params: QueryParams
): Promise<unknown> => {
  switch (query) {
    case 'aiAssert':
      return handleAiAssert(agent, params);

    case 'aiAsk':
      return handleAiAsk(agent, params);

    case 'aiQuery':
      return handleAiQuery(agent, params);

    case 'aiBoolean':
      return handleAiBoolean(agent, params);

    case 'aiNumber':
      return handleAiNumber(agent, params);

    case 'aiString':
      return handleAiString(agent, params);

    case 'aiLocate':
      return handleAiLocate(agent, params);

    case 'location':
      return handleLocation(page);

    case 'getTabs':
      return handleGetTabs(page);

    case 'getLogContent':
      return handleGetLogContent(agent, params);

    default:
      throw new Error(`Unknown query: ${query}`);
  }
};

export const executeQuery = async (
  sessions: Map<string, Session>,
  sessionId: string,
  query: QueryType,
  params: QueryParams,
  logger: winston.Logger
): Promise<unknown> => {
  const session = sessions.get(sessionId);
  const startTime = Date.now();

  if (!session) {
    const error = new Error(`Session ${sessionId} not found`);
    logger.error('Session not found for query', { sessionId, query });
    throw error;
  }

  const { agent, page } = session;
  session.lastActivity = Date.now();

  logger.info('Executing query', { sessionId, query, params });

  try {
    const result = await processQuery(agent, page, query, params);
    const duration = Date.now() - startTime;
    logger.info('Query completed', { sessionId, query, duration });

    return result;
  } catch (error) {
    const err = error as Error;
    const duration = Date.now() - startTime;
    logger.error('Query failed', {
      sessionId,
      query,
      error: err.message,
      duration,
    });

    throw new Error(`Query failed: ${err.message}`);
  }
};
