# Mori - 虚拟AI女友 💕

基于AgentScope框架构建的虚拟AI女友agent系统，提供温暖的陪伴和情感支持。

## ✨ 特性

- 🤖 **基于AgentScope** - 充分利用AgentScope的强大功能
- 💬 **自然对话** - 温柔体贴的对话风格
- 🛠️ **工具支持** - 可以使用各种工具帮助你
- 🎨 **友好界面** - 基于Gradio的Web界面
- ⚙️ **灵活配置** - 支持多种LLM模型
- 📝 **模板化** - 使用Jinja2管理提示词

## 🚀 快速开始

### 1. 环境准备

```bash
# 克隆项目
git clone <your-repo-url>
cd moria

# 创建虚拟环境
uv venv
source .venv/bin/activate  # Windows: .venv\Scripts\activate

# 安装依赖
uv pip install -e .
```

### 2. 配置

```bash
# 复制配置文件示例
cp config/models.yaml.example config/models.yaml
cp config/agents.yaml.example config/agents.yaml
cp config/config.yaml.example config/config.yaml

# 编辑 config/models.yaml，填入你的API密钥
# 例如：将 ${OPENAI_API_KEY} 替换为你的实际密钥
# 或者设置环境变量：
export OPENAI_API_KEY="your-api-key-here"
```

### 3. 运行

```bash
# 启动Web界面
python gui/app.py

# 访问 http://localhost:7860
```

## 📁 项目结构

```
mori/
├── mori/                          # 核心模块
│   ├── mori.py                    # Mori核心类
│   ├── config.py                  # 配置管理
│   ├── template/                  # 模板系统
│   │   ├── loader.py              # Jinja2加载器
│   │   └── internal_template/     # 内置模板
│   │       └── mori.jinja2        # Mori提示词
│   ├── agent/                     # Agent工厂
│   │   └── factory.py
│   ├── tool/                      # 自定义工具
│   │   └── internal_tools/
│   │       └── example_tools.py
│   └── mcp/                       # MCP集成（预留）
├── gui/                           # GUI界面
│   └── app.py                     # Gradio应用
├── logger/                        # 日志系统
│   └── config.py
├── config/                        # 配置文件
│   ├── models.yaml.example
│   ├── agents.yaml.example
│   └── config.yaml.example
└── tests/                         # 测试
```

## 🔧 配置说明

### models.yaml

配置使用的LLM模型：

```yaml
models:
  - model_name: gpt-4
    model_type: openai
    api_key: ${OPENAI_API_KEY}
    generate_kwargs:
      temperature: 0.7
      max_tokens: 2000
```

支持的模型类型：
- `openai` - OpenAI API（包括兼容接口如DeepSeek）
- `dashscope` - 阿里云通义千问
- `anthropic` - Anthropic Claude
- `gemini` - Google Gemini
- `ollama` - 本地Ollama模型

### agents.yaml

配置Agent行为：

```yaml
agents:
  - name: mori
    model: gpt-4
    template: mori  # 简短名称，自动查找 internal_template/mori.jinja2
    parallel_tool_calls: true
```

**模板名称说明**：
- 使用简短名称（如 `mori`）会按优先级查找：
  1. 自定义模板：`config/template/mori.jinja2`（最高优先级）
  2. 内置模板：`mori/template/internal_template/mori.jinja2`
- 也可以使用完整路径（如 `internal_template/mori.jinja2`）
- 支持自定义模板，详见 [`config/template/README.md`](config/template/README.md:1)

### config.yaml

全局配置：

```yaml
global:
  log_level: INFO
  log_dir: logs

server:
  host: 0.0.0.0
  port: 7860
  share: false
```

## 🎨 自定义模板

你可以在 `config/template/` 目录创建自定义提示词模板：

```bash
# 创建自定义模板
cat > config/template/my_assistant.jinja2 << 'EOF'
你是一个专业的助手。

{% if current_time and current_date %}
## 当前信息
- 时间: {{ current_time }}
- 日期: {{ current_date }}
{% endif %}

## 你的职责
- 提供准确的信息
- 高效完成任务
- 保持专业态度
EOF
```

然后在配置中使用：

```yaml
# config/agents.yaml
agents:
  - name: my_agent
    model: gpt-4
    template: my_assistant  # 使用自定义模板
```

**模板特性**：
- 自动注入运行时信息（当前时间、日期）
- 支持Jinja2语法（变量、条件、循环）
- 自定义模板优先级高于内置模板

详细说明请查看：[`config/template/README.md`](config/template/README.md:1)

## 🎯 使用示例

### 基础对话

```python
from mori import Mori
import asyncio

async def main():
    # 初始化Mori
    mori = Mori()

    # 发送消息
    response = await mori.chat("你好，Mori！")
    print(response)

    # 重置对话
    mori.reset()

asyncio.run(main())
```

### 自定义工具

在 `mori/tool/internal_tools/` 中添加新工具：

```python
from agentscope.tool import ToolResponse
from agentscope.message import TextBlock

async def my_tool(param: str) -> ToolResponse:
    """工具描述

    Args:
        param: 参数描述
    """
    return ToolResponse(
        content=[
            TextBlock(type="text", text=f"结果: {param}")
        ]
    )

# 在 register_tools 函数中注册
def register_tools(toolkit):
    toolkit.register_tool_function(my_tool)
```

## 🛠️ 开发

### 安装开发依赖

```bash
uv pip install -e ".[dev]"
```

### 代码规范

```bash
# 安装pre-commit hooks
pre-commit install

# 手动运行检查
pre-commit run --all-files
```

### 运行测试

```bash
pytest tests/
```

## 📚 技术栈

- **AgentScope** - 多智能体框架
- **Gradio** - Web界面
- **Pydantic** - 配置验证
- **Jinja2** - 模板引擎
- **uv** - 依赖管理

## 🗺️ 路线图

- [x] v0.1.0 - 基础框架
  - [x] 核心功能实现
  - [x] 配置系统
  - [x] GUI界面
  - [x] 基础工具

- [ ] v0.2.0 - 功能增强
  - [ ] 长期记忆集成
  - [ ] 更多自定义工具
  - [ ] 对话历史管理
  - [ ] 性能优化

- [ ] v1.0.0 - 完整版本
  - [ ] MCP集成
  - [ ] 多模态支持
  - [ ] 插件系统
  - [ ] 云端部署

## 🤝 贡献

欢迎提交Issue和Pull Request！

## 📄 许可证

本项目采用MIT许可证。详见 [LICENSE](LICENSE) 文件。

## 🙏 致谢

- [AgentScope](https://github.com/modelscope/agentscope) - 强大的多智能体框架
- [Gradio](https://gradio.app/) - 简单易用的Web界面框架

## 📮 联系方式

如有问题或建议，欢迎通过Issue联系我们。

---

用心陪伴，温暖相随 💕
