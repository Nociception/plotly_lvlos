def test_load_config_returns_dict(tmp_path):
    config_file = tmp_path / "config.toml"
    config_file.write_text("""
        [project]
        name = "test-project"
    """)

    from plotly_lvlos.config.loader import load_config

    config = load_config(config_file)

    assert isinstance(config, dict)
    assert config["project"]["name"] == "test-project"
