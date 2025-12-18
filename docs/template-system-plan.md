# Midscene Agent 操作模板/宏系统实现计划

## 项目概述

为 Midscene Agent 添加操作模板/宏系统，解决生产环境中通用操作（如登录）的重复编写问题。系统将支持：
- 预定义常用操作模板（登录、搜索等）
- 简化的调用语法（自然语言 + YAML）
- 参数化模板支持
- 智能上下文管理

## 实现路径

### 阶段 1: 基础框架（预计 1-2 天）

#### 1.1 创建模板模块结构
**新增文件：**
- `runner/template/__init__.py` - 模板模块初始化
- `runner/template/engine.py` - 模板解析和展开引擎
- `runner/template/context.py` - 上下文管理系统
- `runner/template/registry.py` - 模板注册和检索
- `runner/template/exceptions.py` - 模板相关异常
- `runner/template/types.py` - 模板类型定义

#### 1.2 实现核心类
**TemplateRegistry 类：**
- 扫描和注册模板
- 模板分类管理
- 模板查找和加载

**TemplateEngine 类：**
- 模板解析
- 参数替换（${param} 语法）
- 步骤展开

**ContextManager 类：**
- 全局上下文管理
- 会话上下文管理
- 上下文继承机制

#### 1.3 创建示例模板
**新增文件：**
- `runner/templates/__init__.py`
- `runner/templates/registry.yaml`
- `runner/templates/.templates/login/basic.yaml` - 基础登录模板
- `runner/templates/.templates/search/simple.yaml` - 简单搜索模板
- `runner/templates/.templates/common/screenshot.yaml` - 截图模板

### 阶段 2: 核心功能（预计 2-3 天）

#### 2.1 扩展执行器
**修改文件：**
- `runner/executor/text_executor.py` - 自然语言测试执行器
  - 添加模板调用解析（支持 "使用模板 xxx 进行 xxx" 语法）
  - 集成模板引擎
  - 支持模板参数传递

- `runner/executor/yaml_executor.py` - YAML测试执行器
  - 添加 `template:` 操作类型支持
  - 模板参数和上下文支持

#### 2.2 实现参数替换机制
**功能：**
- `${param}` - 参数引用
- `${context.key}` - 上下文变量引用
- `${default_value}` - 默认值支持
- 类型转换和验证

#### 2.3 集成到 Agent
**修改文件：**
- `runner/agent/agent.py`
  - 添加模板引擎初始化
  - 支持模板调用
  - 上下文传递

### 阶段 3: 高级特性（预计 1-2 天）

#### 3.1 条件执行
**功能：**
- 模板中的条件步骤
- 基于上下文的条件判断
- 模板嵌套调用

#### 3.2 模板优化
- 模板编译缓存
- 性能优化
- 错误处理增强

#### 3.3 文档和示例
**新增文件：**
- `docs/templates.md` - 模板系统使用指南
- `docs/examples.md` - 使用示例
- 更新 `README.md` - 添加模板系统说明

## 调用语法示例

### 自然语言格式
```txt
@web:
  url: https://example.com
  headless: false

@task: 用户登录测试

1. 使用模板 login.basic 进行登录
   参数: username="testuser", password="testpass"
2. 验证登录成功
3. 截取登录后的页面截图
```

### YAML格式
```yaml
tasks:
  - name: 用户登录测试
    flow:
      - template:
          name: "login.basic"
          parameters:
            username: "testuser"
            password: "testpass"
      - aiAssert: "验证登录成功"
      - logScreenshot: "登录结果"
```

## 关键文件清单

### 新增文件
1. `runner/template/__init__.py`
2. `runner/template/engine.py`
3. `runner/template/context.py`
4. `runner/template/registry.py`
5. `runner/template/exceptions.py`
6. `runner/template/types.py`
7. `runner/templates/__init__.py`
8. `runner/templates/registry.yaml`
9. `runner/templates/.templates/login/basic.yaml`
10. `runner/templates/.templates/search/simple.yaml`
11. `runner/templates/.templates/common/screenshot.yaml`
12. `docs/templates.md`
13. `docs/examples.md`

### 修改文件
1. `runner/executor/text_executor.py`
2. `runner/executor/yaml_executor.py`
3. `runner/agent/agent.py`
4. `README.md`

## 里程碑

- [ ] 阶段 1 完成：基础框架和示例模板
- [ ] 阶段 2 完成：核心功能和执行器集成
- [ ] 阶段 3 完成：高级特性和文档
- [ ] 测试验证：创建综合测试用例
- [ ] 文档完善：编写完整使用指南

## 技术要点

1. **向后兼容**：不破坏现有测试格式
2. **性能优化**：模板缓存和预编译
3. **错误处理**：详细的错误信息和调试支持
4. **可扩展性**：支持用户自定义模板
5. **类型安全**：参数类型验证和转换

## 风险和缓解

| 风险 | 缓解措施 |
|------|----------|
| 参数替换复杂度 | 使用正则表达式和模板引擎 |
| 性能影响 | 实现模板缓存机制 |
| 错误传播 | 添加详细日志和调试信息 |
| 向后兼容 | 保持现有API不变，新增功能作为扩展 |

## 成功标准

1. ✅ 能够创建和调用登录模板
2. ✅ 支持参数化模板调用
3. ✅ 自然语言调用语法正常工作
4. ✅ YAML格式模板调用正常工作
5. ✅ 上下文管理系统正常工作
6. ✅ 模板缓存和性能优化生效
7. ✅ 文档和示例完整

---

**开始实施时间：** 2025-12-10
**预计完成时间：** 2025-12-15
**实际实施时间：** 根据用户反馈调整
