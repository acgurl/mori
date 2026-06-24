"""Agent管理器模块

负责管理多个agent实例，包括创建、缓存和工具注册。
"""

from logging import Logger
from typing import Dict, List, Optional

from agentscope.agent import ReActAgent
from agentscope.tool import Toolkit

from mori.agent.factory import build_agent
from mori.config import Config, get_agent_config, get_model_config
from mori.template.loader import TemplateLoader
from mori.template.service import load_system_prompt
from mori.tool.agent_tools import create_agent_tool_function
from mori.tool.factory import create_toolkit


class AgentManager:
    """Agent管理器

    负责管理多个agent实例，提供agent创建、缓存和工具注册功能。
    """

    def __init__(self, config: Config, logger: Optional[Logger] = None):
        """初始化Agent管理器

        Args:
            config: 完整配置对象
            logger: 日志记录器（可选）
        """
        self.config = config
        self.logger = logger
        self.agents: Dict[str, ReActAgent] = {}
        self.template_loader = TemplateLoader()
        self.base_toolkit = create_toolkit()  # 创建基础工具集

    def build_agent(self, agent_name: str) -> ReActAgent:
        """构建指定名称的agent实例

        Args:
            agent_name: Agent名称

        Returns:
            构建好的Agent实例

        Raises:
            ValueError: Agent配置不存在或模型配置不存在
        """
        # 获取agent配置
        agent_config = get_agent_config(self.config, agent_name)
        if agent_config is None:
            raise ValueError(f"Agent配置不存在: {agent_name}")

        # 获取模型配置
        model_config = get_model_config(self.config, agent_config.model)
        if model_config is None:
            raise ValueError(
                f"模型配置不存在: {agent_config.model} " f"(agent '{agent_name}' 引用)"
            )

        # 加载系统提示词
        sys_prompt = load_system_prompt(
            template_name=agent_config.template,
            sys_prompt=agent_config.sys_prompt,
            template_loader=self.template_loader,
        )

        # 创建该agent的工具集（仅包含配置中指定的普通工具）
        agent_toolkit = self._create_agent_toolkit(agent_config.tools)

        # 使用build_agent工厂函数构建agent
        agent = build_agent(
            agent_name=agent_name,
            agent_config=agent_config,
            model_config=model_config,
            sys_prompt=sys_prompt,
            toolkit=agent_toolkit,
            config=self.config,
            logger=self.logger,
        )

        if self.logger:
            self.logger.info(f"已构建agent: {agent_name}")

        return agent

    def _create_agent_toolkit(self, tool_names: List[str]) -> Toolkit:
        """为特定agent创建工具集

        根据配置中指定的工具名称，从基础工具集中筛选工具。

        Args:
            tool_names: 工具名称列表

        Returns:
            包含指定工具的Toolkit实例

        Raises:
            ValueError: 工具不存在
        """
        toolkit = Toolkit()
        missing_tools = []

        # 从基础工具集中筛选该agent可用的工具
        for tool_name in tool_names:
            # 从基础工具集获取工具
            tool = self.base_toolkit.tools.get(tool_name)
            if tool is not None:
                toolkit.add(tool)
            else:
                missing_tools.append(tool_name)

        if missing_tools and self.logger:
            self.logger.warning(f"工具不存在: {', '.join(missing_tools)}")

        return toolkit

    def get_agent(self, agent_name: str) -> ReActAgent:
        """获取agent实例（带缓存）

        如果agent已经创建过，直接返回缓存的实例；
        否则创建新实例并缓存。

        Args:
            agent_name: Agent名称

        Returns:
            Agent实例
        """
        if agent_name not in self.agents:
            self.agents[agent_name] = self.build_agent(agent_name)
        return self.agents[agent_name]

    def get_primary_agent(self) -> ReActAgent:
        """获取主agent实例

        Returns:
            主Agent实例
        """
        return self.get_agent(self.config.primary_agent)

    def list_agents(self) -> List[str]:
        """列出所有可用的agent名称

        Returns:
            Agent名称列表
        """
        return list(self.config.agents.keys())

    def register_sub_agents_as_tools(self, primary_agent_name: str) -> None:
        """将所有子agent注册为主agent的工具

        遍历所有非主agent的agent，将它们作为工具注册到主agent的工具集中。
        子agent不能调用其他agent（防止循环调用）。

        Args:
            primary_agent_name: 主agent名称
        """
        # 获取主agent实例
        primary_agent = self.get_agent(primary_agent_name)

        # 遍历所有agent配置
        for agent_name in self.config.agents.keys():
            # 跳过主agent本身
            if agent_name == primary_agent_name:
                continue

            # 获取子agent实例（会触发创建和缓存）
            sub_agent = self.get_agent(agent_name)

            # 创建agent工具函数
            tool_func = create_agent_tool_function(
                agent=sub_agent,
                agent_name=agent_name,
                description=f"调用{agent_name} agent完成专门任务",
            )

            # 注册到主agent的工具集
            primary_agent.toolkit.register_tool_function(tool_func)

            if self.logger:
                self.logger.info(
                    f"已将子agent '{agent_name}' 注册为主agent '{primary_agent_name}' 的工具"
                )
