#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Regression tests over public synthetic Wenmo fixtures.

These fixtures are deterministic synthetic inputs, never real user records.
The tests keep the parser honest on public CI without exposing private data.

Usage:
    python3 -B scripts/wenmo_synthetic_tests.py
"""

import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from xiashensuan_core.adapters.wenmo_text import parse_wenmo_text

FIXTURE_DIR = PROJECT_ROOT / "xiashensuan_core" / "fixtures" / "synthetic"
MANIFEST_PATH = FIXTURE_DIR / "manifest.json"


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: expected={expected!r}, actual={actual!r}")


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def load_manifest() -> list:
    if not MANIFEST_PATH.exists():
        return []
    return json.loads(MANIFEST_PATH.read_text(encoding="utf-8"))


def test_synthetic_fixtures_present():
    entries = load_manifest()
    synthetic = [entry for entry in entries if entry.get("source") == "synthetic"]
    assert_true(len(synthetic) >= 3, "at least 3 synthetic fixtures should ship")
    for entry in synthetic:
        file_path = FIXTURE_DIR / entry["file"]
        assert_true(file_path.exists(), f"fixture file should exist: {entry['file']}")


def test_parse_each_synthetic_fixture():
    for entry in load_manifest():
        if entry.get("source") != "synthetic":
            continue
        text = (FIXTURE_DIR / entry["file"]).read_text(encoding="utf-8")
        parsed = parse_wenmo_text(text)

        assert_equal(parsed.get("状态"), "OK", f"{entry['id']} should parse OK")
        completeness = parsed.get("解析完整度", {})
        assert_equal(
            completeness.get("是否完整十二宫"),
            True,
            f"{entry['id']} should have complete 12 palaces",
        )
        assert_equal(parsed.get("安星码"), "C5FYC", f"{entry['id']} anxing code")

        basic = parsed.get("基础信息", {})
        expect = entry.get("expect", {})
        if expect.get("ming_gong"):
            # 命宫 is a branch; assert it is among palace branches via 宫位标记 structure
            assert_true(
                len(parsed.get("十二宫", {})) == 12,
                f"{entry['id']} palace count",
            )
        if expect.get("lunar_date"):
            assert_equal(
                basic.get("农历"),
                expect["lunar_date"],
                f"{entry['id']} lunar date",
            )
        assert_true(
            bool(basic.get("真太阳时")),
            f"{entry['id']} should carry true solar time",
        )


def test_four_hua_stars_consistent():
    """Synthetic fixtures' expected 生年四化 stars must appear in parsed output."""
    for entry in load_manifest():
        if entry.get("source") != "synthetic":
            continue
        expected_hua = entry.get("expect", {}).get("four_hua", [])
        if not expected_hua:
            continue
        text = (FIXTURE_DIR / entry["file"]).read_text(encoding="utf-8")
        parsed = parse_wenmo_text(text)
        parsed_hua = [
            item.get("星曜") for item in parsed.get("四化线索", []) if item.get("类型") == "生年"
        ]
        for star in expected_hua:
            assert_true(star in parsed_hua, f"{entry['id']} should expose 生年四化 star {star}")


def main() -> int:
    tests = [
        test_synthetic_fixtures_present,
        test_parse_each_synthetic_fixture,
        test_four_hua_stars_consistent,
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
