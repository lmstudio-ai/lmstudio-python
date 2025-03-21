"""Conversion between dicts/public config structs and server KVConfig(Stack)s."""

# Known KV config settings are defined in
# https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-kv-config/src/schema.ts
from dataclasses import dataclass
from typing import Any, Container, Iterable, Sequence, Type, TypeAlias, TypeVar, cast

from .sdk_api import LMStudioValueError
from .schemas import DictObject, DictSchema, ModelSchema, MutableDictObject
from ._sdk_models import (
    EmbeddingLoadModelConfig,
    EmbeddingLoadModelConfigDict,
    KvConfig,
    KvConfigFieldDict,
    KvConfigStack,
    KvConfigStackLayerDict,
    LlmLoadModelConfig,
    LlmLoadModelConfigDict,
    LlmPredictionConfig,
    LlmPredictionConfigDict,
    LlmStructuredPredictionSetting,
    LlmStructuredPredictionSettingDict,
)


@dataclass(frozen=True)
class ConfigField:
    client_key: str

    def to_kv_field(
        self, server_key: str, client_config: DictObject
    ) -> KvConfigFieldDict | None:
        return {
            "key": server_key,
            "value": client_config[self.client_key],
        }

    def update_client_config(
        self, client_config: MutableDictObject, value: Any
    ) -> None:
        client_config[self.client_key] = value


@dataclass(frozen=True)
class CheckboxField(ConfigField):
    def to_kv_field(
        self, server_key: str, client_config: DictObject
    ) -> KvConfigFieldDict | None:
        return {
            "key": server_key,
            "value": {"checked": True, "value": client_config[self.client_key]},
        }

    def update_client_config(
        self, client_config: MutableDictObject, value: DictObject
    ) -> None:
        if value.get("key", False):
            client_config[self.client_key] = value["value"]


@dataclass(frozen=True)
class NestedKeyField(ConfigField):
    nested_key: str

    def to_kv_field(
        self, server_key: str, client_config: DictObject
    ) -> KvConfigFieldDict | None:
        containing_value = client_config[self.client_key]
        nested_key = self.nested_key
        if nested_key not in containing_value:
            return None
        return {
            "key": server_key,
            "value": containing_value[nested_key],
        }

    def update_client_config(
        self, client_config: MutableDictObject, value: Any
    ) -> None:
        containing_value = client_config.setdefault(self.client_key, {})
        containing_value[self.nested_key] = value


@dataclass(frozen=True)
class MultiPartField(ConfigField):
    nested_keys: tuple[str, ...]

    def to_kv_field(
        self, server_key: str, client_config: DictObject
    ) -> KvConfigFieldDict | None:
        containing_value = client_config[self.client_key]
        value: dict[str, Any] = {}
        for key in self.nested_keys:
            value[key] = containing_value[key]
        return {
            "key": server_key,
            "value": value,
        }

    def update_client_config(
        self, client_config: MutableDictObject, value: DictObject
    ) -> None:
        containing_value = client_config.setdefault(self.client_key, {})
        for key in self.nested_keys:
            if key in value:
                containing_value[key] = value[key]


# TODO: figure out a way to compare this module against the lmstudio-js mappings
# TODO: Define a JSON or TOML data file for mapping prediction config
#       fields to config stack entries (preferably JSON exported by
#       lmstudio-js rather than something maintained in the Python SDK)
#       https://github.com/lmstudio-ai/lmstudio-js/issues/253
_COMMON_LLAMA_LOAD_KEYS: DictObject = {
    "keepModelInMemory": ConfigField("keepModelInMemory"),
    "ropeFrequencyBase": CheckboxField("ropeFrequencyBase"),
    "ropeFrequencyScale": CheckboxField("ropeFrequencyScale"),
    "tryMmap": ConfigField("tryMmap"),
    "acceleration": {
        "offloadRatio": NestedKeyField("gpu", "ratio"),
    },
}

_COMMON_MODEL_LOAD_KEYS: DictObject = {
    "contextLength": ConfigField("contextLength"),
}

SUPPORTED_SERVER_KEYS: dict[str, DictObject] = {
    "load": {
        "gpuSplitConfig": MultiPartField(
            "gpu", ("mainGpu", "splitStrategy", "disabledGpus")
        ),
        "gpuStrictVramCap": ConfigField("gpuStrictVramCap"),
    },
    "embedding.load": {
        **_COMMON_MODEL_LOAD_KEYS,
        "llama": _COMMON_LLAMA_LOAD_KEYS,
    },
    "llm.load": {
        **_COMMON_MODEL_LOAD_KEYS,
        "numExperts": ConfigField("numExperts"),
        "seed": CheckboxField("seed"),
        "llama": {
            **_COMMON_LLAMA_LOAD_KEYS,
            "evalBatchSize": ConfigField("evalBatchSize"),
            "flashAttention": ConfigField("flashAttention"),
            "llamaKCacheQuantizationType": CheckboxField("llamaKCacheQuantizationType"),
            "llamaVCacheQuantizationType": CheckboxField("llamaVCacheQuantizationType"),
            "useFp16ForKVCache": ConfigField("useFp16ForKVCache"),
        },
    },
    "llm.prediction": {
        "contextOverflowPolicy": ConfigField("contextOverflowPolicy"),
        "maxPredictedTokens": CheckboxField("maxTokens"),  # Shorter name in client API
        "minPSampling": CheckboxField("minPSampling"),
        "promptTemplate": ConfigField("promptTemplate"),
        "repeatPenalty": CheckboxField("repeatPenalty"),
        "stopStrings": ConfigField("stopStrings"),
        "structured": ConfigField("structured"),
        "temperature": ConfigField("temperature"),
        "toolCallStopStrings": ConfigField("toolCallStopStrings"),
        "tools": ConfigField("rawTools"),  # Encourage calling .act() instead
        "topKSampling": ConfigField("topKSampling"),
        "topPSampling": CheckboxField("topPSampling"),
        "llama": {
            # Nested KV structure is flattened in client API
            "cpuThreads": ConfigField("cpuThreads"),
        },
        "reasoning": {
            # Nested KV structure is flattened in client API
            "parsing": ConfigField("reasoningParsing"),
        },
        "speculativeDecoding": {
            # Nested KV structure is flattened in client API
            "draftModel": ConfigField("draftModel"),
            "minDraftLengthToConsider": ConfigField(
                "speculativeDecodingMinDraftLengthToConsider"
            ),
            "minContinueDraftingProbability": ConfigField(
                "speculativeDecodingMinContinueDraftingProbability"
            ),
            "numDraftTokensExact": ConfigField(
                "speculativeDecodingNumDraftTokensExact"
            ),
        },
    },
}


# Define mappings to translate server KV configs to client config instances
def _iter_server_keys(
    *namespaces: str, excluded: Container[str] = ()
) -> Iterable[tuple[str, ConfigField]]:
    # Map dotted config field names to their client config field counterparts
    for namespace in namespaces:
        scopes: list[tuple[str, DictObject]] = [
            (namespace, SUPPORTED_SERVER_KEYS[namespace])
        ]
        for prefix, scope in scopes:
            for k, v in scope.items():
                if k in excluded:
                    # 'load' config namespace currently includes some LLM-only config keys
                    continue
                prefixed_key = f"{prefix}.{k}" if prefix else k
                if isinstance(v, ConfigField):
                    yield prefixed_key, v
                else:
                    assert isinstance(v, dict)
                    scopes.append((prefixed_key, v))


FROM_SERVER_LOAD_LLM = dict(_iter_server_keys("load", "llm.load"))
FROM_SERVER_LOAD_EMBEDDING = dict(
    _iter_server_keys("load", "embedding.load", excluded="gpuStrictVramCap")
)
FROM_SERVER_PREDICTION = dict(_iter_server_keys("llm.prediction"))
FROM_SERVER_CONFIG = dict(_iter_server_keys(*SUPPORTED_SERVER_KEYS))


# Define mappings to translate client config instances to server KV configs
FromServerKeymap = dict[str, ConfigField]
ToServerKeymap = dict[str, list[tuple[str, ConfigField]]]


def _invert_config_keymap(from_server: FromServerKeymap) -> ToServerKeymap:
    to_server: ToServerKeymap = {}
    for server_key, config_field in sorted(from_server.items()):
        client_key = config_field.client_key
        # There's at least one client field (gpu) which maps to
        # multiple KV config fields, so don't expect a 1:1 mapping
        config_fields = to_server.setdefault(client_key, [])
        config_fields.append((server_key, config_field))
    return to_server


TO_SERVER_LOAD_LLM = _invert_config_keymap(FROM_SERVER_LOAD_LLM)
TO_SERVER_LOAD_EMBEDDING = _invert_config_keymap(FROM_SERVER_LOAD_EMBEDDING)
TO_SERVER_PREDICTION = _invert_config_keymap(FROM_SERVER_PREDICTION)


TLoadConfig = TypeVar("TLoadConfig", LlmLoadModelConfig, EmbeddingLoadModelConfig)
TLoadConfigDict = TypeVar(
    "TLoadConfigDict", LlmLoadModelConfigDict, EmbeddingLoadModelConfigDict
)


def dict_from_kvconfig(config: KvConfig) -> DictObject:
    return {kv.key: kv.value for kv in config.fields}


def parse_server_config(server_config: DictObject) -> DictObject:
    """Map server config fields to client config fields."""
    result: MutableDictObject = {}
    for kv in server_config.get("fields", []):
        key = kv["key"]
        config_field = FROM_SERVER_CONFIG.get(key, None)
        if config_field is None:
            # Skip unknown keys (server might be newer than the SDK)
            continue
        value = kv["value"]
        config_field.update_client_config(result, value)
    return result


def parse_llm_load_config(server_config: DictObject) -> LlmLoadModelConfig:
    return LlmLoadModelConfig._from_any_api_dict(parse_server_config(server_config))


def parse_prediction_config(server_config: DictObject) -> LlmPredictionConfig:
    return LlmPredictionConfig._from_any_api_dict(parse_server_config(server_config))


def _api_override_kv_config_stack(
    fields: list[KvConfigFieldDict],
    additional_layers: Sequence[KvConfigStackLayerDict] = (),
) -> KvConfigStack:
    return KvConfigStack._from_api_dict(
        {
            "layers": [
                {
                    "layerName": "apiOverride",
                    "config": {
                        "fields": fields,
                    },
                },
                *additional_layers,
            ],
        }
    )


def _to_kv_config_stack_base(
    config: DictObject, keymap: ToServerKeymap
) -> list[KvConfigFieldDict]:
    fields: list[KvConfigFieldDict] = []
    remaining_keys = set(config.keys())
    for client_key, config_fields in keymap.items():
        if client_key not in config:
            continue
        remaining_keys.remove(client_key)
        for server_key, config_field in config_fields:
            kv_field = config_field.to_kv_field(server_key, config)
            if kv_field is not None:
                fields.append(kv_field)
    if remaining_keys:
        raise LMStudioValueError(f"Unknown config settings: {sorted(remaining_keys)}")
    return fields


def _client_config_to_kv_config_stack(
    config: DictObject, keymap: ToServerKeymap
) -> KvConfigStack:
    fields = _to_kv_config_stack_base(config, keymap)
    return _api_override_kv_config_stack(fields)


def load_config_to_kv_config_stack(
    config: TLoadConfig | DictObject | None, config_type: Type[TLoadConfig]
) -> KvConfigStack:
    """Helper to convert load configs to KvConfigStack instances with strict typing."""
    dict_config: DictObject
    if config is None:
        dict_config = {}
    elif isinstance(config, config_type):
        dict_config = config.to_dict()
    else:
        assert isinstance(config, dict)
        dict_config = config_type._from_any_dict(config).to_dict()
    if config_type is LlmLoadModelConfig:
        return _client_config_to_kv_config_stack(dict_config, TO_SERVER_LOAD_LLM)
    assert config_type is EmbeddingLoadModelConfig
    return _client_config_to_kv_config_stack(dict_config, TO_SERVER_LOAD_EMBEDDING)


ResponseSchema: TypeAlias = (
    DictSchema
    | LlmStructuredPredictionSetting
    | LlmStructuredPredictionSettingDict
    | type[ModelSchema]
)


def prediction_config_to_kv_config_stack(
    response_format: Type[ModelSchema] | ResponseSchema | None,
    config: LlmPredictionConfig | LlmPredictionConfigDict | None,
    for_text_completion: bool = False,
) -> tuple[bool, KvConfigStack]:
    dict_config: LlmPredictionConfigDict
    if config is None:
        dict_config = {}
    elif isinstance(config, LlmPredictionConfig):
        dict_config = config.to_dict()
    else:
        assert isinstance(config, dict)
        dict_config = LlmPredictionConfig._from_any_dict(config).to_dict()
    if response_format is not None:
        if "structured" in dict_config:
            raise LMStudioValueError(
                "Cannot specify both 'response_format' in API call and 'structured' in config"
            )
        response_schema: LlmStructuredPredictionSettingDict
        structured = True
        if isinstance(response_format, LlmStructuredPredictionSetting):
            response_schema = response_format.to_dict()
        elif isinstance(response_format, type) and issubclass(
            response_format, ModelSchema
        ):
            response_schema = {
                "type": "json",
                "jsonSchema": response_format.model_json_schema(),
            }
        else:
            # Casts are needed as mypy doesn't detect that the given case patterns
            # conform to the definition of LlmStructuredPredictionSettingDict
            match response_format:
                case {"type": "json", "jsonSchema": _} as json_schema:
                    response_schema = cast(
                        LlmStructuredPredictionSettingDict, json_schema
                    )
                case {"type": "gbnf", "gbnfGrammar": _} as gbnf_schema:
                    response_schema = cast(
                        LlmStructuredPredictionSettingDict, gbnf_schema
                    )
                case {"type": _}:
                    # Assume any other input with a type key is a JSON schema definition
                    response_schema = {
                        "type": "json",
                        "jsonSchema": response_format,
                    }
                case _:
                    raise LMStudioValueError(
                        f"Failed to parse response format: {response_format!r}"
                    )
        dict_config["structured"] = response_schema
    else:
        # The response schema may also be passed in via the config
        # (doing it this way type hints as an unstructured result,
        # but we still allow it at runtime for consistency with JS)
        match dict_config:
            case {"structured": {"type": "json" | "gbnf"}}:
                structured = True
            case _:
                structured = False
    fields = _to_kv_config_stack_base(dict_config, TO_SERVER_PREDICTION)
    additional_layers: list[KvConfigStackLayerDict] = []
    if for_text_completion:
        additional_layers.append(_get_completion_config_layer())
    return structured, _api_override_kv_config_stack(fields, additional_layers)


def _get_completion_config_layer() -> KvConfigStackLayerDict:
    """Config layer to request text completion instead of a chat response."""
    # There is only one prediction endpoint in the LM Studio API, and it defaults to chat responses
    jinja_template = "{% for message in messages %}{{ message['content'] }}{% endfor %}"
    jinja_config = {
        "messagesConfig": {
            "contentConfig": {
                "type": "string",
            },
        },
        "useTools": False,
    }
    return {
        "layerName": "completeModeFormatting",
        "config": {
            "fields": [
                {
                    "key": "llm.prediction.promptTemplate",
                    "value": {
                        "type": "jinja",
                        "jinjaPromptTemplate": {
                            "bosToken": "",
                            "eosToken": "",
                            "template": jinja_template,
                            "inputConfig": jinja_config,
                        },
                        "stopStrings": [],
                    },
                }
            ],
        },
    }
