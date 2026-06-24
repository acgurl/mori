"""Agent工厂函数

用于创建和配置AgentScope的ReActAgent实例。
"""

from logging import Logger
from typing import Any, Optional

from agentscope.agent import ReActAgent
from agentscope.formatter import FormatterBase
from agentscope.memory import InMemoryMemory, MemoryBase
from agentscope.model import ChatModelBase
from agentscope.tool import Toolkit

from mori.config import AgentConfig, Config, ModelConfig, get_embedding_model_config
from mori.memory.factory import create_long_term_memory
from mori.model.factory import create_chat_model, create_embedding_model


def create_mori_agent(
    agent_name: str,
    sys_prompt: str,
    model: ChatModelBase,
    formatter: FormatterBase,
    toolkit: Optional[Toolkit] = None,
    parallel_tool_calls: bool = False,
    long_term_memory: Optional[MemoryBase] = None,
    long_term_memory_mode: Optional[str] = None,
    **kwargs: Any,
) -> ReActAgent:
    """创建Mori Agent实例

    这是一个简单的工厂函数，用于创建配置好的ReActAgent。
    直接使用AgentScope的ReActAgent，不做额外封装。

    Args:
        agent_name: Agent名称
        sys_prompt: 系统提示词
        model: AgentScope模型实例
        formatter: 提示词格式化器
        toolkit: 工具集，如果为None则创建空工具集
        parallel_tool_calls: 是否支持并行工具调用
        long_term_memory: 长期记忆实例（可选）
        long_term_memory_mode: 长期记忆模式，可选值: agent_control, static_control, both
        **kwargs: 其他传递给ReActAgent的参数

    Returns:
        配置好的ReActAgent实例
    """
    if toolkit is None:
        toolkit = Toolkit()

    # 创建内存实例
    memory = InMemoryMemory()

    # 构建基础参数字典
    react_kwargs = {
        "name": agent_name,
        "sys_prompt": sys_prompt,
        "model": model,
        "formatter": formatter,
        "memory": memory,
        "toolkit": toolkit,
        "parallel_tool_calls": parallel_tool_calls,
        "long_term_memory": long_term_memory,
        **kwargs,
    }

    # 仅在启用了长期记忆且模式非空时传入该参数，规避断言错误
    if long_term_memory is not None and long_term_memory_mode:
        react_kwargs["long_term_memory_mode"] = long_term_memory_mode

    # 创建并返回ReActAgent
    agent = ReActAgent(**react_kwargs)

    return agent


def build_agent(
    agent_name: str,
    agent_config: AgentConfig,
    model_config: ModelConfig,
    sys_prompt: str,
    toolkit: Toolkit,
    config: Config,
    logger: Optional[Logger] = None,
) -> ReActAgent:
    """构建完整配置的Agent实例

    这是一个高层工厂函数，负责组装所有Agent创建所需的组件，包括：
    - 根据模型配置创建模型和formatter
    - 如果配置了长期记忆，创建长期记忆实例
    - 创建并返回配置完整的ReActAgent

    Args:
        agent_name: Agent名称（来自配置的key）
        agent_config: Agent配置对象
        model_config: 模型配置对象
        sys_prompt: 系统提示词
        toolkit: 工具集
        config: 完整配置对象（用于获取嵌入模型配置等）
        logger: 日志记录器（可选）

    Returns:
        配置完成的ReActAgent实例
    """
    # 创建模型和formatter
    model, formatter = create_chat_model(model_config)

    # 创建长期记忆（如果配置了）
    long_term_memory = None
    long_term_memory_mode = None

    if agent_config.long_term_memory and agent_config.long_term_memory.enabled:
        ltm_config = agent_config.long_term_memory

        # Pydantic 已经在配置加载时验证了所有必需字段和类型，这里直接使用
        # 创建嵌入模型
        embedding_config = get_embedding_model_config(config, ltm_config.embedding_model)
        if embedding_config is None:
            raise ValueError(f"找不到嵌入模型配置: {ltm_config.embedding_model}")

        embedding_model = create_embedding_model(embedding_config, logger)

        # 创建长期记忆实例
        long_term_memory = create_long_term_memory(
            agent_name=agent_name,
            user_name=ltm_config.user_name,
            model=model,
            embedding_model=embedding_model,
            storage_path=ltm_config.storage_path,
            on_disk=ltm_config.on_disk,
            logger=logger,
        )

        long_term_memory_mode = ltm_config.mode

        if logger:
            logger.info(f"长期记忆已启用，模式: {long_term_memory_mode}")

    # 创建Agent
    return create_mori_agent(
        agent_name=agent_name,
        sys_prompt=sys_prompt,
        model=model,
        formatter=formatter,
        toolkit=toolkit,
        parallel_tool_calls=agent_config.parallel_tool_calls,
        long_term_memory=long_term_memory,
        long_term_memory_mode=long_term_memory_mode,
    )
