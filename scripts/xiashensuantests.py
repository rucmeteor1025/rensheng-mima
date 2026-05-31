#!/usr/bin/env python3
# -*- coding: utf-8 -*-

import json
import sys
from importlib.util import module_from_spec, spec_from_file_location
from pathlib import Path


MODULE_PATH = Path(__file__).with_name("xiashensuan.py")
PROJECT_ROOT = MODULE_PATH.parents[1]
WENMO_FIXTURE_DIR = PROJECT_ROOT / "xiashensuan_core" / "fixtures" / "wenmo_cases"


def load_module():
    module_dir = str(MODULE_PATH.parent)
    if module_dir not in sys.path:
        sys.path.insert(0, module_dir)
    spec = spec_from_file_location("xiashensuan", MODULE_PATH)
    module = module_from_spec(spec)
    spec.loader.exec_module(module)
    return module


def assert_equal(actual, expected, message):
    if actual != expected:
        raise AssertionError(f"{message}: expected={expected!r}, actual={actual!r}")


def assert_true(condition, message):
    if not condition:
        raise AssertionError(message)


def test_default_main_flow(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20},
        gender="男",
        place="北京",
    )
    assert_equal(result["版本"]["主流程"], "虾神算V2", "main flow version")
    assert_equal(result["版本"]["默认入口"], "scripts/xiashensuan.py", "default entry path")
    assert_equal(result["版本"]["旧版入口"], "scripts/mingli.py", "legacy entry path")
    assert_equal(module.parse.__module__, "xiashensuan_core.modules.bazi", "main flow should import bazi base functions from core")
    assert_equal(result["紫微斗数"]["安星码"], "C5FYC", "ziwei anxing code")
    assert_equal(result["紫微斗数"]["状态"], "TRIAL_READY", "ziwei engine status")
    assert_equal(result["紫微斗数"]["基础信息"]["命宫"], "亥", "1985 sample ming gong")
    assert_true("专业分析" in result["八字命理"], "bazi should include professional analysis layer")
    assert_true("融合接口" in result["八字命理"], "bazi should include core fusion interface")
    assert_equal(
        result["八字命理"]["融合接口"]["核心权重建议"],
        0.5,
        "bazi should be equal-weight with ziwei in core fusion",
    )
    assert_true(
        "专业分析" in result["八字命理"]["融合接口"]["口径优先级"],
        "bazi fusion interface should document professional-layer priority",
    )
    assert_true(bool(result["融合判断"]["主轴"]), "integrated profile should have main line")
    assert_equal(result["输出架构"]["当前模式"], "life", "default output mode should be life")
    assert_equal(result["风格化输出"]["模式"], "生活版", "default styled output should be life mode")
    assert_true(bool(result["风格化输出"]["整体判断"]), "life mode should produce overall judgment")
    assert_true(
        "你这类人不是" in result["风格化输出"]["整体判断"],
        "life mode should use the nostalgic judgment-first phrasing",
    )
    assert_true(
        "真正适合的，不是" in result["风格化输出"]["事业与财运"],
        "life mode should sound like the nostalgic life-style voice",
    )
    assert_true(
        "盘面支撑" in result["风格化输出"],
        "life mode should keep a supporting trace of the source palaces",
    )


def test_professional_mode(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20},
        gender="男",
        place="北京",
        mode="professional",
    )
    assert_equal(result["输出架构"]["当前模式"], "professional", "professional output mode")
    assert_equal(result["风格化输出"]["模式"], "专业版", "styled output should be professional mode")
    assert_true(result["风格化输出"]["总起断"].startswith("此命"), "professional mode should open with a命理断语")
    assert_true("命盘信息" in result["风格化输出"], "professional mode should include chart info")
    assert_true("紫微斗数排盘" in result["风格化输出"], "professional mode should include ziwei section")
    assert_true(
        "真太阳时" in result["风格化输出"]["命盘信息"],
        "professional mode should surface true solar time in chart info",
    )
    assert_true(
        "翻成白话" in result["风格化输出"]["八字排盘"]["命局结构"],
        "professional mode should mix术语 with plain-language explanation",
    )
    assert_true(
        "月令与根气" in result["风格化输出"]["八字排盘"],
        "professional mode should expose a richer bazi structure block",
    )
    bazi_block = result["风格化输出"]["八字排盘"]
    assert_true("专业分析口径" in bazi_block, "professional mode should expose bazi analysis scope")
    assert_true("十神明细" in bazi_block, "professional mode should expose exact ten-god details")
    assert_true("五行强度" in bazi_block, "professional mode should expose weighted wuxing strength")
    assert_true("旺衰判断" in bazi_block, "professional mode should expose strength evidence")
    assert_true("用神策略" in bazi_block, "professional mode should expose useful-god strategy")
    assert_true("正文分析" in bazi_block, "professional mode should expose bazi body analysis")
    bazi_body = bazi_block["正文分析"]
    for section_name in ["命局总论", "日主旺衰", "十神主轴", "事业财运", "感情婚姻", "健康状态", "大运阶段"]:
        assert_true(section_name in bazi_body, f"bazi body analysis should include {section_name}")
        for field in ["盘面依据", "判断", "建议"]:
            assert_true(field in bazi_body[section_name], f"{section_name} should include {field}")
    assert_true(
        "流年仍为阶段主题提示" in bazi_body["专业正文口径"]["输出边界"],
        "bazi body analysis should keep flow-year event boundary",
    )
    structured_strength = result["八字命理"]["专业分析"]["旺衰判断"]["结构判断"]
    assert_true(
        f"结构判断为{structured_strength}" in bazi_block["基础排盘"],
        "professional bazi base line should prioritize structured strength",
    )
    assert_true(
        f"结构判断{structured_strength}" in bazi_block["命局结构"],
        "professional bazi structure line should use structured strength",
    )
    assert_true(
        f"结构判断{structured_strength}" in result["八字命理"]["融合接口"]["主轴摘要"],
        "bazi fusion summary should prioritize structured strength",
    )
    assert_true(
        "三方四正" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose sanfang-sizheng analysis",
    )
    assert_true(
        "四化流向" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose transformation flow analysis",
    )
    assert_true(
        "四化应事" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose real-world transformation implications",
    )
    assert_true(
        "四化应事分层" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose layered transformation implications",
    )
    hua_layers = result["风格化输出"]["紫微斗数排盘"]["四化应事分层"]
    for hua_name in ["禄", "权", "科", "忌"]:
        assert_true(hua_name in hua_layers, f"layered transformation block should include {hua_name}")
        assert_true("本命长期主题" in hua_layers[hua_name], f"{hua_name} should include long-term theme")
        assert_true("当前大运放大点" in hua_layers[hua_name], f"{hua_name} should include dayun amplification")
    assert_true(
        "宫位联动" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose palace linkages",
    )
    assert_true(
        "事业联动" in result["风格化输出"]["紫微斗数排盘"]["宫位联动"],
        "professional mode should include career linkage analysis",
    )
    assert_true(
        "宫位联动三段式" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose structured linkage triplets",
    )
    career_triplet = result["风格化输出"]["紫微斗数排盘"]["宫位联动三段式"]["事业联动"]
    relation_triplet = result["风格化输出"]["紫微斗数排盘"]["宫位联动三段式"]["感情联动"]
    wealth_triplet = result["风格化输出"]["紫微斗数排盘"]["宫位联动三段式"]["财运联动"]
    for triplet in [career_triplet, relation_triplet, wealth_triplet]:
        assert_true("主因" in triplet, "linkage triplet should include 主因")
        assert_true("触发条件" in triplet, "linkage triplet should include 触发条件")
        assert_true("风险点" in triplet, "linkage triplet should include 风险点")
    assert_true(
        "专题拆盘" in result["风格化输出"]["紫微斗数排盘"],
        "professional mode should expose themed professional reports",
    )
    topic_reports = result["风格化输出"]["紫微斗数排盘"]["专题拆盘"]
    for topic_name in ["事业专题", "感情专题", "财运专题"]:
        assert_true(topic_name in topic_reports, f"topic reports should include {topic_name}")
        for field in ["专题主轴", "关键宫位", "四化牵引", "当前大运切面", "风险提示", "专题结论"]:
            assert_true(field in topic_reports[topic_name], f"{topic_name} should include {field}")
    assert_true(
        "趋避建议" in result["风格化输出"],
        "professional mode should include practical guidance",
    )
    assert_true(
        "盘面依据" in result["风格化输出"]["融合判断"],
        "professional mode should make its reasoning path explicit",
    )


def test_boundary_double_chart(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 15, "minute": 6},
        gender="男",
        place="Demo Longitude 117.29E",
        longitude=117.289841,
        time_accuracy_minutes=10,
    )
    assert_true("边界双盘" in result, "boundary-sensitive input should emit double chart package")
    assert_equal(result["边界双盘"]["mode"], "DOUBLE_CHART", "double chart mode")
    assert_true(
        {"未", "申"}.issubset(set(result["边界双盘"]["validation_summary"]["candidate_branches"])),
        "candidate branches should include 未/申",
    )


def test_true_solar_time_correction(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 15, "minute": 17},
        gender="男",
        place="Demo Longitude 117.29E",
        longitude=117.289841,
        modules="core",
        output_mode="paired",
    )
    assert_equal(result["八字命理"]["八字"], "乙丑 甲申 辛巳 丙申", "liuxing bazi should keep wenmo hour pillar")
    assert_equal(result["八字命理"]["真太阳时"], "1985-08-10 15:01", "bazi should include equation-of-time correction")
    assert_equal(result["八字命理"]["时间校正"]["经度修正分钟"], -11, "bazi should expose longitude correction")
    assert_equal(result["八字命理"]["时间校正"]["时差方程分钟"], -5, "bazi should expose equation-of-time correction")
    ziwei_basic = result["紫微斗数"]["基础信息"]
    assert_equal(ziwei_basic["true_solar_time"], "1985-08-10 15:01", "ziwei should use the same true solar correction")
    assert_equal(ziwei_basic["time_correction"]["delta_minutes"], -16, "ziwei should expose total correction")
    assert_equal(result["基础信息"]["紫微时间来源"], "公历钟表时间+经度校正+时差方程", "time source should document eot correction")


def test_professional_focus_mode(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20},
        gender="男",
        place="北京",
        mode="professional",
        focus="career",
    )
    assert_equal(result["输出架构"]["当前模式"], "professional", "focus mode should still be professional")
    assert_equal(result["输出架构"]["当前专题焦点"], "career", "focus mode should record current focus")
    assert_true(result["输出架构"]["专题聚焦生效"], "focus mode should mark focus as active")
    assert_equal(result["风格化输出"]["专题模式"], "career", "styled output should expose active focus")
    assert_equal(result["风格化输出"]["当前专题"], "事业专题", "career focus should map to 事业专题")
    assert_true("专题引言" in result["风格化输出"], "focus mode should include a topic opening")
    assert_true("专题判断" in result["风格化输出"], "focus mode should expose topic judgment")
    assert_true("专题拆盘" in result["风格化输出"], "focus mode should expose sliced topic report")
    assert_true("事业专题" in result["风格化输出"]["专题拆盘"], "career focus should keep only career topic")
    assert_equal(len(result["风格化输出"]["专题拆盘"]), 1, "focus mode should narrow topic count")
    assert_true("事业联动" in result["风格化输出"]["专题三段式"], "career focus should keep only career triplet")
    assert_equal(len(result["风格化输出"]["专题三段式"]), 1, "focus mode should narrow linkage triplets")
    assert_true("事业趋避" in result["风格化输出"]["趋避建议"], "career focus should keep matching guidance")
    assert_equal(len(result["风格化输出"]["趋避建议"]), 1, "focus mode should narrow guidance block")
    assert_true("专题收束" in result["风格化输出"], "focus mode should include a topic closing")


def test_personality_single_output(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20},
        gender="男",
        modules="mbti,zodiac,blood",
        output_mode="single",
        mbti="INFJ-A",
        blood_type="O",
    )
    route = result["输出架构"]["模块路由"]
    assert_equal(route["启用模块"], ["mbti", "zodiac", "blood"], "single route modules")
    assert_equal(result["风格化输出"]["模式"], "单项模块版", "single output mode")
    assert_equal(result["MBTI"]["基础类型"], "INFJ", "MBTI variant should normalize to base type")
    assert_equal(result["MBTI"]["亚型"], "A", "MBTI variant should keep subtype")
    assert_equal(result["MBTI"]["模块定位"], "人格补充模块", "MBTI should be upgraded to personality supplement")
    assert_true("人格补充画像" in result["MBTI"], "MBTI should expose supplement profile")
    assert_true("四维结构" in result["MBTI"], "MBTI should expose four-dimension structure")
    assert_equal(result["星座"]["模块定位"], "人格补充模块", "zodiac should be upgraded to personality supplement")
    assert_true("人格补充画像" in result["星座"], "zodiac should expose supplement profile")
    assert_true("三分元素" in result["星座"], "zodiac should expose element layer")
    assert_equal(result["血型"]["类型"], "O型", "blood type should normalize")
    assert_equal(result["血型"]["模块定位"], "人格补充模块", "blood should be upgraded to personality supplement")
    assert_true("人格补充画像" in result["血型"], "blood should expose supplement profile")
    assert_true("模块拆解" in result["风格化输出"], "single output should expose module breakdown")
    assert_true("血型" in result["风格化输出"]["模块拆解"], "single output should include blood module")
    assert_true("人格补充画像" in result["风格化输出"], "single output should expose combined personality supplement")
    assert_equal(
        result["风格化输出"]["人格补充画像"]["状态"],
        "OK",
        "combined personality supplement should be valid",
    )


def test_all_fusion_output(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1996, "month": 1, "day": 20, "hour": 14, "minute": 20},
        gender="女",
        modules="all",
        output_mode="fusion",
        mbti="INFJ",
        blood_type="A型",
    )
    assert_equal(result["风格化输出"]["模式"], "融合版", "fusion output mode")
    fusion = result["风格化输出"]["融合画像"]
    assert_true("权重" in fusion, "fusion report should expose weights")
    assert_true("八字" in fusion["权重"], "fusion weights should include bazi")
    assert_true("紫微斗数" in fusion["权重"], "fusion weights should include ziwei")
    assert_true("人格补充" in fusion, "fusion report should include personality supplement")
    assert_equal(fusion["人格补充"]["状态"], "OK", "fusion personality supplement should be valid")
    assert_true("核心命理融合" in fusion, "fusion report should include core bazi-ziwei fusion")
    assert_equal(fusion["核心命理融合"]["核心权重"], {"八字": 0.5, "紫微斗数": 0.5}, "core fusion should keep bazi and ziwei equal")
    assert_true("冲突解释" in fusion, "fusion report should explain conflicts")
    assert_true("融合引擎" in result["融合判断"], "legacy fusion block should keep fusion v1 attachment")


def test_ziwei_professional_only(module):
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1985, "month": 8, "day": 10, "hour": 16, "minute": 20},
        gender="男",
        modules="ziwei",
        output_mode="single",
        mode="professional",
    )
    assert_equal(result["输出架构"]["模块路由"]["启用模块"], ["ziwei"], "ziwei-only route")
    assert_equal(result["风格化输出"]["模式"], "紫微斗数专业版", "ziwei professional renderer")
    assert_true("命身主轴" in result["风格化输出"], "ziwei renderer should expose ming-shen axis")
    assert_true("四化流向" in result["风格化输出"], "ziwei renderer should expose four hua flow")


def test_wenmo_text_adapter(module):
    wenmo_text = """
> **数据源**：文墨天机文字版数据（安星码: C5FYC）
- **昵称**：00
- **性别**：女
- **出生**：1999-07-02 09:00（公历）
- **出生地经度**：120.000
- **真太阳时**：1999-07-02 08:56
- **八字**：己卯 庚午 乙卯 庚辰（节气四柱）
- **五行局**：火六局
- **命主**：禄存；**身主**：天同；**子年斗君**：子；**身宫**：戌
- **身宫**：戌（财帛宫，七杀[庙]）
- **来因宫**：田宅宫（己巳，太阴[陷][↑忌] + 陀罗[陷]）
- **命宫**：丙寅，破军[陷] + 铃星[庙]
- **兄弟宫**：丁丑，空宫 + 火星[旺]
- **夫妻宫**：丙子，紫微[平] + 天魁[旺]
- **财帛宫**：甲戌（身宫），七杀[庙]
- **官禄宫**：庚午，贪狼[旺][生年权] + 文昌[陷][↑科]
- 6~15虚岁：命宫（丙寅）
- 36~45虚岁：田宅宫（己巳，来因宫）
"""
    result = module.full_xiashensuan_analysis(
        birth_time={"year": 1999, "month": 7, "day": 2, "hour": 9, "minute": 0},
        gender="女",
        modules="ziwei",
        output_mode="single",
        mode="professional",
        wenmo_text=wenmo_text,
    )
    assert_true("文墨文字盘" in result, "wenmo text should be parsed")
    assert_equal(result["文墨文字盘"]["解析"]["状态"], "OK", "wenmo parser status")
    assert_true("命宫" in result["文墨文字盘"]["解析"]["十二宫"], "wenmo parser should expose palaces")
    parsed = result["文墨文字盘"]["解析"]
    assert_equal(parsed["解析版本"], "wenmo-text-structured-v2", "wenmo parser version")
    assert_equal(parsed["基础信息"]["出生原文"], "1999-07-02 09:00（公历）", "markdown birth raw")
    assert_equal(parsed["基础信息"]["历法"], "公历", "markdown birth calendar")
    assert_equal(parsed["基础信息"]["钟表时间"], "1999-07-02 09:00（公历）", "markdown clock time fallback")
    assert_equal(parsed["基础信息"]["出生标准时间"], "1999-07-02 09:00", "markdown birth normalized")
    assert_equal(parsed["基础信息"]["出生日期"], "1999-07-02", "markdown birth date")
    assert_equal(parsed["基础信息"]["出生时间"], "09:00", "markdown birth time")
    assert_equal(parsed["基础信息"]["真太阳时原文"], "1999-07-02 08:56", "markdown true solar raw")
    assert_equal(parsed["基础信息"]["真太阳标准时间"], "1999-07-02 08:56", "markdown true solar normalized")
    assert_equal(parsed["基础信息"]["真太阳日期"], "1999-07-02", "markdown true solar date")
    assert_equal(parsed["基础信息"]["真太阳时间"], "08:56", "markdown true solar time")
    assert_equal(parsed["基础信息"]["时间来源格式"], "MARKDOWN_TEXT", "markdown time source format")
    assert_equal(parsed["基础信息"]["身宫详情"]["所属宫位"], "财帛宫", "shengong summary should prefer detailed palace line")
    assert_equal(parsed["基础信息"]["身宫详情"]["星曜"], ["七杀"], "shengong summary should parse stars")
    assert_equal(parsed["基础信息"]["来因宫详情"]["宫干支"], "己巳", "laiyin summary should parse ganzhi")
    assert_equal(parsed["基础信息"]["来因宫详情"]["星曜"], ["太阴", "陀罗"], "laiyin summary should parse stars")
    assert_equal(parsed["十二宫"]["命宫"]["主星"], ["破军"], "palace parser should split main stars")
    assert_equal(parsed["十二宫"]["命宫"]["辅星"], ["铃星"], "palace parser should split support stars")
    assert_equal(parsed["十二宫"]["命宫"]["星曜详情"][0]["亮度"], "陷", "palace parser should parse brightness")
    assert_equal(parsed["十二宫"]["兄弟宫"]["星曜"], ["火星"], "empty palace should keep actual support stars")
    assert_true(parsed["十二宫"]["兄弟宫"]["标记"]["空宫"], "empty palace marker should be kept")
    career_hua = parsed["十二宫"]["官禄宫"]["四化线索"]
    assert_true(
        {"星曜": "贪狼", "化": "权", "类型": "生年", "符号": "", "原文标记": "生年权", "原文": "贪狼[旺][生年权]"} in career_hua,
        "palace parser should parse natal hua marks",
    )
    assert_true(
        {"星曜": "文昌", "化": "科", "类型": "飞化", "符号": "↑", "原文标记": "↑科", "原文": "文昌[陷][↑科]"} in career_hua,
        "palace parser should parse flying hua marks",
    )
    assert_equal(parsed["大限序列"][1]["宫干支"], "己巳", "dayun parser should parse palace ganzhi")
    assert_equal(parsed["大限序列"][1]["标记"], ["来因宫"], "dayun parser should keep markers")
    assert_true("文墨天机文字盘" in result["风格化输出"]["数据源"], "ziwei renderer should mention wenmo source")
    assert_true("文墨文字盘比对" in result["风格化输出"]["校验"], "ziwei renderer should include wenmo comparison")


def load_wenmo_fixture_cases():
    manifest = json.loads((WENMO_FIXTURE_DIR / "manifest.json").read_text(encoding="utf-8"))
    for case in manifest:
        case["text"] = (WENMO_FIXTURE_DIR / case["file"]).read_text(encoding="utf-8")
    return manifest


def assert_wenmo_fixture_case(module, case):
    parsed = module.parse_wenmo_text(case["text"])
    expected = case["expected"]
    label = case["id"]
    assert_equal(parsed["状态"], "OK", f"{label} parser status")
    assert_equal(parsed["解析完整度"]["格式"], expected["format"], f"{label} format")
    assert_equal(parsed["解析完整度"]["宫位数"], expected["palace_count"], f"{label} palace count")
    assert_equal(parsed["基础信息"]["性别"], expected["gender"], f"{label} gender")
    assert_equal(parsed["基础信息"]["真太阳时"], expected["true_solar_time"], f"{label} true solar time")
    if "birth_raw" in expected:
        assert_equal(parsed["基础信息"]["出生原文"], expected["birth_raw"], f"{label} birth raw")
    if "calendar" in expected:
        assert_equal(parsed["基础信息"]["历法"], expected["calendar"], f"{label} calendar")
    if "clock_time" in expected:
        assert_equal(parsed["基础信息"]["钟表时间"], expected["clock_time"], f"{label} clock time")
    if "birth_standard_time" in expected:
        assert_equal(parsed["基础信息"]["出生标准时间"], expected["birth_standard_time"], f"{label} birth standard time")
    if "birth_date" in expected:
        assert_equal(parsed["基础信息"]["出生日期"], expected["birth_date"], f"{label} birth date")
    if "birth_clock_time" in expected:
        assert_equal(parsed["基础信息"]["出生时间"], expected["birth_clock_time"], f"{label} birth clock time")
    if "true_solar_standard_time" in expected:
        assert_equal(parsed["基础信息"]["真太阳标准时间"], expected["true_solar_standard_time"], f"{label} true solar standard time")
    if "true_solar_date" in expected:
        assert_equal(parsed["基础信息"]["真太阳日期"], expected["true_solar_date"], f"{label} true solar date")
    if "true_solar_clock_time" in expected:
        assert_equal(parsed["基础信息"]["真太阳时间"], expected["true_solar_clock_time"], f"{label} true solar clock time")
    if "time_source_format" in expected:
        assert_equal(parsed["基础信息"]["时间来源格式"], expected["time_source_format"], f"{label} time source format")
    assert_equal(parsed["基础信息"]["命主"], expected["mingzhu"], f"{label} mingzhu")
    assert_equal(parsed["基础信息"]["身主"], expected["shenzhu"], f"{label} shenzhu")
    assert_equal(parsed["基础信息"]["子年斗君"], expected["doujun"], f"{label} doujun")
    assert_equal(parsed["基础信息"]["身宫详情"]["所属宫位"], expected["shengong_palace"], f"{label} shengong palace")
    assert_equal(parsed["基础信息"]["来因宫详情"]["宫位"], expected["laiyin_palace"], f"{label} laiyin palace")

    for palace_name, palace_expected in expected.get("palaces", {}).items():
        palace = parsed["十二宫"][palace_name]
        if "main_stars" in palace_expected:
            assert_equal(palace["主星"], palace_expected["main_stars"], f"{label} {palace_name} main stars")
        if "support_stars" in palace_expected:
            assert_equal(palace["辅星"], palace_expected["support_stars"], f"{label} {palace_name} support stars")
        for marker_name, marker_value in palace_expected.get("markers", {}).items():
            assert_equal(palace["标记"][marker_name], marker_value, f"{label} {palace_name} {marker_name} marker")

    for transformation in expected.get("transformations", []):
        palace_name = transformation["palace"]
        expected_transformation = {k: v for k, v in transformation.items() if k != "palace"}
        assert_true(
            expected_transformation in parsed["十二宫"][palace_name]["四化线索"],
            f"{label} should parse {palace_name} transformation {expected_transformation}",
        )

    if "dayun_first_palace" in expected:
        assert_equal(parsed["大限序列"][0]["宫位"], expected["dayun_first_palace"], f"{label} dayun first palace")

    if expected.get("analysis_check"):
        result = module.full_xiashensuan_analysis(
            birth_time=case["birth_time"],
            gender=case["gender"],
            place=case["place"],
            longitude=case["longitude"],
            modules="ziwei",
            output_mode="single",
            mode="professional",
            wenmo_text=case["text"],
        )
        assert_equal(result["基础信息"]["紫微时间来源"], "文墨天机真太阳时原文", f"{label} true solar time source")
        assert_equal(
            result["风格化输出"]["命盘信息"]["公历"],
            expected["normalized_true_solar_datetime"],
            f"{label} normalized true solar time",
        )


def test_wenmo_api_tree_adapter(module):
    cases = load_wenmo_fixture_cases()
    if not cases:
        print("SKIP wenmo_api_tree_adapter: public repository excludes private Wenmo fixture records")
        return
    for case in cases:
        assert_wenmo_fixture_case(module, case)


def test_report_print_view_renderer(module):
    cases = load_wenmo_fixture_cases()
    if not cases:
        print("SKIP report_print_view_renderer: public repository excludes private Wenmo fixture records")
        return
    case = cases[0]
    result = module.full_xiashensuan_analysis(
        birth_time=case["birth_time"],
        gender=case["gender"],
        place=case["place"],
        longitude=case["longitude"],
        modules="ziwei",
        output_mode="single",
        mode="professional",
        wenmo_text=case["text"],
    )
    report = module.build_report_text(result)
    assert_true(report.startswith("# 紫微斗数专业版"), "report view should render markdown title")
    assert_true("## 命盘信息" in report, "report view should include chart info section")
    assert_true("出生：公历 2012-02-24 14:55" in report, "report view should keep original clock birth time")
    assert_true("真太阳时：2012-02-24 14:41" in report, "report view should keep true solar time")
    assert_true("## 总断" in report, "report view should include total judgment")
    assert_true("正文分析" in result["风格化输出"], "ziwei renderer should expose structured body analysis")
    assert_true("阶段提醒" in result["风格化输出"]["正文分析"], "body analysis should include stage reminders")
    assert_true("专业正文口径" in result["风格化输出"]["正文分析"], "body analysis should include reading scope")
    assert_true(
        "盘面依据" in result["风格化输出"]["正文分析"]["事业学业"],
        "topic body analysis should include chart evidence",
    )
    assert_true(
        "建议" in result["风格化输出"]["正文分析"]["感情婚姻"],
        "topic body analysis should include actionable guidance",
    )
    stage = result["风格化输出"]["正文分析"]["阶段提醒"]
    assert_true("低（结构提示）" in stage["置信等级"], "flow-year theme index should be marked low confidence")
    assert_true("前八步大限" in stage, "wenmo report should include dayun summary")
    assert_true("流年主题索引" in stage, "wenmo report should include yearly theme index")
    assert_true(53 in result["文墨文字盘"]["解析"]["十二宫"]["命宫"]["流年"], "tree parser should keep the fifth flow-year age")
    assert_true("5~14虚岁走命宫" in report, "report view should include first dayun reminder")
    assert_true("45~54虚岁走财帛宫" in report, "report view should include fifth dayun reminder")
    assert_true("75~84虚岁走交友宫" in report, "report view should include eighth dayun reminder")
    assert_true("流年主题索引" in report, "report view should use theme-index wording")
    assert_true("5虚岁：主题落命宫" in report, "report view should include yearly theme palace")
    assert_true("54虚岁：主题落父母宫" in report, "report view should include late available theme palace")
    assert_true("不做吉凶与具体事件判断" in report, "report view should warn against event-level flow-year judgment")
    assert_true("## 正文分析" in report, "report view should render detailed body section")
    assert_true("### 专业正文口径" in report, "report view should render professional prose scope")
    assert_true("#### 盘面依据" in report, "report view should render chart evidence blocks")
    assert_true("- 判断：" in report, "report view should render judgment blocks")
    assert_true("- 建议：" in report, "report view should render guidance blocks")
    assert_true("## 趋避建议" in report, "report view should include guidance")
    assert_true("## 校验" in report, "report view should include compact validation")
    assert_true(not report.lstrip().startswith("{"), "report view should not be JSON")
    assert_true("文墨文字盘摘要" not in report, "report view should avoid dumping full wenmo parsed payload")


def main():
    module = load_module()
    tests = [
        ("default_main_flow", test_default_main_flow),
        ("professional_mode", test_professional_mode),
        ("boundary_double_chart", test_boundary_double_chart),
        ("true_solar_time_correction", test_true_solar_time_correction),
        ("professional_focus_mode", test_professional_focus_mode),
        ("personality_single_output", test_personality_single_output),
        ("all_fusion_output", test_all_fusion_output),
        ("ziwei_professional_only", test_ziwei_professional_only),
        ("wenmo_text_adapter", test_wenmo_text_adapter),
        ("wenmo_api_tree_adapter", test_wenmo_api_tree_adapter),
        ("report_print_view_renderer", test_report_print_view_renderer),
    ]
    for name, test in tests:
        test(module)
        print(f"PASS {name}")
    print("ALL TESTS PASSED")


if __name__ == "__main__":
    main()
