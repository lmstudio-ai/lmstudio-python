"""Tests for default parameter values in tool definitions."""

import pytest
from typing import Any

from src.lmstudio.json_api import ToolFunctionDef, ToolFunctionDefDict
from src.lmstudio.schemas import _to_json_schema


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
        The calculated result
    """
    return f"Result: {eval(expression):.{precision}f}"


class TestDefaultValues:
    """Test default parameter value functionality."""
    
    def test_extract_defaults_from_callable(self):
        """Test extracting default values from function signature."""
        tool_def = ToolFunctionDef.from_callable(greet)
        
        assert tool_def.name == "greet"
        assert tool_def.parameter_defaults == {
            "greeting": "Hello",
            "punctuation": "!"
        }
        assert "name" not in tool_def.parameter_defaults
    
    def test_manual_defaults(self):
        """Test manually specifying default values."""
        tool_def = ToolFunctionDef(
            name="calculate",
            description="Calculate a mathematical expression",
            parameters={"expression": str, "precision": int},
            implementation=calculate,
            parameter_defaults={"precision": 2}
        )
        
        assert tool_def.parameter_defaults == {"precision": 2}
        assert "expression" not in tool_def.parameter_defaults
    
    def test_json_schema_with_defaults(self):
        """Test that JSON Schema includes default values."""
        tool_def = ToolFunctionDef.from_callable(greet)
        params_struct, _ = tool_def._to_llm_tool_def()
        json_schema = _to_json_schema(params_struct)
        
        properties = json_schema["properties"]
        
        # name should not have a default (required parameter)
        assert "name" in properties
        assert "default" not in properties["name"]
        
        # greeting should have default "Hello"
        assert "greeting" in properties
        assert properties["greeting"]["default"] == "Hello"
        
        # punctuation should have default "!"
        assert "punctuation" in properties
        assert properties["punctuation"]["default"] == "!"
        
        # Only name should be required
        assert json_schema["required"] == ["name"]
    
    def test_dict_based_definition(self):
        """Test dictionary-based tool definition with defaults."""
        dict_tool: ToolFunctionDefDict = {
            "name": "format_text",
            "description": "Format text with specified style",
            "parameters": {"text": str, "style": str, "uppercase": bool},
            "implementation": lambda text, style="normal", uppercase=False: text.upper() if uppercase else text,
            "parameter_defaults": {"style": "normal", "uppercase": False}
        }
        
        # This should work without errors
        tool_def = ToolFunctionDef(**dict_tool)
        assert tool_def.parameter_defaults == {"style": "normal", "uppercase": False}
    
    def test_no_defaults(self):
        """Test function with no default values."""
        def no_defaults(a: int, b: str) -> str:
            """Function with no default parameters."""
            return f"{a}{b}"
        
        tool_def = ToolFunctionDef.from_callable(no_defaults)
        assert tool_def.parameter_defaults == {}
        
        params_struct, _ = tool_def._to_llm_tool_def()
        json_schema = _to_json_schema(params_struct)
        
        # All parameters should be required
        assert json_schema["required"] == ["a", "b"]
        
        # No properties should have defaults
        for prop in json_schema["properties"].values():
            assert "default" not in prop
    
    def test_mixed_defaults(self):
        """Test function with some parameters having defaults."""
        def mixed_defaults(required: str, optional1: int = 42, optional2: bool = True) -> str:
            """Function with mixed required and optional parameters."""
            return f"{required}{optional1}{optional2}"
        
        tool_def = ToolFunctionDef.from_callable(mixed_defaults)
        assert tool_def.parameter_defaults == {
            "optional1": 42,
            "optional2": True
        }
        
        params_struct, _ = tool_def._to_llm_tool_def()
        json_schema = _to_json_schema(params_struct)
        
        # Only required should be in required list
        assert json_schema["required"] == ["required"]
        
        # Check defaults
        assert json_schema["properties"]["optional1"]["default"] == 42
        assert json_schema["properties"]["optional2"]["default"] is True
        assert "default" not in json_schema["properties"]["required"]
