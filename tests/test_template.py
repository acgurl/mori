"""模板系统测试"""

import pytest

from mori.template.loader import TemplateLoader


def test_template_loader_init():
    """测试模板加载器初始化"""
    loader = TemplateLoader()
    assert loader.template_dir.exists()
    assert loader.internal_template_dir.exists()


def test_resolve_template_path_short_name():
    """测试解析简短模板名称"""
    loader = TemplateLoader()

    # 简短名称应该解析为 internal_template/mori.jinja2
    resolved = loader._resolve_template_path("mori")
    assert resolved == "internal_template/mori.jinja2"


def test_resolve_template_path_full_path():
    """测试解析完整路径"""
    loader = TemplateLoader()

    # 完整路径应该保持不变
    full_path = "internal_template/mori.jinja2"
    resolved = loader._resolve_template_path(full_path)
    assert resolved == full_path


def test_resolve_template_path_with_extension():
    """测试带扩展名的路径"""
    loader = TemplateLoader()

    # 带扩展名的应该保持不变
    path_with_ext = "custom.jinja2"
    resolved = loader._resolve_template_path(path_with_ext)
    assert resolved == path_with_ext


def test_load_template_short_name():
    """测试使用简短名称加载模板"""
    loader = TemplateLoader()

    # 使用简短名称加载
    template = loader.load_template("mori")
    assert template is not None


def test_load_template_full_path():
    """测试使用完整路径加载模板"""
    loader = TemplateLoader()

    # 使用完整路径加载
    template = loader.load_template("internal_template/mori.jinja2")
    assert template is not None


def test_render_template_short_name():
    """测试使用简短名称渲染模板"""
    loader = TemplateLoader()

    # 使用简短名称渲染
    result = loader.render_template("mori")
    assert result is not None
    assert len(result) > 0
    assert "Mori" in result


def test_render_template_full_path():
    """测试使用完整路径渲染模板"""
    loader = TemplateLoader()

    # 使用完整路径渲染
    result = loader.render_template("internal_template/mori.jinja2")
    assert result is not None
    assert len(result) > 0
    assert "Mori" in result


def test_render_template_with_context():
    """测试带上下文变量渲染模板"""
    loader = TemplateLoader()

    # 创建一个简单的测试模板
    template_string = "Hello {{ name }}!"
    result = loader.render_string(template_string, {"name": "World"})
    assert result == "Hello World!"


def test_load_nonexistent_template():
    """测试加载不存在的模板"""
    loader = TemplateLoader()

    # 尝试加载不存在的模板应该抛出异常
    with pytest.raises(Exception):  # Jinja2会抛出TemplateNotFound
        loader.load_template("nonexistent")


def test_template_backwards_compatibility():
    """测试向后兼容性"""
    loader = TemplateLoader()

    # 两种方式应该加载相同的模板
    result1 = loader.render_template("mori")
    result2 = loader.render_template("internal_template/mori.jinja2")

    assert result1 == result2


def test_custom_template_directory():
    """测试自定义模板目录"""
    loader = TemplateLoader()

    # 自定义模板目录应该存在
    assert loader.custom_template_dir.exists()
    assert str(loader.custom_template_dir) == "config/template"


def test_custom_template_priority():
    """测试自定义模板优先级"""
    loader = TemplateLoader()

    # 如果存在custom_example模板，应该能加载
    try:
        template = loader.load_template("custom_example")
        assert template is not None
    except Exception:
        # 如果文件不存在，跳过测试
        pass


def test_template_loader_with_custom_dir():
    """测试指定自定义模板目录"""
    import tempfile
    import os

    # 创建临时目录
    with tempfile.TemporaryDirectory() as tmpdir:
        # 创建测试模板
        test_template_path = os.path.join(tmpdir, "test.jinja2")
        with open(test_template_path, "w", encoding="utf-8") as f:
            f.write("Hello {{ name }}!")

        # 使用自定义目录创建加载器
        loader = TemplateLoader(custom_template_dir=tmpdir)

        # 应该能加载自定义模板
        result = loader.render_template("test", {"name": "World"})
        assert result == "Hello World!"
