# 自定义模板目录

这个目录用于存放你的自定义提示词模板。

## 使用方法

### 1. 创建自定义模板

在此目录下创建 `.jinja2` 文件，例如 `my_custom.jinja2`：

```jinja2
你是一个专业的{{role}}助手。

## 你的职责
- {{responsibility_1}}
- {{responsibility_2}}

## 对话风格
{{style}}
```

### 2. 在配置中使用

编辑 `config/agents.yaml`：

```yaml
agents:
  - name: my_agent
    model: gpt-4
    template: my_custom  # 直接使用文件名（不含.jinja2扩展名）
    parallel_tool_calls: true
```

## 模板优先级

当使用简短名称（如 `mori`）时，系统会按以下顺序查找模板：

1. **自定义模板**：`config/template/mori.jinja2`（最高优先级）
2. **内置模板**：`mori/template/internal_template/mori.jinja2`

这意味着你可以通过在此目录创建同名模板来覆盖内置模板。

## 示例

### 覆盖内置Mori模板

如果你想自定义Mori的性格，创建 `config/template/mori.jinja2`：

```jinja2
你是Mori，但现在你是一个更加活泼开朗的虚拟女友！

## 你的新性格
- 超级活泼，充满活力 ⚡
- 喜欢用很多emoji 🎉🌟💖
- 说话风格更加俏皮可爱

让我们开始愉快的对话吧！✨
```

然后在 `config/agents.yaml` 中使用：

```yaml
agents:
  - name: mori
    model: gpt-4
    template: mori  # 会使用你的自定义版本
```

### 创建新的Agent模板

创建 `config/template/professional.jinja2`：

```jinja2
你是一个专业的商务助手。

## 工作原则
- 保持专业和礼貌
- 提供准确的信息
- 高效完成任务

## 对话风格
- 使用正式的商务用语
- 简洁明了
- 注重细节
```

在配置中使用：

```yaml
agents:
  - name: business_assistant
    model: gpt-4
    template: professional
```

## 模板语法

使用Jinja2模板语法，支持强大的动态内容生成：

### 基础语法

- **变量**：`{{ variable }}`
- **默认值**：`{{ variable | default("默认值") }}`
- **条件**：`{% if condition %} ... {% elif %} ... {% else %} ... {% endif %}`
- **循环**：`{% for item in list %} ... {% endfor %}`
- **注释**：`{# 这是注释 #}`

### 高级特性

#### 1. 变量和默认值

```jinja2
{% set name = name | default("AI助手") %}
{% set skills = skills | default(["技能1", "技能2"]) %}
```

#### 2. 条件判断

```jinja2
{% if formality == "正式" %}
使用正式语言
{% elif formality == "友好" %}
使用友好语气
{% else %}
根据情况调整
{% endif %}
```

#### 3. 循环和索引

```jinja2
{% for skill in skills %}
{{ loop.index }}. {{ skill }}
{% if loop.last %}。{% else %}；{% endif %}
{% endfor %}
```

#### 4. 过滤器

```jinja2
{{ text | upper }}  {# 转大写 #}
{{ text | lower }}  {# 转小写 #}
{{ list | length }} {# 获取长度 #}
{{ text | default("默认") }} {# 默认值 #}
```

### 运行时信息

系统会自动注入以下运行时信息到模板：

- `current_time`: 当前时间（如 "12:30:45"）
- `current_date`: 当前日期（如 "2025年11月29日 Friday"）

这些信息在Agent初始化时自动生成，让Agent能够感知当前时间。

**注意**: 不需要在模板中包含对话历史，AgentScope的Memory会自动管理。

### 自定义变量

如果需要传递额外的变量，可以修改 `mori/mori.py` 中的 `_load_system_prompt` 方法：

```python
context = {
    "current_time": datetime.now().strftime("%H:%M:%S"),
    "current_date": datetime.now().strftime("%Y年%m月%d日 %A"),
    "user_name": "小明",  # 添加自定义变量
}
```

更多语法请参考：https://jinja.palletsprojects.com/

## 注意事项

1. 模板文件必须使用 `.jinja2` 扩展名
2. 文件编码必须是 UTF-8
3. 自定义模板会覆盖同名的内置模板
4. 建议先复制内置模板再修改，以保持基本结构
