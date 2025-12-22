import type {
  ActionOptions,
  ActionParams,
  ActionResult,
  ActionType,
  ScrollOptions,
} from '../types.js';
import { handleActionError, executeAndRecord } from '../action-history.js';
import type { Session, ActionRecord } from '../types.js';
import type WebSocket from 'ws';
import winston from 'winston';
import { PlaywrightAgent } from '@midscene/web';
import type { Page } from 'playwright';

/**
 * 处理导航动作
 * @param page Playwright 页面对象
 * @param params 动作参数，包含 url
 * @returns 动作执行结果
 * @description 使用 Playwright 导航到指定的 URL，等待页面网络空闲状态
 */
const handleNavigate = async (page: Page, params: ActionParams): Promise<ActionResult> => {
  const { url } = params;
  if (!url) {
    throw new Error('navigate requires "url" parameter');
  }
  await page.goto(url, { waitUntil: 'networkidle' });
  return { success: true, url };
};

/**
 * 处理点击动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 locate（定位信息）
 * @returns 动作执行结果
 * @description 使用 AI 定位页面元素并进行点击操作
 */
const handleTap = async (agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> => {
  const { locate } = params;
  if (!locate) {
    throw new Error('aiTap requires "locate" parameter');
  }
  await agent.aiTap(locate, params.options);
  return { success: true, action: 'tap', target: locate };
};

/**
 * 处理输入动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 locate（定位信息）和 value（输入值）
 * @returns 动作执行结果
 * @description 使用 AI 定位输入框并输入指定文本
 */
const handleInput = async (agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> => {
  const { locate, value } = params;
  if (!locate) {
    throw new Error('aiInput requires "locate" parameter');
  }
  if (!value) {
    throw new Error('aiInput requires "value" parameter');
  }

  const inputOptions: any = { ...params.options, value };

  if (params.autoDismissKeyboard !== undefined) {
    inputOptions.autoDismissKeyboard = params.autoDismissKeyboard;
  }
  if (params.mode) {
    inputOptions.mode = params.mode;
  }

  await agent.aiInput(locate, inputOptions);
  return { success: true, action: 'input', value };
};

/**
 * 处理滚动动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 scrollParam（滚动参数对象）、locate（可选）
 * @returns 动作执行结果
 * @description 使用 AI 定位元素并进行滚动操作，支持指定方向和距离
 */
const handleScroll = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  // 处理 scrollParam，可能被 JSON.stringify 处理过
  let resolvedScrollParam: any;

  if (params.scrollParam) {
    // 如果 scrollParam 是字符串，尝试解析为对象
    if (typeof params.scrollParam === 'string') {
      try {
        resolvedScrollParam = JSON.parse(params.scrollParam);
      } catch (e) {
        throw new Error(`Invalid scrollParam JSON: ${params.scrollParam}`);
      }
    } else {
      resolvedScrollParam = params.scrollParam;
    }
  } else {
    // 兼容单独的参数（向后兼容）
    resolvedScrollParam = {
      direction: params.direction,
      scrollType: params.scrollType,
      distance: params.distance,
    };
  }

  const { direction, scrollType, distance } = resolvedScrollParam;

  if (!direction) {
    throw new Error('aiScroll requires "direction" parameter in scrollParam');
  }

  // v1.0.1 兼容性：scrollType 值变化
  const scrollTypeMap: Record<string, string> = {
    once: 'singleAction',
    untilBottom: 'scrollToBottom',
    untilTop: 'scrollToTop',
  };

  const mappedScrollType = scrollTypeMap[scrollType || 'once'] || 'singleAction';

  // 构建滚动选项对象
  const scrollOptions: ScrollOptions = {
    direction,
    scrollType: mappedScrollType as ScrollOptions['scrollType'],
    distance:
      typeof distance === 'string' ? parseInt(distance, 10) : (distance ?? 500),
  };

  // 根据官方文档，aiScroll(scrollParam, locate?, options?)
  await agent.aiScroll(scrollOptions, params.locate, params.options);
  return { success: true, action: 'scroll', direction };
};

/**
 * 处理键盘按键动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 key（按键名称）和 locate（可选，定位信息）
 * @returns 动作执行结果
 * @description 使用 AI 定位元素并执行键盘按键操作，支持特殊键如 Enter、Escape 等
 */
const handleKeyboardPress = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { key } = params;
  if (!key) {
    throw new Error('aiKeyboardPress requires "key" parameter');
  }
  await agent.aiKeyboardPress(key, params.locate, params.options);
  return { success: true, action: 'keypress', key };
};

/**
 * 处理悬停动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 locate（定位信息）
 * @returns 动作执行结果
 * @description 使用 AI 定位页面元素并将鼠标悬停在该元素上，触发 hover 事件
 */
const handleHover = async (agent: PlaywrightAgent, params: ActionParams): Promise<ActionResult> => {
  const { locate } = params;
  if (!locate) {
    throw new Error('aiHover requires "locate" parameter');
  }
  await agent.aiHover(locate, params.options);
  return { success: true, action: 'hover', target: locate };
};

/**
 * 处理等待动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 assertion（断言条件）、timeoutMs（超时时间）、checkIntervalMs（检查间隔）
 * @returns 动作执行结果
 * @description 使用 AI 等待页面满足指定的断言条件，常用于等待元素出现或状态变化
 */
const handleWaitFor = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { assertion } = params;
  if (!assertion) {
    throw new Error('aiWaitFor requires "assertion" parameter');
  }
  await agent.aiWaitFor(assertion, {
    timeoutMs: params.timeoutMs || 30000,
    checkIntervalMs: params.checkIntervalMs || 3000,
  });
  return { success: true, action: 'wait', assertion };
};

/**
 * 处理双击动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 locate（定位信息）
 * @returns 动作执行结果
 * @description 使用 AI 定位页面元素并进行双击操作
 */
const handleDoubleClick = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { locate } = params;
  if (!locate) {
    throw new Error('aiDoubleClick requires "locate" parameter');
  }
  await agent.aiDoubleClick(locate, params.options);
  return { success: true, action: 'doubleclick', target: locate };
};

/**
 * 处理右键点击动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 locate（定位信息）
 * @returns 动作执行结果
 * @description 使用 AI 定位页面元素并右键点击，通常用于打开上下文菜单
 */
const handleRightClick = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { locate } = params;
  if (!locate) {
    throw new Error('aiRightClick requires "locate" parameter');
  }
  await agent.aiRightClick(locate, params.options);
  return { success: true, action: 'rightclick', target: locate };
};

/**
 * 处理 AI 动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 prompt（AI 提示词）
 * @returns 动作执行结果
 * @description 使用 AI 自然语言指令执行复杂的网页操作，AI 会自主决策并执行相应动作
 */
const handleAiAction = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { prompt } = params;
  if (!prompt) {
    throw new Error('aiAction requires "prompt" parameter');
  }
  await agent.aiAction(prompt);
  return { success: true, action: 'aiAction', prompt };
};

/**
 * 处理设置活动标签页动作
 * @param page Playwright 页面对象
 * @param params 动作参数，包含 tabId（标签页 ID）
 * @returns 动作执行结果
 * @description 切换到指定 ID 的浏览器标签页，使其成为当前活动标签页
 */
const handleSetActiveTab = async (page: Page, params: ActionParams): Promise<ActionResult> => {
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
};

/**
 * 处理执行 JavaScript 动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 script（JavaScript 代码）
 * @returns 动作执行结果
 * @description 在浏览器上下文中执行自定义的 JavaScript 代码，并返回执行结果
 */
const handleEvaluateJavaScript = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { script } = params;
  if (!script) {
    throw new Error('evaluateJavaScript requires "script" parameter');
  }
  const result = await agent.evaluateJavaScript(script);
  return { success: true, action: 'evaluateJavaScript', result };
};

/**
 * 处理截图动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 title（截图标题）和 options（选项）
 * @returns 动作执行结果
 * @description 对当前页面进行截图，可指定截图标题和选项，截图结果会保存到日志中
 */
const handleLogScreenshot = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
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
};

/**
 * 处理运行 Yaml 动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 yamlScript（YAML 脚本内容）
 * @returns 动作执行结果
 * @description 执行预定义的 YAML 脚本，YAML 脚本包含一系列自动化步骤
 */
const handleRunYaml = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { yamlScript } = params;
  if (!yamlScript) {
    throw new Error('runYaml requires "yamlScript" parameter');
  }
  const result = await agent.runYaml(yamlScript);
  return { success: true, action: 'runYaml', result };
};

/**
 * 处理设置 AI 动作上下文
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 context（上下文信息）
 * @returns 动作执行结果
 * @description 为后续的 AI 动作设置上下文信息，帮助 AI 更好地理解当前页面状态
 */
const handleSetAIActionContext = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { context } = params;
  if (!context) {
    throw new Error('setAIActionContext requires "context" parameter');
  }
  await agent.setAIActionContext(context);
  return { success: true, action: 'setAIActionContext', context };
};

/**
 * 处理记录截图到报告动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 title（截图标题）和 content（截图描述）
 * @returns 动作执行结果
 * @description 将当前页面截图记录到测试报告中，可添加标题和描述信息
 */
const handleRecordToReport = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { title, content } = params;
  const result = await agent.recordToReport(title, content ? { content } : undefined);
  return {
    success: true,
    action: 'recordToReport',
    title: title || 'untitled',
    content,
    result,
  };
};

/**
 * 处理获取日志内容动作
 * @param agent PlaywrightAgent 实例
 * @param params 动作参数，包含 msgType（日志类型）和 level（日志级别）
 * @returns 动作执行结果
 * @description 获取页面的控制台日志内容，支持按类型和级别过滤
 */
const handleGetLogContent = async (
  agent: PlaywrightAgent,
  params: ActionParams
): Promise<ActionResult> => {
  const { msgType, level } = params;
  const result = agent._unstableLogContent();
  return {
    success: true,
    action: 'getLogContent',
    msgType,
    level,
    result,
  };
};

/**
 * 直接执行动作（无流式）
 * @param agent PlaywrightAgent 实例
 * @param page Playwright 页面对象
 * @param action 动作类型
 * @param params 动作参数
 * @returns 动作执行结果
 * @description 根据动作类型分发到对应的处理函数，支持所有类型的网页自动化动作
 */
const executeActionDirect = async (
  agent: PlaywrightAgent,
  page: Page,
  action: ActionType,
  params: ActionParams
): Promise<ActionResult> => {
  switch (action) {
    case 'navigate':
      return handleNavigate(page, params);

    case 'aiTap':
      return handleTap(agent, params);

    case 'aiInput':
      return handleInput(agent, params);

    case 'aiScroll':
      return handleScroll(agent, params);

    case 'aiKeyboardPress':
      return handleKeyboardPress(agent, params);

    case 'aiHover':
      return handleHover(agent, params);

    case 'aiWaitFor':
      return handleWaitFor(agent, params);

    case 'aiDoubleClick':
      return handleDoubleClick(agent, params);

    case 'aiRightClick':
      return handleRightClick(agent, params);

    case 'aiAction':
      return handleAiAction(agent, params);

    case 'setActiveTab':
      return handleSetActiveTab(page, params);

    case 'evaluateJavaScript':
      return handleEvaluateJavaScript(agent, params);

    case 'logScreenshot':
      return handleLogScreenshot(agent, params);

    case 'freezePageContext':
      await agent.freezePageContext();
      return { success: true, action: 'freezePageContext' };

    case 'unfreezePageContext':
      await agent.unfreezePageContext();
      return { success: true, action: 'unfreezePageContext' };

    case 'runYaml':
      return handleRunYaml(agent, params);

    case 'setAIActionContext':
      return handleSetAIActionContext(agent, params);

    case 'recordToReport':
      return handleRecordToReport(agent, params);

    case 'getLogContent':
      return handleGetLogContent(agent, params);

    default:
      throw new Error(`Unknown action: ${action}`);
  }
};

/**
 * 带进度反馈的动作执行
 * @param config 配置对象，包含 agent、page、action、params、ws、sessionId、actionHistory、logger
 * @returns 动作执行结果
 * @description 通过 WebSocket 实时推送动作执行进度，包括开始、完成和错误事件
 */
const executeActionWithProgress = async (config: {
  agent: PlaywrightAgent;
  page: Page;
  action: ActionType;
  params: ActionParams;
  ws: WebSocket;
  sessionId: string;
  actionHistory: Map<string, ActionRecord[]>;
  logger: winston.Logger;
}): Promise<ActionResult> => {
  const { agent, page, action, params, ws, sessionId, actionHistory, logger } = config;
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
    const result = await executeActionDirect(agent, page, action, params);

    const duration = Date.now() - startTime;

    // 记录历史
    const history = actionHistory.get(sessionId);
    if (history) {
      history.push({
        action,
        params,
        result,
        error: undefined,
        duration,
        timestamp: startTime,
      });
    }

    logger.info('Action completed', {
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
    const history = actionHistory.get(sessionId);
    if (history) {
      history.push({
        action,
        params,
        result: undefined,
        error: err.message,
        duration,
        timestamp: startTime,
      });
    }

    logger.error('Action failed', {
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
};

/**
 * 执行网页自动化动作
 * @param session 会话对象
 * @param sessionId 会话 ID
 * @param action 动作类型
 * @param params 动作参数
 * @param options 动作选项
 * @param actionHistory 动作历史存储 Map
 * @param logger 日志记录器
 * @returns 动作执行结果
 * @description 执行指定的网页自动化动作，支持流式和非流式两种模式：
 * - 流式模式：通过 WebSocket 实时推送执行进度
 * - 非流式模式：直接返回执行结果
 * 记录所有动作的执行历史和日志
 */
export const executeAction = async (
  session: Session,
  sessionId: string,
  action: ActionType,
  params: ActionParams,
  options: ActionOptions,
  actionHistory: Map<string, ActionRecord[]>,
  logger: winston.Logger
): Promise<ActionResult> => {
  const { agent, page } = session;
  const startTime = Date.now();

  logger.info('Executing action', {
    sessionId,
    action,
    params: JSON.stringify(params),
  });

  try {
    // 支持流式响应
    if (options.stream && options.websocket) {
      return await executeActionWithProgress({
        agent,
        page,
        action,
        params,
        ws: options.websocket,
        sessionId,
        actionHistory,
        logger,
      });
    }

    // 执行动作并记录结果
    return await executeAndRecord(actionHistory, logger, {
      sessionId,
      action,
      params,
      startTime,
      executeFn: () => executeActionDirect(agent, page, action, params),
    });
  } catch (error) {
    const err = error as Error;
    handleActionError(actionHistory, logger, {
      sessionId,
      action,
      params,
      startTime,
      error: err,
      options,
    });
    throw error;
  }
};
