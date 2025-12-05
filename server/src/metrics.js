/**
 * 监控指标收集
 * 使用 prom-client 提供 Prometheus 指标
 */

const client = require('prom-client');

// 创建默认指标注册表
const register = new client.Registry();

// 添加默认指标
client.collectDefaultMetrics(register);

// 自定义指标
const actionCounter = new client.Counter({
  name: 'midscene_actions_total',
  help: 'Total number of actions executed',
  labelNames: ['action', 'status'],
  registers: [register]
});

const actionDuration = new client.Histogram({
  name: 'midscene_action_duration_seconds',
  help: 'Duration of action execution in seconds',
  labelNames: ['action'],
  buckets: [0.1, 0.5, 1, 2, 5, 10, 30, 60],
  registers: [register]
});

const sessionCounter = new client.Gauge({
  name: 'midscene_active_sessions',
  help: 'Number of active sessions',
  registers: [register]
});

const memoryUsage = new client.Gauge({
  name: 'midscene_memory_usage_bytes',
  help: 'Memory usage in bytes',
  labelNames: ['type'],
  registers: [register]
});

const requestCounter = new client.Counter({
  name: 'midscene_http_requests_total',
  help: 'Total number of HTTP requests',
  labelNames: ['method', 'route', 'status_code'],
  registers: [register]
});

const requestDuration = new client.Histogram({
  name: 'midscene_http_request_duration_seconds',
  help: 'HTTP request duration in seconds',
  labelNames: ['method', 'route'],
  buckets: [0.1, 0.5, 1, 2, 5, 10],
  registers: [register]
});

/**
 * 记录动作执行
 */
function incrementActionCounter(action, status) {
  actionCounter.inc({ action, status });
}

/**
 * 记录动作持续时间
 */
function observeActionDuration(action, duration) {
  actionDuration.observe({ action }, duration);
}

/**
 * 更新活跃会话数
 */
function setActiveSessions(count) {
  sessionCounter.set(count);
}

/**
 * 更新内存使用情况
 */
function updateMemoryUsage() {
  const memUsage = process.memoryUsage();
  memoryUsage.set({ type: 'rss' }, memUsage.rss);
  memoryUsage.set({ type: 'heapTotal' }, memUsage.heapTotal);
  memoryUsage.set({ type: 'heapUsed' }, memUsage.heapUsed);
  memoryUsage.set({ type: 'external' }, memUsage.external);
  memoryUsage.set({ type: 'arrayBuffers' }, memUsage.arrayBuffers);
}

/**
 * 记录 HTTP 请求
 */
function incrementRequestCounter(method, route, statusCode) {
  requestCounter.inc({ method, route, status_code: statusCode.toString() });
}

/**
 * 记录 HTTP 请求持续时间
 */
function observeRequestDuration(method, route, duration) {
  requestDuration.observe({ method, route }, duration);
}

/**
 * 获取所有指标
 */
async function getMetrics() {
  return await register.metrics();
}

/**
 * 获取指标注册表
 */
function getRegistry() {
  return register;
}

/**
 * 中间件：HTTP 请求监控
 */
function httpMetricsMiddleware() {
  return (req, res, next) => {
    const start = Date.now();

    res.on('finish', () => {
      const duration = (Date.now() - start) / 1000;
      const route = req.route ? req.route.path : req.path;

      incrementRequestCounter(req.method, route, res.statusCode);
      observeRequestDuration(req.method, route, duration);
    });

    next();
  };
}

/**
 * 定期更新系统指标
 */
function startMetricsCollection(orchestrator) {
  // 每 10 秒更新一次内存使用情况
  setInterval(() => {
    updateMemoryUsage();
    setActiveSessions(orchestrator.sessions.size);
  }, 10000);
}

module.exports = {
  registerMetrics: register,
  incrementActionCounter,
  observeActionDuration,
  setActiveSessions,
  updateMemoryUsage,
  incrementRequestCounter,
  observeRequestDuration,
  getMetrics,
  getRegistry,
  httpMetricsMiddleware,
  startMetricsCollection
};