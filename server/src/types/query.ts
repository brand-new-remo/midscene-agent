/**
 * @fileoverview Query 相关类型定义
 * @description 定义网页信息查询的所有类型，包括查询类型、参数和结果
 */

/**
 * 查询类型枚举
 * @description 所有支持的 Midscene 网页信息查询类型
 */
export type QueryType =
  | 'aiAssert' /** AI 智能断言 - 使用 AI 验证页面状态是否符合预期 */
  | 'aiAsk' /** AI 智能询问 - 使用 AI 回答关于页面的问题 */
  | 'aiQuery' /** AI 数据提取 - 使用 AI 从页面提取结构化数据 */
  | 'aiBoolean' /** AI 布尔查询 - 使用 AI 验证页面是否满足布尔条件 */
  | 'aiNumber' /** AI 数值查询 - 使用 AI 从页面提取数值信息 */
  | 'aiString' /** AI 文本查询 - 使用 AI 从页面  | 'ai提取文本信息 */
  | 'aiLocate' /** AI 元素定位 - 使用 AI 定位页面上的元素 */
  | 'location' /** 获取位置信息 - 获取当前页面 URL、标题和路径 */
  | 'getTabs'; /** 获取标签页列表 - 获取所有浏览器标签页信息 */

/**
 * 查询参数接口
 * @description 定义各种查询类型的参数结构
 */
export interface QueryParams {
  // 断言相关参数
  /** AI 断言描述（aiAssert 查询必需） */
  assertion?: string;
  /** 断言失败时的自定义错误消息 */
  errorMsg?: string;

  // 文本提示参数
  /** AI 查询的文本提示（aiAsk, aiBoolean, aiNumber, aiString, aiLocate 查询必需） */
  prompt?: string;

  // 数据提取参数
  /** 要提取的数据需求描述（aiQuery 查询必需） */
  dataDemand?: string | Record<string, string>;

  // 元素定位参数
  /** 目标元素的定位提示（aiLocate 查询必需） */
  locate?: string;

  // 通用选项参数
  /** 其他查询特定的选项配置 */
  options?: Record<string, unknown>;
}

/**
 * 页面位置信息结果接口
 * @description location 查询的返回结果
 */
export interface LocationResult {
  /** 当前页面的完整 URL */
  url: string;

  /** 当前页面的标题 */
  title: string;

  /** 当前页面的路径部分（不包含域名） */
  path: string;
}

/**
 * 标签页信息接口
 * @description getTabs 查询返回的单个标签页信息
 */
export interface TabInfo {
  /** 标签页在浏览器中的索引位置 */
  id: number;

  /** 标签页当前加载的 URL */
  url: string;

  /** 标签页的页面标题（可能是 Promise 异步获取） */
  title: string | Promise<string>;
}
