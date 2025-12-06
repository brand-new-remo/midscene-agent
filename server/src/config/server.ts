/**
 * 服务器配置常量
 */

export const SERVER_CONFIG = {
  PORT: parseInt(process.env.PORT || '3000', 10),
  JSON_LIMIT: '10mb',
  GRACEFUL_SHUTDOWN_TIMEOUT: 10000, // 10 seconds
} as const;

export const WEBSOCKET_CONFIG = {
  HEARTBEAT_INTERVAL: 30000, // 30 seconds
  MAX_CONNECTIONS: 100,
} as const;

export const LOG_CONFIG = {
  ENABLED: true,
  LEVEL: process.env.LOG_LEVEL || 'info',
} as const;
