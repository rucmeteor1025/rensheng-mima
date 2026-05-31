#!/usr/bin/env python3
# -*- coding: utf-8 -*-

from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("ziwei_wenmo.py")


def load_module():
    spec = spec_from_file_location("ziwei_wenmo", MODULE_PATH)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: expected={expected!r}, actual={actual!r}")


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def test_reference_selfcheck(module):
    report = module.run_reference_selfcheck()
    assert_true(report["status"] in {"PASS", "PARTIAL"}, "reference selfcheck status should be explicit")
    assert_equal(len(report["case_results"]), 5, "reference selfcheck case count")
    passed_cases = [case["name"] for case in report["case_results"] if case["status"] == "PASS"]
    for case_name in [
        "wenmo_case_19850810_1620_male",
        "wenmo_case_19960120_1420_female",
        "wenmo_case_19990702_0900_female",
    ]:
        assert_true(case_name in passed_cases, f"{case_name} should remain calibrated")
    if report["status"] == "PARTIAL":
        assert_true(report["mismatch_count"] > 0, "partial calibration should expose mismatches")
        assert_true(bool(report["blocking_items"]), "partial calibration should expose blocking items")


def test_reference_match(module):
    result = module.generate_ziwei_chart(
        module.ZiweiInput(gender="男", birth_date="1985-08-10", birth_time="16:20")
    )
    reference_match = result.validation["reference_match"]
    assert_true(reference_match["matched"], "reference case should be matched")
    assert_equal(reference_match["status"], "PASS", "reference case comparison status")
    assert_equal(result.validation["文墨C5FYC逐盘校验"], "PASS", "reference validation final status")


def test_boundary_single(module):
    result = module.generate_ziwei_chart(
        module.ZiweiInput(
            gender="男",
            birth_date="1985-08-10",
            birth_time="15:06",
            longitude=117.289841,
            place="Demo Longitude 117.29E",
        )
    )
    boundary = result.validation["boundary"]
    assert_equal(boundary["status"], "NEAR_BOUNDARY", "single-chart boundary status")
    assert_equal(boundary["details"]["current_time_branch"], "未", "single-chart current time branch")
    assert_true(not boundary["details"]["should_generate_double_chart"], "single-chart should not emit double chart")


def test_true_solar_time_correction(module):
    result = module.generate_ziwei_chart(
        module.ZiweiInput(
            gender="男",
            birth_date="1985-08-10",
            birth_time="15:17",
            longitude=117.289841,
            place="Demo Longitude 117.29E",
        )
    )
    basic = result.basic_info
    assert_equal(basic["true_solar_time"], "1985-08-10 15:01", "true solar time should include equation-of-time correction")
    assert_equal(basic["time_correction"]["longitude_delta_minutes"], -11, "longitude correction should be exposed")
    assert_equal(basic["time_correction"]["equation_of_time_minutes"], -5, "equation-of-time correction should be exposed")
    assert_equal(basic["time_correction"]["delta_minutes"], -16, "total true solar correction should be exposed")

    already_true = module.generate_ziwei_chart(
        module.ZiweiInput(
            gender="女",
            birth_date="2012-02-24",
            birth_time="14:41",
            longitude=120.0,
            place="文墨真太阳时",
            time_is_true_solar=True,
        )
    )
    assert_equal(already_true.basic_info["true_solar_time"], "2012-02-24 14:41", "wenmo true solar input should not be corrected twice")
    assert_true(already_true.basic_info["time_correction"]["input_is_true_solar"], "true-solar flag should be preserved")


def test_boundary_double(module):
    package = module.generate_ziwei_chart_with_boundary_support(
        module.ZiweiInput(
            gender="男",
            birth_date="1985-08-10",
            birth_time="15:06",
            longitude=117.289841,
            place="Demo Longitude 117.29E",
            time_accuracy_minutes=10,
        )
    )
    summary = package["validation_summary"]
    assert_equal(package["mode"], "DOUBLE_CHART", "double-chart mode")
    assert_equal(package["boundary_analysis"]["status"], "BOUNDARY_SENSITIVE", "double-chart boundary status")
    assert_true({"未", "申"}.issubset(set(summary["candidate_branches"])), "double-chart candidate branches should include 未/申")
    assert_true({"命宫", "身宫", "命主", "子斗", "命宫干支"}.issubset(set(summary["differing_fields"])), "double-chart should expose core differing fields")


def test_first_batch_assist_stars(module):
    result_1985 = module.generate_ziwei_chart(
        module.ZiweiInput(gender="男", birth_date="1985-08-10", birth_time="16:20")
    )
    palace_map_1985 = {palace["宫位"]: palace for palace in result_1985.palaces}
    assert_true("天马" in palace_map_1985["命宫"]["辅星"], "1985 sample 命宫 should contain 天马")
    assert_true("左辅" in palace_map_1985["夫妻宫"]["辅星"], "1985 sample 夫妻宫 should contain 左辅")
    assert_true("文曲" in palace_map_1985["父母宫"]["辅星"], "1985 sample 父母宫 should contain 文曲")
    assert_true("天魁" in palace_map_1985["父母宫"]["辅星"], "1985 sample 父母宫 should contain 天魁")

    result_1999 = module.generate_ziwei_chart(
        module.ZiweiInput(gender="女", birth_date="1999-07-02", birth_time="09:00")
    )
    palace_map_1999 = {palace["宫位"]: palace for palace in result_1999.palaces}
    assert_true("左辅" in palace_map_1999["迁移宫"]["辅星"], "1999 sample 迁移宫 should contain 左辅")
    assert_true("文曲" in palace_map_1999["迁移宫"]["辅星"], "1999 sample 迁移宫 should contain 文曲")
    assert_true("天钺" in palace_map_1999["迁移宫"]["辅星"], "1999 sample 迁移宫 should contain 天钺")
    assert_true("天魁" in palace_map_1999["夫妻宫"]["辅星"], "1999 sample 夫妻宫 should contain 天魁")
    assert_equal(result_1999.transformations["四化"]["忌"]["宫支"], "申", "1999 sample 文曲化忌 should now be located")
    assert_equal(result_1999.transformations["四化"]["忌"]["状态"], "LOCATED", "1999 sample 文曲化忌 state")


def test_second_batch_assist_stars(module):
    result_1985 = module.generate_ziwei_chart(
        module.ZiweiInput(gender="男", birth_date="1985-08-10", birth_time="16:20")
    )
    palace_map_1985 = {palace["宫位"]: palace for palace in result_1985.palaces}
    assert_true("火星" in palace_map_1985["命宫"]["辅星"], "1985 sample 命宫 should contain 火星")
    assert_true("天喜" in palace_map_1985["子女宫"]["辅星"], "1985 sample 子女宫 should contain 天喜")
    assert_true("三台" in palace_map_1985["子女宫"]["辅星"], "1985 sample 子女宫 should contain 三台")
    assert_true("红鸾" in palace_map_1985["田宅宫"]["辅星"], "1985 sample 田宅宫 should contain 红鸾")
    assert_true("华盖" in palace_map_1985["福德宫"]["神煞"], "1985 sample 福德宫 should contain 华盖")

    result_1999 = module.generate_ziwei_chart(
        module.ZiweiInput(gender="女", birth_date="1999-07-02", birth_time="09:00")
    )
    palace_map_1999 = {palace["宫位"]: palace for palace in result_1999.palaces}
    assert_true("红鸾" in palace_map_1999["夫妻宫"]["辅星"], "1999 sample 夫妻宫 should contain 红鸾")
    assert_true("八座" in palace_map_1999["夫妻宫"]["辅星"], "1999 sample 夫妻宫 should contain 八座")
    assert_true("天贵" in palace_map_1999["兄弟宫"]["辅星"], "1999 sample 兄弟宫 should contain 天贵")
    assert_true("截空" in palace_map_1999["疾厄宫"]["神煞"], "1999 sample 疾厄宫 should contain 截空")
    assert_true("旬空" in palace_map_1999["夫妻宫"]["神煞"], "1999 sample 夫妻宫 should contain 旬空")


def test_brightness_and_palace_map(module):
    result = module.generate_ziwei_chart(
        module.ZiweiInput(gender="男", birth_date="1985-08-10", birth_time="16:20")
    )
    assert_true("命宫" in result.palace_map, "result should expose palace_map index")
    assert_equal(result.palace_map["迁移宫"]["主星"], ["紫微", "七杀"], "palace_map migration palace main stars")
    assert_equal(result.palace_map["迁移宫"]["星曜亮度"]["主星"]["紫微"], "旺", "紫微 brightness at 巳 should be 旺")
    assert_equal(result.palace_map["父母宫"]["星曜亮度"]["辅星"]["文曲"], "得", "文曲 brightness at 子 should be 得")
    assert_equal(result.validation["brightness"]["status"], "PARTIAL_VERIFIED", "brightness validation status")


def main():
    module = load_module()
    tests = [
        ("reference_selfcheck", test_reference_selfcheck),
        ("reference_match", test_reference_match),
        ("boundary_single", test_boundary_single),
        ("true_solar_time_correction", test_true_solar_time_correction),
        ("boundary_double", test_boundary_double),
        ("first_batch_assist_stars", test_first_batch_assist_stars),
        ("second_batch_assist_stars", test_second_batch_assist_stars),
        ("brightness_and_palace_map", test_brightness_and_palace_map),
    ]
    for name, test in tests:
        test(module)
        print(f"PASS {name}")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
