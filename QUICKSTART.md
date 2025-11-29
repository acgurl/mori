# 快速开始指南 🚀

本指南将帮助你在5分钟内运行Mori项目。

## 前置要求

- Python 3.10+
- uv（Python包管理器）
- 一个LLM API密钥（OpenAI、DeepSeek、通义千问等）

## 步骤1: 安装依赖

```bash
# 创建虚拟环境
uv venv

# 激活虚拟环境
# Windows PowerShell:
.venv\Scripts\activate
# Linux/Mac:
source .venv/bin/activate

# 安装项目
uv pip install -e .
```

## 步骤2: 配置

### 方式A: 使用环境变量（推荐）

```bash
# Windows PowerShell:
$env:OPENAI_API_KEY="your-api-key-here"

# Linux/Mac:
export OPENAI_API_KEY="your-api-key-here"
```

然后复制配置文件：

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

### 方式B: 直接编辑配置文件

1. 复制配置文件（同上）
2. 编辑 `config/models.yaml`，将 `${OPENAI_API_KEY}` 替换为你的实际API密钥

```yaml
models:
  - model_name: gpt-4
    model_type: openai
    api_key: sk-your-actual-key-here  # 直接填入密钥
    generate_kwargs:
      temperature: 0.7
      max_tokens: 2000
```

## 步骤3: 运行

```bash
python gui/app.py
```

然后在浏览器中访问: http://localhost:7860

## 使用其他模型

### DeepSeek

```yaml
# config/models.yaml
models:
  - model_name: deepseek-chat
    model_type: openai
    api_key: ${DEEPSEEK_API_KEY}
    base_url: https://api.deepseek.com/v1
    generate_kwargs:
      temperature: 0.7
```

```yaml
# config/agents.yaml
agents:
  - name: mori
    model: deepseek-chat  # 使用DeepSeek
    template: mori  # 使用简短名称
    parallel_tool_calls: true
```

### 通义千问（DashScope）

```yaml
# config/models.yaml
models:
  - model_name: qwen-max
    model_type: dashscope
    api_key: ${DASHSCOPE_API_KEY}
    generate_kwargs:
      temperature: 0.7
```

```yaml
# config/agents.yaml
agents:
  - name: mori
    model: qwen-max  # 使用通义千问
    template: mori  # 使用简短名称
    parallel_tool_calls: true
```

### Ollama（本地模型）

```yaml
# config/models.yaml
models:
  - model_name: llama3
    model_type: ollama
    base_url: http://localhost:11434
    generate_kwargs:
      temperature: 0.8
```

```yaml
# config/agents.yaml
agents:
  - name: mori
    model: llama3  # 使用本地Ollama模型
    template: mori  # 使用简短名称
    parallel_tool_calls: false  # Ollama可能不支持并行工具调用
```

## 常见问题

### Q: 启动时提示找不到配置文件

A: 确保你已经复制了配置文件示例：
```bash
cp config/models.yaml.example config/models.yaml
cp config/agents.yaml.example config/agents.yaml
cp config/config.yaml.example config/config.yaml
```

### Q: API密钥错误

A: 检查以下几点：
1. 环境变量是否正确设置
2. 配置文件中的API密钥是否正确
3. 如果使用环境变量，确保格式为 `${ENV_VAR_NAME}`

### Q: 端口被占用

A: 修改 `config/config.yaml` 中的端口：
```yaml
server:
  port: 8080  # 改为其他端口
```

### Q: 模型响应很慢

A: 可以尝试：
1. 使用更快的模型（如gpt-3.5-turbo）
2. 减少 `max_tokens` 参数
3. 使用本地Ollama模型

## 下一步

- 查看 [README.md](README.md) 了解更多功能
- 查看 [ARCHITECTURE.md](ARCHITECTURE.md) 了解架构设计
- 自定义提示词模板：编辑 `mori/template/internal_template/mori.jinja2`
- 添加自定义工具：在 `mori/tool/internal_tools/` 中添加新工具

## 获取帮助

如有问题，请查看：
- [README.md](README.md) - 完整文档
- [ARCHITECTURE.md](ARCHITECTURE.md) - 架构说明
- GitHub Issues - 提交问题

祝你使用愉快！💕
