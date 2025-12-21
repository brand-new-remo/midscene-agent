/**
 * 操作去重中间件
 * 用于防止相同操作在短时间内重复执行
 */

import winston from 'winston';
import type { ActionParams, ActionResult } from '../../types/action.js';

// 定义类型
export interface CachedAction {
  action: string;
  params: ActionParams;
  result: ActionResult;
  timestamp: number;
  duration: number;
}

export interface DeduplicationConfig {
  timeWindow: number; // 时间窗口（毫秒），默认5秒
  maxCacheSize: number; // 最大缓存大小，默认1000
  enableLogging: boolean; // 是否启用日志，默认true
}

/**
 * 操作去重器
 * 检查相同操作是否在时间窗口内重复执行
 */
export class ActionDeduplicator {
  private actionCache: Map<string, CachedAction> = new Map();

  private config: DeduplicationConfig;

  private logger: winston.Logger;

  constructor(logger: winston.Logger, config: Partial<DeduplicationConfig> = {}) {
    this.logger = logger;

    this.config = {
      timeWindow: 5000, // 5秒
      maxCacheSize: 1000,
      enableLogging: true,
      ...config,
    };

    // 使用默认logger或创建新的logger
    if (!logger) {
      this.logger = winston.createLogger({
        level: 'info',
        format: winston.format.combine(winston.format.timestamp(), winston.format.json()),
        transports: [new winston.transports.Console()],
      });
    }
  }

  /**
   * 生成操作缓存键
   */
  private static generateKey(action: string, params: ActionParams): string {
    // 使用JSON.stringify生成唯一键
    // 注意：这里假设参数是JSON可序列化的
    return `${action}:${JSON.stringify(params)}`;
  }

  /**
   * 检查是否应该执行操作
   * @param _sessionId 会话ID
   * @param action 操作类型
   * @param params 操作参数
   * @returns true表示应该执行，false表示应该跳过
   */
  shouldExecute(_sessionId: string, action: string, params: ActionParams): boolean {
    const key = ActionDeduplicator.generateKey(action, params);
    const cached = this.actionCache.get(key);

    // 如果没有缓存，执行操作
    if (!cached) {
      return true;
    }

    // 检查是否在时间窗口内
    const timeDiff = Date.now() - cached.timestamp;
    const shouldSkip = timeDiff <= this.config.timeWindow;

    if (shouldSkip && this.config.enableLogging) {
      this.logger.info('检测到重复操作，已跳过', {
        action,
        params,
        cachedTimestamp: cached.timestamp,
        timeDiff,
        timeWindow: this.config.timeWindow,
      });
    }

    return !shouldSkip;
  }

  /**
   * 记录操作结果
   * @param _sessionId 会话ID
   * @param action 操作类型
   * @param params 操作参数
   * @param result 操作结果
   */
  record(_sessionId: string, action: string, params: ActionParams, result: ActionResult): void {
    const key = ActionDeduplicator.generateKey(action, params);
    const cached: CachedAction = {
      action,
      params,
      result,
      timestamp: Date.now(),
      duration: result.duration || 0,
    };

    // 存储到缓存
    this.actionCache.set(key, cached);

    // 如果缓存超过最大大小，删除最旧的项
    if (this.actionCache.size > this.config.maxCacheSize) {
      const firstKey = this.actionCache.keys().next().value;
      if (firstKey !== undefined) {
        this.actionCache.delete(firstKey);
      }
    }

    if (this.config.enableLogging) {
      this.logger.debug('记录操作到缓存', {
        action,
        params,
        cacheSize: this.actionCache.size,
        key,
      });
    }
  }

  /**
   * 获取缓存的操作结果
   * @param _sessionId 会话ID
   * @param action 操作类型
   * @param params 操作参数
   * @returns 缓存的结果，如果没有则返回null
   */
  getCachedResult(_sessionId: string, action: string, params: ActionParams): ActionResult | null {
    const key = ActionDeduplicator.generateKey(action, params);
    const cached = this.actionCache.get(key);

    if (cached) {
      return cached.result;
    }

    return null;
  }

  /**
   * 清理过期的缓存项
   * @param _sessionId 可选，指定会话ID，只清理该会话的缓存
   */
  cleanExpired(_sessionId?: string): number {
    const now = Date.now();
    let cleanedCount = 0;

    Array.from(this.actionCache.entries()).forEach(([key, cached]) => {
      const timeDiff = now - cached.timestamp;

      // 清理超过时间窗口的缓存项
      if (timeDiff > this.config.timeWindow) {
        this.actionCache.delete(key);
        cleanedCount += 1;
      }
    });

    if (cleanedCount > 0 && this.config.enableLogging) {
      this.logger.info('清理过期缓存', {
        cleanedCount,
        remainingCacheSize: this.actionCache.size,
      });
    }

    return cleanedCount;
  }

  /**
   * 获取缓存统计信息
   */
  getStats(): {
    cacheSize: number;
    maxCacheSize: number;
    timeWindow: number;
    config: DeduplicationConfig;
  } {
    return {
      cacheSize: this.actionCache.size,
      maxCacheSize: this.config.maxCacheSize,
      timeWindow: this.config.timeWindow,
      config: { ...this.config },
    };
  }

  /**
   * 清空所有缓存
   */
  clear(): void {
    const { size } = this.actionCache;
    this.actionCache.clear();

    if (this.config.enableLogging && size > 0) {
      this.logger.info('清空去重缓存', { clearedCount: size });
    }
  }

  /**
   * 检查两个参数是否相似（用于更智能的去重）
   * @param params1 参数1
   * @param params2 参数2
   * @param similarityThreshold 相似度阈值（0-1）
   * @returns 相似度分数
   */
  static calculateSimilarity(
    params1: ActionParams,
    params2: ActionParams,
    similarityThreshold = 0.8
  ): number {
    const keys1 = Object.keys(params1).sort();
    const keys2 = Object.keys(params2).sort();

    // 如果键集合完全不同，相似度为0
    if (JSON.stringify(keys1) !== JSON.stringify(keys2)) {
      return 0;
    }

    let matchCount = 0;
    const totalKeys = keys1.length;

    keys1.forEach((key) => {
      const val1 = params1[key];
      const val2 = params2[key];

      // 如果值完全匹配
      if (JSON.stringify(val1) === JSON.stringify(val2)) {
        matchCount += 1;
      }
      // 如果是字符串，可以添加模糊匹配逻辑
      else if (typeof val1 === 'string' && typeof val2 === 'string') {
        const similarity = ActionDeduplicator.stringSimilarity(val1, val2);
        if (similarity >= similarityThreshold) {
          matchCount += similarity;
        }
      }
    });

    return totalKeys > 0 ? matchCount / totalKeys : 0;
  }

  /**
   * 计算两个字符串的相似度（简单的编辑距离）
   */
  private static stringSimilarity(str1: string, str2: string): number {
    const longer = str1.length > str2.length ? str1 : str2;
    const shorter = str1.length > str2.length ? str2 : str1;

    if (longer.length === 0) {
      return 1.0;
    }

    const editDistance = ActionDeduplicator.levenshteinDistance(longer, shorter);
    return (longer.length - editDistance) / longer.length;
  }

  /**
   * 计算编辑距离
   */
  private static levenshteinDistance(str1: string, str2: string): number {
    const matrix: number[][] = [];

    for (let i = 0; i <= str2.length; i += 1) {
      matrix[i] = [i];
    }

    for (let j = 0; j <= str1.length; j += 1) {
      matrix[0][j] = j;
    }

    for (let i = 1; i <= str2.length; i += 1) {
      for (let j = 1; j <= str1.length; j += 1) {
        if (str2.charAt(i - 1) === str1.charAt(j - 1)) {
          matrix[i][j] = matrix[i - 1][j - 1];
        } else {
          matrix[i][j] = Math.min(
            matrix[i - 1][j - 1] + 1, // substitution
            matrix[i][j - 1] + 1, // insertion
            matrix[i - 1][j] + 1 // deletion
          );
        }
      }
    }

    return matrix[str2.length][str1.length];
  }
}
