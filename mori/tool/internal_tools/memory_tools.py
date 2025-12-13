"""长期记忆工具函数

提供记忆记录和检索功能的工具函数。
"""

from typing import Any

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse

from mori.exceptions import MemoryError


async def record_to_memory(content: str, topic: str = "general") -> ToolResponse:
    """将内容记录到长期记忆中

    Args:
        content: 要记录的内容
        topic: 记忆主题（可选）

    Returns:
        ToolResponse: 包含操作结果的响应
    """
    try:
        # 这是一个占位函数，实际的实现会在AgentScope的Mem0LongTermMemory中处理
        # 这里定义函数签名以便AgentScope能够识别和注册
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"已尝试将内容记录到主题 '{topic}' 的长期记忆中: {content[:50]}...",
                )
            ]
        )
    except Exception as e:
        # 抛出MemoryError异常，以便在mori.py中进行类型匹配
        raise MemoryError(f"记录到记忆时出错: {str(e)}")


async def retrieve_from_memory(query: str, topic: str = "general") -> ToolResponse:
    """从长期记忆中检索相关信息

    Args:
        query: 检索查询
        topic: 记忆主题（可选）

    Returns:
        ToolResponse: 包含检索结果的响应
    """
    try:
        # 这是一个占位函数，实际的实现会在AgentScope的Mem0LongTermMemory中处理
        # 这里定义函数签名以便AgentScope能够识别和注册
        return ToolResponse(
            content=[
                TextBlock(
                    type="text",
                    text=f"已尝试从主题 '{topic}' 的长期记忆中检索: {query}",
                )
            ]
        )
    except Exception as e:
        # 抛出MemoryError异常，以便在mori.py中进行类型匹配
        raise MemoryError(f"从记忆检索时出错: {str(e)}")


def register_memory_tools(toolkit: Any) -> None:
    """注册长期记忆工具到Toolkit

    Args:
        toolkit: AgentScope的Toolkit实例
    """
    toolkit.register_tool_function(record_to_memory)
    toolkit.register_tool_function(retrieve_from_memory)
