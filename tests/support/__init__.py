"""Common test support interfaces and expected value definitions."""

import sys

from contextlib import closing, contextmanager
from pathlib import Path
from typing import Generator
from typing_extensions import (
    # Native in 3.11+
    Never,
    NoReturn,
)

import pytest

# Imports from the real LM Studio SDK
from lmstudio import (
    BaseModel,
    DictObject,
    DictSchema,
    LlmLoadModelConfig,
    LMStudioServerError,
    LMStudioChannelClosedError,
)
from lmstudio.json_api import ChannelEndpoint
from lmstudio._sdk_models import LlmPredictionConfigDict, LlmStructuredPredictionSetting

# Imports from the nominal "SDK" used in some test cases
from .lmstudio import ErrFunc

THIS_DIR = Path(__file__).parent

LOCAL_API_HOST = "localhost:1234"

####################################################
# Embedding model testing
####################################################
EXPECTED_EMBEDDING = "nomic-ai/nomic-embed-text-v1.5"
EXPECTED_EMBEDDING_ID = "text-embedding-nomic-embed-text-v1.5"
EXPECTED_EMBEDDING_LENGTH = 768  # nomic has embedding dimension 768
EXPECTED_EMBEDDING_CONTEXT_LENGTH = 2048  # nomic accepts a 2048 token context

####################################################
# Text LLM testing
####################################################
EXPECTED_LLM = "hugging-quants/llama-3.2-1b-instruct"
EXPECTED_LLM_ID = "llama-3.2-1b-instruct"
PROMPT = "Hello"
MAX_PREDICTED_TOKENS = 50
# Use a dict here to ensure dicts are accepted in all config APIs,
# and camelCase keys so it passes static type checks
# snake_case keys won't pass static type checks, but their runtime
# acceptance is covered in test_kv_config
# Note: while MyPy accepts this as a valid prediction config dict, it
# doesn't *infer* the right type without the explicit declaration :(
SHORT_PREDICTION_CONFIG: LlmPredictionConfigDict = {
    "maxTokens": MAX_PREDICTED_TOKENS,
    "temperature": 0,
}
LLM_LOAD_CONFIG = LlmLoadModelConfig(seed=11434)

####################################################
# Visual LLM testing
####################################################
EXPECTED_VLM = "ZiangWu/MobileVLM_V2-1.7B-GGUF"
EXPECTED_VLM_ID = "mobilevlm_v2-1.7b"
IMAGE_FILEPATH = THIS_DIR / "files/lemmy.png"
VLM_PROMPT = "What color is this figure?"

####################################################
# Tool use LLM testing
####################################################
TOOL_LLM_ID = "qwen2.5-7b-instruct-1m"

####################################################
# Other specific models needed for testing
####################################################
SMALL_LLM_SEARCH_TERM = "smollm2-135m"
SMALL_LLM_ID = "smollm2-135m-instruct"

####################################################
# Structured LLM responses
####################################################

# Schema includes both snake_case and camelCase field
# names to ensure the special-casing of snake_case
# fields in dict inputs doesn't corrupt schema inputs
SCHEMA_FIELDS = {
    "response": {
        "type": "string",
    },
    "first_word_in_response": {
        "type": "string",
    },
    "lastWordInResponse": {
        "type": "string",
    },
}
SCHEMA_FIELD_NAMES = list(SCHEMA_FIELDS.keys())

# Specify a JSON response format, so this can pass the JSON test cases
# String field definition is from the Llama JSON GBNF example at:
# https://github.com/ggml-org/llama.cpp/blob/960e72607761eb2dd170b33f02a5a2840ec412fe/grammars/json.gbnf#L16C1-L20C13
# Note: comments and blank lines in the grammar are not yet supported
GBNF_GRAMMAR = r"""
root ::= "{\"response\":" response ",\"first_word_in_response\":" first-word-in-response ",\"lastWordInResponse\":" last-word-in-response "}"
response ::= string
first-word-in-response ::= string
last-word-in-response ::= string
string ::=
  "\"" (
    [^"\\\x7f\x00-\x1f] |
    "\\" (["\\bfnrt] | "u" [0-9a-fA-F]{4})
  )* "\""
""".lstrip()

SCHEMA = {
    "$schema": "http://json-schema.org/draft-07/schema#",
    "type": "object",
    "required": SCHEMA_FIELD_NAMES,
    "properties": SCHEMA_FIELDS,
    "additionalProperties": False,
}
RESPONSE_SCHEMA = {
    "$defs": {
        "schema": {
            "properties": SCHEMA_FIELDS,
            "required": SCHEMA_FIELD_NAMES,
            "title": "schema",
            "type": "object",
        }
    },
    "$ref": "#/$defs/schema",
}


class OtherResponseFormat:
    @classmethod
    def model_json_schema(cls) -> DictSchema:
        return RESPONSE_SCHEMA


class LMStudioResponseFormat(BaseModel):
    response: str
    first_word_in_response: str
    lastWordInResponse: str


TYPED_JSON_SCHEMA = LlmStructuredPredictionSetting(type="json", json_schema=SCHEMA)
TYPED_JSON_SCHEMA_DICT = {
    "type": "json",
    "jsonSchema": SCHEMA,
}

TYPED_GBNF_GRAMMAR = LlmStructuredPredictionSetting(
    type="gbnf", gbnf_grammar=GBNF_GRAMMAR
)
TYPED_GBNF_GRAMMAR_DICT = {
    "type": "gbnf",
    "gbnfGrammar": GBNF_GRAMMAR,
}


RESPONSE_FORMATS = (
    LMStudioResponseFormat,
    OtherResponseFormat,
    SCHEMA,
    TYPED_JSON_SCHEMA,
    TYPED_JSON_SCHEMA_DICT,
    TYPED_GBNF_GRAMMAR,
    TYPED_GBNF_GRAMMAR_DICT,
)

####################################################
# Provoke/emulate connection issues
####################################################


class InvalidEndpoint(ChannelEndpoint[str, Never, dict[str, object]]):
    _API_ENDPOINT = "noSuchEndpoint"
    _NOTICE_PREFIX = "Invalid endpoint"

    def __init__(self) -> None:
        super().__init__({})

    def iter_message_events(self, _contents: DictObject | None) -> NoReturn:
        raise NotImplementedError

    def handle_rx_event(self, _event: Never) -> None:
        raise NotImplementedError


INVALID_API_HOST = "domain.invalid:1234"


@contextmanager
def nonresponsive_api_host() -> Generator[str, None, None]:
    """Open a listening TCP port on localhost and ignore all requests."""
    from socketserver import TCPServer, BaseRequestHandler

    with TCPServer(("localhost", 0), BaseRequestHandler) as s:
        listening_port = s.server_address[1]
        yield f"localhost:{listening_port}"


def find_free_local_port() -> int:
    """Get a local TCP port with no listener at the time of the call."""
    import socket

    with closing(socket.socket(socket.AF_INET, socket.SOCK_STREAM)) as s:
        s.bind(("", 0))
        s.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        return int(s.getsockname()[1])


def closed_api_host() -> str:
    """Get a local API host address with no listener at the time of the call."""
    return f"localhost:{find_free_local_port()}"


####################################################
# Check details of raised SDK errors
####################################################

# The truncation method used is only effective on Python 3.11+
# Earlier versions report the traceback separately from the
# exception value, so it gets restored after clearing the attribute
EXPECT_TB_TRUNCATION = sys.version_info >= (3, 11)


def check_sdk_error(
    exc_info: pytest.ExceptionInfo[BaseException],
    calling_file: str,
    *,
    sdk_frames: int = 0,
    check_exc: bool = True,
) -> None:
    # If possible, traceback should be truncated at the SDK boundary,
    # potentially showing the specified number of SDK frames
    tb = exc_info.tb
    assert tb.tb_frame.f_code.co_filename == calling_file
    for _ in range(sdk_frames):
        tb_next = tb.tb_next
        assert tb_next is not None
        tb = tb_next
        sdk_frame_path = Path(tb.tb_frame.f_code.co_filename)
        if "lmstudio" not in sdk_frame_path.parts:
            # Report full traceback if it is not as expected
            raise Exception(
                f"Unexpected frame location: {sdk_frame_path}"
            ) from exc_info.value
    if EXPECT_TB_TRUNCATION and tb.tb_next is not None:
        # Report full traceback if it is not as expected
        raise Exception("Traceback not truncated at SDK boundary") from exc_info.value
    if not check_exc:
        # Allow the exception value checks to be skipped
        return
    # Exception should report itself under its top-level name
    assert exc_info.type.__module__ == "lmstudio"
    # Check additional details for specific exception types
    match exc_info.value:
        case LMStudioChannelClosedError(
            _raw_error=raw_error, server_error=server_error
        ):
            assert raw_error is None
            assert server_error is None
        case LMStudioServerError(_raw_error=raw_error, server_error=server_error):
            assert raw_error is not None
            assert "stack" not in raw_error
            assert server_error is not None
            assert server_error.stack is None


def check_unfiltered_error(
    exc_info: pytest.ExceptionInfo[BaseException],
    calling_file: str,
    err_func: ErrFunc,
) -> None:
    # Traceback should NOT be truncated at the SDK boundary
    tb = exc_info.tb
    assert tb.tb_frame.f_code.co_filename == calling_file
    while (tb_next := tb.tb_next) is not None:
        tb = tb_next
        sdk_frame_path = Path(tb.tb_frame.f_code.co_filename)
        if "contextlib.py" in sdk_frame_path.parts:
            # Traceback filtering uses the contextlib module
            continue
        if "lmstudio" not in sdk_frame_path.parts:
            # Report full traceback if it is not as expected
            raise Exception(
                f"Unexpected frame location: {sdk_frame_path}"
            ) from exc_info.value
    # Traceback should go all the way to the raising func
    assert tb.tb_frame.f_code is err_func.__code__
