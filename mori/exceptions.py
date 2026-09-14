"""自定义异常类

提供项目特定的异常类，便于区分和处理不同类型的错误。
"""



class MoriError(Exception):
    """Mori 项目的基础异常类

    所有自定义异常都应该继承此类。
    """

    def __init__(self, message: str, details: str | None = None):
        """初始化异常

        Args:
            message: 错误消息
            details: 详细错误信息（可选）
        """
        self.message = message
        self.details = details
        super().__init__(self.message)

    def __str__(self) -> str:
        """返回字符串表示"""
        if self.details:
            return f"{self.message}\n详情: {self.details}"
        return self.message


class ConfigError(MoriError):
    """配置相关错误

    当配置文件加载、解析或验证失败时抛出。
    """



class ConfigFileNotFoundError(ConfigError):
    """配置文件不存在"""

    def __init__(self, file_path: str):
        super().__init__(f"配置文件不存在: {file_path}", "请确保配置文件存在且路径正确")
        self.file_path = file_path


class ConfigParseError(ConfigError):
    """配置文件解析错误"""

    def __init__(self, file_path: str, original_error: Exception):
        super().__init__(f"配置文件解析失败: {file_path}", str(original_error))
        self.file_path = file_path
        self.original_error = original_error


class ConfigValidationError(ConfigError):
    """配置验证错误"""

    def __init__(self, message: str, validation_errors: list[str] | None = None):
        details = None
        if validation_errors:
            details = "\n".join(f"  - {err}" for err in validation_errors)
        super().__init__(message, details)
        self.validation_errors = validation_errors or []


class ModelError(MoriError):
    """模型相关错误

    当模型创建、初始化或调用失败时抛出。
    """



class ModelConfigError(ModelError):
    """模型配置错误"""

    def __init__(self, model_name: str, reason: str):
        super().__init__(f"模型 '{model_name}' 配置错误", reason)
        self.model_name = model_name


class ModelNotFoundError(ModelError):
    """模型不存在"""

    def __init__(self, model_name: str, available_models: list[str] | None = None):
        details = None
        if available_models:
            details = f"可用模型: {', '.join(available_models)}"
        super().__init__(f"模型 '{model_name}' 不存在", details)
        self.model_name = model_name
        self.available_models = available_models or []


class AgentError(MoriError):
    """Agent 相关错误

    当 Agent 创建、初始化或执行失败时抛出。
    """



class AgentConfigError(AgentError):
    """Agent 配置错误"""

    def __init__(self, agent_name: str, reason: str):
        super().__init__(f"Agent '{agent_name}' 配置错误", reason)
        self.agent_name = agent_name


class AgentNotFoundError(AgentError):
    """Agent 不存在"""

    def __init__(self, agent_name: str, available_agents: list[str] | None = None):
        details = None
        if available_agents:
            details = f"可用 Agent: {', '.join(available_agents)}"
        super().__init__(f"Agent '{agent_name}' 不存在", details)
        self.agent_name = agent_name
        self.available_agents = available_agents or []


class ToolError(MoriError):
    """工具相关错误

    当工具注册、查找或执行失败时抛出。
    """



class ToolExecutionError(ToolError):
    """工具执行错误"""

    def __init__(self, tool_name: str, original_error: Exception):
        super().__init__(f"工具 '{tool_name}' 执行失败", str(original_error))
        self.tool_name = tool_name
        self.original_error = original_error


class MemoryError(MoriError):
    """记忆系统相关错误

    当记忆系统初始化或操作失败时抛出。
    """



class MemoryConfigError(MemoryError):
    """记忆系统配置错误"""

    def __init__(self, reason: str):
        super().__init__("记忆系统配置错误", reason)


class TemplateError(MoriError):
    """模板相关错误

    当模板加载或渲染失败时抛出。
    """



class TemplateNotFoundError(TemplateError):
    """模板不存在"""

    def __init__(self, template_name: str, search_paths: list[str] | None = None):
        details = None
        if search_paths:
            details = f"搜索路径: {', '.join(search_paths)}"
        super().__init__(f"模板 '{template_name}' 不存在", details)
        self.template_name = template_name
        self.search_paths = search_paths or []


class TemplateRenderError(TemplateError):
    """模板渲染错误"""

    def __init__(self, template_name: str, original_error: Exception):
        super().__init__(f"模板 '{template_name}' 渲染失败", str(original_error))
        self.template_name = template_name
        self.original_error = original_error
