"""Test translation from flat dict configs to KvConfig layer stacks."""

from typing import Any

import msgspec

import pytest

from lmstudio import BaseModel, DictObject, LMStudioValueError
from lmstudio.schemas import LMStudioStruct
from lmstudio._kv_config import (
    ToServerKeymap,
    TO_SERVER_LOAD_EMBEDDING,
    TO_SERVER_LOAD_LLM,
    TO_SERVER_PREDICTION,
    load_config_to_kv_config_stack,
    prediction_config_to_kv_config_stack,
)
from lmstudio._sdk_models import (
    EmbeddingLoadModelConfig,
    EmbeddingLoadModelConfigDict,
    GpuSetting,
    GpuSettingDict,
    LlmLoadModelConfig,
    LlmLoadModelConfigDict,
    LlmPredictionConfig,
    LlmPredictionConfigDict,
)

# Note: configurations below are just for data manipulation round-trip testing,
#       so they don't necessarily make sense as actual model configurations

GPU_CONFIG: GpuSettingDict = {
    "mainGpu": 0,
    "ratio": 0.5,
    "splitStrategy": "evenly",
    "disabledGpus": [1, 2],
}
SC_GPU_CONFIG = {
    "main_gpu": 0,
    "ratio": 0.5,
    "split_strategy": "evenly",
    "disabled_gpus": [1, 2],
}

LOAD_CONFIG_EMBEDDING: EmbeddingLoadModelConfigDict = {
    "contextLength": 1978,
    "gpu": GPU_CONFIG,
    "keepModelInMemory": True,
    "ropeFrequencyBase": 10.0,
    "ropeFrequencyScale": 1.5,
    "tryMmap": False,
}

SC_LOAD_CONFIG_EMBEDDING = {
    "context_length": 1978,
    "gpu": SC_GPU_CONFIG,
    "keep_model_in_memory": True,
    "rope_frequency_base": 10.0,
    "rope_frequency_scale": 1.5,
    "try_mmap": False,
}

LOAD_CONFIG_LLM: LlmLoadModelConfigDict = {
    "contextLength": 1978,
    "evalBatchSize": 42,
    "flashAttention": False,
    "gpu": GPU_CONFIG,
    "gpuStrictVramCap": False,
    "keepModelInMemory": True,
    "llamaKCacheQuantizationType": "q8_0",
    "llamaVCacheQuantizationType": "f32",
    "numExperts": 0,
    "ropeFrequencyBase": 10.0,
    "ropeFrequencyScale": 1.5,
    "seed": 313,
    "tryMmap": False,
    "useFp16ForKVCache": True,
}

SC_LOAD_CONFIG_LLM = {
    "context_length": 1978,
    "eval_batch_size": 42,
    "flash_attention": False,
    "gpu": SC_GPU_CONFIG,
    "gpu_strict_vram_cap": False,
    "keep_model_in_memory": True,
    "llama_k_cache_quantization_type": "q8_0",
    "llama_v_cache_quantization_type": "f32",
    "num_experts": 0,
    "rope_frequency_base": 10.0,
    "rope_frequency_scale": 1.5,
    "seed": 313,
    "try_mmap": False,
    "use_fp16_for_kv_cache": True,
}

PREDICTION_CONFIG: LlmPredictionConfigDict = {
    "contextOverflowPolicy": "rollingWindow",
    "cpuThreads": 7,
    "draftModel": "some-model-key",
    "maxTokens": 1234,
    "minPSampling": 5.5,
    "promptTemplate": {
        "type": "manual",
        "stopStrings": ["Nevermore"],
        "manualPromptTemplate": {
            "beforeSystem": "example prefix",
            "afterSystem": "example suffix",
            "beforeUser": "example prefix",
            "afterUser": "example suffix",
            "beforeAssistant": "example prefix",
            "afterAssistant": "example suffix",
        },
    },
    "reasoningParsing": {"enabled": False, "startString": "", "endString": ""},
    "repeatPenalty": 6.5,
    "speculativeDecodingNumDraftTokensExact": 2,
    "speculativeDecodingMinDraftLengthToConsider": 5,
    "speculativeDecodingMinContinueDraftingProbability": 0.1,
    "stopStrings": ["Banana!"],
    "structured": {"type": "json", "jsonSchema": {"type": "string"}},
    "temperature": 2.5,
    "toolCallStopStrings": ["yellow"],
    "rawTools": {"type": "none"},
    "topKSampling": 3.5,
    "topPSampling": 4.5,
}

SC_PREDICTION_CONFIG = {
    "context_overflow_policy": "rollingWindow",
    "cpu_threads": 7,
    "draft_model": "some-model-key",
    "max_tokens": 1234,
    "min_p_sampling": 5.5,
    "prompt_template": {
        "type": "manual",
        "stop_strings": ["Nevermore"],
        "manual_prompt_template": {
            "before_system": "example prefix",
            "after_system": "example suffix",
            "before_user": "example prefix",
            "after_user": "example suffix",
            "before_assistant": "example prefix",
            "after_assistant": "example suffix",
        },
    },
    "reasoning_parsing": {"enabled": False, "start_string": "", "end_string": ""},
    "repeat_penalty": 6.5,
    "speculative_decoding_num_draft_tokens_exact": 2,
    "speculative_decoding_min_draft_length_to_consider": 5,
    "speculative_decoding_min_continue_drafting_probability": 0.1,
    "stop_strings": ["Banana!"],
    "structured": {"type": "json", "json_schema": {"type": "string"}},
    "temperature": 2.5,
    "tool_call_stop_strings": ["yellow"],
    "raw_tools": {"type": "none"},
    "top_k_sampling": 3.5,
    "top_p_sampling": 4.5,
}


CONFIG_DICTS = (
    GPU_CONFIG,
    LOAD_CONFIG_EMBEDDING,
    LOAD_CONFIG_LLM,
    PREDICTION_CONFIG,
)

SC_DICTS = (
    SC_GPU_CONFIG,
    SC_LOAD_CONFIG_EMBEDDING,
    SC_LOAD_CONFIG_LLM,
    SC_PREDICTION_CONFIG,
)

CONFIG_TYPES = (
    GpuSetting,
    EmbeddingLoadModelConfig,
    LlmLoadModelConfig,
    LlmPredictionConfig,
)

KEYMAP_DICTS = (
    TO_SERVER_LOAD_EMBEDDING,
    TO_SERVER_LOAD_LLM,
    TO_SERVER_PREDICTION,
)

KEYMAP_TYPES = CONFIG_TYPES[1:]


# Define strict variants that don't implicitly discard unknown keys
class GpuSettingStrict(GpuSetting, forbid_unknown_fields=True):
    pass


class EmbeddingLoadModelConfigStrict(
    EmbeddingLoadModelConfig, forbid_unknown_fields=True
):
    pass


class LlmLoadModelConfigStrict(LlmLoadModelConfig, forbid_unknown_fields=True):
    pass


class LlmPredictionConfigStrict(LlmPredictionConfig, forbid_unknown_fields=True):
    pass


STRICT_TYPES = (
    GpuSettingStrict,
    EmbeddingLoadModelConfigStrict,
    LlmLoadModelConfigStrict,
    LlmPredictionConfigStrict,
)


@pytest.mark.parametrize("config_dict,config_type", zip(CONFIG_DICTS, CONFIG_TYPES))
def test_struct_field_coverage(
    config_dict: DictObject, config_type: LMStudioStruct[Any]
) -> None:
    # Ensure all expected keys are covered (even those with default values)
    mapped_keys = set(config_type.__struct_encode_fields__)
    expected_keys = config_dict.keys()
    missing_keys = expected_keys - mapped_keys
    assert not missing_keys
    # Ensure no extra keys are mistakenly defined
    unknown_keys = mapped_keys - expected_keys
    assert not unknown_keys
    # Ensure the config can be loaded
    config_struct = config_type._from_api_dict(config_dict)
    assert config_struct.to_dict() == config_dict


@pytest.mark.parametrize(
    "input_dict,expected_dict,config_type", zip(SC_DICTS, CONFIG_DICTS, STRICT_TYPES)
)
def test_snake_case_conversion(
    input_dict: DictObject, expected_dict: DictObject, config_type: LMStudioStruct[Any]
) -> None:
    # Ensure snake case keys are converted to camelCase for user-supplied dicts
    config_struct = config_type.from_dict(input_dict)
    assert config_struct.to_dict() == expected_dict
    # Ensure no conversion is applied when reading API dicts
    with pytest.raises(msgspec.ValidationError):
        config_type._from_api_dict(input_dict)


@pytest.mark.parametrize("keymap,config_type", zip(KEYMAP_DICTS, KEYMAP_TYPES))
def test_kv_stack_field_coverage(
    keymap: ToServerKeymap, config_type: LMStudioStruct[Any]
) -> None:
    # Ensure all expected keys are covered (even those with default values)
    mapped_keys = keymap.keys()
    expected_keys = set(config_type.__struct_encode_fields__)
    missing_keys = expected_keys - mapped_keys
    assert not missing_keys
    # Ensure no extra keys are mistakenly defined
    unknown_keys = mapped_keys - expected_keys
    assert not unknown_keys


EXPECTED_KV_STACK_LOAD_EMBEDDING = {
    "layers": [
        {
            "config": {
                "fields": [
                    {"key": "embedding.load.contextLength", "value": 1978},
                    {
                        "key": "embedding.load.llama.acceleration.offloadRatio",
                        "value": 0.5,
                    },
                    {
                        "key": "load.gpuSplitConfig",
                        "value": {
                            "mainGpu": 0,
                            "splitStrategy": "evenly",
                            "disabledGpus": [1, 2],
                        },
                    },
                    {"key": "embedding.load.llama.keepModelInMemory", "value": True},
                    {
                        "key": "embedding.load.llama.ropeFrequencyBase",
                        "value": {"checked": True, "value": 10.0},
                    },
                    {
                        "key": "embedding.load.llama.ropeFrequencyScale",
                        "value": {"checked": True, "value": 1.5},
                    },
                    {"key": "embedding.load.llama.tryMmap", "value": False},
                ],
            },
            "layerName": "apiOverride",
        },
    ],
}

EXPECTED_KV_STACK_LOAD_LLM = {
    "layers": [
        {
            "layerName": "apiOverride",
            "config": {
                "fields": [
                    {"key": "llm.load.contextLength", "value": 1978},
                    {"key": "llm.load.llama.acceleration.offloadRatio", "value": 0.5},
                    {
                        "key": "load.gpuSplitConfig",
                        "value": {
                            "mainGpu": 0,
                            "splitStrategy": "evenly",
                            "disabledGpus": [1, 2],
                        },
                    },
                    {"key": "llm.load.llama.evalBatchSize", "value": 42},
                    {"key": "llm.load.llama.flashAttention", "value": False},
                    {"key": "llm.load.llama.keepModelInMemory", "value": True},
                    {
                        "key": "llm.load.llama.llamaKCacheQuantizationType",
                        "value": {"checked": True, "value": "q8_0"},
                    },
                    {
                        "key": "llm.load.llama.llamaVCacheQuantizationType",
                        "value": {"checked": True, "value": "f32"},
                    },
                    {
                        "key": "llm.load.llama.ropeFrequencyBase",
                        "value": {"checked": True, "value": 10.0},
                    },
                    {
                        "key": "llm.load.llama.ropeFrequencyScale",
                        "value": {"checked": True, "value": 1.5},
                    },
                    {"key": "llm.load.llama.tryMmap", "value": False},
                    {"key": "llm.load.llama.useFp16ForKVCache", "value": True},
                    {"key": "llm.load.numExperts", "value": 0},
                    {"key": "llm.load.seed", "value": {"checked": True, "value": 313}},
                    {"key": "load.gpuStrictVramCap", "value": False},
                ]
            },
        }
    ]
}

EXPECTED_KV_STACK_PREDICTION = {
    "layers": [
        {
            "config": {
                "fields": [
                    {
                        "key": "llm.prediction.contextOverflowPolicy",
                        "value": "rollingWindow",
                    },
                    {"key": "llm.prediction.llama.cpuThreads", "value": 7},
                    {
                        "key": "llm.prediction.maxPredictedTokens",
                        "value": {"checked": True, "value": 1234},
                    },
                    {
                        "key": "llm.prediction.minPSampling",
                        "value": {"checked": True, "value": 5.5},
                    },
                    {
                        "key": "llm.prediction.promptTemplate",
                        "value": {
                            "manualPromptTemplate": {
                                "afterAssistant": "example suffix",
                                "afterSystem": "example suffix",
                                "afterUser": "example suffix",
                                "beforeAssistant": "example prefix",
                                "beforeSystem": "example prefix",
                                "beforeUser": "example prefix",
                            },
                            "stopStrings": ["Nevermore"],
                            "type": "manual",
                        },
                    },
                    {
                        "key": "llm.prediction.reasoning.parsing",
                        "value": {"enabled": False, "startString": "", "endString": ""},
                    },
                    {
                        "key": "llm.prediction.repeatPenalty",
                        "value": {"checked": True, "value": 6.5},
                    },
                    {
                        "key": "llm.prediction.speculativeDecoding.draftModel",
                        "value": "some-model-key",
                    },
                    {
                        "key": "llm.prediction.speculativeDecoding.minContinueDraftingProbability",
                        "value": 0.1,
                    },
                    {
                        "key": "llm.prediction.speculativeDecoding.minDraftLengthToConsider",
                        "value": 5,
                    },
                    {
                        "key": "llm.prediction.speculativeDecoding.numDraftTokensExact",
                        "value": 2,
                    },
                    {"key": "llm.prediction.stopStrings", "value": ["Banana!"]},
                    {
                        "key": "llm.prediction.structured",
                        "value": {"jsonSchema": {"type": "string"}, "type": "json"},
                    },
                    {"key": "llm.prediction.temperature", "value": 2.5},
                    {
                        "key": "llm.prediction.toolCallStopStrings",
                        "value": ["yellow"],
                    },
                    {"key": "llm.prediction.tools", "value": {"type": "none"}},
                    {"key": "llm.prediction.topKSampling", "value": 3.5},
                    {
                        "key": "llm.prediction.topPSampling",
                        "value": {"checked": True, "value": 4.5},
                    },
                ],
            },
            "layerName": "apiOverride",
        },
    ],
}


@pytest.mark.parametrize(
    "config_dict", (LOAD_CONFIG_EMBEDDING, SC_LOAD_CONFIG_EMBEDDING)
)
def test_kv_stack_load_config_embedding(config_dict: DictObject) -> None:
    kv_stack = load_config_to_kv_config_stack(config_dict, EmbeddingLoadModelConfig)
    assert kv_stack.to_dict() == EXPECTED_KV_STACK_LOAD_EMBEDDING


@pytest.mark.parametrize("config_dict", (LOAD_CONFIG_LLM, SC_LOAD_CONFIG_LLM))
def test_kv_stack_load_config_llm(config_dict: DictObject) -> None:
    kv_stack = load_config_to_kv_config_stack(config_dict, LlmLoadModelConfig)
    assert kv_stack.to_dict() == EXPECTED_KV_STACK_LOAD_LLM


@pytest.mark.parametrize("config_dict", (PREDICTION_CONFIG, SC_PREDICTION_CONFIG))
def test_kv_stack_prediction_config(config_dict: DictObject) -> None:
    # MyPy complains here that it can't be sure the dict has all the right keys
    # It is correct about that, but we want to ensure it is handled at runtime
    structured, kv_stack = prediction_config_to_kv_config_stack(None, config_dict)  # type: ignore[arg-type]
    assert structured
    assert kv_stack.to_dict() == EXPECTED_KV_STACK_PREDICTION


def test_kv_stack_prediction_config_conflict() -> None:
    with pytest.raises(
        LMStudioValueError, match="Cannot specify.*response_format.*structured"
    ):
        prediction_config_to_kv_config_stack(BaseModel, PREDICTION_CONFIG)


# TODO: Come up with a way to do the strict checks that applies to nested dicts
#       (this will most likely involve changing the data model code generation)
# def test_nested_unknown_keys() -> None:
#     config = LOAD_CONFIG_EMBEDDING.copy()
#     LOAD_CONFIG_EMBEDDING["gpu"] = SC_GPU_CONFIG
#     with pytest.raises(msgspec.ValidationError):
#         EmbeddingLoadModelConfigStrict._from_api_dict(config)
