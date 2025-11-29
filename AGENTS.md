# AGENTS.md

This file provides guidance to agents when working with code in this repository.

## 项目特定约定

### 模板系统优先级
- 模板查找顺序：`config/template/` (自定义) > `mori/template/internal_template/` (内置)
- 简短名称（如 `mori`）自动添加 `.jinja2` 扩展名并按优先级查找
- 运行时信息（`current_time`, `current_date`）在 [`mori.py:_load_system_prompt()`](mori/mori.py:85) 中注入，不在模板中硬编码

### 配置加载机制
- 环境变量格式：`${ENV_VAR_NAME}` 在 [`config.py:resolve_env_var()`](mori/config.py:25) 中解析
- 配置文件必须分离：`models.yaml` (模型), `agents.yaml` (agent), `config.yaml` (全局)
- Agent 通过 `model` 字段引用 `models.yaml` 中的模型名称，不是直接配置

### Model 和 Formatter 配对
- 每个模型类型必须配对对应的 Formatter（见 [`mori.py:_create_model()`](mori/mori.py:108)）
- OpenAI 兼容接口使用 `model_type: openai` + `base_url` 参数
- `client_args` 用于传递额外的客户端参数（如 `base_url`）

### 工具注册模式
- 工具函数必须返回 [`ToolResponse`](mori/tool/internal_tools/example_tools.py:13) 对象，不是普通字符串
- 使用 [`toolkit.register_tool_function()`](mori/tool/internal_tools/example_tools.py:92) 注册，AgentScope 自动解析函数签名为 JSON Schema
- 工具函数支持 async/await

### 响应内容提取
- Agent 响应可能是字符串或包含 `TextBlock` 的列表
- 使用 [`_extract_text_from_response()`](mori/mori.py:197) 统一处理不同格式

## 测试命令

```bash
# 运行所有测试
pytest tests/

# 运行特定测试文件
pytest tests/test_config.py

# 带详细输出
pytest tests/ -v
```

## 代码风格

- Line length: 100 (black/ruff 配置)
- Python 3.10+ 语法
- 使用 pre-commit hooks: `pre-commit run --all-files`
