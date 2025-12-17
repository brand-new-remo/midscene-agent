# UV 迁移方案详细计划

## 项目概述

**项目名称**: Midscene Agent  
**当前状态**: 基于 runner/ 子目录的 Python 包  
**迁移目标**: 使用 UV 包管理器，项目根目录运行模式  
**迁移范围**: Python 代码、配置文件、命令执行方式

---

## 当前状态分析

### 1. 目录结构
```
/e/code/midscene-agent/
├── runner/                      # 当前 Python 代码位置
│   ├── run.py                   # 交互式启动器
│   ├── check_config.py          # 配置检查工具
│   ├── executor/
│   │   ├── yaml_executor.py     # YAML 测试执行器
│   │   └── text_executor.py     # 自然语言测试执行器
│   ├── modes/
│   │   ├── yaml_mode.py         # YAML 测试模式
│   │   ├── text_mode.py         # 自然语言测试模式
│   │   └── custom_mode.py       # 自定义任务模式
│   ├── agent/
│   │   ├── __init__.py          # 使用相对导入
│   │   ├── agent.py
│   │   ├── config.py
│   │   └── http_client.py
│   ├── utils/
│   │   └── path_utils.py
│   ├── requirements.txt         # Python 依赖
│   └── .env                     # 环境变量
├── graph/
│   ├── langgraph.json          # LangGraph 配置（使用绝对路径）
│   ├── langgraph_cli.py        # CLI 入口
│   └── cli_adapter.py          # 导入 runner 模块
└── ...
```

### 2. 依赖关系
- **requirements.txt** 包含 10+ 依赖包
- **.env** 文件包含 DEEPSEEK 配置
- **langgraph.json** 指向硬编码绝对路径

### 3. 导入关系分析

**内部导入模式**:
1. **run.py**: 
   - `sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))`
   - `from check_config import check_config`
   - `from modes import yaml_mode, text_mode, custom_mode`

2. **executor/*.py**:
   - `runner_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))`
   - `sys.path.insert(0, runner_dir)`
   - `from agent.agent import MidsceneAgent`
   - `from template.engine import TemplateEngine`

3. **modes/*.py**:
   - `from utils.path_utils import get_tests_dir`

4. **cli_adapter.py** (在 graph/ 目录):
   - `from runner.agent.http_client import SessionConfig`
   - `from runner.agent.config import Config`
   - `from runner.agent.agent import MidsceneAgent`

**外部依赖**:
- LangGraph, LangChain
- aiohttp
- pydantic
- python-dotenv
- asyncio-throttle

---

## 迁移目标

1. 项目根目录管理: 所有依赖文件放到 /e/code/midscene-agent/
2. 命令从根执行: uv run python ... 从根目录执行
3. 保持包结构: runner/ 目录保持现有结构
4. 路径兼容性: 所有导入路径正常工作
5. LangGraph支持: 保持 LangGraph CLI 和绝对路径配置

