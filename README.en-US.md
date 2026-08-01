

# 🌸 Mori

> A virtual AI girlfriend Agent system based on AgentScope

[![Python Version](https://img.shields.io/badge/python-3.10%2B-blue.svg)](https://www.python.org/downloads/)
[![License](https://img.shields.io/badge/license-MIT-green.svg)](LICENSE)
[![AgentScope](https://img.shields.io/badge/AgentScope-1.0.8%2B-orange.svg)](https://github.com/modelscope/agentscope)
[![Code Style](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

---

## 📖 Project Overview

**Mori** is a virtual AI girlfriend Agent system built on the [AgentScope](https://github.com/modelscope/agentscope) framework. The project leverages existing AgentScope capabilities (Model, Agent, Tool, Memory, etc.) and focuses on implementing business logic and user experience.

### 🎯 Problems Solved

- **Emotional Companionship**: Provides users with a warm and caring virtual companionship experience
- **Personalized Interaction**: Remembers user preferences through long-term memory for personalized conversations
- **Flexible Extensibility**: Supports a multi-Agent collaboration architecture, allowing features to be extended as needed

### 💡 Core Value

- **Gentle & Caring Persona**: Mori exhibits a gentle, empathetic, and humorous personality
- **Persistent Memory**: Remembers user preferences, habits, and important information across sessions
- **Multi-Model Support**: Supports various LLMs including OpenAI, Tongyi Qianwen, DeepSeek, Ollama, etc.
- **Easy Customization**: Easily customize Agent personas and behaviors via the Jinja2 template system

---

## ✨ Features

### Core Features

- 🤖 **Multi-Agent Architecture**: Supports collaboration between primary and sub-Agents, with sub-Agents automatically registered as tools for the primary Agent
- 🧠 **Long-Term Memory**: Built on Mem0, supports cross-session memory of user preferences and important information
- 💬 **Streaming Chat**: Supports streaming output for a more natural conversational experience
- 🔧 **Tool Calling**: Supports custom tools and parallel tool execution
- 🌐 **MCP Protocol**: Reserved interface for Model Context Protocol integration

### Supported Models

| Model Type | Provider | Description |
|---------|--------|------|
| OpenAI | OpenAI | GPT-4, GPT-3.5-Turbo, etc. |
| DashScope | Alibaba Cloud | Tongyi Qianwen series |
| DeepSeek | DeepSeek | DeepSeek-Chat, etc. |
| Ollama | Local | Local models like Llama3, Qwen, etc. |
| Gemini | Google | Gemini series |

### Supported Embedding Models

- DashScope (text-embedding-v2/v3)
- OpenAI (text-embedding-3-small/large)
- Gemini (text-embedding-004)
- Ollama (nomic-embed-text, mxbai-embed-large)

---

## 🛠️ Tech Stack

| Category | Technology | Version |
|------|------|------|
| **Core Framework** | AgentScope | 1.0.8+ |
| **Template Engine** | Jinja2 | 3.1.0+ |
| **Config Validation** | Pydantic | 2.0+ |
| **GUI Framework** | Gradio | 4.0.0+ |
| **Long-Term Memory** | Mem0AI | 0.1.0+ |
| **HTTP Client** | httpx | 0.25.0+ |
| **Dependency Management** | uv | - |
| **Code Style** | black, ruff, pre-commit | - |
| **Python** | Python | 3.10+ |

---

## 🚀 Quick Start

### Prerequisites

- Python 3.10 or higher
- [uv](https://github.com/astral-sh/uv) package manager
- An LLM API key (OpenAI, DeepSeek, Tongyi Qianwen, etc.)

### Installation Steps

#### 1. Clone the Repository

```bash
git clone https://github.com/acgurl/mori.git
cd mori
```

#### 2. Create Virtual Environment & Install Dependencies

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装项目依赖
uv pip install -e .

# 安装开发依赖（可选）
uv pip install -e ".[dev]"
```

#### 3. Configuration Files

```bash
# Windows PowerShell:
Copy-Item config\models.yaml.example config\models.yaml
Copy-Item config\agents.yaml.example config\agents.yaml
Copy-Item config\config.yaml.example config\config.yaml

# Linux/Mac:
cp config/models.yaml.example config/models.yaml
cp config/agents.yaml.example config/agents.yaml
cp config/config.yaml.example config/config.yaml
```

#### 4. Set API Keys

```bash
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac:
export OPENAI_API_KEY="your-api-key-here"
```

#### 5. Run the Application

```bash
python gui/app.py
```

Then open your browser and visit: http://localhost:7860

---

## ⚙️ Configuration Guide

### Configuration File Structure

```
config/
├── models.yaml          # 模型配置
├── agents.yaml          # Agent 配置
├── config.yaml          # 全局配置
├── mcp.json             # MCP 配置（可选）
└── template/            # 自定义模板目录
    └── custom.jinja2    # 自定义提示词模板
```

### models.yaml - Model Configuration

```yaml
models:
  # OpenAI 配置
  main_gpt4:
    model_name: gpt-4
    model_type: openai
    api_key: ${OPENAI_API_KEY}  # 从环境变量读取
    generate_kwargs:
      temperature: 0.7
      max_tokens: 2000

  # DeepSeek 配置（OpenAI 兼容接口）
  deepseek_chat:
    model_name: deepseek-chat
    model_type: openai
    api_key: ${DEEPSEEK_API_KEY}
    base_url: https://api.deepseek.com/v1
    generate_kwargs:
      temperature: 0.7

  # 通义千问配置
  qwen_max:
    model_name: qwen-max
    model_type: dashscope
    api_key: ${DASHSCOPE_API_KEY}

  # Ollama 本地模型
  local_llama3:
    model_name: llama3
    model_type: ollama
    base_url: http://localhost:11434

# 嵌入模型配置（用于长期记忆）
embedding_models:
  dashscope_embedding:
    model_name: text-embedding-v2
    model_type: dashscope
    api_key: ${DASHSCOPE_API_KEY}
```

### agents.yaml - Agent Configuration

```yaml
# 指定主 Agent
primary_agent: mori

agents:
  # 主 Agent - 虚拟 AI 女友
 mori:
    model: main_gpt4           # 引用 models.yaml 中的配置
    template: mori             # 模板名称
    parallel_tool_calls: true
    memory_config:
      type: memory
      max_length: 100

    # 长期记忆配置
    long_term_memory:
      enabled: true
      mode: "agent_control"    # agent_control / static_control / both
      user_name: "user"
      embedding_model: "dashscope_embedding"
      storage_path: "data/memory/mori"
      on_disk: true
```

### config.yaml - Global Configuration

```yaml
global:
  log_level: INFO
  log_dir: logs

server:
  host: 127.0.0.1
  port: 7860
 share: false
```

### Environment Variables

| Variable Name | Description |
|--------|------|
| `OPENAI_API_KEY` | OpenAI API Key |
| `DASHSCOPE_API_KEY` | Alibaba Cloud DashScope API Key |
| `DEEPSEEK_API_KEY` | DeepSeek API Key |
| `GEMINI_API_KEY` | Google Gemini API Key |

---

## 📁 Project Structure

```
mori/
├── mori/                          # 核心模块
│   ├── __init__.py
│   ├── mori.py                    # Mori 核心封装类
│   ├── config.py                  # 配置加载和验证
│   ├── exceptions.py              # 自定义异常
│   │
│   ├── agent/                     # Agent 相关
│   │   ├── factory.py             # Agent 工厂
│   │   └── manager.py             # Agent 管理器
│   │
│   ├── model/                     # 模型相关
│   │   └── factory.py             # 模型工厂
│   │
│   ├── memory/                    # 记忆相关
│   │   └── factory.py             # 记忆工厂
│   │
│   ├── template/                  # 模板系统
│   │   ├── loader.py              # 模板加载器
│   │   ├── service.py             # 模板服务
│   │   └── internal_template/     # 内置模板
│   │       └── mori.jinja2        # Mori 提示词模板
│   │
│   ├── tool/                      # 工具系统
│   │   ├── factory.py             # 工具工厂
│   │   ├── agent_tools.py         # Agent 工具
│   │   └── internal_tools/        # 内置工具
│   │       └── example_tools.py   # 示例工具
│   │
│   ├── mcp/                       # MCP 集成（预留）
│   │   └── README.md
│   │
│   └── utils/                     # 工具函数
│       ├── model_wrapper.py       # 模型包装器
│       └── response.py            # 响应处理
│
├── gui/                           # GUI 界面
│   └── app.py                     # Gradio 应用
│
├── logger/                        # 日志系统
│   └── config.py                  # 日志配置
│
├── config/                        # 配置文件
│   ├── models.yaml.example        # 模型配置示例
│   ├── agents.yaml.example        # Agent 配置示例
│   ├── config.yaml.example        # 全局配置示例
│   └── template/                  # 自定义模板目录
│
├── tests/                         # 测试
│   ├── test_config.py
│   ├── test_template.py
│   └── ...
│
├── docs/                          # 文档
│   ├── ARCHITECTURE.md            # 架构设计
│   ├── QUICKSTART.md              # 快速开始
│   ├── LONG_TERM_MEMORY.md        # 长期记忆指南
│   └── ...
│
├── pyproject.toml                 # 项目配置
├── .pre-commit-config.yaml        # pre-commit 配置
├── LICENSE                        # MIT 许可证
└── README.md                      # 项目说明
```

---

## 📝 Usage Examples

### Basic Chat

```python
import asyncio
from mori.mori import Mori

async def main():
    # 初始化 Mori
    mori = Mori(config_dir="config")

    # 发送消息
    response = await mori.chat("你好，今天过得怎么样？")
    print(response)

    # 继续对话
    response = await mori.chat("我今天工作有点累")
    print(response)

    # 重置对话历史
    await mori.reset()

if __name__ == "__main__":
    asyncio.run(main())
```

### Using Long-Term Memory

```python
import asyncio
from mori.mori import Mori

async def memory_example():
    mori = Mori(config_dir="config")

    # 分享偏好（Agent 会自动记录）
    response = await mori.chat("我喜欢喝拿铁咖啡")
    print(response)

    # 清空短期记忆（模拟新会话）
    await mori.reset()

    # 询问偏好（Agent 会从长期记忆检索）
    response = await mori.chat("我喜欢喝什么咖啡？")
    print(response)

asyncio.run(memory_example())
```

### Multi-Agent Collaboration

```python
import asyncio
from mori.mori import Mori

async def multi_agent_example():
    mori = Mori(config_dir="config")

    # 主 Agent 会根据任务自动调用子 Agent
    response = await mori.chat("帮我写一首关于春天的诗")
    print(response)

    # 查看可用的 Agent
    print(f"可用 Agents: {mori.list_agents()}")
    print(f"主 Agent: {mori.get_primary_agent_name()}")

asyncio.run(multi_agent_example())
```

### Custom Templates

Create a custom template in the `config/template/` directory:

```jinja2
{# config/template/custom.jinja2 #}
你是一个专业的技术助手。

## 当前信息
{% if current_time %}
- **当前时间**: {{ current_time }}
{% endif %}

## 你的职责
- 回答技术问题
- 提供代码示例
- 解释技术概念

请用专业、清晰的语言回答用户的问题。
```

Then reference it in `agents.yaml`:

```yaml
agents:
  tech_assistant:
    model: main_gpt4
    template: custom  # 使用自定义模板
```

---

## 🧪 Development Guide

### Install Development Dependencies

```bash
uv pip install -e ".[dev]"
pre-commit install
```

### Run Tests

```bash
# 运行所有测试
pytest tests/

# 运行特定测试
pytest tests/test_config.py

# 带详细输出
pytest tests/ -v
```

### Code Style

```bash
# 运行所有检查
pre-commit run --all-files

# 格式化代码
black .

# 检查代码风格
ruff check .
```

### Adding Custom Tools

Create new tools in `mori/tool/internal_tools/`:

```python
from agentscope.tool import ToolResponse
from agentscope.message import TextBlock

async def my_custom_tool(param: str) -> ToolResponse:
    """我的自定义工具

    Args:
        param: 参数说明

    Returns:
        ToolResponse: 工具响应
    """
    result = f"处理结果: {param}"
    return ToolResponse(
        content=[TextBlock(type="text", text=result)]
    )

# 注册工具
def register_tools(toolkit):
    toolkit.register_tool_function(my_custom_tool)
```

---

## 🤝 Contribution Guide

We welcome contributions of all kinds!

### How to Contribute

1. **Fork** this repository
2. Create a feature branch (`git checkout -b feature/AmazingFeature`)
3. Commit your changes (`git commit -m 'Add some AmazingFeature'`)
4. Push to the branch (`git push origin feature/AmazingFeature`)
5. Create a **Pull Request**

### Contribution Guidelines

- Follow the existing code style (using black and ruff)
- Add tests for new features
- Update relevant documentation
- Write clear and descriptive commit messages

### Reporting Issues

If you find a bug or have a feature request, please submit it via [GitHub Issues](https://github.com/acgurl/mori/issues).

---

## 📄 License

This project is licensed under the [MIT License](LICENSE).

```
MIT License

Copyright (c) 2025 ACGURL

Permission is hereby granted, free of charge, to any person obtaining a copy
of this software and associated documentation files (the "Software"), to deal
in the Software without restriction, including without limitation the rights
to use, copy, modify, merge, publish, distribute, sublicense, and/or sell
copies of the Software, and to permit persons to whom the Software is
furnished to do so, subject to the following conditions:

The above copyright notice and this permission notice shall be included in all
copies or substantial portions of the Software.
```

---

## 🔗 Related Links

- **Project Repository**: [https://github.com/acgurl/mori](https://github.com/acgurl/mori)
- **Issue Tracking**: [GitHub Issues](https://github.com/acgurl/mori/issues)
- **AgentScope**: [https://github.com/modelscope/agentscope](https://github.com/modelscope/agentscope)
- **AgentScope Docs**: [https://doc.agentscope.io/](https://doc.agentscope.io/)

---

## 📚 More Documentation

- [Architecture Design](docs/ARCHITECTURE.md) - Detailed system architecture overview
- [Quick Start](docs/QUICKSTART.md) - 5-minute quick setup guide
- [Long-Term Memory Guide](docs/LONG_TERM_MEMORY.md) - In-depth guide to long-term memory features
- [Logging System](docs/LOGGING.md) - Logging configuration guide

---

<p align="center">
  Made with 💕 by <a href="https://github.com/acgurl">ACGURL</a>
</p>
