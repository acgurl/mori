"""模板服务模块

提供提示词加载和渲染服务。
"""

from datetime import datetime
from typing import Any

from mori.template.loader import TemplateLoader


def load_system_prompt(
    template_name: str,
    sys_prompt: str | None = None,
    template_loader: TemplateLoader | None = None,
) -> str:
    """加载系统提示词

    如果提供了 sys_prompt 则直接返回，否则从模板加载并注入运行时信息。

    Args:
        template_name: 模板名称
        sys_prompt: 直接提供的系统提示词（可选）
        template_loader: 模板加载器实例（可选，如果为 None 则创建新实例）

    Returns:
        系统提示词字符串
    """
    if sys_prompt:
        return sys_prompt

    # 准备模板上下文（运行时信息）
    context: dict[str, Any] = {
        "current_time": datetime.now().strftime("%H:%M:%S"),
        "current_date": datetime.now().strftime("%Y年%m月%d日 %A"),
    }

    # 从模板加载并渲染
    if template_loader is None:
        template_loader = TemplateLoader()

    return template_loader.render_template(template_name, context=context)
