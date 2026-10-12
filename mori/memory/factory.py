"""长期记忆工厂模块

负责根据配置创建长期记忆实例。
"""

from logging import Logger
from pathlib import Path

from agentscope.embedding import EmbeddingModelBase
from agentscope.memory import Mem0LongTermMemory
from agentscope.model import ChatModelBase

from mori.constants import (
    DEFAULT_COLLECTION_NAME,
    DEFAULT_EMBEDDING_DIM,
    DEFAULT_VECTOR_STORE_PROVIDER,
)
from mori.utils.model_wrapper import NonStreamingModelWrapper


def create_long_term_memory(
    agent_name: str,
    user_name: str,
    model: ChatModelBase,
    embedding_model: EmbeddingModelBase,
    storage_path: str = "data/memory",
    on_disk: bool = True,
    vector_store_provider: str = DEFAULT_VECTOR_STORE_PROVIDER,
    collection_name: str = DEFAULT_COLLECTION_NAME,
    logger: Logger | None = None,
) -> Mem0LongTermMemory:
    """根据配置创建长期记忆实例

    本函数封装了 Mem0LongTermMemory 的创建逻辑，包括：
    - 包装模型以禁用流式输出（Mem0 要求）
    - 配置向量存储
    - 设置持久化选项

    Args:
        agent_name: Agent名称
        user_name: 用户名称
        model: 主模型实例
        embedding_model: 嵌入模型实例
        storage_path: 存储路径
        on_disk: 是否持久化存储
        vector_store_provider: 向量存储提供者
        collection_name: 向量集合名称
        logger: 日志记录器（可选）

    Returns:
        Mem0LongTermMemory实例
    """
    # 确保存储目录存在
    if on_disk:
        Path(storage_path).mkdir(parents=True, exist_ok=True)
        if logger:
            logger.info(f"长期记忆存储路径: {storage_path}")

    # 包装模型以禁用流式输出（Mem0 不支持流式响应）
    wrapped_model = NonStreamingModelWrapper(model)

    # 获取嵌入模型维度
    embedding_dim = getattr(embedding_model, "dimensions", DEFAULT_EMBEDDING_DIM)
    if logger:
        logger.info(f"嵌入模型维度: {embedding_dim}")

    # 导入 Mem0 配置类
    try:
        from mem0.vector_stores.configs import VectorStoreConfig
    except ImportError as e:
        raise ImportError(
            "无法导入 mem0.vector_stores.configs.VectorStoreConfig。"
            "请确保已安装 mem0ai 库：pip install mem0ai"
        ) from e

    # 创建向量存储配置（必须显式传递 embedding_model_dims）
    vector_store_config = VectorStoreConfig(
        provider=vector_store_provider,
        config={
            "collection_name": collection_name,
            "embedding_model_dims": embedding_dim,
            "on_disk": on_disk,
            "path": storage_path if on_disk else None,
        },
    )

    ltm_kwargs = {
        "agent_name": agent_name,
        "user_name": user_name,
        "model": wrapped_model,
        "embedding_model": embedding_model,
        "vector_store_config": vector_store_config,
    }

    if on_disk:
        ltm_kwargs["storage_path"] = storage_path

    if logger:
        logger.info("准备创建 Mem0LongTermMemory")
        logger.info(
            f"向量存储配置: provider={vector_store_provider}, "
            f"collection={collection_name}, dims={embedding_dim}, on_disk={on_disk}"
        )

    long_term_memory = Mem0LongTermMemory(**ltm_kwargs)

    if logger:
        logger.info(f"长期记忆已创建 - 用户: {user_name}, 持久化: {on_disk}")

    return long_term_memory
