"""Agent工厂函数

用于创建和配置AgentScope的ReActAgent实例。
"""

from typing import Optional

from agentscope.agent import ReActAgent
from agentscope.memory import InMemoryMemory
from agentscope.model import ChatModelBase
from agentscope.tool import Toolkit


def create_mori_agent(
    name: str,
    sys_prompt: str,
    model: ChatModelBase,
    formatter,
    toolkit: Optional[Toolkit] = None,
    parallel_tool_calls: bool = False,
    **kwargs,
) -> ReActAgent:
    """创建Mori Agent实例

    这是一个简单的工厂函数，用于创建配置好的ReActAgent。
    直接使用AgentScope的ReActAgent，不做额外封装。

    Args:
        name: Agent名称
        sys_prompt: 系统提示词
        model: AgentScope模型实例
        formatter: 提示词格式化器
        toolkit: 工具集，如果为None则创建空工具集
        parallel_tool_calls: 是否支持并行工具调用
        **kwargs: 其他传递给ReActAgent的参数

    Returns:
        配置好的ReActAgent实例
    """
    if toolkit is None:
        toolkit = Toolkit()

    # 创建内存实例
    memory = InMemoryMemory()

    # 创建并返回ReActAgent
    agent = ReActAgent(
        name=name,
        sys_prompt=sys_prompt,
        model=model,
        formatter=formatter,
        memory=memory,
        toolkit=toolkit,
        parallel_tool_calls=parallel_tool_calls,
        **kwargs,
    )

    return agent
