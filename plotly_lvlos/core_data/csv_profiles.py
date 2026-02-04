CSV_PROFILES: dict[str, dict] = {
    "clean": {
        "strict_mode": True,
        "parallel": True,
    },
    "dusty": {
        "strict_mode": False,
        "null_padding": True,
        "parallel": False,
    },
}
