# XMind 转换工具

将 XMind 思维导图格式的测试用例转换为自然语言测试文件（.txt 格式）。

## 功能特点

- ✅ **XMind → 自然语言测试文件**：将 XMind 思维导图转换为 tests/texts/ 格式
- ✅ **模块化输出**：每个模块生成独立的 .txt 文件
- ✅ **占位符配置**：@web 配置使用占位符，便于后续填写
- ✅ **零依赖**：仅使用 Python 标准库
- ✅ **批量转换**：支持单个文件或目录批量转换

## 安装

本工具仅使用 Python 标准库，无需额外安装依赖：

```bash
# 确保 Python 版本 >= 3.7
python --version
```

## 使用方法

### 命令行接口

#### 转换单个 XMind 文件

```bash
python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/
```

#### 批量转换目录

```bash
python -m converter.cli -i xmind/ -o tests/texts/
```

#### 详细输出模式

```bash
python -m converter.cli -i xmind/V5.60测试用例.xmind -o tests/texts/ --verbose
```

### 命令行参数

- `-i, --input`：输入的 XMind 文件路径或目录（必需）
- `-o, --output`：输出目录路径（必需）
- `--verbose`：显示详细输出
- `--version`：显示版本信息

## 输入格式

### XMind 结构

```
根节点: 版本信息 (如: "V5.60测试用例")
└── 第1层: #模块名 (如: "#登录管理")
    └── 第2层: 用例名 (如: "交互验证")
        └── 第3层: 操作步骤 (多行，编号列表)
            └── 第4层: 验证步骤 (编号列表)
```

## 输出格式

### 生成的 .txt 文件格式

```txt
# 模块名

@web:
  url: https://example.com  # TODO: 请填写实际 URL
  headless: false
  viewportWidth: 1280
  viewportHeight: 768

@task: 用例名

1. 步骤内容
2. 步骤内容
3. 验证步骤

@task: 下一个用例名

...
```

## 示例

### 输入：XMind 文件结构

```
V5.60测试用例
└── #登录管理
    └── 交互验证
        ├── 操作步骤 (多行)
        │   1. 导航到 httpbin.org 首页
        │   2. 等待2秒钟让页面完全加载
        │   3. 截取一张 HTTPBin 首页的截图
        └── 验证步骤
            1. 验证页面是否正确显示了 API 端点信息
```

### 输出：tests/texts/登录管理.txt

```txt
# 登录管理

@web:
  url: https://example.com  # TODO: 请填写实际 URL
  headless: false
  viewportWidth: 1280
  viewportHeight: 768

@task: 交互验证

1. 导航到 httpbin.org 首页
2. 等待2秒钟让页面完全加载
3. 截取一张 HTTPBin 首页的截图
4. 验证页面是否正确显示了 API 端点信息

```

## 编程接口

```python
from pathlib import Path
from converter import XMindParser, TextGenerator

# 解析 XMind 文件
parser = XMindParser()
document = parser.parse_file(Path("V5.60测试用例.xmind"))

# 生成文本文件
generator = TextGenerator()
output_files = generator.generate(document, Path("tests/texts/"))
```

## 异常处理

工具提供完整的异常处理机制：

- `XMindParseError`：XMind 文件解析错误
- `ValidationError`：验证错误
- `FileNotFoundError`：文件未找到错误
- `BuildError`：构建文件错误

## 注意事项

1. **@web 配置**：生成的文本文件中 @web 配置使用占位符 `https://example.com`，请根据实际需要修改
2. **文件命名**：模块名中的特殊字符会被自动替换为下划线
3. **多模块**：每个模块会生成独立的 .txt 文件
4. **步骤合并**：操作步骤和验证步骤会合并为连续编号

## 许可证

MIT License

## 更新日志

### v1.0.0

- 初始版本
- 支持 XMind 转自然语言测试文件
- 支持单个文件和批量转换
- 零依赖设计
