"""Agent工具包装模块

将Agent包装为工具，使主agent可以调用子agent。
"""

from collections.abc import Callable

from agentscope.agent import ReActAgent
from agentscope.message import Msg
from agentscope.tool import ToolResponse

from mori.utils.response import extract_text_from_response


class AgentTool:
    """将Agent包装为工具

    此类将一个Agent实例包装成可以被其他Agent调用的工具。
    """

    def __init__(self, agent: ReActAgent, agent_name: str):
        """初始化Agent工具

        Args:
            agent: Agent实例
            agent_name: Agent名称
        """
        self.agent = agent
        self.agent_name = agent_name

    async def __call__(self, task: str) -> ToolResponse:
        """调用子agent完成任务

        Args:
            task: 要委派给子agent的任务描述

        Returns:
            ToolResponse对象，包含子agent的执行结果
        """
        # 创建消息
        msg = Msg(name="user", content=task, role="user")

        # 调用子agent
        response = await self.agent(msg)

        # 提取响应文本
        result = extract_text_from_response(response)

        # 返回ToolResponse
        return ToolResponse(content=result, metadata={"agent_name": self.agent_name, "task": task})


def create_agent_tool_function(
    agent: ReActAgent, agent_name: str, description: str | None = None
) -> Callable[[str], ToolResponse]:
    """创建agent工具函数

    将Agent实例包装为可注册到toolkit的函数。
    AgentScope会自动解析函数签名生成JSON Schema。

    Args:
        agent: Agent实例
        agent_name: Agent名称
        description: 工具描述，如果为None则使用默认描述

    Returns:
        可注册到toolkit的异步函数
    """
    agent_tool = AgentTool(agent, agent_name)

    # 生成默认描述
    if description is None:
        description = (
            f"调用{agent_name} agent完成专门任务。将任务描述传递给该agent，它会完成任务并返回结果。"
        )

    async def tool_function(task: str) -> ToolResponse:
        """{description}

        Args:
            task: 要委派给{agent_name} agent的任务描述

        Returns:
            任务执行结果
        """
        return await agent_tool(task)

    # 设置函数名称和文档字符串
    tool_function.__name__ = f"call_{agent_name}_agent"
    tool_function.__doc__ = f"""{description}

    Args:
        task: 要委派给{agent_name} agent的任务描述

    Returns:
        任务执行结果
    """

    return tool_function
