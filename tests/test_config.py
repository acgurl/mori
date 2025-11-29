"""配置模块测试"""

import os

import pytest
from pydantic import ValidationError

from mori.config import (
    AgentConfig,
    Config,
    GlobalConfig,
    ModelConfig,
    ServerConfig,
    get_agent_config,
    get_model_config,
)


def test_model_config():
    """测试模型配置"""
    config = ModelConfig(
        model_name="gpt-4",
        model_type="openai",
        api_key="test-key",
        generate_kwargs={"temperature": 0.7},
    )

    assert config.model_name == "gpt-4"
    assert config.model_type == "openai"
    assert config.api_key == "test-key"
    assert config.generate_kwargs["temperature"] == 0.7


def test_model_config_env_var():
    """测试环境变量解析"""
    os.environ["TEST_API_KEY"] = "env-key"

    config = ModelConfig(model_name="gpt-4", model_type="openai", api_key="${TEST_API_KEY}")

    assert config.api_key == "env-key"

    del os.environ["TEST_API_KEY"]


def test_agent_config():
    """测试Agent配置"""
    config = AgentConfig(
        name="mori",
        model="gpt-4",
        template="internal_template/mori.jinja2",
        parallel_tool_calls=True,
    )

    assert config.name == "mori"
    assert config.model == "gpt-4"
    assert config.parallel_tool_calls is True


def test_global_config():
    """测试全局配置"""
    config = GlobalConfig(log_level="DEBUG", log_dir="test_logs")

    assert config.log_level == "DEBUG"
    assert config.log_dir == "test_logs"


def test_global_config_defaults():
    """测试全局配置默认值"""
    config = GlobalConfig()

    assert config.log_level == "INFO"
    assert config.log_dir == "logs"


def test_server_config():
    """测试服务器配置"""
    config = ServerConfig(host="127.0.0.1", port=8080, share=True)

    assert config.host == "127.0.0.1"
    assert config.port == 8080
    assert config.share is True


def test_config():
    """测试完整配置"""
    config = Config(
        models=[ModelConfig(model_name="gpt-4", model_type="openai", api_key="test-key")],
        agents=[AgentConfig(name="mori", model="gpt-4", template="internal_template/mori.jinja2")],
    )

    assert len(config.models) == 1
    assert len(config.agents) == 1
    assert config.models[0].model_name == "gpt-4"
    assert config.agents[0].name == "mori"


def test_get_model_config():
    """测试获取模型配置"""
    config = Config(
        models=[
            ModelConfig(model_name="gpt-4", model_type="openai", api_key="test-key"),
            ModelConfig(model_name="gpt-3.5-turbo", model_type="openai", api_key="test-key"),
        ],
        agents=[AgentConfig(name="mori", model="gpt-4", template="internal_template/mori.jinja2")],
    )

    model = get_model_config(config, "gpt-4")
    assert model is not None
    assert model.model_name == "gpt-4"

    model = get_model_config(config, "non-existent")
    assert model is None


def test_get_agent_config():
    """测试获取Agent配置"""
    config = Config(
        models=[ModelConfig(model_name="gpt-4", model_type="openai", api_key="test-key")],
        agents=[
            AgentConfig(name="mori", model="gpt-4", template="internal_template/mori.jinja2"),
            AgentConfig(
                name="assistant",
                model="gpt-4",
                template="internal_template/assistant.jinja2",
            ),
        ],
    )

    agent = get_agent_config(config, "mori")
    assert agent is not None
    assert agent.name == "mori"

    agent = get_agent_config(config, "non-existent")
    assert agent is None


def test_config_validation_error():
    """测试配置验证错误"""
    with pytest.raises(ValidationError):
        # 缺少必需字段
        ModelConfig(model_name="gpt-4")  # type: ignore
