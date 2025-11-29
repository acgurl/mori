"""配置加载和验证模块

使用Pydantic进行配置验证，支持从YAML文件加载配置。
"""

import os
from pathlib import Path
from typing import Any, Dict, List, Optional

import yaml
from pydantic import BaseModel, Field, field_validator


class ModelConfig(BaseModel):
    """模型配置 - 对应AgentScope的模型配置格式"""

    model_name: str = Field(..., description="模型名称")
    model_type: str = Field(..., description="模型类型，如openai, dashscope, ollama等")
    api_key: Optional[str] = Field(None, description="API密钥")
    base_url: Optional[str] = Field(None, description="API基础URL")
    generate_kwargs: Optional[Dict[str, Any]] = Field(
        default_factory=dict, description="生成参数，如temperature, max_tokens等"
    )

    @field_validator("api_key", mode="before")
    @classmethod
    def resolve_env_var(cls, v: Optional[str]) -> Optional[str]:
        """解析环境变量"""
        if v and v.startswith("${") and v.endswith("}"):
            env_var = v[2:-1]
            return os.getenv(env_var)
        return v


class AgentConfig(BaseModel):
    """Agent配置"""

    name: str = Field(..., description="Agent名称")
    model: str = Field(..., description="使用的模型名称，引用models.yaml中的模型")
    template: str = Field(..., description="提示词模板文件路径")
    sys_prompt: Optional[str] = Field(None, description="系统提示词，如果为None则使用模板")
    memory_config: Optional[Dict[str, Any]] = Field(default_factory=dict, description="记忆配置")
    parallel_tool_calls: bool = Field(False, description="是否支持并行工具调用")


class GlobalConfig(BaseModel):
    """全局配置"""

    log_level: str = Field("INFO", description="日志级别")
    log_dir: str = Field("logs", description="日志目录")


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = Field("0.0.0.0", description="服务器地址")
    port: int = Field(7860, description="服务器端口")
    share: bool = Field(False, description="是否创建公共链接")


class Config(BaseModel):
    """完整配置"""

    models: List[ModelConfig] = Field(..., description="模型配置列表")
    agents: List[AgentConfig] = Field(..., description="Agent配置列表")
    global_config: GlobalConfig = Field(default_factory=GlobalConfig, description="全局配置")
    server: ServerConfig = Field(default_factory=ServerConfig, description="服务器配置")


def load_yaml(file_path: str) -> Dict[str, Any]:
    """加载YAML文件

    Args:
        file_path: YAML文件路径

    Returns:
        解析后的字典

    Raises:
        FileNotFoundError: 文件不存在
        yaml.YAMLError: YAML解析错误
    """
    path = Path(file_path)
    if not path.exists():
        raise FileNotFoundError(f"配置文件不存在: {file_path}")

    with open(path, "r", encoding="utf-8") as f:
        return yaml.safe_load(f)


def load_config(config_dir: str = "config") -> Config:
    """加载并验证配置

    Args:
        config_dir: 配置文件目录

    Returns:
        验证后的配置对象

    Raises:
        FileNotFoundError: 配置文件不存在
        ValidationError: 配置验证失败
    """
    config_path = Path(config_dir)

    # 加载各个配置文件
    models_data = load_yaml(config_path / "models.yaml")
    agents_data = load_yaml(config_path / "agents.yaml")

    # 尝试加载全局配置，如果不存在则使用默认值
    try:
        global_data = load_yaml(config_path / "config.yaml")
    except FileNotFoundError:
        global_data = {}

    # 合并配置
    config_data = {
        "models": models_data.get("models", []),
        "agents": agents_data.get("agents", []),
        "global_config": global_data.get("global", {}),
        "server": global_data.get("server", {}),
    }

    # 验证并返回配置
    return Config(**config_data)


def get_model_config(config: Config, model_name: str) -> Optional[ModelConfig]:
    """根据名称获取模型配置

    Args:
        config: 配置对象
        model_name: 模型名称

    Returns:
        模型配置，如果不存在则返回None
    """
    for model in config.models:
        if model.model_name == model_name:
            return model
    return None


def get_agent_config(config: Config, agent_name: str) -> Optional[AgentConfig]:
    """根据名称获取Agent配置

    Args:
        config: 配置对象
        agent_name: Agent名称

    Returns:
        Agent配置，如果不存在则返回None
    """
    for agent in config.agents:
        if agent.name == agent_name:
            return agent
    return None
