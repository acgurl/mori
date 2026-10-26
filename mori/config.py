"""配置加载和验证模块

使用Pydantic进行配置验证，支持从YAML文件加载配置。
"""

from __future__ import annotations

import logging
import os
import re
from pathlib import Path
from typing import Any

import yaml
from pydantic import BaseModel, Field, ValidationError, field_validator, model_validator

from mori.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_LOG_DIR,
    DEFAULT_LOG_LEVEL,
    DEFAULT_MEMORY_STORAGE_PATH,
    DEFAULT_SERVER_HOST,
    DEFAULT_SERVER_PORT,
    DEFAULT_VECTOR_STORE_PROVIDER,
    VALID_MEMORY_MODES,
)
from mori.exceptions import (
    ConfigError,
    ConfigFileNotFoundError,
    ConfigParseError,
    ConfigValidationError,
)

logger = logging.getLogger(__name__)


def resolve_env_var(value: str | None) -> str | None:
    """解析环境变量引用

    支持 ${ENV_VAR_NAME} 格式的环境变量引用

    Args:
        value: 可能包含环境变量引用的字符串

    Returns:
        解析后的值，如果是环境变量则返回其值，否则返回原值
    """
    if value and value.startswith("${") and value.endswith("}"):
        env_var = value[2:-1]
        # 验证环境变量名称格式，防止注入攻击
        if not re.match(r"^[A-Za-z_][A-Za-z0-9_]*$", env_var):
            logger.error(f"无效的环境变量名称: {env_var}")
            return value
        result = os.getenv(env_var)
        if result is None:
            logger.warning(f"环境变量 {env_var} 未定义")
        return result
    return value


class ModelConfig(BaseModel):
    """模型配置 - 对应AgentScope的模型配置格式"""

    model_name: str = Field(..., description="模型名称")
    model_type: str = Field(..., description="模型类型，如openai, dashscope, ollama等")
    api_key: str | None = Field(None, description="API密钥")
    base_url: str | None = Field(None, description="API基础URL")
    generate_kwargs: dict[str, Any] | None = Field(
        default_factory=dict, description="生成参数，如temperature, max_tokens等"
    )

    @field_validator("api_key", mode="before")
    @classmethod
    def resolve_api_key_env(cls, v: str | None) -> str | None:
        """解析API密钥中的环境变量引用"""
        return resolve_env_var(v)


class EmbeddingModelConfig(BaseModel):
    """嵌入模型配置"""

    model_name: str = Field(..., description="嵌入模型名称")
    model_type: str = Field(..., description="嵌入模型类型，如dashscope, openai, gemini, ollama")
    api_key: str | None = Field(None, description="API密钥")
    base_url: str | None = Field(None, description="API基础URL")
    dimensions: int | None = Field(None, description="向量维度")
    generate_kwargs: dict[str, Any] | None = Field(default_factory=dict, description="生成参数")

    @field_validator("api_key", mode="before")
    @classmethod
    def resolve_api_key_env(cls, v: str | None) -> str | None:
        """解析API密钥中的环境变量引用"""
        return resolve_env_var(v)


class LongTermMemoryConfig(BaseModel):
    """长期记忆配置"""

    enabled: bool = Field(..., description="是否启用长期记忆")
    user_name: str = Field(..., description="用户名，用于隔离不同用户的记忆数据")
    embedding_model: str = Field(..., description="引用models.yaml中的嵌入模型配置名")
    mode: str = Field("agent_control", description="记忆模式: agent_control, static_control, both")
    storage_path: str = Field(DEFAULT_MEMORY_STORAGE_PATH, description="存储路径")
    on_disk: bool = Field(True, description="是否持久化存储到磁盘")
    vector_store_provider: str = Field(DEFAULT_VECTOR_STORE_PROVIDER, description="向量存储提供者")
    collection_name: str = Field(DEFAULT_COLLECTION_NAME, description="向量集合名称")

    @field_validator("mode")
    @classmethod
    def validate_mode(cls, v: str) -> str:
        """验证记忆模式是否为有效值"""
        if v not in VALID_MEMORY_MODES:
            raise ValueError(f"无效的记忆模式 '{v}'，必须是 {VALID_MEMORY_MODES} 之一")
        return v


class AgentConfig(BaseModel):
    """Agent配置"""

    model: str = Field(..., description="引用models.yaml中的模型配置名")
    template: str = Field(..., description="提示词模板文件路径")
    sys_prompt: str | None = Field(None, description="系统提示词，如果为None则使用模板")
    memory_config: dict[str, Any] | None = Field(default_factory=dict, description="记忆配置")
    parallel_tool_calls: bool = Field(False, description="是否支持并行工具调用")
    tools: list[str] = Field(default_factory=list, description="可用的普通工具列表")
    long_term_memory: LongTermMemoryConfig | None = Field(
        None,
        description="长期记忆配置",
    )


class GlobalConfig(BaseModel):
    """全局配置"""

    log_level: str = Field(DEFAULT_LOG_LEVEL, description="日志级别")
    log_dir: str = Field(DEFAULT_LOG_DIR, description="日志目录")


class ServerConfig(BaseModel):
    """服务器配置"""

    host: str = Field(DEFAULT_SERVER_HOST, description="服务器地址")
    port: int = Field(DEFAULT_SERVER_PORT, description="服务器端口")
    share: bool = Field(False, description="是否创建公共链接")


class Config(BaseModel):
    """完整配置"""

    models: dict[str, ModelConfig] = Field(..., description="模型配置字典，key为配置名")
    agents: dict[str, AgentConfig] = Field(..., description="Agent配置字典，key为agent名称")
    primary_agent: str = Field(..., description="主agent名称")
    global_config: GlobalConfig = Field(default_factory=GlobalConfig, description="全局配置")
    server: ServerConfig = Field(default_factory=ServerConfig, description="服务器配置")
    embedding_models: dict[str, EmbeddingModelConfig] = Field(
        default_factory=dict, description="嵌入模型配置字典，key为配置名"
    )

    @model_validator(mode="after")
    def validate_references(self) -> Config:
        """验证配置引用的完整性

        Raises:
            ConfigValidationError: 配置验证失败
        """
        errors = []

        try:
            self._validate_primary_agent()
        except ValueError as e:
            errors.append(str(e))

        try:
            self._validate_agent_references()
        except ValueError as e:
            errors.append(str(e))

        if errors:
            raise ConfigValidationError("配置验证失败", errors)

        return self

    def _validate_primary_agent(self) -> None:
        """验证主Agent是否存在

        Raises:
            ValueError: 主Agent不存在
        """
        if self.primary_agent not in self.agents:
            available = ", ".join(self.agents.keys())
            raise ValueError(f"主Agent '{self.primary_agent}' 不存在。可用: {available}")

    def _validate_agent_references(self) -> None:
        """验证所有Agent的配置引用

        Raises:
            ValueError: Agent配置引用错误
        """
        for agent_name, agent_cfg in self.agents.items():
            self._validate_model_reference(agent_name, agent_cfg.model)
            self._validate_embedding_model_reference(agent_name, agent_cfg)

    def _validate_model_reference(self, agent_name: str, model_name: str) -> None:
        """验证Agent引用的模型是否存在

        Args:
            agent_name: Agent名称
            model_name: 模型名称

        Raises:
            ValueError: 模型不存在
        """
        if model_name not in self.models:
            available = ", ".join(self.models.keys())
            raise ValueError(
                f"Agent '{agent_name}' 引用了不存在的模型 '{model_name}'。可用: {available}"
            )

    def _validate_embedding_model_reference(self, agent_name: str, agent_cfg: AgentConfig) -> None:
        """验证Agent长期记忆引用的嵌入模型是否存在

        Args:
            agent_name: Agent名称
            agent_cfg: Agent配置

        Raises:
            ValueError: 嵌入模型不存在
        """
        if not (agent_cfg.long_term_memory and agent_cfg.long_term_memory.enabled):
            return

        embedding_model = agent_cfg.long_term_memory.embedding_model
        if embedding_model not in self.embedding_models:
            available = ", ".join(self.embedding_models.keys())
            raise ValueError(
                f"Agent '{agent_name}' 引用了不存在的嵌入模型 '{embedding_model}'。"
                f"可用: {available}"
            )


def load_yaml(file_path: str | Path) -> dict[str, Any]:
    """加载YAML文件

    Args:
        file_path: YAML文件路径

    Returns:
        解析后的字典

    Raises:
        ConfigFileNotFoundError: 文件不存在
        ConfigParseError: YAML解析错误
        ConfigError: 其他配置相关错误
    """
    path = Path(file_path)

    # 检查文件是否存在
    if not path.exists():
        logger.error(f"配置文件不存在: {file_path}")
        raise ConfigFileNotFoundError(str(file_path))

    try:
        logger.debug(f"正在加载配置文件: {file_path}")
        with open(path, "r", encoding="utf-8") as f:
            result = yaml.safe_load(f)

            # 检查 yaml.safe_load 返回 None 的情况（空文件或只有注释）
            if result is None:
                logger.error(f"YAML文件为空或无有效内容: {file_path}")
                raise ConfigParseError(str(file_path), ValueError("YAML文件为空或无有效内容"))

            # 确保返回字典类型
            if not isinstance(result, dict):
                logger.error(
                    f"YAML文件内容必须是字典类型，实际为 {type(result).__name__}: {file_path}"
                )
                raise ConfigParseError(
                    str(file_path),
                    ValueError(f"YAML文件内容必须是字典类型，实际为 {type(result).__name__}"),
                )

            logger.debug(f"成功加载配置文件: {file_path}")
            return result

    except yaml.YAMLError as e:
        logger.error(f"YAML解析错误 ({file_path}): {e}")
        raise ConfigParseError(str(file_path), e)
    except (ConfigFileNotFoundError, ConfigParseError):
        raise
    except Exception as e:
        logger.error(f"加载YAML文件时发生未知错误 ({file_path}): {e}")
        raise ConfigError(f"加载配置文件失败: {file_path}", str(e))


def load_config(config_dir: str = "config") -> Config:
    """加载并验证配置

    Args:
        config_dir: 配置文件目录

    Returns:
        验证后的配置对象

    Raises:
        ConfigFileNotFoundError: 必需的配置文件不存在
        ConfigParseError: 配置文件解析失败
        ConfigValidationError: 配置验证失败
        ConfigError: 其他配置相关错误
    """
    config_path = Path(config_dir)
    logger.info(f"开始加载配置，配置目录: {config_dir}")

    try:
        # 加载必需的配置文件
        logger.debug("加载模型配置文件 (models.yaml)")
        models_data = load_yaml(config_path / "models.yaml")

        logger.debug("加载 Agent 配置文件 (agents.yaml)")
        agents_data = load_yaml(config_path / "agents.yaml")

        # 尝试加载全局配置，如果不存在则使用默认值
        try:
            logger.debug("加载全局配置文件 (config.yaml)")
            global_data = load_yaml(config_path / "config.yaml")
        except ConfigFileNotFoundError:
            logger.info("未找到全局配置文件 (config.yaml)，使用默认值")
            global_data = {}

        # 合并配置
        config_data = {
            "models": models_data.get("models", {}),
            "agents": agents_data.get("agents", {}),
            "primary_agent": agents_data.get("primary_agent"),
            "global_config": global_data.get("global", {}),
            "server": global_data.get("server", {}),
            "embedding_models": models_data.get("embedding_models", {}),
        }

        # 验证并返回配置
        logger.debug("验证配置...")
        config = Config(**config_data)
        logger.info("配置加载和验证成功")
        return config

    except ValidationError as e:
        logger.error(f"配置验证失败: {e}")
        # 提取 Pydantic 验证错误信息
        errors = [f"{err['loc']}: {err['msg']}" for err in e.errors()]
        raise ConfigValidationError("配置验证失败", errors)
    except (ConfigFileNotFoundError, ConfigParseError, ConfigValidationError):
        raise
    except Exception as e:
        logger.error(f"加载配置时发生未知错误: {e}")
        raise ConfigError("加载配置失败", str(e))


def get_model_config(config: Config, config_name: str) -> ModelConfig | None:
    """根据配置名获取模型配置

    Args:
        config: 配置对象
        config_name: 模型配置名

    Returns:
        模型配置，如果不存在则返回None
    """
    return config.models.get(config_name)


def get_agent_config(config: Config, agent_name: str) -> AgentConfig | None:
    """根据名称获取Agent配置

    Args:
        config: 配置对象
        agent_name: Agent名称

    Returns:
        Agent配置，如果不存在则返回None
    """
    return config.agents.get(agent_name)


def get_embedding_model_config(config: Config, config_name: str) -> EmbeddingModelConfig | None:
    """根据配置名获取嵌入模型配置

    Args:
        config: 配置对象
        config_name: 嵌入模型配置名

    Returns:
        嵌入模型配置，如果不存在则返回None
    """
    return config.embedding_models.get(config_name)
