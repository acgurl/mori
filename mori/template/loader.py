"""Jinja2模板加载器

用于加载和渲染提示词模板。
支持内置模板和自定义模板。
"""

from pathlib import Path
from typing import Any, Dict, List, Optional

from jinja2 import ChoiceLoader, Environment, FileSystemLoader, Template, select_autoescape


class TemplateLoader:
    """Jinja2模板加载器

    支持多个模板目录的加载，按优先级查找：
    1. 自定义模板目录 (config/template/)
    2. 内置模板目录 (mori/template/internal_template/)
    """

    def __init__(
        self, template_dir: Optional[str] = None, custom_template_dir: Optional[str] = None
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

        self.template_dir = Path(template_dir)
        self.internal_template_dir = self.template_dir / "internal_template"
        self.custom_template_dir = Path(custom_template_dir)

        # 确保自定义模板目录存在
        self.custom_template_dir.mkdir(parents=True, exist_ok=True)

        # 创建多个加载器，按优先级排序
        loaders: List[FileSystemLoader] = []

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
            TemplateNotFound: 模板文件不存在
        """
        resolved_path = self._resolve_template_path(template_name)
        return self.env.get_template(resolved_path)

    def render_template(self, template_name: str, context: Optional[Dict[str, Any]] = None) -> str:
        """加载并渲染模板

        Args:
            template_name: 模板名称、文件名或相对路径
                          支持简短名称（如"mori"）或完整路径（如"internal_template/mori.jinja2"）
                          优先级：自定义模板 > 内置模板
            context: 模板上下文变量

        Returns:
            渲染后的字符串

        Raises:
            TemplateNotFound: 模板文件不存在
        """
        if context is None:
            context = {}

        template = self.load_template(template_name)
        return template.render(**context)

    def render_string(self, template_string: str, context: Optional[Dict[str, Any]] = None) -> str:
        """渲染模板字符串

        Args:
            template_string: 模板字符串
            context: 模板上下文变量

        Returns:
            渲染后的字符串
        """
        if context is None:
            context = {}

        template = self.env.from_string(template_string)
        return template.render(**context)


def load_template_file(template_path: str, context: Optional[Dict[str, Any]] = None) -> str:
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
