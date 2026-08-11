#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Validate engine output against versioned JSON Schema contracts.

The schemas live in xiashensuan_core/schemas/*.schema.json and are consumed
by frontend and downstream integrations. This suite keeps the engine honest
against those contracts without pulling in a third-party validator.

Usage:
    python3 -B scripts/schema_contract_tests.py
"""

import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

SCHEMA_DIR = PROJECT_ROOT / "xiashensuan_core" / "schemas"
SCRIPT_PATH = PROJECT_ROOT / "scripts" / "xiashensuan.py"

SCHEMA_TO_SECTION = {
    "bazi.schema.json": "八字命理",
    "ziwei.schema.json": "紫微斗数",
    "fusion.schema.json": "融合判断",
    "web_summary.schema.json": "风格化输出",
}

# Sample inputs used for contract validation (deterministic synthetic only).
SAMPLE_INPUTS = [
    {"birth_time": {"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20}, "gender": "男", "place": "北京"},
    {"birth_time": {"year": 1990, "month": 1, "day": 15, "hour": 14, "minute": 30}, "gender": "男", "place": "北京"},
    {"birth_time": {"year": 1996, "month": 1, "day": 20, "hour": 14, "minute": 20}, "gender": "女", "place": "广州"},
    {"birth_time": {"year": 2003, "month": 11, "day": 2, "hour": 21, "minute": 45}, "gender": "男", "place": "上海"},
]


def load_module():
    spec = spec_from_file_location("xiashensuan", SCRIPT_PATH)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def load_schemas() -> dict:
    schemas = {}
    for path in SCHEMA_DIR.glob("*.schema.json"):
        schemas[path.name] = json.loads(path.read_text(encoding="utf-8"))
    return schemas


def _type_name(value):
    if value is None:
        return "null"
    if isinstance(value, bool):
        return "boolean"
    if isinstance(value, str):
        return "string"
    if isinstance(value, int):
        return "integer"
    if isinstance(value, float):
        return "number"
    if isinstance(value, list):
        return "array"
    if isinstance(value, dict):
        return "object"
    return type(value).__name__


def validate_schema(instance, schema, path="$") -> list:
    """Minimal JSON Schema draft-07 subset: type, required, properties,
    items, enum, pattern, minItems, additionalProperties."""
    errors = []
    expected_type = schema.get("type")
    if expected_type:
        actual_type = _type_name(instance)
        if actual_type != expected_type:
            return [f"{path}: expected {expected_type}, got {actual_type}"]
    if instance is None:
        return errors

    if isinstance(instance, dict):
        if "required" in schema:
            for key in schema["required"]:
                if key not in instance:
                    errors.append(f"{path}: missing required key {key!r}")
        if schema.get("additionalProperties") is False:
            allowed = set(schema.get("properties", {}).keys())
            for key in instance:
                if key not in allowed:
                    errors.append(f"{path}: unexpected key {key!r}")
        for key, sub_schema in schema.get("properties", {}).items():
            if key in instance:
                errors.extend(validate_schema(instance[key], sub_schema, f"{path}.{key}"))
    elif isinstance(instance, list):
        if "minItems" in schema and len(instance) < schema["minItems"]:
            errors.append(f"{path}: expected >= {schema['minItems']} items, got {len(instance)}")
        if "items" in schema:
            for index, item in enumerate(instance):
                errors.extend(validate_schema(item, schema["items"], f"{path}[{index}]"))
    elif isinstance(instance, str):
        if "enum" in schema and instance not in schema["enum"]:
            errors.append(f"{path}: {instance!r} not in enum {schema['enum']}")
        if "pattern" in schema:
            import re
            if not re.search(schema["pattern"], instance):
                errors.append(f"{path}: {instance!r} does not match pattern {schema['pattern']}")
    return errors


def test_schema_files_parse():
    schemas = load_schemas()
    assert len(schemas) == 4, f"expected 4 schema files, got {len(schemas)}"
    for name, schema in schemas.items():
        assert schema.get("$schema", "").endswith("draft-07/schema#"), f"{name} should be draft-07"
        assert schema.get("version"), f"{name} should carry a version"
        assert "required" in schema, f"{name} should declare required fields"


def test_output_matches_schemas():
    module = load_module()
    schemas = load_schemas()
    tested_sections = 0
    for input_kwargs in SAMPLE_INPUTS:
        result = module.full_xiashensuan_analysis(**input_kwargs)
        for file_name, section in SCHEMA_TO_SECTION.items():
            if section not in result:
                continue
            schema = schemas[file_name]
            errors = validate_schema(result[section], schema)
            assert not errors, f"{file_name} vs {section}: {errors}"
            tested_sections += 1
    assert tested_sections >= 4, f"expected at least 4 section validations, got {tested_sections}"


def test_professional_mode_has_same_core_sections():
    module = load_module()
    schemas = load_schemas()
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20},
        gender="男",
        place="北京",
        mode="professional",
    )
    # Core engine sections must satisfy the same contracts in both modes.
    for file_name, section in SCHEMA_TO_SECTION.items():
        assert section in result, f"professional mode should include {section}"
        if file_name == "web_summary.schema.json":
            continue  # styled output uses mode-specific layouts; checked below
        errors = validate_schema(result[section], schemas[file_name])
        assert not errors, f"professional {file_name} vs {section}: {errors}"
    # 风格化输出 uses a professional layout; assert its mode marker only.
    styled = result.get("风格化输出", {})
    assert styled.get("模式") == "专业版", "professional styled output should declare mode"
    assert "总起断" in styled and "趋避建议" in styled, "professional styled output should keep its layout"


def main() -> int:
    tests = [
        test_schema_files_parse,
        test_output_matches_schemas,
        test_professional_mode_has_same_core_sections,
    ]
    failed = 0
    for test in tests:
        try:
            test()
            print(f"PASS {test.__name__}")
        except AssertionError as exc:
            failed += 1
            print(f"FAIL {test.__name__}: {exc}")
    if failed:
        print(f"{failed} test(s) failed")
        return 1
    print("ALL TESTS PASSED")
    return 0


if __name__ == "__main__":
    sys.exit(main())
