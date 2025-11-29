"""示例工具函数

使用AgentScope的Toolkit注册自定义工具。
工具函数需要返回ToolResponse对象。
"""

from datetime import datetime

from agentscope.message import TextBlock
from agentscope.tool import ToolResponse, Toolkit


async def get_current_time() -> ToolResponse:
    """获取当前时间

    Returns:
        ToolResponse: 包含当前时间的响应
    """
    current_time = datetime.now().strftime("%Y年%m月%d日 %H:%M:%S")
    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"现在是 {current_time} 💫",
            )
        ]
    )


async def get_current_date() -> ToolResponse:
    """获取当前日期

    Returns:
        ToolResponse: 包含当前日期的响应
    """
    current_date = datetime.now().strftime("%Y年%m月%d日")
    weekday = ["星期一", "星期二", "星期三", "星期四", "星期五", "星期六", "星期日"][
        datetime.now().weekday()
    ]
    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"今天是 {current_date} {weekday} 🌸",
            )
        ]
    )


async def get_greeting(name: str = "亲爱的") -> ToolResponse:
    """生成问候语

    Args:
        name: 要问候的人的称呼

    Returns:
        ToolResponse: 包含问候语的响应
    """
    hour = datetime.now().hour
    if 5 <= hour < 12:
        greeting = "早上好"
        emoji = "🌅"
    elif 12 <= hour < 14:
        greeting = "中午好"
        emoji = "☀️"
    elif 14 <= hour < 18:
        greeting = "下午好"
        emoji = "🌤️"
    elif 18 <= hour < 22:
        greeting = "晚上好"
        emoji = "🌙"
    else:
        greeting = "夜深了"
        emoji = "✨"

    return ToolResponse(
        content=[
            TextBlock(
                type="text",
                text=f"{greeting}，{name}！{emoji}",
            )
        ]
    )


def register_tools(toolkit: Toolkit) -> None:
    """注册所有自定义工具到Toolkit

    Args:
        toolkit: AgentScope的Toolkit实例
    """
    toolkit.register_tool_function(get_current_time)
    toolkit.register_tool_function(get_current_date)
    toolkit.register_tool_function(get_greeting)
