"""
Declarative schema for the expected structure of a config.toml file.

This module defines the *closed* and *normative* structure of the
configuration file used by plotly_lvlos.

The schema is expressed as a nested dictionary whose keys represent
**the complete and exact set** of required sections and sub-sections.
No additional sections or keys are allowed beyond what is defined here.

The values in the schema are example values whose sole purpose is to
define the expected types and structure of each field.

This schema serves as:
- a single source of truth for configuration structure
- a reference for validation logic
- a shared contract between code, tests, and documentation

STRICTNESS:
- All sections and keys defined here are mandatory
- No extra sections or keys are allowed
- Missing or unexpected entries must be treated as configuration errors
- Extra_data fields can be optional if not needed for a given analysis

IMPORTANT:
- This is NOT runtime configuration
- This is NOT user-provided data
- This is NOT meant to be mutated at runtime
"""

CONFIG_TOML_DICT_SCHEMA = {
    "project": {
        "name": "plotly-lvlos",  # str
        "description": """
        Animated comparison of linear
        vs logarithmic x-scale effects
        """,  # str
        "output_dir": "build",  # str
    },
    "data": {
        "x_file": "data/x.csv",  # str
        "y_file": "data/y.csv",  # str
        "extra_data_point_file": "data/edpf.csv",  # str
        "extra_data_x_file": "data/edxf.csv",  # str
        "entity_column": "country",  # str
        "overlap_column": "year",  # str
        "overlap_start": 1800,  # int
        "overlap_end": 2050,  # int
    },
    "analysis": {
        "min_points_per_year": 5,  # int
    },
    "visualization": {
        "width": 1200,  # int
        "height": 800,  # int
        "frame_duration_ms": 300,  # int
        "transition_duration_ms": 0,  # int
    },
}

CONFIG_TOML_DICT_SCHEMA_CONSTRAINTS = {
    "project": {
        "name": {
            "type": str,
            "len_min": 1,
            "len_max": 100,
            "strip": True,
        },
        "description": {
            "type": str,
            "len_min": 1,
            "len_max": 5000,
            "strip": True,
        },
        "output_dir": {
            "type": str,
            "len_min": 1,
            "len_max": 255,
            "strip": True,
        },
    },
    "data": {
        "x_file": {
            "type": str,
            "len_min": 1,
            "len_max": 255,
            "strip": True,
        },
        "y_file": {
            "type": str,
            "len_min": 1,
            "len_max": 255,
            "strip": True,
        },
        "extra_data_point_file": {
            "type": str,
            "len_min": 0,
            "len_max": 255,
            "strip": True,
        },
        "extra_data_x_file": {
            "type": str,
            "len_min": 0,
            "len_max": 255,
            "strip": True,
        },
        "entity_column": {
            "type": str,
            "len_min": 1,
            "len_max": 100,
            "strip": True,
        },
        "overlap_column": {
            "type": str,
            "len_min": 1,
            "len_max": 100,
            "strip": True,
        },
        "overlap_start": {"type": int},
        "overlap_end": {
            "type": int,
        },
    },
    "analysis": {
        "min_points_per_year": {
            "type": int,
            "min": 2,
            "max": 100,
        },
    },
    "visualization": {
        "width": {
            "type": int,
            "min": 100,
            "max": 10000,
        },
        "height": {
            "type": int,
            "min": 100,
            "max": 10000,
        },
        "frame_duration_ms": {
            "type": int,
            "min": 10,
            "max": 10000,
        },
        "transition_duration_ms": {
            "type": int,
            "min": 0,
            "max": 10000,
        },
    },
}
