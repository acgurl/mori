"""Gradio GUI应用

使用Gradio创建Web界面，提供友好的用户交互体验。
"""

from typing import List, Dict

import gradio as gr

from mori import Mori


class MoriGUI:
    """Mori GUI封装类"""

    def __init__(self, config_dir: str = "config"):
        """初始化GUI

        Args:
            config_dir: 配置文件目录
        """
        self.mori = Mori(config_dir)
        self.config = self.mori.config

    async def chat(
        self, message: str, history: List[Dict[str, str]]
    ) -> tuple[str, List[Dict[str, str]]]:
        """处理聊天消息

        Args:
            message: 用户消息
            history: 对话历史（Gradio 6.0格式）

        Returns:
            (空字符串, 更新后的历史)
        """
        if not message.strip():
            return "", history

        # 获取回复
        response = await self.mori.chat(message)

        # 更新历史 - Gradio 6.0格式
        history.append({"role": "user", "content": message})
        history.append({"role": "assistant", "content": response})

        return "", history

    async def reset(self) -> List[Dict[str, str]]:
        """重置对话

        Returns:
            空的对话历史
        """
        print("DEBUG: reset() 被调用")  # 调试日志
        await self.mori.reset()
        print("DEBUG: mori.reset() 执行完成")  # 调试日志
        return []

    def create_interface(self) -> gr.Blocks:
        """创建Gradio界面

        Returns:
            Gradio Blocks对象
        """
        with gr.Blocks(
            title="Mori - 虚拟AI女友",
        ) as app:
            gr.Markdown(
                """
                # 💕 Mori - 你的虚拟AI女友

                欢迎来到Mori的世界！我会用心陪伴你，倾听你的心声。✨
                """
            )

            with gr.Row():
                with gr.Column(scale=4):
                    chatbot = gr.Chatbot(
                        label="与Mori聊天",
                        height=500,
                        show_label=True,
                        avatar_images=(None, "🌸"),
                    )

                    with gr.Row():
                        msg = gr.Textbox(
                            label="",
                            placeholder="和Mori说点什么吧... 💭",
                            show_label=False,
                            scale=4,
                        )
                        submit = gr.Button("发送 💌", scale=1, variant="primary")

                    with gr.Row():
                        clear = gr.Button("清空对话 🔄", scale=1)

                with gr.Column(scale=1):
                    gr.Markdown(
                        """
                        ### 💡 使用提示

                        - 和Mori分享你的心情
                        - 聊聊你的日常生活
                        - 寻求情感支持
                        - 或者只是闲聊 😊

                        ### ⚙️ 当前配置
                        """
                    )

                    gr.Markdown(
                        f"""
                        - **Agent**: {self.mori.agent_config.name}
                        - **模型**: {self.mori.agent_config.model}
                        - **工具**: {len(self.mori.toolkit.get_json_schemas())} 个
                        """
                    )

            # 绑定事件
            msg.submit(
                self.chat,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
            )

            submit.click(
                self.chat,
                inputs=[msg, chatbot],
                outputs=[msg, chatbot],
            )

            clear.click(
                fn=self.reset,
                inputs=None,
                outputs=[chatbot],
            )

        return app

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
    # 创建GUI实例
    gui = MoriGUI()

    # 使用配置文件中的服务器设置
    gui.launch(
        server_name=gui.config.server.host,
        server_port=gui.config.server.port,
        share=gui.config.server.share,
    )


if __name__ == "__main__":
    main()
