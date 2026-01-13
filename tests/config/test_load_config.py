from plotly_lvlos.config.load_config import load_config
from plotly_lvlos.utils.errors import ConfigError


def test_load_config_returns_empty_dict_for_empty_file(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("")

    result = None
    error_raised = False

    try:
        result = load_config(config_file)
    except ConfigError:
        error_raised = True

    assert error_raised is False
    assert isinstance(result, dict)
    assert result == {}
