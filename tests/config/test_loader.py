import pytest
from pathlib import Path
from plotly_lvlos.config.loader import load_config
from plotly_lvlos.utils.errors import ConfigError

SCENARIO_DIR = Path(__file__).parent / "scenarios"

@pytest.fixture
def valid_config_file():
    return SCENARIO_DIR / "valid" / "valid_config.toml"

def test_load_config_returns_dict(valid_config_file):
    config = load_config(valid_config_file)
    assert isinstance(config, dict)
    assert config["project"]["name"] == "test-project"


@pytest.fixture
def invalid_config_file():
    return SCENARIO_DIR / "invalid" / "invalid_config.toml"

def test_load_config_invalid_raises_config_error(invalid_config_file):
    with pytest.raises(ConfigError) as excinfo:
        load_config(invalid_config_file)
    assert "Invalid TOML config" in str(excinfo.value)


@pytest.fixture
def missing_config_file():
    return SCENARIO_DIR / "missing_file" / "not_supposed_to_exist_config.toml"

def test_load_config_missing_file_raises_config_error(missing_config_file):
    with pytest.raises(ConfigError) as excinfo:
        load_config(missing_config_file)
    assert "Config file not found" in str(excinfo.value)


def test_config_has_required_sections(valid_config_file):
    config = load_config(valid_config_file)
    required_sections = ["project", "data", "analysis", "enrichment", "visualization"]
    for section in required_sections:
        assert section in config
