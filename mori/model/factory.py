"""模型工厂模块

负责根据配置创建模型实例。
这些逻辑从 mori.py 中提取，遵循单一职责原则。

使用注册表模式，支持动态添加新模型类型，符合开闭原则。
"""

from __future__ import annotations

import logging
from logging import Logger
from typing import Any

from agentscope.embedding import (
    DashScopeTextEmbedding,
    GeminiTextEmbedding,
    OllamaTextEmbedding,
    OpenAITextEmbedding,
)
from agentscope.formatter import (
    AnthropicChatFormatter,
    DashScopeChatFormatter,
    GeminiChatFormatter,
    OllamaChatFormatter,
    OpenAIChatFormatter,
)
from agentscope.model import (
    AnthropicChatModel,
    ChatModelBase,
    DashScopeChatModel,
    GeminiChatModel,
    OllamaChatModel,
    OpenAIChatModel,
)

from mori.config import EmbeddingModelConfig, ModelConfig
from mori.exceptions import ModelConfigError, ModelError

logger = logging.getLogger(__name__)


class ModelRegistry:
    """模型注册表

    使用注册表模式管理聊天模型类型，支持动态添加新模型。
    符合开闭原则：对扩展开放，对修改封闭。
    """

    def __init__(self):
        self._registry: dict[str, tuple[type[ChatModelBase], type[Any]]] = {}

    def register(
        self, model_type: str, model_class: type[ChatModelBase], formatter_class: type[Any]
    ) -> None:
        """注册新的模型类型

        Args:
            model_type: 模型类型标识（如 'openai', 'anthropic'）
            model_class: 模型类
            formatter_class: 对应的 Formatter 类
        """
        model_type = model_type.lower()
        if model_type in self._registry:
            logger.warning(f"模型类型 '{model_type}' 已存在，将被覆盖")
        self._registry[model_type] = (model_class, formatter_class)
        logger.debug(f"注册模型类型: {model_type}")

    def get(self, model_type: str) -> tuple[type[ChatModelBase], type[Any]]:
        """获取模型类型对应的类

        Args:
            model_type: 模型类型标识

        Returns:
            (模型类, Formatter类)

        Raises:
            ModelConfigError: 模型类型不存在
        """
        model_type = model_type.lower()
        if model_type not in self._registry:
            supported = ", ".join(self._registry.keys())
            raise ModelConfigError(
                model_type, f"不支持的模型类型: {model_type}. 支持的类型: {supported}"
            )
        return self._registry[model_type]

    def list_types(self) -> list[str]:
        """列出所有已注册的模型类型"""
        return list(self._registry.keys())

    def is_registered(self, model_type: str) -> bool:
        """检查模型类型是否已注册"""
        return model_type.lower() in self._registry


class EmbeddingModelRegistry:
    """嵌入模型注册表

    使用注册表模式管理嵌入模型类型，支持动态添加新模型。
    """

    def __init__(self):
        self._registry: dict[str, type[Any]] = {}

    def register(self, model_type: str, model_class: type[Any]) -> None:
        """注册新的嵌入模型类型

        Args:
            model_type: 模型类型标识（如 'openai', 'ollama'）
            model_class: 嵌入模型类
        """
        model_type = model_type.lower()
        if model_type in self._registry:
            logger.warning(f"嵌入模型类型 '{model_type}' 已存在，将被覆盖")
        self._registry[model_type] = model_class
        logger.debug(f"注册嵌入模型类型: {model_type}")

    def get(self, model_type: str) -> type[Any]:
        """获取嵌入模型类型对应的类

        Args:
            model_type: 模型类型标识

        Returns:
            嵌入模型类

        Raises:
            ModelConfigError: 模型类型不存在
        """
        model_type = model_type.lower()
        if model_type not in self._registry:
            supported = ", ".join(self._registry.keys())
            raise ModelConfigError(
                model_type, f"不支持的嵌入模型类型: {model_type}. 支持的类型: {supported}"
            )
        return self._registry[model_type]

    def list_types(self) -> list[str]:
        """列出所有已注册的嵌入模型类型"""
        return list(self._registry.keys())

    def is_registered(self, model_type: str) -> bool:
        """检查嵌入模型类型是否已注册"""
        return model_type.lower() in self._registry


# 全局注册表实例
_chat_model_registry = ModelRegistry()
_embedding_model_registry = EmbeddingModelRegistry()


# 预注册内置模型类型
def _register_builtin_models():
    """预注册所有内置模型类型"""
    # 注册聊天模型
    _chat_model_registry.register("openai", OpenAIChatModel, OpenAIChatFormatter)
    _chat_model_registry.register("dashscope", DashScopeChatModel, DashScopeChatFormatter)
    _chat_model_registry.register("anthropic", AnthropicChatModel, AnthropicChatFormatter)
    _chat_model_registry.register("gemini", GeminiChatModel, GeminiChatFormatter)
    _chat_model_registry.register("ollama", OllamaChatModel, OllamaChatFormatter)

    # 注册嵌入模型
    _embedding_model_registry.register("dashscope", DashScopeTextEmbedding)
    _embedding_model_registry.register("openai", OpenAITextEmbedding)
    _embedding_model_registry.register("gemini", GeminiTextEmbedding)
    _embedding_model_registry.register("ollama", OllamaTextEmbedding)

    logger.debug("内置模型类型注册完成")


# 模块加载时自动注册内置模型
_register_builtin_models()


# 公开 API：允许外部注册自定义模型
def register_chat_model(
    model_type: str, model_class: type[ChatModelBase], formatter_class: type[Any]
) -> None:
    """注册自定义聊天模型类型

    允许用户扩展框架支持新的模型类型，无需修改源代码。

    Args:
        model_type: 模型类型标识
        model_class: 模型类
        formatter_class: 对应的 Formatter 类

    Example:
        >>> from my_models import MyCustomModel, MyCustomFormatter
        >>> register_chat_model("custom", MyCustomModel, MyCustomFormatter)
    """
    _chat_model_registry.register(model_type, model_class, formatter_class)


def register_embedding_model(model_type: str, model_class: type[Any]) -> None:
    """注册自定义嵌入模型类型

    允许用户扩展框架支持新的嵌入模型类型，无需修改源代码。

    Args:
        model_type: 模型类型标识
        model_class: 嵌入模型类

    Example:
        >>> from my_models import MyCustomEmbedding
        >>> register_embedding_model("custom", MyCustomEmbedding)
    """
    _embedding_model_registry.register(model_type, model_class)


def create_chat_model(model_config: ModelConfig) -> tuple[ChatModelBase, Any]:
    """根据配置创建聊天模型实例和对应的formatter

    本函数封装了根据 model_type 选择不同 AgentScope 模型类的逻辑。
    AgentScope 提供了各种模型类，我们只是根据配置选择并实例化。

    Args:
        model_config: 模型配置对象

    Returns:
        (模型实例, formatter实例)

    Raises:
        ModelConfigError: 模型配置错误
        ModelError: 模型创建失败
    """
    model_type = model_config.model_type.lower()
    model_name = model_config.model_name

    logger.info(f"创建聊天模型: {model_name} (类型: {model_type})")

    try:
        # 从注册表获取模型类和 Formatter 类
        model_class, formatter_class = _chat_model_registry.get(model_type)
        logger.debug(f"从注册表获取模型类: {model_class.__name__}")
    except ModelConfigError:
        logger.error(f"不支持的模型类型: {model_type}")
        raise

    try:
        # 构建模型参数
        model_kwargs: dict[str, Any] = {"model_name": model_name}

        if model_config.api_key:
            model_kwargs["api_key"] = model_config.api_key
            logger.debug("API 密钥已设置")

        if model_config.generate_kwargs:
            model_kwargs["generate_kwargs"] = model_config.generate_kwargs
            logger.debug(f"生成参数: {model_config.generate_kwargs}")

        # 处理 base_url（OpenAI 和 Ollama 通过 client_args 传递）
        if model_config.base_url and model_type in ["openai", "ollama"]:
            model_kwargs["client_args"] = {"base_url": model_config.base_url}
            logger.debug(f"设置 base_url: {model_config.base_url}")

        # 实例化 AgentScope 提供的模型类
        logger.debug(f"实例化模型类: {model_class.__name__}")

        model = model_class(**model_kwargs)
        formatter = formatter_class()

        logger.info(f"聊天模型创建成功: {model_name}")
        return model, formatter

    except Exception as e:
        logger.error(f"创建聊天模型失败 ({model_name}): {e}")
        raise ModelError(f"创建模型 '{model_name}' 失败", str(e))


def create_embedding_model(
    embedding_config: EmbeddingModelConfig, custom_logger: Logger | None = None
):
    """根据配置创建嵌入模型实例

    本函数封装了根据 model_type 选择不同 AgentScope 嵌入模型类的逻辑。

    Args:
        embedding_config: 嵌入模型配置对象
        custom_logger: 自定义日志记录器（可选）

    Returns:
        嵌入模型实例

    Raises:
        ModelConfigError: 嵌入模型配置错误
        ModelError: 嵌入模型创建失败
    """
    log = custom_logger or logger
    model_type = embedding_config.model_type.lower()
    model_name = embedding_config.model_name

    log.info(f"创建嵌入模型: {model_name} (类型: {model_type})")

    try:
        # 从注册表获取嵌入模型类
        embedding_model_class = _embedding_model_registry.get(model_type)
        log.debug(f"从注册表获取嵌入模型类: {embedding_model_class.__name__}")
    except ModelConfigError:
        log.error(f"不支持的嵌入模型类型: {model_type}")
        raise

    try:
        # 构建模型参数
        model_kwargs: dict[str, Any] = {"model_name": model_name}

        if embedding_config.api_key:
            model_kwargs["api_key"] = embedding_config.api_key
            log.debug("API 密钥已设置")

        # 关键：显式设置 dimensions（Mem0 需要）
        if embedding_config.dimensions:
            model_kwargs["dimensions"] = embedding_config.dimensions
            log.info(f"设置嵌入模型维度: {embedding_config.dimensions}")

        # 处理 base_url
        # OpenAI 嵌入模型将 kwargs 直接传递给 openai.AsyncClient，所以直接传 base_url
        # Ollama 嵌入模型通过 client_args 传递
        if embedding_config.base_url:
            if model_type == "openai":
                model_kwargs["base_url"] = embedding_config.base_url
                log.info(f"OpenAI 嵌入模型直接传递 base_url: {embedding_config.base_url}")
            elif model_type == "ollama":
                model_kwargs["client_args"] = {"base_url": embedding_config.base_url}
                log.info(
                    f"Ollama 嵌入模型通过 client_args 传递 base_url: {embedding_config.base_url}"
                )

        # 处理额外参数
        if embedding_config.generate_kwargs:
            model_kwargs.update(embedding_config.generate_kwargs)
            log.debug(f"生成参数: {embedding_config.generate_kwargs}")

        # 实例化 AgentScope 提供的嵌入模型类
        log.debug(f"实例化嵌入模型类: {embedding_model_class.__name__}")

        embedding_model = embedding_model_class(**model_kwargs)

        # 验证维度属性
        if hasattr(embedding_model, "dimensions"):
            log.info(f"嵌入模型 dimensions 属性: {embedding_model.dimensions}")
        else:
            log.warning("嵌入模型没有 dimensions 属性！")

        log.info(f"嵌入模型创建成功: {model_name}")
        return embedding_model

    except Exception as e:
        log.error(f"创建嵌入模型失败 ({model_name}): {e}")
        raise ModelError(f"创建嵌入模型 '{model_name}' 失败", str(e))
