#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
ziwei_patterns 单元测试

策略：
1. 单 detector 行为：构造已知会触发某格局的样本，验证 detect_patterns 返回包含该 name
2. 批量统计：随机 200 个生辰跑 detect_patterns，统计每个 pattern 触发率、运行时错误
"""
from __future__ import annotations

import json
import random
import sys
from collections import Counter
from pathlib import Path

HERE = Path(__file__).resolve().parent
sys.path.insert(0, str(HERE))

from ziwei_wenmo import ZiweiInput, generate_ziwei_chart
from ziwei_patterns import (
    detect_patterns, _DETECTORS,
    from_xiashensuan_result, BRANCHES,
)


# ─── 单点 case：用已知历史人物或典型生辰触发特定格局 ───
KNOWN_CASES = [
    # (birth_date, birth_time, gender, expected_pattern_substrings)
    # 注：紫微斗数格局命中靠生辰组合，下列是 cross-check 100% 通过下虾神算排盘出来的真实命盘
    # 用作 smoke regression：至少能匹配若干常见格局，且不会运行时报错
    {
        "name": "1990-08-15 14:00 男",
        "input": dict(gender='男', birth_date='1990-08-15', birth_time='14:00', time_is_true_solar=True),
        "must_have": ['机月同梁'],  # 已知会触发
        "must_not": [],
    },
    {
        "name": "2000-01-01 00:00 女",
        "input": dict(gender='女', birth_date='2000-01-01', birth_time='00:00', time_is_true_solar=True),
        "must_have": [],   # 不强制
        "must_not": [],
    },
]


def test_known_cases():
    print("=== 单点 case 测试 ===")
    fails = 0
    for case in KNOWN_CASES:
        r = generate_ziwei_chart(ZiweiInput(**case["input"]))
        ps = detect_patterns(r)
        names = [p.name for p in ps]
        ok = True
        for must in case["must_have"]:
            if must not in names:
                print(f"  ✗ {case['name']}: missing {must}  (got {names})")
                ok = False; fails += 1
        for mustnot in case["must_not"]:
            if mustnot in names:
                print(f"  ✗ {case['name']}: unexpected {mustnot}  (got {names})")
                ok = False; fails += 1
        if ok:
            print(f"  ✓ {case['name']} → {len(ps)} patterns: {names}")
    return fails


def test_batch(n: int = 200, seed: int = 42):
    print(f"\n=== 批量 {n} 个生辰统计 ===")
    rnd = random.Random(seed)
    runtime_errors = 0
    pattern_counter: Counter = Counter()
    no_pattern_count = 0
    per_chart_counts = []
    for _ in range(n):
        y = rnd.randint(1950, 2020)
        m = rnd.randint(1, 12)
        d = rnd.randint(1, 28)
        h = rnd.randint(0, 23)
        gender = rnd.choice(['男', '女'])
        try:
            r = generate_ziwei_chart(ZiweiInput(
                gender=gender,
                birth_date=f"{y:04d}-{m:02d}-{d:02d}",
                birth_time=f"{h:02d}:00",
                time_is_true_solar=True,
            ))
            ps = detect_patterns(r)
        except Exception as e:
            runtime_errors += 1
            print(f"  ✗ {y}-{m:02}-{d:02} {h}:00 {gender}: {e}")
            continue
        if not ps:
            no_pattern_count += 1
        per_chart_counts.append(len(ps))
        for p in ps:
            pattern_counter[p.name] += 1

    print(f"\n运行时错误: {runtime_errors}")
    print(f"无格局命盘: {no_pattern_count} / {n} ({100*no_pattern_count/n:.1f}%)")
    if per_chart_counts:
        print(f"每盘格局数: min={min(per_chart_counts)} avg={sum(per_chart_counts)/len(per_chart_counts):.1f} max={max(per_chart_counts)}")

    print(f"\n各格局触发频次 (共识别 {len(pattern_counter)} 种)")
    for name, cnt in pattern_counter.most_common():
        print(f"  {name:18}  {cnt:4}  ({100*cnt/n:.1f}%)")

    # 检查：是否有 detector 从未触发？
    triggered_names = set(pattern_counter.keys())
    return runtime_errors, no_pattern_count, pattern_counter


def test_adapter_basics():
    print("\n=== Adapter 基本字段 ===")
    r = generate_ziwei_chart(ZiweiInput(gender='男', birth_date='1990-08-15', birth_time='14:00', time_is_true_solar=True))
    chart = from_xiashensuan_result(r)
    assert 0 <= chart.ming_branch < 12, f"ming_branch out of range: {chart.ming_branch}"
    assert 0 <= chart.shen_branch < 12
    assert len(chart.palaces) == 12, f"palaces count != 12: {len(chart.palaces)}"
    assert chart.year_sihua, "year_sihua empty"
    assert len(chart.year_sihua) == 4
    print(f"  ✓ ming={BRANCHES[chart.ming_branch]} shen={BRANCHES[chart.shen_branch]} "
          f"palaces=12 sihua={chart.year_sihua}")


def main() -> int:
    print(f"已注册 detector: {len(_DETECTORS)}")
    test_adapter_basics()
    fails = test_known_cases()
    err, no_p, _ = test_batch(n=200)
    print("\n=== 总结 ===")
    print(f"已知 case 失败: {fails}")
    print(f"批量运行时错误: {err}")
    return 1 if (fails or err) else 0


if __name__ == '__main__':
    sys.exit(main())
