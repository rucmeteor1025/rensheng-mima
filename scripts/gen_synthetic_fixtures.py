#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""Generate synthetic Wenmo-format chart fixtures for public regression.

Privacy rule: every fixture below is a deterministic synthetic input that does
not come from a real user. No real birth records, names, or private reports
are ever emitted. Re-run this script to regenerate fixtures deterministically.

Usage:
    python3 -B scripts/gen_synthetic_fixtures.py [--verify]
"""

import argparse
import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

FIXTURE_DIR = PROJECT_ROOT / "xiashensuan_core" / "fixtures" / "synthetic"
MANIFEST_PATH = FIXTURE_DIR / "manifest.json"

# Deterministic synthetic inputs only. These are NOT real people.
SYNTHETIC_CASES = [
    {
        "id": "synthetic_19880620_0915_female",
        "gender": "女",
        "birth_date": "1988-06-20",
        "birth_time": "09:15",
        "place": "上海",
        "note": "Synthetic fixture A (deterministic demo input)",
    },
    {
        "id": "synthetic_20031102_2145_male",
        "gender": "男",
        "birth_date": "2003-11-02",
        "birth_time": "21:45",
        "place": "广州",
        "note": "Synthetic fixture B (deterministic demo input)",
    },
    {
        "id": "synthetic_19760308_0630_female",
        "gender": "女",
        "birth_date": "1976-03-08",
        "birth_time": "06:30",
        "place": "成都",
        "note": "Synthetic fixture C (deterministic demo input)",
    },
]


def load_engine_module() -> Any:
    module_path = PROJECT_ROOT / "scripts" / "ziwei_wenmo.py"
    spec = spec_from_file_location("ziwei_wenmo", module_path)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def _brightness_text(brightness: Dict[str, Dict[str, str]], star: str) -> str:
    for group in ("主星", "辅星"):
        value = brightness.get(group, {}).get(star, "")
        if value and value != "未定义":
            return f"[{value}]"
    return ""


def _four_hua_mark(star: str, transformations: Dict[str, Any]) -> str:
    """Return a 生年四化 mark like [生年禄] for a star, if present."""
    for hua_name, detail in transformations.get("四化", {}).items():
        if detail.get("星曜") == star:
            return f"[生年{hua_name}]"
    return ""


def render_tree_chart(engine: Any, case: Dict[str, str]) -> str:
    """Render a full Wenmo-style tree chart from the engine output."""
    result = engine.generate_ziwei_chart(
        engine.ZiweiInput(
            gender=case["gender"],
            birth_date=case["birth_date"],
            birth_time=case["birth_time"],
            place=case["place"],
        )
    )
    basic = result.basic_info
    lines: List[str] = []
    lines.append("文墨天机紫微斗数命盘（合成样例 / synthetic fixture）")
    lines.append(f"安星码：{basic['anxing_code']}")
    lines.append(f"性别：{basic['gender']}")
    lines.append(f"钟表时间：{basic['birth_date']} {basic['birth_time']}")
    lines.append(f"真太阳时：{basic['true_solar_time']}")
    lines.append(f"农历时间：{basic['lunar_date']}")
    lines.append(
        "节气四柱：{}年{}月{}日{}时".format(
            basic["year_ganzhi"],
            basic["month_ganzhi"],
            basic["day_ganzhi"],
            basic["time_ganzhi"],
        )
    )
    lines.append(f"五行局数：{basic['局名']}")
    lines.append(f"命主：{basic['命主']}")
    lines.append(f"身主：{basic['身主']}")
    lines.append(f"子年斗君：{basic['子斗']}")
    lines.append(f"身宫：{basic['身宫']}（{basic['身宫所属宫位']}）")
    lines.append("")

    shen_palace = basic.get("身宫所属宫位", "")
    for palace in result.palaces:
        name = palace["宫位"]
        ganzhi = palace["宫位干支"]
        flags = "[身宫]" if name == shen_palace else ""
        lines.append(f"├─{name}[{ganzhi}]{flags}")

        main_stars = palace.get("主星", [])
        assist_stars = palace.get("辅星", [])
        brightness = palace.get("星曜亮度", {})
        hua_map = result.transformations or {}

        main_text = "，".join(
            f"{star}{_brightness_text(brightness, star)}{_four_hua_mark(star, hua_map)}"
            for star in main_stars
        )
        lines.append(f"│  主星：{main_text if main_text else '空宫'}")
        if assist_stars:
            assist_text = "，".join(
                f"{star}{_brightness_text(brightness, star)}{_four_hua_mark(star, hua_map)}"
                for star in assist_stars
            )
            lines.append(f"│  辅星：{assist_text}")
        lines.append("")

    return "\n".join(lines)


def update_manifest(entries: List[Dict[str, Any]]) -> None:
    """Persist manifest entries with parse expectations (no real people)."""
    manifest: List[Dict[str, Any]] = []
    for entry in entries:
        basic = entry["basic"]
        manifest.append(
            {
                "id": entry["id"],
                "source": "synthetic",
                "note": entry["note"],
                "gender": basic["gender"],
                "birth_raw": f"{basic['birth_date']} {basic['birth_time']}",
                "calendar": "公历",
                "birth_standard_time": f"{basic['birth_date']} {basic['birth_time']}",
                "birth_date": basic["birth_date"],
                "birth_clock_time": basic["birth_time"],
                "true_solar_standard_time": basic["true_solar_time"],
                "true_solar_date": basic["true_solar_time"][:10],
                "true_solar_clock_time": basic["true_solar_time"][11:],
                "anxing_code": basic["anxing_code"],
                "expect": {
                    "ming_gong": basic["命宫"],
                    "shen_palace": basic["身宫所属宫位"],
                    "lunar_date": basic["lunar_date"],
                    "four_hua": sorted(
                        hua_detail.get("星曜", "")
                        for hua_detail in entry["transformations"].get("四化", {}).values()
                    ),
                },
                "file": entry["file"],
            }
        )
    FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
    MANIFEST_PATH.write_text(
        json.dumps(manifest, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )


def verify_fixture(text: str) -> Dict[str, Any]:
    """Parse fixture text back and report readiness summary."""
    from xiashensuan_core.adapters.wenmo_text import parse_wenmo_text

    parsed = parse_wenmo_text(text)
    completeness = parsed.get("解析完整度", {})
    return {
        "状态": parsed.get("状态"),
        "宫位数": completeness.get("宫位数", 0),
        "完整十二宫": completeness.get("是否完整十二宫", False),
        "安星码": parsed.get("安星码", ""),
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--verify", action="store_true", help="re-parse fixtures after writing")
    args = parser.parse_args()

    engine = load_engine_module()
    entries: List[Dict[str, Any]] = []
    for case in SYNTHETIC_CASES:
        result = engine.generate_ziwei_chart(
            engine.ZiweiInput(
                gender=case["gender"],
                birth_date=case["birth_date"],
                birth_time=case["birth_time"],
                place=case["place"],
            )
        )
        text = render_tree_chart(engine, case)
        file_name = f"{case['id']}.txt"
        (FIXTURE_DIR / file_name).write_text(text, encoding="utf-8")
        entries.append(
            {
                "id": case["id"],
                "note": case["note"],
                "file": file_name,
                "basic": result.basic_info,
                "transformations": result.transformations or {},
            }
        )
        print(f"wrote {file_name}")

    update_manifest(entries)
    print(f"manifest updated: {len(entries)} synthetic entries")

    if args.verify:
        print("\n== verify ==")
        for case in SYNTHETIC_CASES:
            file_name = f"{case['id']}.txt"
            summary = verify_fixture((FIXTURE_DIR / file_name).read_text(encoding="utf-8"))
            ok = summary["状态"] == "OK" and summary["完整十二宫"]
            print(f"{file_name}: {summary} -> {'OK' if ok else 'FAIL'}")
            if not ok:
                return 1
    return 0


if __name__ == "__main__":
    sys.exit(main())
