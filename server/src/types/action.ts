/**
 * @fileoverview Action 相关类型定义
 * @description 定义网页自动化动作的所有类型，包括动作类型、参数、结果和记录
 */

import type WebSocket from 'ws';

/**
 * 动作类型枚举
 * @description 所有支持的 Midscene 网页自动化动作类型
 */
export type ActionType =
  | 'navigate' /** 页面导航 - 打开指定 URL */
  | 'aiTap' /** AI 智能点击 - 基于 AI 理解点击目标 */
  | 'aiInput' /** AI 智能输入 - 基于 AI 理解输入框并输入文本 */
  | 'aiScroll' /** AI 智能滚动 - 基于 AI 理解页面结构进行滚动 */
  | 'aiKeyboardPress' /** AI 智能按键 - 基于 AI 理解目标位置按键盘 */
  | 'aiHover' /** AI 智能悬停 - 基于 AI 理解目标位置悬停鼠标 */
  | 'aiWaitFor' /** AI 智能等待 - 基于 AI 理解等待特定元素或状态 */
  | 'aiDoubleClick' /** AI 智能双击 - 基于 AI 理解目标位置双击 */
  | 'aiRightClick' /** AI 智能右键 - 基于 AI 理解目标位置右键点击 */
  | 'aiAction' /** AI 智能动作 - 执行自定义 AI 动作描述 */
  | 'setActiveTab' /** 切换标签页 - 激活指定索引的标签页 */
  | 'evaluateJavaScript' /** 执行 JavaScript - 在页面中执行 JS 代码 */
  | 'logScreenshot' /** 截图保存 - 截取当前页面并保存 */
  | 'freezePageContext' /** 冻结页面上下文 - 暂停页面交互 */
  | 'unfreezePageContext' /** 解冻页面上下文 - 恢复页面交互 */
  | 'runYaml' /** 运行 YAML 脚本 - 执行 Midscene YAML 脚本 */
  | 'setAIActionContext' /** 设置 AI 动作上下文 - 为后续 AI 动作设置上下文信息 */
  | 'recordToReport' /** 记录截图到报告 - 将当前截图记录到测试报告中 */
  | 'getLogContent'; /** 获取日志内容 - 获取页面控制台日志 */

/**
 * 动作参数接口
 * @description 定义各种动作类型的参数结构
 */
export interface ActionParams {
  // 页面导航参数
  /** 目标 URL 地址（navigate 动作必需） */
  url?: string;

  // 元素定位参数
  /** 目标元素的定位提示（aiTap, aiInput, aiScroll 等动作必需） */
  locate?: string;

  // 输入相关参数
  /** 要输入的文本内容（aiInput 动作必需） */
  value?: string;

  // 滚动相关参数
  /** 滚动参数对象，包含 direction、scrollType、distance 属性 */
  scrollParam?: {
    direction?: 'up' | 'down' | 'left' | 'right';
    scrollType?: 'singleAction' | 'scrollToBottom' | 'scrollToTop' | 'scrollToRight' | 'scrollToLeft';
    distance?: number | string | null;
  };
  /** 滚动方向：'up' | 'down' | 'left' | 'right'（向后兼容，建议使用 scrollParam） */
  direction?: 'up' | 'down' | 'left' | 'right';
  /** 滚动类型：'singleAction' | 'scrollToBottom' | 'scrollToTop' | 'scrollToRight' | 'scrollToLeft'（向后兼容，建议使用 scrollParam） */
  scrollType?: 'singleAction' | 'scrollToBottom' | 'scrollToTop' | 'scrollToRight' | 'scrollToLeft';
  /** 滚动距离（像素），设置为 null 表示由 AI 自动决定（向后兼容，建议使用 scrollParam） */
  distance?: number | string | null;

  // 键盘相关参数
  /** 要按下的键名或按键组合（如 'Enter', 'Tab', 'Control+C'） */
  key?: string;

  // 等待断言相关参数
  /** AI 断言描述（aiWaitFor 动作必需） */
  assertion?: string;
  /** 等待超时时间（毫秒，默认：15000） */
  timeoutMs?: number;
  /** 检查间隔时间（毫秒，默认：3000） */
  checkIntervalMs?: number;

  // 通用文本提示参数
  /** AI 动作或查询的文本提示（aiAction 动作必需） */
  prompt?: string;

  // 标签页相关参数
  /** 目标标签页索引（setActiveTab 动作必需） */
  tabId?: number;

  // JavaScript 执行参数
  /** 要执行的 JavaScript 代码字符串（evaluateJavaScript 动作必需） */
  script?: string;

  // 截图相关参数
  /** 截图标题或文件名（logScreenshot 动作可选） */
  title?: string;
  /** 截图描述信息 */
  content?: string;

  // YAML 脚本相关参数
  /** Midscene YAML 脚本内容（runYaml 动作必需） */
  yamlScript?: string;

  // AI 上下文相关参数
  /** 为后续 AI 动作设置的上下文信息 */
  context?: string;

  // 增强的交互参数
  /** 是否开启深度思考模式（对新一代模型收益不明显） */
  deepThink?: boolean;
  /** 目标元素的 xpath 路径，优先级：xpath > 缓存 > AI 模型 */
  xpath?: string;
  /** 是否允许缓存当前 API 调用结果 */
  cacheable?: boolean;

  // aiInput 特殊参数
  /** 键盘是否在输入文本后自动关闭（仅 Android/iOS 有效） */
  autoDismissKeyboard?: boolean;
  /** 输入模式：'replace'(先清空再输入) | 'clear'(仅清空) | 'append'(追加) */
  mode?: 'replace' | 'clear' | 'append';

  // 增强的查询参数
  /** 是否向模型发送精简后的 DOM 信息 */
  domIncluded?: boolean | 'visible-only';
  /** 是否向模型发送截图 */
  screenshotIncluded?: boolean;

  // 日志相关参数
  /** 日志类型过滤（如 'error', 'warn', 'info' 等） */
  msgType?: string;
  /** 日志级别过滤 */
  level?: string;

  // 通用选项参数
  /** 其他动作特定的选项配置 */
  options?: Record<string, unknown>;

  // 索引签名，允许任意属性
  [key: string]: unknown;
}

/**
 * 动作结果接口
 * @description 所有动作执行后的标准返回格式
 */
export interface ActionResult {
  /** 执行是否成功 */
  success: boolean;

  // 结果数据字段（可选）
  /** 执行的动作类型 */
  action?: string;
  /** 页面 URL（navigate 动作） */
  url?: string;
  /** 动作目标（如点击目标） */
  target?: string;
  /** 输入的文本值（aiInput 动作） */
  value?: string;
  /** 滚动方向 */
  direction?: string;
  /** 按下的按键 */
  key?: string;
  /** 等待的断言条件 */
  assertion?: string;
  /** 动作提示文本 */
  prompt?: string;
  /** 切换的标签页 ID */
  tabId?: number;
  /** JavaScript 执行结果或截图结果等 */
  result?: unknown;
  /** 截图标题 */
  title?: string;
  /** 截图描述信息 */
  content?: string;
  /** 设置的上下文信息 */
  context?: string;
  /** 日志类型过滤 */
  msgType?: string;
  /** 日志级别过滤 */
  level?: string;

  // 时间相关字段（用于去重和性能监控）
  /** 动作执行时间戳（Unix 毫秒时间戳） */
  timestamp?: number;
  /** 动作执行耗时（毫秒） */
  duration?: number;
}

/**
 * 动作记录接口
 * @description 用于记录会话中的动作执行历史
 */
export interface ActionRecord {
  /** 执行的动作类型 */
  action: string;

  /** 动作执行时的参数 */
  params: ActionParams;

  /** 动作执行结果（成功时） */
  result?: ActionResult;

  /** 动作执行错误信息（失败时） */
  error?: string;

  /** 动作执行耗时（毫秒） */
  duration: number;

  /** 动作执行时间戳（Unix 毫秒时间戳） */
  timestamp: number;
}

/**
 * 动作执行选项接口
 * @description 定义动作执行时的可选配置
 */
export interface ActionOptions {
  /** 是否启用流式响应（通过 WebSocket 实时推送进度） */
  stream?: boolean;

  /** WebSocket 连接实例（流式响应时必需） */
  websocket?: WebSocket;
}

/**
 * 滚动选项接口
 * @description 定义 AI 智能滚动动作的选项配置
 */
export interface ScrollOptions {
  /** 滚动方向 */
  direction?: 'up' | 'down' | 'left' | 'right';
  /** 滚动类型 */
  scrollType?: 'singleAction' | 'scrollToBottom' | 'scrollToTop' | 'scrollToRight' | 'scrollToLeft';
  /** 滚动距离（像素），设置为 null 表示由 AI 自动决定 */
  distance?: number | null;
}
