"""Mori核心封装类

封装AgentScope功能，提供简洁的API接口。
作为编排层，组装各个模块，不包含具体业务逻辑。
支持多agent架构。
"""

from typing import Any, Dict, List

from agentscope.message import Msg

from logger import setup_logger
from mori.agent.manager import AgentManager
from mori.config import load_config
from mori.exceptions import MemoryError
from mori.utils.response import extract_text_from_response


class Mori:
    """Mori核心类

    封装AgentScope的功能，提供简洁的使用接口。
    作为编排层，负责组装各个模块，不包含具体业务逻辑。
    支持多agent架构，主agent可以调用子agent作为工具。
    """

    def __init__(self, config_dir: str = "config"):
        """初始化Mori系统

        Args:
            config_dir: 配置文件目录路径
        """
        # 加载配置
        self.config = load_config(config_dir)

        # 设置日志
        self.logger = setup_logger(
            name="mori",
            level=self.config.global_config.log_level,
            log_dir=self.config.global_config.log_dir,
        )
        self.logger.info("正在初始化Mori系统（多agent模式）...")

        # 验证配置
        if not self.config.agents:
            raise ValueError("配置文件中没有定义任何agent")
        if not self.config.primary_agent:
            raise ValueError("配置文件中没有指定主agent（primary_agent）")
        if self.config.primary_agent not in self.config.agents:
            raise ValueError(f"主agent '{self.config.primary_agent}' 不存在于agents配置中")

        # 创建Agent管理器
        self.agent_manager = AgentManager(self.config, self.logger)

        # 获取主agent
        self.primary_agent = self.agent_manager.get_primary_agent()

        # 将所有子agent注册为主agent的工具
        self.agent_manager.register_sub_agents_as_tools(self.config.primary_agent)

        self.logger.info(
            f"Mori系统初始化完成！主agent: {self.config.primary_agent}, "
            f"可用agents: {self.agent_manager.list_agents()}"
        )

    async def chat(self, message: str) -> str:
        """发送消息并获取回复

        消息会发送给主agent处理，主agent可以自主决定是否调用子agent。

        Args:
            message: 用户消息

        Returns:
            主Agent的回复内容
        """
        self.logger.info(f"处理用户消息: {message}")

        try:
            # 创建消息对象
            msg = Msg(name="user", content=message, role="user")

            # 调用主Agent
            response = await self.primary_agent(msg)

            # DEBUG: 记录完整响应对象
            self.logger.debug(f"[DEBUG] Agent响应对象: {response}")
            self.logger.debug(f"[DEBUG] 响应name: {response.name}")
            self.logger.debug(f"[DEBUG] 响应role: {response.role}")
            self.logger.debug(f"[DEBUG] 响应content类型: {type(response.content)}")
            self.logger.debug(f"[DEBUG] 响应content: {response.content}")

            # 提取文本内容
            reply_text = extract_text_from_response(response)

            self.logger.debug(f"[DEBUG] 提取后的文本: {reply_text}")
            self.logger.info("成功生成回复")
            return reply_text

        except MemoryError as e:
            # 捕获长期记忆相关错误
            self.logger.error(f"处理记忆相关请求时发生错误: {str(e)}", exc_info=True)
            return "抱歉,我在尝试记忆信息时遇到了问题。我已经记录了这个错误,会尽快修复。"
        except Exception as e:
            # 捕获所有其他异常,包括 API 错误、工具错误等
            error_msg = str(e)
            self.logger.error(f"处理消息时发生错误: {error_msg}", exc_info=True)

            if "can only concatenate list" in error_msg:
                return "抱歉,处理您的请求时出现了内部错误。请稍后再试。"
            elif "text cannot be empty" in error_msg:
                return "抱歉,生成回复时出现了格式错误。请重新提问。"
            else:
                # 其他未知错误
                return f"抱歉,处理您的请求时出现了错误: {error_msg}"

    async def reset(self) -> None:
        """重置主agent的对话历史"""
        await self.primary_agent.memory.clear()
        self.logger.info("主agent对话历史已重置")

    async def get_history(self) -> List[Dict[Any, Any]]:
        """获取主agent的对话历史

        Returns:
            对话历史列表
        """
        history: List[Dict[Any, Any]] = await self.primary_agent.memory.get_memory()
        return history

    def list_agents(self) -> List[str]:
        """列出所有可用的agent名称

        Returns:
            Agent名称列表
        """
        return self.agent_manager.list_agents()

    def get_primary_agent_name(self) -> str:
        """获取主agent名称

        Returns:
            主agent名称
        """
        return self.config.primary_agent
