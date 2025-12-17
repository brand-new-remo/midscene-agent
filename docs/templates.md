# Midscene Agent 操作模板系统

## 目录

1. [系统概述](#1-系统概述)
2. [快速开始](#2-快速开始)
3. [核心概念](#3-核心概念)
4. [使用示例](#4-使用示例)
5. [模板定义](#5-模板定义)
6. [上下文管理](#6-上下文管理)
7. [高级特性](#7-高级特性)
8. [API 参考](#8-api-参考)
9. [最佳实践](#9-最佳实践)
10. [故障排除](#10-故障排除)

---

## 1. 系统概述

### 1.1 什么是操作模板系统？

操作模板系统是 Midscene Agent 的一个强大功能，旨在简化生产环境中的通用网页自动化操作。它允许你：

- **预定义常用操作**：如登录、搜索、表单填写等
- **简化指令编写**：使用自然语言描述复杂操作流程
- **参数化执行**：通过参数自定义模板行为
- **上下文共享**：自动继承系统信息和用户状态
- **可复用性**：一个模板可用于多个测试用例

### 1.2 为什么需要模板系统？

在生产环境中，测试用例往往包含大量重复操作：

**❌ 没有模板系统的问题：**
```txt
@task: 用户登录测试

1. 导航到登录页面 https://example.com/login
2. 在用户名输入框中输入 "testuser"
3. 在密码输入框中输入 "testpass123"
4. 点击登录按钮
5. 等待页面跳转到主页
6. 验证是否显示用户信息

@task: 管理员登录测试

1. 导航到登录页面 https://example.com/login
2. 在用户名输入框中输入 "admin"
3. 在密码输入框中输入 "admin123"
4. 点击登录按钮
5. 等待页面跳转到主页
6. 验证是否显示用户信息
```

**✅ 使用模板系统：**
```txt
@task: 用户登录测试

1. 使用模板 login.basic 进行登录
   参数: username="testuser", password="testpass123"
2. 验证登录成功

@task: 管理员登录测试

1. 使用模板 login.basic 进行登录
   参数: username="admin", password="admin123"
2. 验证登录成功
```

### 1.3 核心特性

- **🎯 简单易用**：自然语言调用，无需复杂配置
- **🔧 参数化**：支持动态参数传递和默认值
- **📊 上下文管理**：四级上下文继承机制
- **🔄 可嵌套**：模板可以调用其他模板
- **🎨 条件执行**：基于上下文的条件判断
- **📝 向后兼容**：不破坏现有测试格式
- **⚡ 高性能**：模板缓存和预编译
- **🛡️ 类型安全**：参数类型验证和转换

### 1.4 适用场景

- **登录认证**：标准化的登录流程
- **搜索操作**：通用搜索功能测试
- **表单填写**：标准表单提交流程
- **数据提取**：结构化数据获取
- **用户操作**：如添加、编辑、删除等
- **系统检查**：健康检查和状态验证

---

## 2. 快速开始

### 2.1 安装和配置

模板系统是 Midscene Agent 的内置功能，无需额外安装。确保项目结构如下：

```
runner/
├── templates/                 # 模板目录
│   ├── registry.yaml          # 模板注册表
│   └── .templates/            # 系统模板
│       ├── login/
│       ├── search/
│       └── common/
├── template/                  # 模板引擎核心
│   ├── engine.py
│   ├── context.py
│   ├── registry.py
│   └── ...
└── executor/
    └── text_executor.py       # 已支持模板调用
```

### 2.2 第一个模板调用

创建测试文件 `tests/texts/login_demo.txt`：

```txt
@web:
  url: https://example.com
  headless: false

@task: 用户登录演示

1. 使用模板 login.basic 进行登录
   参数: username="testuser", password="testpass123"
2. 验证登录成功
3. 截取登录后的页面截图
```

执行测试：

```bash
cd runner
python -m executor.text_executor ../../tests/texts/login_demo.txt
```

### 2.3 查看可用模板

```python
from template import TemplateRegistry

registry = TemplateRegistry("templates")
print("可用模板：", registry.list_templates())
print("模板分类：", registry.get_categories())
```

输出示例：
```
可用模板： ['common.screenshot', 'login.basic', 'search.simple']
模板分类： ['authentication', 'common', 'search']
```

---

## 3. 核心概念

### 3.1 模板生命周期

```
┌─────────────────────────────────────────────────────────────┐
│                     模板生命周期                              │
├─────────────────────────────────────────────────────────────┤
│                                                              │
│  1. 定义模板 ──→ 2. 注册模板 ──→ 3. 调用模板 ──→ 4. 展开模板 │
│      ↓              ↓              ↓              ↓           │
│  .yaml 文件      registry.yaml    测试用例      实际步骤      │
│                                                              │
│  5. 执行步骤 ──→ 6. 返回结果                               │
│      ↓              ↓                                       │
│  AI 操作       执行结果                                     │
└─────────────────────────────────────────────────────────────┘
```

### 3.2 关键组件

#### 3.2.1 TemplateEngine（模板引擎）

负责模板的解析、编译和展开。

```python
from template import TemplateEngine, TemplateRegistry, ContextManager

registry = TemplateRegistry("templates")
context_manager = ContextManager()
engine = TemplateEngine(registry, context_manager)
```

**主要功能：**
- 模板调用展开
- 参数替换
- 上下文注入
- 条件执行判断

#### 3.2.2 TemplateRegistry（模板注册表）

管理所有可用模板的注册和检索。

```python
registry = TemplateRegistry("templates")

# 获取模板
template = registry.get_template("login.basic")

# 列出模板
templates = registry.list_templates()
categories = registry.get_categories()
```

**主要功能：**
- 模板扫描和注册
- 分类和标签管理
- 模板查找和检索
- 版本控制

#### 3.2.3 ContextManager（上下文管理器）

管理多层级的上下文信息。

```python
context_manager = ContextManager()

# 设置全局上下文
context_manager.set_global("user.default_username", "testuser")

# 设置会话上下文
context_manager.set_session(session_id, "current_user", "john")

# 获取上下文（支持继承）
username = context_manager.get("user.default_username")
```

**四级上下文：**
1. **全局上下文** (`GLOBAL`) - 所有测试共享
2. **会话上下文** (`SESSION`) - 当前测试会话
3. **模板上下文** (`TEMPLATE`) - 当前模板执行
4. **步骤上下文** (`STEP`) - 当前步骤执行

### 3.3 模板调用流程

```
用户输入：
"使用模板 login.basic 进行登录 参数: username="test""

     ↓
步骤解析器识别模板调用

     ↓
TemplateEngine 获取模板定义

     ↓
验证参数和上下文

     ↓
展开模板步骤

     ↓
执行实际步骤

     ↓
返回结果
```

---

## 4. 使用示例

### 4.1 自然语言测试格式

#### 4.1.1 基础调用

```txt
# tests/texts/basic_login.txt
@web:
  url: https://example.com/login
  headless: false

@task: 用户登录测试

1. 使用模板 login.basic 进行登录
   参数: username="testuser", password="testpass123"
2. 验证登录成功
3. 截取登录结果截图
```

#### 4.1.2 简化调用

```txt
# tests/texts/simple_login.txt
@web:
  url: https://example.com

@task: 快速登录

1. 登录系统 (使用 testuser/testpass)
2. 检查是否显示用户信息
```

#### 4.1.3 混合调用

```txt
# tests/texts/mixed_operations.txt
@web:
  url: https://example.com
  headless: false

@task: 搜索功能测试

1. 登录系统 (使用 admin/admin123)
2. 搜索 "Python 教程"
   参数: keyword="Python 教程", result_count=5
3. 点击第一个搜索结果
4. 验证页面内容
5. 截图记录结果
```

### 4.2 YAML 测试格式

#### 4.2.1 显式参数

```yaml
# tests/yamls/login_test.yaml
web:
  url: https://example.com
  headless: false

tasks:
  - name: 用户登录测试
    flow:
      - template:
          name: "login.basic"
          parameters:
            username: "testuser"
            password: "testpass123"
            remember_me: true
      - aiAssert: "验证登录成功"
      - logScreenshot: "登录成功截图"
```

#### 4.2.2 隐式参数

```yaml
tasks:
  - name: 管理员登录
    flow:
      - template: "login.basic"
        context:
          username: "admin"
          password: "admin123"
      - aiAssert: "验证管理员权限"
```

#### 4.2.3 条件调用

```yaml
tasks:
  - name: 条件登录
    flow:
      - template:
          name: "login.with_otp"
          parameters:
            username: "user"
            password: "pass"
          condition: "needs_otp == true"
      - template: "login.basic"
        condition: "needs_otp == false"
```

### 4.3 完整测试用例示例

#### 4.3.1 电商网站测试

```txt
# tests/texts/ecommerce_test.txt
@web:
  url: https://shop.example.com
  headless: false

@task: 完整的购物流程测试

1. 登录系统 (使用 buyer/buyer123)
2. 搜索商品
   参数: keyword="iPhone 15", result_count=10
3. 点击第一个商品
4. 选择规格和数量
5. 添加到购物车
6. 进入购物车页面
7. 点击结算
8. 填写收货地址
9. 选择支付方式
10. 确认订单
11. 验证订单成功
12. 截图记录整个流程
```

#### 4.3.2 内容管理系统测试

```txt
# tests/texts/cms_test.txt
@web:
  url: https://cms.example.com/admin
  headless: false

@task: 文章管理功能测试

1. 登录系统 (使用 editor/editor123)
2. 进入文章管理页面
3. 点击"新建文章"
4. 填写文章标题和内容
5. 设置分类和标签
6. 发布文章
7. 验证文章显示
8. 编辑文章
9. 保存修改
10. 验证修改生效
11. 删除文章
12. 验证删除结果
```

---

## 5. 模板定义

### 5.1 模板文件结构

模板文件使用 YAML 格式，存储在 `templates/.templates/` 目录下：

```
templates/
└── .templates/
    ├── login/
    │   ├── basic.yaml          # 基础登录模板
    │   ├── with_otp.yaml       # 带OTP验证的登录
    │   └── with_captcha.yaml   # 带验证码的登录
    ├── search/
    │   ├── simple.yaml         # 简单搜索
    │   └── advanced.yaml       # 高级搜索
    └── common/
        ├── screenshot.yaml     # 截图模板
        └── wait_for_element.yaml
```

### 5.2 模板定义语法

```yaml
# 模板元数据
template:
  name: "模板名称"
  version: "1.0.0"
  description: "模板描述"
  category: "分类名称"
  tags: ["标签1", "标签2"]
  author: "作者"

  # 参数定义
  parameters:
    param_name:
      type: "string"              # 参数类型: string, number, boolean, url, selector
      required: true              # 是否必需
      description: "参数描述"      # 参数说明
      default: "默认值"           # 默认值
      choices: ["选项1", "选项2"]  # 可选值列表

  # 默认上下文
  context:
    key: "value"                  # 默认上下文变量
    selector: "CSS选择器"          # 默认选择器

  # 步骤定义
  steps:
    - id: "step1"                 # 步骤ID
      action: "ai"                # 操作类型
      params:                     # 步骤参数
        prompt: "操作描述"
      description: "步骤描述"      # 人类可读的描述
      condition: "条件表达式"      # 执行条件
      continue_on_error: false    # 错误时是否继续

  # 后置步骤（始终执行）
  post_steps:
    - action: "logScreenshot"
      params:
        title: "结果截图"

  # 条件步骤
  conditional_steps:
    - condition: "${param} == value"
      steps:
        - action: "aiTap"
          params:
            locate: "确认按钮"
```

### 5.3 参数类型

| 类型 | 描述 | 示例 |
|------|------|------|
| `string` | 字符串 | `"username"` |
| `number` | 数字 | `123` 或 `45.67` |
| `boolean` | 布尔值 | `true` 或 `false` |
| `url` | URL地址 | `"https://example.com/login"` |
| `selector` | CSS选择器 | `"input[name='username']"` |

### 5.4 参数替换语法

在模板步骤中，使用 `${param_name}` 引用参数：

```yaml
steps:
  - action: "aiInput"
    params:
      locate: "用户名输入框"
      value: "${username}"        # 引用 username 参数

  - action: "ai"
    params:
      prompt: "导航到 ${url}"       # 引用 url 参数
```

### 5.5 完整模板示例

#### 5.5.1 基础登录模板

```yaml
# templates/.templates/login/basic.yaml
template:
  name: "基础登录模板"
  version: "1.0.0"
  description: "标准用户名密码登录流程，支持错误处理和重试"
  category: "authentication"
  tags: ["login", "auth", "basic"]
  author: "system"

  parameters:
    username:
      type: "string"
      required: true
      description: "登录用户名"
      default: "${user.default_username}"
    password:
      type: "string"
      required: true
      description: "登录密码"
      default: "${user.default_password}"
    url:
      type: "url"
      required: false
      description: "登录页面URL"
      default: "${app.login_url}"
    remember_me:
      type: "boolean"
      required: false
      description: "是否记住登录状态"
      default: false

  context:
    username_selector: "input[name='username'], input[id='username']"
    password_selector: "input[name='password'], input[type='password']"
    submit_selector: "button[type='submit'], button:contains('登录')"
    error_selector: ".error, .alert-error"

  steps:
    - id: "navigate"
      action: "ai"
      params:
        prompt: "导航到登录页面 ${url}，等待页面完全加载"
      description: "导航到登录页面"

    - id: "input_username"
      action: "aiInput"
      params:
        locate: "用户名输入框"
        value: "${username}"
      description: "输入用户名"

    - id: "input_password"
      action: "aiInput"
      params:
        locate: "密码输入框"
        value: "${password}"
      description: "输入密码"

    - id: "remember_me"
      action: "aiTap"
      params:
        locate: "记住我选项"
      condition: "${remember_me} == true"
      description: "勾选记住我"

    - id: "click_submit"
      action: "aiTap"
      params:
        locate: "登录按钮"
      description: "点击登录按钮"

    - id: "wait_response"
      action: "aiWaitFor"
      params:
        assertion: "等待页面响应，检查是否跳转或显示错误"
        timeoutMs: 30000
      description: "等待登录响应"

    - id: "verify_result"
      action: "aiAssert"
      params:
        assertion: "检查是否登录成功"
      description: "验证登录结果"

  post_steps:
    - id: "screenshot"
      action: "logScreenshot"
      params:
        title: "登录${'成功' if last_assertion_success else '失败'}"
        content: "用户 ${username} 的登录结果"
```

#### 5.5.2 搜索模板

```yaml
# templates/.templates/search/simple.yaml
template:
  name: "简单搜索模板"
  version: "1.0.0"
  description: "通用网页搜索流程"
  category: "search"
  tags: ["search", "basic"]
  author: "system"

  parameters:
    keyword:
      type: "string"
      required: true
      description: "搜索关键词"
    search_url:
      type: "url"
      required: false
      description: "搜索页面URL"
      default: "${app.base_url}/search"
    result_count:
      type: "number"
      required: false
      description: "期望结果数量"
      default: 10

  context:
    search_selector: "input[name='q'], input[id='search']"
    submit_selector: "button[type='submit'], .search-btn"

  steps:
    - action: "ai"
      params:
        prompt: "导航到搜索页面 ${search_url}"
    - action: "aiInput"
      params:
        locate: "搜索框"
        value: "${keyword}"
    - action: "aiTap"
      params:
        locate: "搜索按钮"
    - action: "aiWaitFor"
      params:
        assertion: "等待搜索结果加载"
        timeoutMs: 30000
    - action: "aiQuery"
      params:
        name: "search_results"
        prompt: "提取前${result_count}个搜索结果"
    - action: "logScreenshot"
      params:
        title: "搜索结果 - ${keyword}"
```

---

## 6. 上下文管理

### 6.1 上下文类型

模板系统支持四级上下文，按优先级从高到低：

```
步骤上下文 (STEP)
    ↑
模板上下文 (TEMPLATE)
    ↑
会话上下文 (SESSION)
    ↑
全局上下文 (GLOBAL)
```

### 6.2 全局上下文

全局上下文在所有测试中共享，适合存储系统配置、默认用户信息等。

```python
from template import ContextManager

context_manager = ContextManager()

# 设置全局上下文
context_manager.set_global("system.name", "My Test System")
context_manager.set_global("user.default_username", "testuser")
context_manager.set_global("user.default_password", "testpass")
context_manager.set_global("app.base_url", "https://example.com")
context_manager.set_global("app.login_url", "https://example.com/login")

# 获取全局上下文
username = context_manager.get_global("user.default_username")
```

在模板中使用：
```yaml
context:
  username: "${user.default_username}"  # 从全局上下文获取
  login_url: "${app.login_url}"         # 从全局上下文获取
```

### 6.3 会话上下文

会话上下文存储当前测试会话的信息。

```python
# 设置会话上下文
context_manager.set_session(session_id, "current_user", "john_doe")
context_manager.set_session(session_id, "is_logged_in", True)

# 获取会话上下文
current_user = context_manager.get_session(session_id, "current_user")
```

### 6.4 上下文继承

上下文变量会按优先级继承，高优先级会覆盖低优先级：

```python
# 全局上下文
context_manager.set_global("color", "blue")

# 模板上下文
context_manager.set_template("color", "red")

# 步骤上下文
context_manager.set_step("color", "green")

# 获取时，优先返回步骤上下文的值
color = context_manager.get("color")  # 返回 "green"
```

### 6.5 变量替换

使用 `${variable}` 语法引用上下文变量：

```yaml
# 简单变量
"导航到 ${url}"

# 带默认值
"用户名: ${username:未设置}"

# 嵌套路径
"系统名称: ${system.name}"
"用户信息: ${user.name} (${user.email})"
```

---

## 7. 高级特性

### 7.1 条件执行

根据上下文条件决定是否执行某些步骤：

```yaml
conditional_steps:
  - condition: "${remember_me} == true"
    steps:
      - action: "aiTap"
        params:
          locate: "记住我选项"

  - condition: "${needs_otp} == true"
    steps:
      - action: "aiInput"
        params:
          locate: "验证码输入框"
          value: "${otp_code}"
```

### 7.2 模板嵌套调用

一个模板可以调用其他模板：

```yaml
steps:
  - action: "template"
    params:
      name: "login.basic"
      parameters:
        username: "${username}"
        password: "${password}"

  - action: "template"
    params:
      name: "search.simple"
      parameters:
        keyword: "${search_keyword}"
```

### 7.3 模板编译缓存

模板引擎会缓存编译后的模板，提高性能：

```python
engine = TemplateEngine(registry, context_manager)

# 查看缓存信息
cache_info = engine.get_cache_info()
print(cache_info)

# 清空缓存
engine.clear_cache()
```

### 7.4 错误处理

支持多种错误处理策略：

```yaml
steps:
  - id: "risky_operation"
    action: "aiTap"
    params:
      locate: "删除按钮"
    continue_on_error: true  # 错误时继续执行

  - id: "verify"
    action: "aiAssert"
    params:
      assertion: "确认删除成功"
    condition: "last_step_success == true"  # 仅在上一步成功时执行
```

### 7.5 自定义模板

创建自定义模板 `templates/user/my_template.yaml`：

```yaml
template:
  name: "我的自定义模板"
  version: "1.0.0"
  description: "自定义业务逻辑模板"
  category: "custom"
  tags: ["custom", "business"]
  author: "your_name"

  parameters:
    param1:
      type: "string"
      required: true
      description: "参数1"
    param2:
      type: "number"
      required: false
      description: "参数2"
      default: 10

  steps:
    - action: "ai"
      params:
        prompt: "执行自定义操作: ${param1}"
    - action: "aiAssert"
      params:
        assertion: "验证结果正确"
```

---

## 8. API 参考

### 8.1 TemplateEngine

#### 8.1.1 初始化

```python
from template import TemplateEngine, TemplateRegistry, ContextManager

registry = TemplateRegistry("templates")
context_manager = ContextManager()
engine = TemplateEngine(registry, context_manager)
```

#### 8.1.2 展开模板调用

```python
from template import TemplateCall

call = TemplateCall(
    name="login.basic",
    parameters={"username": "test", "password": "123"},
    context={}
)

expanded_steps = await engine.expand_template_call(call)

for step in expanded_steps:
    print(step)
```

### 8.2 TemplateRegistry

#### 8.2.1 获取模板

```python
# 根据名称获取
template = registry.get_template("login.basic")

# 列出所有模板
all_templates = registry.list_templates()

# 按分类过滤
login_templates = registry.get_templates_by_category("authentication")
```

#### 8.2.2 搜索模板

```python
# 搜索模板
results = registry.search_templates("login")
print(results)  # ['login.basic', 'login.with_otp']

# 按标签过滤
templates = registry.list_templates(tag="basic")
```

### 8.3 ContextManager

#### 8.3.1 设置上下文

```python
# 全局上下文
context_manager.set_global("key", "value")

# 会话上下文
context_manager.set_session(session_id, "key", "value")

# 模板上下文
context_manager.set_template("key", "value")

# 步骤上下文
context_manager.set_step("key", "value")
```

#### 8.3.2 获取上下文

```python
# 获取全局上下文
value = context_manager.get_global("key")

# 获取会话上下文
value = context_manager.get_session(session_id, "key")

# 获取任意上下文（支持继承）
value = context_manager.get("key")

# 检查是否存在
exists = context_manager.has("key")
```

#### 8.3.3 变量替换

```python
# 在文本中替换变量
text = "用户名: ${username}"
result = context_manager.substitute_variables(text)
# 结果: "用户名: testuser"
```

---

## 9. 最佳实践

### 9.1 模板设计原则

1. **单一职责**：每个模板只负责一个特定操作
2. **参数化**：将可变部分提取为参数
3. **可复用**：设计通用的模板，避免业务特定逻辑
4. **文档化**：为每个模板添加清晰的描述和注释

### 9.2 命名规范

- **模板名称**：使用 `分类.名称` 格式
  - ✅ `login.basic`
  - ✅ `search.advanced`
  - ✅ `common.screenshot`
  - ❌ `login`
  - ❌ `用户登录`

- **参数名称**：使用 snake_case
  - ✅ `username`, `password`, `search_keyword`
  - ❌ `userName`, `SearchKeyword`

- **步骤ID**：使用有意义的名称
  - ✅ `navigate`, `input_username`, `click_submit`
  - ❌ `step1`, `step2`, `action1`

### 9.3 参数设计

```yaml
# ✅ 好的参数设计
parameters:
  username:
    type: "string"
    required: true
    description: "登录用户名"
    default: "${user.default_username}"
  password:
    type: "string"
    required: true
    description: "登录密码"
  timeout:
    type: "number"
    required: false
    description: "操作超时时间（毫秒）"
    default: 30000
```

### 9.4 错误处理

```yaml
steps:
  - id: "risky_operation"
    action: "aiTap"
    params:
      locate: "删除按钮"
    continue_on_error: true  # 允许错误

  - id: "verify"
    action: "aiAssert"
    params:
      assertion: "确认操作成功"
    condition: "last_step_success == true"  # 条件执行

  - id: "cleanup"
    action: "ai"
    params:
      prompt: "清理操作"
    continue_on_error: true  # 始终执行清理
```

### 9.5 性能优化

1. **使用缓存**：模板引擎会缓存编译结果，避免重复解析
2. **合理分组**：将相关操作放在一个模板中，减少模板调用次数
3. **避免嵌套过深**：模板嵌套不超过 3 层
4. **重用上下文**：合理使用全局和会话上下文

```python
# 查看缓存统计
cache_info = engine.get_cache_info()
print(f"缓存命中率: {cache_info['hit_rate']}")
```

### 9.6 测试建议

1. **单元测试**：为复杂模板编写单元测试
2. **集成测试**：在真实环境中测试模板调用
3. **边界测试**：测试参数边界值和异常情况
4. **回归测试**：确保模板修改不影响现有测试

---

## 10. 故障排除

### 10.1 常见错误

#### 10.1.1 模板未找到

```
❌ TemplateNotFoundError: Template 'login.basic' not found
```

**解决方案：**
1. 检查模板名称是否正确
2. 确认模板文件存在于 `templates/.templates/` 目录
3. 检查 `registry.yaml` 是否包含该模板

```bash
# 查看可用模板
python -c "from template import TemplateRegistry; r = TemplateRegistry('templates'); print(r.list_templates())"
```

#### 10.1.2 参数验证失败

```
❌ TemplateValidationError: Required parameter 'username' is missing
```

**解决方案：**
1. 检查必需参数是否提供
2. 确认参数名称拼写正确
3. 查看模板定义的参数要求

```python
# 检查模板参数
template = registry.get_template("login.basic")
print(template.parameters)
```

#### 10.1.3 变量替换失败

```
❌ 未替换的变量: ${undefined_var}
```

**解决方案：**
1. 检查变量名是否正确
2. 确认上下文中有该变量
3. 使用默认值语法 `${var:default}`

```python
# 检查上下文
contexts = context_manager.get_all_contexts()
print(contexts)
```

### 10.2 调试技巧

#### 10.2.1 启用详细日志

```python
import logging
logging.basicConfig(level=logging.DEBUG)

# 现在会输出详细的调试信息
engine = TemplateEngine(registry, context_manager)
```

#### 10.2.2 查看模板展开结果

```python
from template import TemplateCall

call = TemplateCall(
    name="login.basic",
    parameters={"username": "test", "password": "123"}
)

expanded_steps = await engine.expand_template_call(call)

print("展开后的步骤:")
for i, step in enumerate(expanded_steps, 1):
    print(f"{i}. {step}")
```

#### 10.2.3 检查上下文状态

```python
# 查看所有上下文
contexts = context_manager.get_all_contexts()
for scope, vars in contexts.items():
    print(f"\n{scope}:")
    for key, value in vars.items():
        print(f"  {key}: {value}")
```

### 10.3 性能问题

#### 10.3.1 模板展开慢

**可能原因：**
- 模板嵌套过深
- 复杂的参数替换
- 缺少缓存

**解决方案：**
1. 减少模板嵌套层数
2. 使用缓存
3. 预编译常用模板

```python
# 清空并重建缓存
engine.clear_cache()

# 查看缓存统计
print(engine.get_cache_info())
```

#### 10.3.2 内存使用高

**可能原因：**
- 上下文变量过多
- 缓存过大
- 未及时清理

**解决方案：**
1. 定期清理不需要的上下文
2. 限制缓存大小
3. 使用会话上下文而非全局上下文

```python
# 清理上下文
context_manager.clear_scope(ContextScope.STEP)
context_manager.clear_scope(ContextScope.TEMPLATE)

# 清理缓存
engine.clear_cache()
```

### 10.4 兼容性

#### 10.4.1 旧版本测试文件

模板系统向后兼容，现有测试文件无需修改：

```txt
# 旧的测试文件仍然有效
1. 导航到 https://example.com
2. 点击登录按钮
3. 输入用户名和密码
```

#### 10.4.2 新旧格式混用

可以在同一个测试文件中混用新旧格式：

```txt
1. 使用模板 login.basic 进行登录
   参数: username="test", password="123"

2. 导航到用户页面

3. 使用模板 search.simple 搜索
   参数: keyword="产品"
```

---

## 结语

操作模板系统是 Midscene Agent 的强大功能，它能够：

- **简化测试编写**：通过预定义模板减少重复代码
- **提高可维护性**：集中管理通用操作逻辑
- **增强可复用性**：一个模板可用于多个测试
- **降低出错率**：标准化操作流程

通过合理使用模板系统，你可以显著提高测试用例的开发效率和可维护性。

如果在使用过程中遇到问题，请参考本文档的故障排除部分，或查看项目源码获取更多详细信息。

---

## 附录

### A. 内置模板列表

| 模板名称 | 分类 | 描述 | 标签 |
|----------|------|------|------|
| `login.basic` | authentication | 基础用户名密码登录 | login, auth, basic |
| `login.with_otp` | authentication | 带OTP验证的登录 | login, otp, 2fa |
| `search.simple` | search | 简单搜索模板 | search, basic |
| `common.screenshot` | common | 通用截图模板 | screenshot, debug |

### B. 完整示例项目

参考 `tests/texts/` 目录下的示例文件：
- `template_demo.txt` - 模板调用演示
- `login_with_template.txt` - 使用模板的登录测试
- `mixed_operations.txt` - 混合操作测试

### C. 相关资源

- [Midscene 官方文档](https://midscenejs.com)
- [LangGraph 文档](https://langchain-ai.github.io/langgraph/)
- [DeepSeek API 文档](https://platform.deepseek.com/docs)

---

**版本信息：** v1.0.0
**最后更新：** 2025-12-10
**作者：** Midscene Agent Team
