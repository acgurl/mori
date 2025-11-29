"""Mori核心封装类

封装AgentScope功能，提供简洁的API接口。
"""

from typing import List

from agentscope.message import Msg
from agentscope.model import (
    AnthropicChatModel,
    DashScopeChatModel,
    GeminiChatModel,
    OllamaChatModel,
    OpenAIChatModel,
)
from agentscope.formatter import (
    AnthropicChatFormatter,
    DashScopeChatFormatter,
    GeminiChatFormatter,
    OllamaChatFormatter,
    OpenAIChatFormatter,
)
from agentscope.tool import Toolkit

from logger import setup_logger
from mori.agent.factory import create_mori_agent
from mori.config import load_config
from mori.template.loader import TemplateLoader
from mori.tool.internal_tools.example_tools import register_tools


class Mori:
    """Mori核心类

    封装AgentScope的功能，提供简洁的使用接口。
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
        self.logger.info("正在初始化Mori系统...")

        # 初始化模板加载器
        self.template_loader = TemplateLoader()

        # 获取第一个agent配置（默认使用第一个）
        if not self.config.agents:
            raise ValueError("配置文件中没有定义任何agent")
        self.agent_config = self.config.agents[0]

        # 加载系统提示词
        sys_prompt = self._load_system_prompt()

        # 创建模型和formatter
        self.model, self.formatter = self._create_model()

        # 创建工具集
        self.toolkit = self._create_toolkit()

        # 创建Agent
        self.agent = create_mori_agent(
            name=self.agent_config.name,
            sys_prompt=sys_prompt,
            model=self.model,
            formatter=self.formatter,
            toolkit=self.toolkit,
            parallel_tool_calls=self.agent_config.parallel_tool_calls,
        )

        self.logger.info("Mori系统初始化完成！")

    def _load_system_prompt(self) -> str:
        """加载系统提示词

        Returns:
            系统提示词字符串
        """
        if self.agent_config.sys_prompt:
            return self.agent_config.sys_prompt

        # 准备模板上下文（运行时信息）
        from datetime import datetime

        context = {
            "current_time": datetime.now().strftime("%H:%M:%S"),
            "current_date": datetime.now().strftime("%Y年%m月%d日 %A"),
        }

        # 从模板加载并渲染
        return self.template_loader.render_template(self.agent_config.template, context=context)

    def _create_model(self):
        """创建模型实例和对应的formatter

        Returns:
            (模型实例, formatter实例)

        Raises:
            ValueError: 模型配置不存在或模型类型不支持
        """
        # 获取模型配置
        model_config = None
        for model in self.config.models:
            if model.model_name == self.agent_config.model:
                model_config = model
                break

        if model_config is None:
            raise ValueError(f"找不到模型配置: {self.agent_config.model}")

        # 根据模型类型创建实例
        model_type = model_config.model_type.lower()
        model_kwargs = {
            "model_name": model_config.model_name,
        }

        if model_config.api_key:
            model_kwargs["api_key"] = model_config.api_key

        if model_config.generate_kwargs:
            model_kwargs["generate_kwargs"] = model_config.generate_kwargs

        if model_type == "openai":
            if model_config.base_url:
                model_kwargs["client_args"] = {"base_url": model_config.base_url}
            return OpenAIChatModel(**model_kwargs), OpenAIChatFormatter()

        elif model_type == "dashscope":
            return DashScopeChatModel(**model_kwargs), DashScopeChatFormatter()

        elif model_type == "anthropic":
            return AnthropicChatModel(**model_kwargs), AnthropicChatFormatter()

        elif model_type == "gemini":
            return GeminiChatModel(**model_kwargs), GeminiChatFormatter()

        elif model_type == "ollama":
            if model_config.base_url:
                model_kwargs["client_args"] = {"base_url": model_config.base_url}
            return OllamaChatModel(**model_kwargs), OllamaChatFormatter()

        else:
            raise ValueError(f"不支持的模型类型: {model_type}")

    def _create_toolkit(self) -> Toolkit:
        """创建工具集

        Returns:
            配置好的Toolkit实例
        """
        toolkit = Toolkit()
        # 注册内置工具
        register_tools(toolkit)
        return toolkit

    async def chat(self, message: str) -> str:
        """发送消息并获取回复

        Args:
            message: 用户消息

        Returns:
            Agent的回复内容
        """
        self.logger.debug(f"用户消息: {message}")

        # 创建消息对象
        msg = Msg(name="user", content=message, role="user")

        # 调用Agent
        response = await self.agent(msg)

        # 提取文本内容
        reply_text = self._extract_text_from_response(response)

        self.logger.debug(f"Mori回复: {reply_text}")
        return reply_text

    def _extract_text_from_response(self, response: Msg) -> str:
        """从响应消息中提取文本内容

        Args:
            response: Agent的响应消息

        Returns:
            提取的文本内容
        """
        if isinstance(response.content, str):
            return response.content

        if isinstance(response.content, list):
            text_parts = []
            for item in response.content:
                if isinstance(item, dict) and item.get("type") == "text":
                    text_parts.append(item.get("text", ""))
                elif isinstance(item, str):
                    text_parts.append(item)
            return "\n".join(text_parts)

        return str(response.content)

    async def reset(self) -> None:
        """重置对话历史"""
        await self.agent.memory.clear()
        self.logger.info("对话历史已重置")

    async def get_history(self) -> List[dict]:
        """获取对话历史

        Returns:
            对话历史列表
        """
        return await self.agent.memory.get_memory()
