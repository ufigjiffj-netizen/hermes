import os
import tempfile

import pytest
import yaml

from hermes.core.config import load_config


def test_load_config_default_only():
    config = load_config()
    assert isinstance(config, dict)
    assert config["app"]["name"] == "hermes"


def test_load_config_with_custom_yaml():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"custom_key": "custom_value", "nested": {"enabled": True}}, f)
        temp_file_name = f.name

    try:
        config = load_config(temp_file_name)
        assert config["custom_key"] == "custom_value"
        assert config["nested"]["enabled"] is True
    finally:
        os.remove(temp_file_name)


def test_load_config_merging():
    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"app": {"port": 9090}}, f)
        temp_file_name = f.name

    try:
        config = load_config(temp_file_name)
        assert config["app"]["name"] == "hermes"
        assert config["app"]["port"] == 9090
    finally:
        os.remove(temp_file_name)


def test_load_config_file_not_found():
    with pytest.raises(FileNotFoundError):
        load_config("nonexistent_file.yaml")


def test_load_config_populates_secret_store():
    from hermes.core.secrets import get_secret

    with tempfile.NamedTemporaryFile(mode="w", suffix=".yaml", delete=False) as f:
        yaml.dump({"funpay": {"golden_key": "my_secret_token"}}, f)
        temp_file_name = f.name

    try:
        load_config(temp_file_name)
        assert get_secret("golden_key") == "my_secret_token"
    finally:
        os.remove(temp_file_name)
