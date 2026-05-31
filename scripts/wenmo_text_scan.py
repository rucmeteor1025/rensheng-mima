#!/usr/bin/env python3
# -*- coding: utf-8 -*-

"""Scan local Wenmo text charts and summarize parser readiness."""

import argparse
import json
import re
import sys
from pathlib import Path
from typing import Any, Dict, List


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from xiashensuan_core.adapters.wenmo_text import GANZHI_RE, parse_wenmo_text


WENMO_SOURCE_RE = re.compile(r"文墨天机文字版|紫微层面（文字版数据）|文墨天机紫微斗数命盘", re.I)
ANXING_RE = re.compile(r"安星码\s*(?:\*\*)?\s*[:：]\s*C5FYC", re.I)
PALACE_STRUCTURE_RE = re.compile(
    rf"\*\*[\u4e00-\u9fff\s]+宫\*\*\s*[:：]|[├└]─?\s*[\u4e00-\u9fff\s]+宫\[{GANZHI_RE}\]"
)


def _read_text(path: Path, max_kb: int) -> str:
    if path.stat().st_size > max_kb * 1024:
        return ""
    return path.read_text(encoding="utf-8", errors="ignore")


def _is_strong_case(parsed: Dict[str, Any]) -> bool:
    basic = parsed.get("基础信息", {})
    completeness = parsed.get("解析完整度", {})
    return bool(
        parsed.get("状态") == "OK"
        and completeness.get("是否完整十二宫")
        and basic.get("性别")
        and basic.get("出生")
        and basic.get("真太阳时")
        and parsed.get("安星码")
    )


def _is_wenmo_candidate(text: str) -> bool:
    has_source_signal = bool(WENMO_SOURCE_RE.search(text) or ANXING_RE.search(text))
    has_palace_structure = bool(PALACE_STRUCTURE_RE.search(text))
    return has_source_signal and has_palace_structure


def scan_wenmo_files(record_dir: Path, max_kb: int = 512) -> Dict[str, Any]:
    rows: List[Dict[str, Any]] = []
    skipped_large = 0
    for path in sorted(record_dir.glob("*.md")):
        if path.stat().st_size > max_kb * 1024:
            skipped_large += 1
            continue
        text = _read_text(path, max_kb)
        if not _is_wenmo_candidate(text):
            continue
        parsed = parse_wenmo_text(text)
        completeness = parsed.get("解析完整度", {})
        basic = parsed.get("基础信息", {})
        rows.append(
            {
                "文件": str(path.relative_to(PROJECT_ROOT)),
                "状态": parsed.get("状态"),
                "强回归候选": _is_strong_case(parsed),
                "安星码": parsed.get("安星码"),
                "性别": basic.get("性别"),
                "出生": basic.get("出生"),
                "真太阳时": basic.get("真太阳时"),
                "宫位数": completeness.get("宫位数", 0),
                "完整十二宫": completeness.get("是否完整十二宫", False),
                "四化线索数": completeness.get("四化线索数", 0),
                "大限数": completeness.get("大限数", 0),
            }
        )

    return {
        "扫描目录": str(record_dir),
        "候选文件数": len(rows),
        "可解析文件数": sum(1 for row in rows if row["状态"] == "OK"),
        "完整十二宫数": sum(1 for row in rows if row["完整十二宫"]),
        "强回归候选数": sum(1 for row in rows if row["强回归候选"]),
        "跳过超大文件数": skipped_large,
        "文件": rows,
    }


def _print_text(summary: Dict[str, Any]) -> None:
    print("文墨文字盘扫描")
    print(f"扫描目录: {summary['扫描目录']}")
    print(
        "候选/可解析/完整十二宫/强回归: "
        f"{summary['候选文件数']}/{summary['可解析文件数']}/"
        f"{summary['完整十二宫数']}/{summary['强回归候选数']}"
    )
    if summary["跳过超大文件数"]:
        print(f"跳过超大文件: {summary['跳过超大文件数']}")
    print()
    for row in summary["文件"]:
        strong = "强样本" if row["强回归候选"] else "待补"
        print(
            f"- {row['文件']} | {row['状态']} | {strong} | "
            f"宫位 {row['宫位数']} | 四化 {row['四化线索数']} | 大限 {row['大限数']}"
        )


def main() -> None:
    parser = argparse.ArgumentParser(description="扫描文墨天机文字盘，评估 Adapter 解析完整度。")
    parser.add_argument(
        "--record-dir",
        default=str(PROJECT_ROOT / "private_records"),
        help="私有文墨样例目录，默认使用项目内 private_records（不应提交到 GitHub）。",
    )
    parser.add_argument("--max-kb", type=int, default=512, help="单文件读取上限，默认 512KB。")
    parser.add_argument("--json", action="store_true", help="输出 JSON 摘要。")
    args = parser.parse_args()

    summary = scan_wenmo_files(Path(args.record_dir), args.max_kb)
    if args.json:
        print(json.dumps(summary, ensure_ascii=False, indent=2))
    else:
        _print_text(summary)


if __name__ == "__main__":
    main()
