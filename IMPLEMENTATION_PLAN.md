# Mori项目实施计划

## 项目概述

基于AgentScope框架构建虚拟AI女友agent系统，充分利用框架已有功能，专注于业务逻辑实现。

## 核心设计原则

1. **不重复造轮子** - 直接使用AgentScope的Model、Agent、Tool、Memory等功能
2. **薄封装层** - 只做必要的业务逻辑封装
3. **配置驱动** - 通过YAML配置灵活调整
4. **模板化** - 使用Jinja2管理提示词

## 实施步骤

### 阶段1: 基础设施搭建

1. **创建项目目录结构**
   - mori/ (核心模块)
   - gui/ (界面)
   - logger/ (日志)
   - config/ (配置)
   - tests/ (测试)

2. **配置开发环境**
   - .pre-commit-config.yaml (代码规范)
   - 已有: pyproject.toml, .gitignore

### 阶段2: 核心功能实现

3. **配置系统** (mori/config.py)
   - Pydantic模型: ModelConfig, AgentConfig, GlobalConfig
   - 配置加载函数
   - 环境变量支持

4. **模板系统** (mori/template/)
   - loader.py: Jinja2模板加载器
   - internal_template/mori.jinja2: Mori提示词模板

5. **日志系统** (logger/config.py)
   - 统一日志配置
   - 文件和控制台输出

6. **Agent工厂** (mori/agent/factory.py)
   - 创建ReActAgent的工厂函数
   - 简单封装，主要用于配置注入

7. **自定义工具** (mori/tool/internal_tools/)
   - example_tools.py: 示例工具（时间查询等）
   - 使用AgentScope的Toolkit注册

8. **Mori核心类** (mori/mori.py)
   - 封装AgentScope功能
   - 提供chat()、reset()等简洁API
   - 集成配置、模板、工具

### 阶段3: 用户界面

9. **Gradio GUI** (gui/app.py)
   - 聊天界面
   - 历史记录
   - 清空对话功能

### 阶段4: 配置和文档

10. **配置文件示例** (config/)
    - models.yaml.example
    - agents.yaml.example
    - config.yaml.example
    - mcp.json.example

11. **README文档**
    - 项目介绍
    - 快速开始
    - 配置说明
    - 使用示例

12. **测试用例** (tests/)
    - test_config.py
    - test_template.py
    - test_mori.py

## 技术栈映射

| 功能 | 使用的技术 | 说明 |
|------|-----------|------|
| Model管理 | AgentScope Model | 直接使用，不重复实现 |
| Agent | AgentScope ReActAgent | 直接使用，薄封装 |
| Tool管理 | AgentScope Toolkit | 直接使用，注册自定义工具 |
| Memory | AgentScope InMemoryMemory | 直接使用 |
| 配置验证 | Pydantic | 我们实现 |
| 提示词模板 | Jinja2 | 我们实现 |
| GUI | Gradio | 我们实现 |
| 日志 | Python logging | 我们实现 |

## 关键代码示例

### 使用AgentScope创建Agent

```python
from agentscope.agent import ReActAgent
from agentscope.model import OpenAIChatModel
from agentscope.memory import InMemoryMemory
from agentscope.tool import Toolkit

# 创建模型（AgentScope提供）
model = OpenAIChatModel(
    model_name="gpt-4",
    api_key="your-key"
)

# 创建工具集（AgentScope提供）
toolkit = Toolkit()
toolkit.register_tool_function(your_tool_function)

# 创建Agent（AgentScope提供）
agent = ReActAgent(
    name="mori",
    sys_prompt="你是Mori...",
    model=model,
    memory=InMemoryMemory(),
    toolkit=toolkit
)

# 使用Agent
response = await agent(Msg("user", "你好", "user"))
```

### 我们的封装

```python
class Mori:
    """薄封装层，简化使用"""

    def __init__(self, config_dir: str = "config"):
        # 加载配置
        self.config = load_config(config_dir)

        # 加载模板
        sys_prompt = load_template(self.config.agent.template)

        # 创建AgentScope组件
        self.model = create_model(self.config.model)
        self.toolkit = create_toolkit()
        self.agent = ReActAgent(...)

    async def chat(self, message: str) -> str:
        """简化的聊天接口"""
        msg = Msg("user", message, "user")
        response = await self.agent(msg)
        return response.content
```

## 预期成果

完成后将得到：

1. ✅ 可运行的虚拟AI女友agent系统
2. ✅ 清晰的项目结构
3. ✅ 完整的配置系统
4. ✅ 友好的Web界面
5. ✅ 可扩展的工具系统
6. ✅ 完善的文档

## 时间估算

- 阶段1: 0.5小时
- 阶段2: 2-3小时
- 阶段3: 1小时
- 阶段4: 1小时

总计: 约4-6小时

## 后续扩展方向

1. 集成长期记忆（AgentScope已支持）
2. 添加更多自定义工具
3. 实现MCP集成
4. 多模态支持
5. 个性化配置
