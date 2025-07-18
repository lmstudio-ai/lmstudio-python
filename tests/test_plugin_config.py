"""Test plugin config schema definitions."""

from lmstudio.plugin import BaseConfigSchema, config_field


def test_empty_config() -> None:
    class ConfigSchema(BaseConfigSchema):
        pass

    assert ConfigSchema._to_kv_config_schematics() is None


def test_config_field_bool() -> None:
    class ConfigSchema(BaseConfigSchema):
        setting: bool = config_field(label="UI label", hint="UI tooltip", default=True)

    assert ConfigSchema.setting is True
    assert ConfigSchema().setting is True
    kv_config_schematics = ConfigSchema._to_kv_config_schematics()
    assert kv_config_schematics is not None
    expected_kv_config_schematics = {
        "fields": [
            {
                "defaultValue": True,
                "fullKey": "setting",
                "shortKey": "setting",
                "typeKey": "boolean",
                "typeParams": {
                    "displayName": "UI label",
                    "hint": "UI tooltip",
                },
            }
        ]
    }
    assert kv_config_schematics.to_dict() == expected_kv_config_schematics


def test_config_field_int() -> None:
    class ConfigSchema(BaseConfigSchema):
        setting: int = config_field(label="UI label", hint="UI tooltip", default=42)

    assert ConfigSchema.setting == 42
    assert ConfigSchema.setting == 42
    kv_config_schematics = ConfigSchema._to_kv_config_schematics()
    assert kv_config_schematics is not None
    expected_kv_config_schematics = {
        "fields": [
            {
                "defaultValue": 42,
                "fullKey": "setting",
                "shortKey": "setting",
                "typeKey": "numeric",
                "typeParams": {
                    "displayName": "UI label",
                    "hint": "UI tooltip",
                    "int": True,
                },
            }
        ]
    }
    assert kv_config_schematics.to_dict() == expected_kv_config_schematics


def test_config_field_float() -> None:
    class ConfigSchema(BaseConfigSchema):
        setting: float = config_field(label="UI label", hint="UI tooltip", default=4.2)

    assert ConfigSchema.setting == 4.2
    assert ConfigSchema().setting == 4.2
    kv_config_schematics = ConfigSchema._to_kv_config_schematics()
    assert kv_config_schematics is not None
    expected_kv_config_schematics = {
        "fields": [
            {
                "defaultValue": 4.2,
                "fullKey": "setting",
                "shortKey": "setting",
                "typeKey": "numeric",
                "typeParams": {
                    "displayName": "UI label",
                    "hint": "UI tooltip",
                    "int": False,
                },
            }
        ]
    }
    assert kv_config_schematics.to_dict() == expected_kv_config_schematics


def test_config_field_str() -> None:
    class ConfigSchema(BaseConfigSchema):
        setting: str = config_field(label="UI label", hint="UI tooltip", default="text")

    assert ConfigSchema.setting == "text"
    assert ConfigSchema().setting == "text"
    kv_config_schematics = ConfigSchema._to_kv_config_schematics()
    assert kv_config_schematics is not None
    expected_kv_config_schematics = {
        "fields": [
            {
                "defaultValue": "text",
                "fullKey": "setting",
                "shortKey": "setting",
                "typeKey": "string",
                "typeParams": {
                    "displayName": "UI label",
                    "hint": "UI tooltip",
                },
            }
        ]
    }
    assert kv_config_schematics.to_dict() == expected_kv_config_schematics
