"""Gradio GUI应用

使用Gradio创建Web界面，提供友好的用户交互体验。
"""

import asyncio
import traceback
from typing import Generator

import gradio as gr

from logger.config import get_logger
from mori import Mori
from mori.exceptions import ConfigError, MoriError

# 使用统一的 "mori" logger，避免日志传播导致的重复打印
logger = get_logger("mori")


class MoriGUI:
    """Mori GUI封装类"""

    def __init__(self, config_dir: str = "config"):
        """初始化GUI

        Args:
            config_dir: 配置文件目录

        Raises:
            ConfigError: 配置加载失败
            MoriError: Mori 初始化失败
        """
        try:
            logger.info(f"初始化 Mori GUI，配置目录: {config_dir}")
            self.mori = Mori(config_dir)
            self.config = self.mori.config
            logger.info("Mori GUI 初始化成功")
        except ConfigError as e:
            logger.error(f"配置加载失败: {e}")
            raise
        except Exception as e:
            logger.error(f"Mori 初始化失败: {e}")
            logger.debug(traceback.format_exc())
            raise MoriError("GUI 初始化失败", str(e))

    def respond(self, message: str, history: list) -> Generator[str, None, None]:
        """处理聊天消息（生成器版本，用于流式输出）

        Args:
            message: 用户消息
            history: 对话历史

        Yields:
            响应文本
        """
        if not message.strip():
            logger.debug("收到空消息，忽略")
            yield ""
            return

        try:
            # 使用 asyncio.run 运行异步方法
            response = asyncio.run(self.mori.chat(message))
            yield response

        except Exception as e:
            # 最后一道防线: 捕获任何未被 mori.chat 处理的异常
            logger.error(f"GUI层捕获到未处理的错误: {e}", exc_info=True)
            yield "抱歉，系统出现了意外错误。请稍后重试。"

    def create_interface(self) -> gr.ChatInterface:
        """创建Gradio聊天界面

        Returns:
            Gradio ChatInterface对象
        """
        # 获取主agent配置信息
        primary_agent_name = self.mori.get_primary_agent_name()
        primary_agent_config = self.config.agents.get(primary_agent_name)
        primary_agent = self.mori.primary_agent

        description = f"""
        欢迎来到Mori的世界！我会用心陪伴你，倾听你的心声。✨

        **当前配置**: 主Agent: {primary_agent_name} | 模型: {primary_agent_config.model if primary_agent_config else 'N/A'} | 工具: {len(primary_agent.toolkit.get_json_schemas())} 个
        """

        chat_interface = gr.ChatInterface(
            fn=self.respond,
            title="💕 Mori - 你的虚拟AI女友",
            description=description,
            examples=[
                "你好，今天过得怎么样？",
                "我今天心情不太好...",
                "给我讲个有趣的故事吧",
            ],
        )

        return chat_interface

    def launch(
        self,
        server_name: str = "0.0.0.0",
        server_port: int = 7860,
        share: bool = False,
    ):
        """启动GUI应用

        Args:
            server_name: 服务器地址
            server_port: 服务器端口
            share: 是否创建公共链接
        """
        app = self.create_interface()
        app.launch(
            server_name=server_name,
            server_port=server_port,
            share=share,
        )


def main():
    """主函数"""
    try:
        # 创建GUI实例
        logger.info("启动 Mori GUI 应用")
        gui = MoriGUI()

        # 使用配置文件中的服务器设置
        logger.info(f"启动服务器: {gui.config.server.host}:{gui.config.server.port}")
        gui.launch(
            server_name=gui.config.server.host,
            server_port=gui.config.server.port,
            share=gui.config.server.share,
        )
    except ConfigError as e:
        logger.critical(f"配置错误，无法启动应用: {e}")
        if e.details:
            logger.critical(f"详情: {e.details}")
        print(f"\n❌ 配置错误: {e}")
        if e.details:
            print(f"详情: {e.details}")
        print("\n请检查配置文件后重试。")
        return
    except MoriError as e:
        logger.critical(f"启动失败: {e}")
        if e.details:
            logger.critical(f"详情: {e.details}")
        print(f"\n❌ 启动失败: {e.message}")
        if e.details:
            print(f"详情: {e.details}")
        return
    except Exception as e:
        logger.critical(f"未知错误导致启动失败: {e}")
        logger.critical(traceback.format_exc())
        print(f"\n❌ 发生未知错误: {e}")
        print("请查看日志获取详细信息。")
        return


if __name__ == "__main__":
    main()
