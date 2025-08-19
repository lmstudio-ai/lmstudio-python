"""Tests for default parameter values in tool definitions."""

import pytest

from msgspec import defstruct

from lmstudio.json_api import _NO_DEFAULT, ToolFunctionDef, ToolFunctionDefDict
from lmstudio.schemas import _to_json_schema


def greet(name: str, greeting: str = "Hello", punctuation: str = "!") -> str:
    """Greet someone with a customizable message.

    Args:
        name: The name of the person to greet
        greeting: The greeting word to use (default: "Hello")
        punctuation: The punctuation to end with (default: "!")

    Returns:
        A greeting message
    """
    return f"{greeting}, {name}{punctuation}"


def calculate(expression: str, precision: int = 2) -> str:
    """Calculate a mathematical expression.

    Args:
        expression: The mathematical expression to evaluate
        precision: Number of decimal places (default: 2)

    Returns:
        The calculated result as a string
    """
    return f"Result: {eval(expression):.{precision}f}"


class TestDefaultValues:
    """Test cases for default parameter values in tool definitions."""

    def test_extract_defaults_from_callable(self) -> None:
        """Test extracting default values from a callable function."""
        tool_def = ToolFunctionDef.from_callable(greet)

        assert tool_def.name == "greet"
        # Check that defaults are converted to inline format
        assert tool_def.parameters["greeting"] == {"type": str, "default": "Hello"}
        assert tool_def.parameters["punctuation"] == {"type": str, "default": "!"}
        assert tool_def.parameters["name"] is str  # No default, just type

    def test_manual_inline_defaults(self) -> None:
        """Test manually specifying default values in inline format."""
        tool_def = ToolFunctionDef(
            name="calculate",
            description="Calculate a mathematical expression",
            parameters={"expression": str, "precision": {"type": int, "default": 2}},
            implementation=calculate,
        )

        # Check that the inline format is preserved
        assert tool_def.parameters["precision"] == {"type": int, "default": 2}
        assert tool_def.parameters["expression"] is str  # No default, just type

    def test_json_schema_with_defaults(self) -> None:
        """Test that JSON schema includes default values."""
        tool_def = ToolFunctionDef.from_callable(greet)
        params_struct, _ = tool_def._to_llm_tool_def()

        json_schema = _to_json_schema(params_struct)

        # Check that default values are included in the schema
        assert json_schema["properties"]["greeting"]["default"] == "Hello"
        assert json_schema["properties"]["punctuation"]["default"] == "!"
        assert "default" not in json_schema["properties"]["name"]

    def test_dict_based_definition(self) -> None:
        """Test dictionary-based tool definition with inline defaults."""
        dict_tool: ToolFunctionDefDict = {
            "name": "format_text",
            "description": "Format text with specified style",
            "parameters": {
                "text": str,
                "style": {"type": str, "default": "normal"},
                "uppercase": {"type": bool, "default": False},
            },
            "implementation": lambda text, style="normal", uppercase=False: text.upper()
            if uppercase
            else text,
        }

        # This should work without errors
        tool_def = ToolFunctionDef(**dict_tool)
        assert tool_def.parameters["style"] == {"type": str, "default": "normal"}
        assert tool_def.parameters["uppercase"] == {"type": bool, "default": False}
        assert tool_def.parameters["text"] is str  # No default, just type

    def test_no_defaults(self) -> None:
        """Test function with no default values."""

        def no_defaults(a: int, b: str) -> str:
            """Function with no default parameters."""
            return f"{a}: {b}"

        tool_def = ToolFunctionDef.from_callable(no_defaults)
        # All parameters should be simple types without defaults
        assert tool_def.parameters["a"] is int
        assert tool_def.parameters["b"] is str

        params_struct, _ = tool_def._to_llm_tool_def()
        json_schema = _to_json_schema(params_struct)

        # No default values should be present
        assert "default" not in json_schema["properties"]["a"]
        assert "default" not in json_schema["properties"]["b"]

    def test_mixed_defaults(self) -> None:
        """Test function with some parameters having defaults and others not."""

        def mixed_defaults(
            required: str, optional1: int = 42, optional2: bool = True
        ) -> str:
            """Function with mixed required and optional parameters."""
            return f"{required}: {optional1}, {optional2}"

        tool_def = ToolFunctionDef.from_callable(mixed_defaults)
        # Check inline format for parameters with defaults
        assert tool_def.parameters["optional1"] == {"type": int, "default": 42}
        assert tool_def.parameters["optional2"] == {"type": bool, "default": True}
        assert tool_def.parameters["required"] is str  # No default, just type

        params_struct, _ = tool_def._to_llm_tool_def()
        json_schema = _to_json_schema(params_struct)

        # Check that default values are correctly included in schema
        assert json_schema["properties"]["optional1"]["default"] == 42
        assert json_schema["properties"]["optional2"]["default"] is True
        assert "default" not in json_schema["properties"]["required"]

    def test_extract_type_and_default_method(self) -> None:
        """Test the _extract_type_and_default helper method."""

        # Test simple type
        param_type, default = ToolFunctionDef._extract_type_and_default(str)
        assert param_type is str
        assert default is _NO_DEFAULT

        # Test inline format with missing type key
        with pytest.raises(TypeError, match="Missing 'type' key"):
            param_type, default = ToolFunctionDef._extract_type_and_default(
                {"default": 42}  # type: ignore[arg-type]
            )

        # Test inline format with no default
        param_type, default = ToolFunctionDef._extract_type_and_default({"type": int})
        assert param_type is int
        assert default is _NO_DEFAULT

        # Test inline format with default
        param_type, default = ToolFunctionDef._extract_type_and_default(
            {"type": int, "default": 42}
        )
        assert param_type is int
        assert default == 42

        # Test complex default
        param_type, default = ToolFunctionDef._extract_type_and_default(
            {"type": list, "default": [1, 2, 3]}
        )
        assert param_type is list
        assert default == [1, 2, 3]

    def test_msgspec_auto_defaults(self) -> None:
        """msgspec automatically reflects default values in the JSON schema."""
        TestStruct = defstruct(
            "TestStruct",
            [
                ("name", str),
                ("age", int, 18),
                ("active", bool, True),
            ],
            kw_only=True,
        )

        schema = _to_json_schema(TestStruct)
        properties = schema.get("properties", {})
        required = schema.get("required", [])

        assert "name" in properties and "default" not in properties["name"]
        assert properties["age"].get("default") == 18
        assert properties["active"].get("default") is True
        assert "name" in required and "age" not in required and "active" not in required
