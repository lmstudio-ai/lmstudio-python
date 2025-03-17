"""Conversion between dicts/public config structs and server KVConfig(Stack)s."""

# Known KV config settings are defined in
# https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-kv-config/src/schema.ts
from typing import Any, Sequence, Type, TypeVar

from .sdk_api import LMStudioValueError
from .schemas import DictSchema, DictObject, ModelSchema
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
)

# TODO we can reasonably add unit tests for this module: compare against lmstudio-js?


TLoadConfig = TypeVar("TLoadConfig", LlmLoadModelConfig, EmbeddingLoadModelConfig)
TLoadConfigDict = TypeVar(
    "TLoadConfigDict", LlmLoadModelConfigDict, EmbeddingLoadModelConfigDict
)


def dict_from_kvconfig(config: KvConfig) -> DictObject:
    return {kv.key: kv.value for kv in config.fields}


def dict_from_fields_key(config: DictObject) -> DictObject:
    return {kv["key"]: kv["value"] for kv in config.get("fields", [])}


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


def _to_simple_kv(prefix: str, key: str, value: Any) -> KvConfigFieldDict:
    return {
        "key": f"{prefix}.{key}",
        "value": value,
    }


def _to_checkbox_kv(prefix: str, key: str, value: Any) -> KvConfigFieldDict:
    return {
        "key": f"{prefix}.{key}",
        "value": {
            "checked": True,
            "value": value,
        },
    }


def _gpu_offload_fields(
    endpoint: str,
    offload_settings: DictObject,
) -> Sequence[KvConfigFieldDict]:
    fields: list[KvConfigFieldDict] = []
    remaining_keys = set(offload_settings.keys())
    simple_gpu_keys = (("ratio", f"{endpoint}.load.llama.acceleration.offloadRatio"),)
    for key, mapped_key in simple_gpu_keys:
        if key in offload_settings:
            remaining_keys.remove(key)
            fields.append({"key": mapped_key, "value": offload_settings[key]})
    split_config_keys = ("mainGpu", "splitStrategy", "disabledGpus")
    split_config_settings: dict[str, Any] = {}
    for key in split_config_keys:
        if key in offload_settings:
            remaining_keys.remove(key)
            split_config_settings[key] = offload_settings[key]
    if split_config_settings:
        fields.append({"key": "load.gpuSplitConfig", "value": split_config_settings})
    if remaining_keys:
        raise LMStudioValueError(
            f"Unknown GPU offload settings: {sorted(remaining_keys)}"
        )
    return fields


# Some fields have different names in the client and server configs
# (this map has also been used to avoid adding new key categories for new setting scopes)
_CLIENT_TO_SERVER_KEYMAP = {
    "maxTokens": "maxPredictedTokens",
    "rawTools": "tools",
    # "reasoning" scope
    "reasoningParsing": "reasoning.parsing",
    # "speculativeDecoding" scope
    "draftModel": "speculativeDecoding.draftModel",
    "speculativeDecodingNumDraftTokensExact": "speculativeDecoding.numDraftTokensExact",
    "speculativeDecodingMinDraftLengthToConsider": "speculativeDecoding.minDraftLengthToConsider",
    "speculativeDecodingMinContinueDraftingProbability": "speculativeDecoding.minContinueDraftingProbability",
}


def _to_server_key(key: str) -> str:
    return _CLIENT_TO_SERVER_KEYMAP.get(key, key)


_NOT_YET_SUPPORTED_KEYS: set[str] = set()


def _to_kv_config_stack_base(
    config: DictObject,
    namespace: str,
    request: str,
    /,
    checkbox_keys: Sequence[str],
    simple_keys: Sequence[str],
    llama_keys: Sequence[str],
    llama_checkbox_keys: Sequence[str],
    gpu_offload_keys: Sequence[str] = (),
) -> list[KvConfigFieldDict]:
    fields: list[KvConfigFieldDict] = []
    # TODO: Define a JSON or TOML data file for mapping prediction config
    #       fields to config stack entries (preferably JSON exported by
    #       lmstudio-js rather than something maintained in the Python SDK)
    #       https://github.com/lmstudio-ai/lmstudio-js/issues/253
    remaining_keys = set(config.keys() - _NOT_YET_SUPPORTED_KEYS)

    for client_key in checkbox_keys:
        if client_key in config:
            remaining_keys.remove(client_key)
            server_key = _to_server_key(client_key)
            fields.append(
                _to_checkbox_kv(
                    f"{namespace}.{request}", server_key, config[client_key]
                )
            )
    for client_key in simple_keys:
        if client_key in config:
            remaining_keys.remove(client_key)
            server_key = _to_server_key(client_key)
            fields.append(
                _to_simple_kv(f"{namespace}.{request}", server_key, config[client_key])
            )
    for client_key in llama_keys:
        if client_key in config:
            remaining_keys.remove(client_key)
            server_key = _to_server_key(client_key)
            fields.append(
                _to_simple_kv(
                    f"{namespace}.{request}.llama", server_key, config[client_key]
                )
            )
    for client_key in llama_checkbox_keys:
        if client_key in config:
            remaining_keys.remove(client_key)
            server_key = _to_server_key(client_key)
            fields.append(
                _to_checkbox_kv(
                    f"{namespace}.{request}.llama",
                    server_key,
                    config[client_key],
                )
            )
    for gpu_offload_key in gpu_offload_keys:
        if gpu_offload_key in config:
            remaining_keys.remove(gpu_offload_key)
            fields.extend(_gpu_offload_fields(namespace, config[gpu_offload_key]))

    if remaining_keys:
        raise LMStudioValueError(f"Unknown config settings: {sorted(remaining_keys)}")

    return fields


_LLM_LOAD_CONFIG_KEYS = {
    "checkbox_keys": [
        "seed",
    ],
    "simple_keys": [
        "contextLength",
        "numExperts",
    ],
    "llama_keys": [
        "evalBatchSize",
        "flashAttention",
        "keepModelInMemory",
        "useFp16ForKVCache",
        "tryMmap",
    ],
    "llama_checkbox_keys": [
        "ropeFrequencyBase",
        "ropeFrequencyScale",
        "llamaKCacheQuantizationType",
        "llamaVCacheQuantizationType",
    ],
    "gpu_offload_keys": [
        "gpuOffload",
    ],
}


_EMBEDDING_LOAD_CONFIG_KEYS = {
    "checkbox_keys": [],
    "simple_keys": [
        "contextLength",
    ],
    "llama_keys": [
        "keepModelInMemory",
        "tryMmap",
    ],
    "llama_checkbox_keys": [
        "ropeFrequencyBase",
        "ropeFrequencyScale",
    ],
    "gpu_offload_keys": [
        "gpuOffload",
    ],
}


def _llm_load_config_to_kv_config_stack(
    config: DictObject,
) -> KvConfigStack:
    fields = _to_kv_config_stack_base(config, "llm", "load", **_LLM_LOAD_CONFIG_KEYS)
    return _api_override_kv_config_stack(fields)


def _embedding_load_config_to_kv_config_stack(
    config: DictObject,
) -> KvConfigStack:
    fields = _to_kv_config_stack_base(
        config,
        "embedding",
        "load",
        **_EMBEDDING_LOAD_CONFIG_KEYS,
    )
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
    if config_type is EmbeddingLoadModelConfig:
        return _embedding_load_config_to_kv_config_stack(dict_config)
    assert config_type is LlmLoadModelConfig
    return _llm_load_config_to_kv_config_stack(dict_config)


_PREDICTION_CONFIG_KEYS = {
    "checkbox_keys": [
        "maxTokens",
        "minPSampling",
        "repeatPenalty",
        "topPSampling",
        # "logProbs",  # Not yet supported via the SDK API
    ],
    "simple_keys": [
        "contextOverflowPolicy",
        "promptTemplate",
        "stopStrings",
        "structured",
        "temperature",
        "topKSampling",
        "toolCallStopStrings",
        "rawTools",
        "reasoningParsing",
        "draftModel",
        "speculativeDecodingNumDraftTokensExact",
        "speculativeDecodingMinDraftLengthToConsider",
        "speculativeDecodingMinContinueDraftingProbability",
    ],
    "llama_keys": [
        "cpuThreads",
    ],
    "llama_checkbox_keys": [
        # "xtcProbability",  # Not yet supported via the SDK API
        # "xtcThreshold",  # Not yet supported via the SDK API
    ],
}


def prediction_config_to_kv_config_stack(
    response_format: Type[ModelSchema] | DictSchema | None,
    config: LlmPredictionConfig | LlmPredictionConfigDict | None,
    for_text_completion: bool = False,
) -> tuple[bool, KvConfigStack]:
    dict_config: DictObject
    if config is None:
        dict_config = {}
    elif isinstance(config, LlmPredictionConfig):
        dict_config = config.to_dict()
    else:
        assert isinstance(config, dict)
        dict_config = LlmPredictionConfig._from_any_dict(config).to_dict()
    response_schema: DictSchema | None = None
    if response_format is not None:
        structured = True
        if "structured" in dict_config:
            raise LMStudioValueError(
                "Cannot specify both 'response_format' in API call and 'structured' in config"
            )
        if isinstance(response_format, type) and issubclass(
            response_format, ModelSchema
        ):
            response_schema = response_format.model_json_schema()
        else:
            response_schema = response_format
    else:
        # The response schema may also be passed in via the config
        # (doing it this way type hints as an unstructured result,
        # but we still allow it at runtime for consistency with JS)
        match dict_config:
            case {"structured": {"type": "json"}}:
                structured = True
            case _:
                structured = False
    fields = _to_kv_config_stack_base(
        dict_config,
        "llm",
        "prediction",
        **_PREDICTION_CONFIG_KEYS,
    )
    if response_schema is not None:
        fields.append(
            {
                "key": "llm.prediction.structured",
                "value": {
                    "type": "json",
                    "jsonSchema": response_schema,
                },
            }
        )
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
