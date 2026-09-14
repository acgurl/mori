"""Jinja2模板加载器

用于加载和渲染提示词模板。
支持内置模板和自定义模板。
"""

import logging
from pathlib import Path
from typing import Any

from jinja2 import (
    ChoiceLoader,
    Environment,
    FileSystemLoader,
    Template,
    TemplateNotFound,
    TemplateSyntaxError,
    select_autoescape,
)

from mori.exceptions import TemplateError, TemplateNotFoundError, TemplateRenderError

logger = logging.getLogger(__name__)


class TemplateLoader:
    """Jinja2模板加载器

    支持多个模板目录的加载，按优先级查找：
    1. 自定义模板目录 (config/template/)
    2. 内置模板目录 (mori/template/internal_template/)
    """

    def __init__(
        self, template_dir: str | None = None, custom_template_dir: str | None = None
    ):
        """初始化模板加载器

        Args:
            template_dir: 内置模板目录路径，如果为None则使用默认路径
            custom_template_dir: 自定义模板目录路径，如果为None则使用 config/template
        """
        if template_dir is None:
            # 默认使用mori/template目录
            template_dir = str(Path(__file__).parent)

        if custom_template_dir is None:
            # 默认使用config/template目录
            custom_template_dir = "config/template"

        # 验证路径安全性（解析为绝对路径）
        self.template_dir = Path(template_dir).resolve()
        self.internal_template_dir = self.template_dir / "internal_template"
        self.custom_template_dir = Path(custom_template_dir).resolve()

        # 确保内置模板目录存在
        if not self.template_dir.exists():
            raise ValueError(f"模板目录不存在: {self.template_dir}")

        # 确保自定义模板目录存在
        self.custom_template_dir.mkdir(parents=True, exist_ok=True)

        # 创建多个加载器，按优先级排序
        loaders: list[FileSystemLoader] = []

        # 1. 自定义模板目录（最高优先级）
        if self.custom_template_dir.exists():
            loaders.append(FileSystemLoader(str(self.custom_template_dir)))

        # 2. 内置模板的internal_template子目录
        if self.internal_template_dir.exists():
            loaders.append(FileSystemLoader(str(self.internal_template_dir)))

        # 3. 内置模板根目录（用于完整路径）
        loaders.append(FileSystemLoader(str(self.template_dir)))

        # 使用ChoiceLoader按顺序查找模板
        self.env = Environment(
            loader=ChoiceLoader(loaders),
            autoescape=select_autoescape(),
            trim_blocks=True,
            lstrip_blocks=True,
        )

    def _resolve_template_path(self, template_name: str) -> str:
        """解析模板路径

        支持以下格式：
        1. 简短名称：mori
           - 优先在 config/template/mori.jinja2 查找（自定义）
           - 然后在 mori/template/internal_template/mori.jinja2 查找（内置）
        2. 完整路径：internal_template/mori.jinja2 或 custom/my_template.jinja2

        Args:
            template_name: 模板名称或路径

        Returns:
            解析后的模板路径
        """
        # 如果已经是完整路径（包含目录分隔符或扩展名），直接返回
        if "/" in template_name or "\\" in template_name or template_name.endswith(".jinja2"):
            return template_name

        # 简短名称：添加.jinja2扩展名
        # ChoiceLoader会按优先级自动查找：
        # 1. config/template/mori.jinja2
        # 2. mori/template/internal_template/mori.jinja2
        return f"{template_name}.jinja2"

    def load_template(self, template_name: str) -> Template:
        """加载模板

        Args:
            template_name: 模板名称、文件名或相对路径
                          支持简短名称（如"mori"）或完整路径（如"internal_template/mori.jinja2"）
                          优先级：自定义模板 > 内置模板

        Returns:
            Jinja2模板对象

        Raises:
            TemplateNotFoundError: 模板文件不存在
            TemplateError: 其他模板相关错误
        """
        try:
            resolved_path = self._resolve_template_path(template_name)
            logger.debug(f"加载模板: {resolved_path}")
            template = self.env.get_template(resolved_path)
            logger.debug(f"模板加载成功: {resolved_path}")
            return template
        except TemplateNotFound:
            logger.error(f"模板不存在: {template_name}")
            search_paths = [
                str(self.custom_template_dir),
                str(self.internal_template_dir),
            ]
            raise TemplateNotFoundError(template_name, search_paths)
        except TemplateSyntaxError as e:
            logger.error(f"模板语法错误 ({template_name}): {e}")
            raise TemplateError(f"模板语法错误: {template_name}", str(e))
        except Exception as e:
            logger.error(f"加载模板失败 ({template_name}): {e}")
            raise TemplateError(f"加载模板失败: {template_name}", str(e))

    def render_template(self, template_name: str, context: dict[str, Any] | None = None) -> str:
        """加载并渲染模板

        Args:
            template_name: 模板名称、文件名或相对路径
                          支持简短名称（如"mori"）或完整路径（如"internal_template/mori.jinja2"）
                          优先级：自定义模板 > 内置模板
            context: 模板上下文变量

        Returns:
            渲染后的字符串

        Raises:
            TemplateNotFoundError: 模板文件不存在
            TemplateRenderError: 模板渲染失败
            TemplateError: 其他模板相关错误
        """
        if context is None:
            context = {}

        try:
            template = self.load_template(template_name)
            logger.debug(f"渲染模板: {template_name}")
            result: str = template.render(**context)
            logger.debug(f"模板渲染成功: {template_name}")
            return result
        except (TemplateNotFoundError, TemplateError):
            raise
        except Exception as e:
            logger.error(f"渲染模板失败 ({template_name}): {e}")
            raise TemplateRenderError(template_name, e)

    def render_string(self, template_string: str, context: dict[str, Any] | None = None) -> str:
        """渲染模板字符串

        Args:
            template_string: 模板字符串
            context: 模板上下文变量

        Returns:
            渲染后的字符串

        Raises:
            TemplateError: 模板渲染失败
        """
        if context is None:
            context = {}

        try:
            logger.debug("渲染模板字符串")
            template = self.env.from_string(template_string)
            result: str = template.render(**context)
            logger.debug("模板字符串渲染成功")
            return result
        except TemplateSyntaxError as e:
            logger.error(f"模板字符串语法错误: {e}")
            raise TemplateError("模板字符串语法错误", str(e))
        except Exception as e:
            logger.error(f"渲染模板字符串失败: {e}")
            raise TemplateError("渲染模板字符串失败", str(e))


def load_template_file(template_path: str, context: dict[str, Any] | None = None) -> str:
    """便捷函数：加载并渲染模板文件

    Args:
        template_path: 模板文件的完整路径
        context: 模板上下文变量

    Returns:
        渲染后的字符串

    Raises:
        FileNotFoundError: 模板文件不存在
    """
    path = Path(template_path)
    if not path.exists():
        raise FileNotFoundError(f"模板文件不存在: {template_path}")

    # 获取模板目录和文件名
    template_dir = str(path.parent)
    template_name = path.name

    loader = TemplateLoader(template_dir)
    return loader.render_template(template_name, context)
