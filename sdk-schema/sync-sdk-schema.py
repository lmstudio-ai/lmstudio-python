#!/usr/bin/env python
"""Generate Python data model classes from lmstudio-js zod schema.

Recreates the Python data model classes from the exported JSON schema
(generating the JSON schema only if necessary).
Pass `--regen-schema` to request a full export from Typescript.
"""

# Uses `npm run zod-to-json-schema` to populate `./_json_schema`
# Uses https://github.com/koxudaxi/datamodel-code-generator/
# to emit Python data model classes for the defined JSON schemas
# to `../src/lmstudio/_sdk_models`


# * invokes `npm run build` and `npm run make-schemas` in the
#   `lmstudio-js` submodule's `packages/lms-json-schema` project
#   to create JSON schema files in
#   `./lmstudio-js/packages/lms-json-schema/schemas/lms.json`
# * uses `datamodel-code-generator` to produce Python data model
#   classes from the exported JSON schema files

import ast
import builtins
import json
import shutil
import subprocess
import sys
import tokenize

from collections import defaultdict
from contextlib import chdir
from pathlib import Path
from typing import Any

from datamodel_code_generator import (
    DataModelType,
    InputFileType,
    generate,
    LiteralType,
    PythonVersion,
)

_THIS_DIR = Path(__file__).parent
_LMSJS_DIR = _THIS_DIR / "lmstudio-js"
_EXPORTER_DIR = _LMSJS_DIR / "packages/lms-json-schema"
_SCHEMA_DIR = _EXPORTER_DIR / "schemas"
_SCHEMA_PATH = _SCHEMA_DIR / "lms.json"
_CACHED_SCHEMA_PATH = _THIS_DIR / _SCHEMA_PATH.name
_INFERRED_SCHEMA_PATH = _THIS_DIR / "lms-with-inferred-unions.json"
_TEMPLATE_DIR = _THIS_DIR / "_templates"
_MODEL_DIR = _THIS_DIR.parent / "src/lmstudio/_sdk_models"
_MODEL_PATH = _MODEL_DIR / "__init__.py"

# The following schemas are not actually used anywhere,
# so they're excluded to avoid any conflicts with automatically
# generated names of otherwise anonymous classes
# Note: this list is NOT checked to ensure the named schemas aren't
#       referenced from any other parts of the schema
_EXCLUDE_EXPORTED_SCHEMAS = (
    "llmContextReferenceJsonFile",
    "llmContextReferenceYamlFile",
)


# TODO:
# * Figure out a way to avoid the full clean-and-build
#   cycle when regenerating the lmstudio-js JSON schemas
#
# * Potentially include models for the websocket channel,
#   rpc, and signal message formats:
#   https://github.com/lmstudio-ai/lmstudio-js/blob/main/packages/lms-communication/src/Transport.ts


def _export_zod_schemas_to_json_schema() -> None:
    """Run the lmstudio-js JSON schema export in the submodule."""
    _SCHEMA_PATH.unlink(missing_ok=True)
    _CACHED_SCHEMA_PATH.unlink(missing_ok=True)
    with chdir(_LMSJS_DIR):
        subprocess.run(["npm", "install", "-D"]).check_returncode()
        subprocess.run(["npm", "run", "build"]).check_returncode()
    with chdir(_EXPORTER_DIR):
        subprocess.run(["npm", "install", "-D"]).check_returncode()
        subprocess.run(["npm", "run", "make-schemas"]).check_returncode()
    if not _SCHEMA_PATH.exists():
        raise RuntimeError(f"Failed to create {_SCHEMA_PATH!r}")


def _cache_json_schema() -> None:
    """Cache the built JSON schema file outside the submodule."""
    if not _SCHEMA_PATH.exists():
        msg = f"Require {_CACHED_SCHEMA_PATH} or {_SCHEMA_PATH!r} to generate data model classes"
        raise RuntimeError(msg)
    _CACHED_SCHEMA_PATH.unlink(missing_ok=True)
    shutil.copy(_SCHEMA_PATH, _CACHED_SCHEMA_PATH)


_SchemaObject = dict[str, Any]
_SchemaList = list[_SchemaObject]
_SchemaDef = dict[str, _SchemaObject]


def _resolve_json_ref(json_schema: _SchemaObject, ref: str) -> _SchemaObject:
    ref_parts = ref.split("/")
    if ref_parts[0] != "#":
        raise RuntimeError(f"Only internal refs are supported, not {ref}")
    ref_target = json_schema[ref_parts[1]]
    for ref_part in ref_parts[2:]:
        ref_target = ref_target[ref_part]
    return ref_target


_POTENTIAL_TAG_FIELDS = ("type", "success", "role", "code")


def _check_discriminator(tag_field: str, union_array: _SchemaList) -> bool:
    for entry in union_array:
        properties = entry.get("properties", None)
        if properties is None:
            # Not actually an object instance
            return False
        field_def = properties.get(tag_field, None)
        if field_def is None:
            # Can only be a discriminated union on this tag if all variants have it
            return False
        if field_def["type"] != "string":
            # Only string based unions are defined in lmstudio-js
            return False
        tag_value = field_def.get("const", None)
        if tag_value is None:
            # All variants in a discriminated union must define a constant tag field value
            return False
    # All union members have this field defined as const string value
    return True


def _make_spec_name(parent_name: str, suffix: str) -> str:
    # datamodel-code-generator handles "/" in names by splitting on it and then
    # combining the result strings into CamelCase data model class names
    # We also want that behaviour for "." in field names, rather than their
    # default handling (treating them as modular references)
    # However, leaving it to datamodel-code-generator to handle the "/" conversion
    # means the schema generator may miss name collisions with explicitly exported
    # names, so we instead adjust the added suffixes directly.
    parts = suffix.replace(".", "/").split("/")
    camel_cased = [p[0].upper() + p[1:] for p in parts]
    return parent_name + "".join(camel_cased)


def _merge_defs(existing_defs: _SchemaDef, new_defs: _SchemaDef | None) -> None:
    if not new_defs:
        return
    duplicate_defs = existing_defs.keys() & new_defs.keys()
    if duplicate_defs:
        raise RuntimeError(f"Duplicate extracted definitions: {duplicate_defs}")
    existing_defs.update(new_defs)


class _SchemaProcessor:
    """Process schema to identify discriminated union fields."""

    def __init__(self, schema_path: Path) -> None:
        self._schema = json.loads(schema_path.read_text(encoding="utf-8"))
        self._processed = False

    def infer_unions(self) -> _SchemaObject:
        if not self._processed:
            self._process_schema()
        return self._schema

    def _process_schema(self) -> None:
        # Collect new named union types and their variants in order for appending
        # to the collection of schema object definitions
        schema_defs: _SchemaDef = self._schema["definitions"]
        new_defs: _SchemaDef = {}
        for excluded_def in _EXCLUDE_EXPORTED_SCHEMAS:
            del schema_defs[excluded_def]
        for name, spec in schema_defs.items():
            _merge_defs(new_defs, self._process_named_spec(name, spec))
        _merge_defs(schema_defs, new_defs)
        self._processed = True

    def _process_named_spec(self, name: str, spec: _SchemaObject) -> _SchemaDef | None:
        match spec:
            case {"anyOf": [*_]}:
                # Existing named union, extract the variant schema defs
                return self._extract_union_variants(name, spec)
            # As further top-level entries for processing are identified, add them here
            case _:
                return self._process_subschema(name, spec)
        return None

    def _extract_union_variants(
        self, name: str, spec: _SchemaObject
    ) -> _SchemaDef | None:
        union_member_specs = spec["anyOf"]
        spec_refs: list[str | None] = []
        resolved_specs: _SchemaList = []
        for member_spec in union_member_specs:
            existing_ref = member_spec.get("$ref", None)
            if existing_ref:
                # Member is already defined as a named subschema
                spec_refs.append(existing_ref)
                resolved_spec = _resolve_json_ref(self._schema, existing_ref)
                resolved_specs.append(resolved_spec)
                continue
            # Anonymous union member to convert to a named subschema
            spec_refs.append(None)
            resolved_specs.append(member_spec)
        # First check if this is a *discriminated* union or just a structural union
        discriminator: str | None = None
        for tag_field in _POTENTIAL_TAG_FIELDS:
            if _check_discriminator(tag_field, resolved_specs):
                discriminator = tag_field
                break
        if discriminator is None:
            if name.endswith("/returns"):
                # RPC result schemas may allow the result to be omitted entirely
                return self._process_rpc_result_union(name, spec)
            return None
        # Build the discriminator map, adding subschemas as necessary
        print(f"Defining discriminated union {name} on {discriminator!r}")
        new_defs: _SchemaDef = {}
        discriminator_map: dict[str, str] = {}
        tag_title = discriminator.capitalize()
        for idx, (spec_ref, resolved_spec) in enumerate(zip(spec_refs, resolved_specs)):
            tag_spec = resolved_spec["properties"][discriminator]
            tag_value = tag_spec["const"]
            if spec_ref is None:
                # Convert anonymous union member to a named subschema
                new_spec_name = _make_spec_name(name, tag_value)
                spec_ref = f"#/definitions/{new_spec_name}"
                new_defs[new_spec_name] = resolved_spec
                union_member_specs[idx] = {"$ref": spec_ref}
                print(f"  Extracted union member variant {new_spec_name}")
            else:
                existing_spec_name = spec_ref.removeprefix("#/definitions/")
                print(f"  Using existing union member variant {existing_spec_name}")
            # Map this value to the existing/extracted union variant
            discriminator_map[tag_value] = spec_ref
            # Field value also needs to be set as the field default
            tag_spec.setdefault("default", tag_value)
            # Field needs a title to be correctly marked as a discriminator field
            tag_spec.setdefault("title", tag_title)
        spec["discriminator"] = {
            "mapping": discriminator_map,
            "propertyName": discriminator,
        }
        return new_defs

    @staticmethod
    def _is_void_union(union_members: _SchemaList) -> _SchemaObject | None:
        if len(union_members) != 2:
            return None
        # Note: the "void spec" definition is actually an error in the lmstudio-js
        #       schema exporter, since it is defined as meaning "may be anything" in JSON
        #       schema, but the exporter is wanting to specify "may be omitted entirely".
        #       That "may be omitted" aspect would be specified by declaring the "result"
        #       field as optional when specifying the "rpcResult" channel message (if that
        #       comms protocol structure was included in the exported JSON schema).
        #       Fortunately, since actual "may be anything" schemas are emitted as empty
        #       dictionaries, it can be safely processed as being equivalent to a
        #       null specification.
        void_spec: _SchemaObject = {"not": {}}
        null_spec: _SchemaObject = {"type": "null"}
        allows_omission = (void_spec, null_spec)
        first, second = union_members
        if first in allows_omission:
            if second not in allows_omission:
                return second
        elif second in allows_omission:
            return first
        # Either both are regular schemas, or both allow omission
        # Either way, this isn't a valid optional void union
        return None

    def _process_rpc_result_union(
        self, name: str, spec: _SchemaObject
    ) -> _SchemaObject | None:
        union_member_specs = spec["anyOf"]
        result_spec = self._is_void_union(union_member_specs)
        if result_spec is None:
            return None
        result_spec_name = f"{name.removesuffix('/returns')}ReturnValue"
        result_spec_ref = f"#/definitions/{result_spec_name}"
        union_member_specs[:] = [{"$ref": result_spec_ref}, {"type": "null"}]
        return {result_spec_name: result_spec}

    def _process_subschema(self, name: str, spec: _SchemaObject) -> _SchemaDef | None:
        match spec:
            case {"anyOf": [*_]}:
                # Anonymous union as an object property or array item schema
                pass
            case {"type": "array", "items": {} as item_spec}:
                # Array, recurse into the item definition
                item_spec_name = f"{name}Item"
                return self._process_subschema(item_spec_name, item_spec)
            case {"type": "object", "properties": {} as field_defs}:
                # Object with defined properties, recurse into the field definitions
                extracted_defs: _SchemaDef = {}
                for field_name, field_spec in field_defs.items():
                    field_spec_name = _make_spec_name(name, field_name)
                    _merge_defs(
                        extracted_defs,
                        self._process_subschema(field_spec_name, field_spec),
                    )
                return extracted_defs
            case _:
                # Some other field type, nothing to do here
                return None
        union_member_defs = self._extract_union_variants(name, spec)
        if union_member_defs is None:
            # It's a union, but not a discriminated union
            return None
        named_union_ref = f"#/definitions/{name}"
        # Copy the spec as a new named union schema
        union_defs = {name: spec.copy()}
        # Replace the original anonymous union with a reference
        spec.clear()
        spec["$ref"] = named_union_ref
        print(f"  Extracted discriminated union {name}")
        # Report the new named union schema and its variants
        _merge_defs(union_defs, union_member_defs)
        return union_defs


def _infer_schema_unions() -> None:
    if not _CACHED_SCHEMA_PATH.exists():
        msg = f"Require {_CACHED_SCHEMA_PATH} to infer unions in data model classes"
        raise RuntimeError(msg)
    _INFERRED_SCHEMA_PATH.unlink(missing_ok=True)
    schema_processor = _SchemaProcessor(_CACHED_SCHEMA_PATH)
    processed_schema = schema_processor.infer_unions()
    # Avoid sorting keys to preserve the original read/insertion order in dicts
    _INFERRED_SCHEMA_PATH.write_text(json.dumps(processed_schema, indent=2))


def _generate_data_model_from_json_schema() -> None:
    """Produce Python data model classes from the exported JSON schema file."""
    if not _CACHED_SCHEMA_PATH.exists():
        _cache_json_schema()
    _infer_schema_unions()
    _MODEL_PATH.unlink(missing_ok=True)
    print("Generating data model source code...")
    generate(
        _INFERRED_SCHEMA_PATH,
        input_file_type=InputFileType.JsonSchema,
        output=_MODEL_PATH,
        output_model_type=DataModelType.MsgspecStruct,
        custom_template_dir=_TEMPLATE_DIR,
        base_class="..schemas.LMStudioStruct",
        additional_imports=[
            "typing_extensions.NotRequired",
            "typing.TypedDict",
        ],
        snake_case_field=True,
        # Enums don't play nice with TypedDict, so use Literal instead
        enum_field_as_literal=LiteralType("all"),
        field_constraints=True,
        use_annotated=True,
        use_double_quotes=True,
        use_generic_container_types=True,
        use_union_operator=True,
        extra_template_data=defaultdict(
            dict,
            {
                "#all#": {
                    "base_class_kwargs": {
                        # Set on base class, but also needs to be set
                        # on subclasses for static check visibility
                        "kw_only": True,
                    }
                }
            },
        ),
        # Keep this in sync with the minimum version in pyproject.toml
        target_python_version=PythonVersion.PY_310,
    )
    if not _MODEL_PATH.exists():
        raise RuntimeError(f"Failed to create {_MODEL_PATH!r}")
    # Generated source code post-processing:
    #
    # * Fix up typed dicts to be defined in terms of nested dicts
    # * Add an `__all__` definition for wildcard imports (which also
    #   serves as a top level summary of the defined schemas)
    print("Post-processing generated source code...")
    model_source = _MODEL_PATH.read_text()
    model_ast = ast.parse(model_source)
    dict_token_replacements: dict[str, str] = {}
    exported_names: list[str] = []
    for node in model_ast.body:
        match node:
            case ast.ClassDef(name=name):
                name = node.name
                exported_names.append(name)
                if name.endswith("Dict"):
                    struct_name = name.removesuffix("Dict")
                    dict_token_replacements[struct_name] = name
            case ast.Assign(targets=[ast.Name(id=alias)], value=expr):
                # We don't want to require the specific aliased types for dict inputs
                match expr:
                    case (
                        ast.Name(id=name)
                        | ast.Subscript(
                            value=ast.Name(id="Annotated"),
                            slice=ast.Tuple(elts=[ast.Name(id=name), *_]),
                        )
                    ):
                        if hasattr(builtins, name):
                            dict_token_replacements[alias] = name

    # Additional type union names to be translated
    # Inject the dict versions of required type unions
    # (This is a brute force hack, but it's good enough while there's only a few that matter)
    _single_line_union = (" = ", " | ", "")
    _multi_line_union = (" = (\n    ", "\n    | ", "\n)")
    _dict_unions = (
        (
            "ChatMessageData",
            (
                "ChatMessageDataAssistant",
                "ChatMessageDataUser",
                "ChatMessageDataSystem",
                "ChatMessageDataTool",
            ),
            _multi_line_union,
        ),
        (
            "LlmToolUseSetting",
            ("LlmToolUseSettingNone", "LlmToolUseSettingToolArray"),
            _single_line_union,
        ),
        (
            "ModelSpecifier",
            ("ModelSpecifierQuery", "ModelSpecifierInstanceReference"),
            _single_line_union,
        ),
    )
    combined_union_defs: dict[str, str] = {}
    for union_name, union_members, (assign_sep, union_sep, union_end) in _dict_unions:
        dict_union_name = f"{union_name}Dict"
        dict_token_replacements[union_name] = dict_union_name
        if dict_union_name != f"{union_name}Dict":
            raise RuntimeError(
                f"Union {union_name!r} mapped to unexpected name {dict_union_name!r}"
            )
        union_def = (
            f"{union_name}{assign_sep}{union_sep.join(union_members)}{union_end}"
        )
        dict_union_def = f"{dict_union_name}{assign_sep}{('Dict' + union_sep).join(union_members)}Dict{union_end}"
        combined_union_defs[union_def] = f"{union_def}\n{dict_union_def}"
    # Additional type aliases for translation
    # TODO: Rather than setting these on an ad hoc basis, record all the pure aliases
    #       during the AST scan, and add the extra dict token replacements automatically
    dict_token_replacements["PromptTemplate"] = "LlmPromptTemplateDict"
    dict_token_replacements["ReasoningParsing"] = "LlmReasoningParsingDict"
    dict_token_replacements["RawTools"] = "LlmToolUseSettingDict"
    dict_token_replacements["LlmTool"] = "LlmToolFunctionDict"
    dict_token_replacements["LlmToolParameters"] = "LlmToolParametersObjectDict"
    # Replace struct names in TypedDict definitions with their dict counterparts
    model_tokens = tokenize.tokenize(_MODEL_PATH.open("rb").readline)
    updated_tokens: list[tokenize.TokenInfo] = []
    checking_class_header = False
    processing_typed_dict = False
    for token_info in model_tokens:
        token_type, token, _, _, _ = token_info
        if checking_class_header:
            # Checking if this is the start of a TypedDict definition
            assert token_type == tokenize.NAME
            if token.endswith("Dict"):
                processing_typed_dict = True
            # Either way, not checking the class header anymore
            checking_class_header = False
        elif processing_typed_dict:
            # Stop processing at the next dedent (no methods in the typed dicts)
            if token_type == tokenize.DEDENT:
                processing_typed_dict = False
            elif token_type == tokenize.NAME:
                # Check all name tokens for potential translation
                token = dict_token_replacements.get(token, token)
                token_info = token_info._replace(string=token)
        else:
            # Looking for the start of the next class definition
            if token_type == tokenize.NAME and token == "class":
                checking_class_header = True
        updated_tokens.append(token_info)
    updated_source: str = tokenize.untokenize(updated_tokens).decode("utf-8")
    # Inject the dict versions of required type unions
    for union_def, combined_def in combined_union_defs.items():
        updated_source = updated_source.replace(union_def, combined_def)
    # Insert __all__ between the imports and the schema definitions
    name_lines = (f'    "{name}",' for name in (sorted(exported_names)))
    lines_to_insert = ["__all__ = [", *name_lines, "]", "", ""]
    updated_source_lines = updated_source.splitlines()
    for idx, line in enumerate(updated_source_lines):
        if line.startswith("class"):
            break
    updated_source_lines[idx:idx] = lines_to_insert
    _MODEL_PATH.write_text("\n".join(updated_source_lines) + "\n")


def _main() -> None:
    if sys.argv[1:] == ["--regen-schema"] or not _SCHEMA_PATH.exists():
        _export_zod_schemas_to_json_schema()
    _generate_data_model_from_json_schema()
    print("Running automatic formatter after data model code generation")
    subprocess.run(["tox", "-e", "format"])


if __name__ == "__main__":
    _main()
