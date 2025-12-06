import fs from 'fs';
import path from 'path';
import { fileURLToPath } from 'url';
import winston from 'winston';

/**
 * 初始化 Winston 日志记录器
 * @returns 配置好的 Winston Logger 实例
 * @description 创建并返回一个配置好的日志记录器，支持：
 * - 文件输出（错误日志和综合日志）
 * - 控制台输出
 * - 时间戳和 JSON 格式
 */
export const initializeLogger = (): winston.Logger => {
  return winston.createLogger({
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
};

/**
 * 确保日志目录存在
 * @description 检查 logs 目录是否存在，如果不存在则创建
 * 用于确保日志文件能够正常写入
 */
export const ensureLogDirectory = (): void => {
  const filename = fileURLToPath(import.meta.url);
  const dirname = path.dirname(filename);
  const logDir = path.join(dirname, '../logs');

  if (!fs.existsSync(logDir)) {
    fs.mkdirSync(logDir, { recursive: true });
  }
};
