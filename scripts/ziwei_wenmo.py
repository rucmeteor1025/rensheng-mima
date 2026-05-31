#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
文墨天机 C5FYC 对齐版紫微斗数重构模块（独立新版）

说明：
- 本模块独立于旧版 mingli.py，避免影响现有八字/紫微逻辑
- 当前目标是提供“可试盘”的文墨天机 C5FYC 重构底盘
- 可确定部分按公开三合派安星公式落地；未拿到文墨天机专有校验依据的部分显式标记为未校验
"""

from dataclasses import dataclass, asdict
from datetime import datetime, timedelta
import math
from typing import Dict, Any, List, Tuple

BEIJING_LONGITUDE = 116.4
ANXING_CODE = "C5FYC"
EARTH_ROTATION_MIN_PER_DEGREE = 4

HEAVENLY_STEMS = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
EARTHLY_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
PALACE_BRANCHES_FROM_YIN = ["寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥", "子", "丑"]
PALACE_OUTPUT_ORDER = ["亥", "戌", "酉", "申", "未", "午", "巳", "辰", "卯", "寅", "丑", "子"]
HOUR_BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
PALACE_NAME_SEQUENCE = [
    "命宫",
    "兄弟宫",
    "夫妻宫",
    "子女宫",
    "财帛宫",
    "疾厄宫",
    "迁移宫",
    "交友宫",
    "官禄宫",
    "田宅宫",
    "福德宫",
    "父母宫",
]
SHEN_GONG_ALLOWED = {"命宫", "夫妻宫", "财帛宫", "迁移宫", "官禄宫", "福德宫"}

SI_HUA_TABLE = {
    "甲": {"禄": "廉贞", "权": "破军", "科": "武曲", "忌": "太阳"},
    "乙": {"禄": "天机", "权": "天梁", "科": "紫微", "忌": "太阴"},
    "丙": {"禄": "天同", "权": "天机", "科": "文昌", "忌": "廉贞"},
    "丁": {"禄": "太阴", "权": "天同", "科": "天机", "忌": "巨门"},
    "戊": {"禄": "贪狼", "权": "太阴", "科": "右弼", "忌": "天机"},
    "己": {"禄": "武曲", "权": "贪狼", "科": "天梁", "忌": "文曲"},
    "庚": {"禄": "太阳", "权": "武曲", "科": "太阴", "忌": "天同"},
    "辛": {"禄": "巨门", "权": "太阳", "科": "文曲", "忌": "文昌"},
    "壬": {"禄": "天梁", "权": "紫微", "科": "左辅", "忌": "武曲"},
    "癸": {"禄": "破军", "权": "巨门", "科": "太阴", "忌": "贪狼"},
}

MING_ZHU_TABLE = {
    "子": "贪狼",
    "丑": "巨门",
    "寅": "禄存",
    "卯": "文曲",
    "辰": "廉贞",
    "巳": "武曲",
    "午": "破军",
    "未": "武曲",
    "申": "廉贞",
    "酉": "文曲",
    "戌": "禄存",
    "亥": "巨门",
}

SHEN_ZHU_TABLE = {
    "子": "火星",
    "丑": "天相",
    "寅": "天梁",
    "卯": "天同",
    "辰": "文昌",
    "巳": "天机",
    "午": "火星",
    "未": "天相",
    "申": "天梁",
    "酉": "天同",
    "戌": "文昌",
    "亥": "天机",
}

WUXING_JU_LABELS = {
    "水": "水二局",
    "木": "木三局",
    "金": "金四局",
    "土": "土五局",
    "火": "火六局",
}

ZIWEI_GROUP_OFFSETS = [
    ("紫微", 0),
    ("天机", -1),
    ("太阳", -3),
    ("武曲", -4),
    ("天同", -5),
    ("廉贞", -8),
]

TIANFU_GROUP_OFFSETS = [
    ("天府", 0),
    ("太阴", 1),
    ("贪狼", 2),
    ("巨门", 3),
    ("天相", 4),
    ("天梁", 5),
    ("七杀", 6),
    ("破军", 10),
]

LUCUN_BY_YEAR_STEM = {
    "甲": "寅",
    "乙": "卯",
    "丙": "巳",
    "丁": "午",
    "戊": "巳",
    "己": "午",
    "庚": "申",
    "辛": "酉",
    "壬": "亥",
    "癸": "子",
}

TIANKUI_TIANYUE_BY_YEAR_STEM = {
    "甲": ("丑", "未"),
    "乙": ("子", "申"),
    "丙": ("亥", "酉"),
    "丁": ("亥", "酉"),
    "戊": ("丑", "未"),
    "己": ("子", "申"),
    "庚": ("丑", "未"),
    "辛": ("午", "寅"),
    "壬": ("卯", "巳"),
    "癸": ("卯", "巳"),
}

TIANMA_BY_YEAR_BRANCH = {
    "寅": "申",
    "午": "申",
    "戌": "申",
    "申": "寅",
    "子": "寅",
    "辰": "寅",
    "巳": "亥",
    "酉": "亥",
    "丑": "亥",
    "亥": "巳",
    "卯": "巳",
    "未": "巳",
}

HUOLING_STARTS_BY_YEAR_BRANCH = {
    "申": ("寅", "戌"),
    "子": ("寅", "戌"),
    "辰": ("寅", "戌"),
    "寅": ("丑", "卯"),
    "午": ("丑", "卯"),
    "戌": ("丑", "卯"),
    "巳": ("卯", "戌"),
    "酉": ("卯", "戌"),
    "丑": ("卯", "戌"),
    "亥": ("酉", "戌"),
    "卯": ("酉", "戌"),
    "未": ("酉", "戌"),
}

JIANGXING_BY_YEAR_BRANCH = {
    "寅": "午",
    "午": "午",
    "戌": "午",
    "申": "子",
    "子": "子",
    "辰": "子",
    "巳": "酉",
    "酉": "酉",
    "丑": "酉",
    "亥": "卯",
    "卯": "卯",
    "未": "卯",
}

HUAGAI_BY_YEAR_BRANCH = {
    "子": "辰",
    "辰": "辰",
    "申": "辰",
    "丑": "丑",
    "巳": "丑",
    "酉": "丑",
    "寅": "戌",
    "午": "戌",
    "戌": "戌",
    "卯": "未",
    "未": "未",
    "亥": "未",
}

JIEKONG_BY_YEAR_STEM = {
    "甲": ("申", "酉"),
    "己": ("申", "酉"),
    "乙": ("午", "未"),
    "庚": ("午", "未"),
    "丙": ("辰", "巳"),
    "辛": ("辰", "巳"),
    "丁": ("寅", "卯"),
    "壬": ("寅", "卯"),
    "戊": ("子", "丑"),
    "癸": ("子", "丑"),
}

STAR_BRIGHTNESS_BY_BRANCH = {
    "紫微": dict(zip(PALACE_BRANCHES_FROM_YIN, ["旺", "旺", "得", "旺", "庙", "庙", "旺", "旺", "得", "旺", "平", "庙"])),
    "天机": dict(zip(PALACE_BRANCHES_FROM_YIN, ["得", "旺", "利", "平", "庙", "陷", "得", "旺", "利", "平", "庙", "陷"])),
    "太阳": dict(zip(PALACE_BRANCHES_FROM_YIN, ["旺", "庙", "旺", "旺", "旺", "得", "得", "陷", "不", "陷", "陷", "不"])),
    "武曲": dict(zip(PALACE_BRANCHES_FROM_YIN, ["得", "利", "庙", "平", "旺", "庙", "得", "利", "庙", "平", "旺", "庙"])),
    "天同": dict(zip(PALACE_BRANCHES_FROM_YIN, ["利", "平", "平", "庙", "陷", "不", "旺", "平", "平", "庙", "旺", "不"])),
    "廉贞": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "平", "利", "陷", "平", "利", "庙", "平", "利", "陷", "平", "利"])),
    "天府": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "得", "庙", "得", "旺", "庙", "得", "旺", "庙", "得", "庙", "庙"])),
    "太阴": dict(zip(PALACE_BRANCHES_FROM_YIN, ["旺", "陷", "陷", "陷", "不", "不", "利", "不", "旺", "庙", "庙", "庙"])),
    "贪狼": dict(zip(PALACE_BRANCHES_FROM_YIN, ["平", "利", "庙", "陷", "旺", "庙", "平", "利", "庙", "陷", "旺", "庙"])),
    "巨门": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "庙", "陷", "旺", "旺", "不", "庙", "庙", "陷", "旺", "旺", "不"])),
    "天相": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "陷", "得", "得", "庙", "得", "庙", "陷", "得", "得", "庙", "庙"])),
    "天梁": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "庙", "庙", "陷", "庙", "旺", "陷", "得", "庙", "陷", "庙", "旺"])),
    "七杀": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "旺", "庙", "平", "旺", "庙", "庙", "庙", "庙", "平", "旺", "庙"])),
    "破军": dict(zip(PALACE_BRANCHES_FROM_YIN, ["得", "陷", "旺", "平", "庙", "旺", "得", "陷", "旺", "平", "庙", "旺"])),
    "文昌": dict(zip(PALACE_BRANCHES_FROM_YIN, ["陷", "利", "得", "庙", "陷", "利", "得", "庙", "陷", "利", "得", "庙"])),
    "文曲": dict(zip(PALACE_BRANCHES_FROM_YIN, ["平", "旺", "得", "庙", "陷", "旺", "得", "庙", "陷", "旺", "得", "庙"])),
    "火星": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "利", "陷", "得", "庙", "利", "陷", "得", "庙", "利", "陷", "得"])),
    "铃星": dict(zip(PALACE_BRANCHES_FROM_YIN, ["庙", "利", "陷", "得", "庙", "利", "陷", "得", "庙", "利", "陷", "得"])),
}

NAYIN_WUXING_MAP = {
    ("甲子", "乙丑"): "金",
    ("丙寅", "丁卯"): "火",
    ("戊辰", "己巳"): "木",
    ("庚午", "辛未"): "土",
    ("壬申", "癸酉"): "金",
    ("甲戌", "乙亥"): "火",
    ("丙子", "丁丑"): "水",
    ("戊寅", "己卯"): "土",
    ("庚辰", "辛巳"): "金",
    ("壬午", "癸未"): "木",
    ("甲申", "乙酉"): "水",
    ("丙戌", "丁亥"): "土",
    ("戊子", "己丑"): "火",
    ("庚寅", "辛卯"): "木",
    ("壬辰", "癸巳"): "水",
    ("甲午", "乙未"): "金",
    ("丙申", "丁酉"): "火",
    ("戊戌", "己亥"): "木",
    ("庚子", "辛丑"): "土",
    ("壬寅", "癸卯"): "金",
    ("甲辰", "乙巳"): "火",
    ("丙午", "丁未"): "水",
    ("戊申", "己酉"): "土",
    ("庚戌", "辛亥"): "金",
    ("壬子", "癸丑"): "木",
    ("甲寅", "乙卯"): "水",
    ("丙辰", "丁巳"): "土",
    ("戊午", "己未"): "火",
    ("庚申", "辛酉"): "木",
    ("壬戌", "癸亥"): "水",
}


@dataclass
class ZiweiInput:
    gender: str
    birth_date: str  # YYYY-MM-DD
    birth_time: str  # HH:MM
    longitude: float = BEIJING_LONGITUDE
    place: str = "北京"
    time_accuracy_minutes: int = 0
    boundary_threshold_minutes: int = 15
    time_is_true_solar: bool = False


@dataclass
class ZiweiResult:
    version: str
    anxing_code: str
    status: str
    message: str
    basic_info: Dict[str, Any]
    palaces: List[Dict[str, Any]]
    palace_map: Dict[str, Dict[str, Any]]
    transformations: Dict[str, Any]
    validation: Dict[str, Any]


REFERENCE_WENMO_CASES = [
    {
        "name": "wenmo_case_19850810_1620_male",
        "input": {"gender": "男", "birth_date": "1985-08-10", "birth_time": "16:20"},
        "expected_basic": {
            "year_ganzhi": "乙丑",
            "month_ganzhi": "甲申",
            "day_ganzhi": "辛巳",
            "time_ganzhi": "丙申",
            "命局": "阴男土五局",
            "命宫": "亥",
            "身宫": "卯",
            "身宫所属宫位": "官禄宫",
            "命宫干支": "丁亥",
            "局名": "土五局",
            "命主": "巨门",
            "身主": "天相",
            "子斗": "卯",
        },
        "expected_main_stars": {
            "命宫": ["天府"],
            "迁移宫": ["紫微", "七杀"],
            "官禄宫": ["天相"],
            "田宅宫": ["太阳", "巨门"],
            "福德宫": ["武曲", "贪狼"],
            "父母宫": ["天同", "太阴"],
        },
        "expected_transformations": {
            "禄": {"星曜": "天机", "宫支": "辰", "状态": "LOCATED"},
            "权": {"星曜": "天梁", "宫支": "辰", "状态": "LOCATED"},
            "科": {"星曜": "紫微", "宫支": "巳", "状态": "LOCATED"},
            "忌": {"星曜": "太阴", "宫支": "子", "状态": "LOCATED"},
        },
        "expected_boundary": {
            "status": "STABLE",
            "current_time_branch": "申",
            "candidate_branches": ["申"],
            "should_generate_double_chart": False,
            "near_boundary": False,
        },
    },
    {
        "name": "wenmo_case_19960120_1420_female",
        "input": {"gender": "女", "birth_date": "1996-01-20", "birth_time": "14:20"},
        "expected_basic": {
            "year_ganzhi": "乙亥",
            "month_ganzhi": "己丑",
            "day_ganzhi": "丙辰",
            "time_ganzhi": "乙未",
            "命局": "阴女木三局",
            "命宫": "午",
            "身宫": "申",
            "身宫所属宫位": "福德宫",
            "命宫干支": "壬午",
            "局名": "木三局",
            "命主": "破军",
            "身主": "天机",
            "子斗": "申",
        },
        "expected_main_stars": {
            "命宫": ["七杀"],
            "夫妻宫": ["紫微", "天相"],
            "财帛宫": ["贪狼"],
            "疾厄宫": ["太阳", "太阴"],
            "迁移宫": ["武曲", "天府"],
        },
        "expected_transformations": {
            "禄": {"星曜": "天机", "宫支": "卯", "状态": "LOCATED"},
            "权": {"星曜": "天梁", "宫支": "巳", "状态": "LOCATED"},
            "科": {"星曜": "紫微", "宫支": "辰", "状态": "LOCATED"},
            "忌": {"星曜": "太阴", "宫支": "丑", "状态": "LOCATED"},
        },
        "expected_boundary": {
            "status": "STABLE",
            "current_time_branch": "未",
            "candidate_branches": ["未"],
            "should_generate_double_chart": False,
            "near_boundary": False,
        },
    },
    {
        "name": "wenmo_case_19990702_0900_female",
        "input": {"gender": "女", "birth_date": "1999-07-02", "birth_time": "09:00"},
        "expected_basic": {
            "year_ganzhi": "己卯",
            "month_ganzhi": "庚午",
            "day_ganzhi": "乙卯",
            "time_ganzhi": "庚辰",
            "命局": "阴女火六局",
            "命宫": "寅",
            "身宫": "戌",
            "身宫所属宫位": "财帛宫",
            "命宫干支": "丙寅",
            "局名": "火六局",
            "命主": "禄存",
            "身主": "天同",
            "子斗": "子",
        },
        "expected_main_stars": {
            "命宫": ["破军"],
            "夫妻宫": ["紫微"],
            "福德宫": ["廉贞", "天府"],
            "疾厄宫": ["太阳", "天梁"],
            "财帛宫": ["七杀"],
            "子女宫": ["天机"],
        },
        "expected_transformations": {
            "禄": {"星曜": "武曲", "宫支": "申", "状态": "LOCATED"},
            "权": {"星曜": "贪狼", "宫支": "午", "状态": "LOCATED"},
            "科": {"星曜": "天梁", "宫支": "酉", "状态": "LOCATED"},
            "忌": {"星曜": "文曲", "宫支": "申", "状态": "LOCATED"},
        },
        "expected_boundary": {
            "status": "STABLE",
            "current_time_branch": "辰",
            "candidate_branches": ["辰"],
            "should_generate_double_chart": False,
            "near_boundary": False,
        },
    },
    {
        "name": "wenmo_case_19850810_1506_male",
        "input": {"gender": "男", "birth_date": "1985-08-10", "birth_time": "15:06"},
        "expected_basic": {
            "year_ganzhi": "乙丑", "month_ganzhi": "甲申", "day_ganzhi": "辛巳", "time_ganzhi": "丙申",
            "命局": "阴男土五局", "命宫": "亥", "身宫": "卯", "身宫所属宫位": "官禄宫",
            "命宫干支": "丁亥", "局名": "土五局", "命主": "巨门", "身主": "天相", "子斗": "卯",
        },
        "expected_main_stars": {
            "命宫": ["天府"], "迁移宫": ["紫微", "七杀"], "官禄宫": ["天相"],
            "田宅宫": ["太阳", "巨门"], "福德宫": ["武曲", "贪狼"], "父母宫": ["天同", "太阴"],
        },
        "expected_transformations": {
            "禄": {"星曜": "天机", "宫支": "辰", "状态": "LOCATED"},
            "权": {"星曜": "天梁", "宫支": "辰", "状态": "LOCATED"},
            "科": {"星曜": "紫微", "宫支": "巳", "状态": "LOCATED"},
            "忌": {"星曜": "太阴", "宫支": "子", "状态": "LOCATED"},
        },
        "expected_boundary": {
            "status": "NEAR_BOUNDARY", "current_time_branch": "未",
            "candidate_branches": ["未"], "should_generate_double_chart": False, "near_boundary": True,
        },
    },
    {
        "name": "wenmo_case_20190124_1112_male_peter",
        "input": {"gender": "男", "birth_date": "2019-01-24", "birth_time": "11:12"},
        "expected_basic": {
            "year_ganzhi": "戊戌", "month_ganzhi": "乙丑", "day_ganzhi": "辛酉", "time_ganzhi": "甲午",
            "命局": "阳男火六局", "命宫": "未", "身宫": "未", "身宫所属宫位": "命宫",
            "命宫干支": "己未", "局名": "火六局", "命主": "武曲", "身主": "文昌", "子斗": "未",
        },
        "expected_main_stars": {
            "命宫": ["天同", "巨门"], "兄弟宫": ["贪狼"], "夫妻宫": ["太阴"],
            "子女宫": ["廉贞", "天府"], "财帛宫": [], "疾厄宫": ["破军"],
            "迁移宫": [], "官禄宫": ["天机"], "福德宫": ["太阳", "天梁"],
            "田宅宫": ["七杀"], "父母宫": ["武曲", "天相"],
        },
        "expected_transformations": {
            "禄": {"星曜": "贪狼", "宫支": "午", "状态": "LOCATED"},
            "权": {"星曜": "太阴", "宫支": "巳", "状态": "LOCATED"},
            "科": {"星曜": "天机", "宫支": "亥", "状态": "LOCATED"},
            "忌": {"星曜": "天机", "宫支": "亥", "状态": "LOCATED"},
        },
        "expected_boundary": {
            "status": "STABLE", "current_time_branch": "午",
            "candidate_branches": ["午"], "should_generate_double_chart": False, "near_boundary": False,
        },
    },
]
REFERENCE_MATCH_KEYS = ("gender", "birth_date", "birth_time")
CORE_DIFFERENCE_FIELDS = ("命宫", "身宫", "命主", "子斗", "命宫干支")


def _equation_of_time_minutes(dt: datetime) -> int:
    """近似计算时差方程（分钟），用于贴近文墨真太阳时口径。"""
    day_of_year = dt.timetuple().tm_yday
    b = math.radians((360 / 365) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return round(eot)


def _true_solar_delta(input_dt: datetime, longitude: float, already_true_solar: bool = False) -> Dict[str, int]:
    if already_true_solar:
        return {"longitude_delta_minutes": 0, "equation_of_time_minutes": 0, "delta_minutes": 0}
    longitude_delta = round((longitude - 120.0) * EARTH_ROTATION_MIN_PER_DEGREE)
    eot_delta = _equation_of_time_minutes(input_dt)
    return {
        "longitude_delta_minutes": longitude_delta,
        "equation_of_time_minutes": eot_delta,
        "delta_minutes": longitude_delta + eot_delta,
    }


def _hour_to_branch(hour: int, minute: int = 0) -> str:
    hm = hour + minute / 60
    if hm >= 23 or hm < 1:
        return "子"
    if hm < 3:
        return "丑"
    if hm < 5:
        return "寅"
    if hm < 7:
        return "卯"
    if hm < 9:
        return "辰"
    if hm < 11:
        return "巳"
    if hm < 13:
        return "午"
    if hm < 15:
        return "未"
    if hm < 17:
        return "申"
    if hm < 19:
        return "酉"
    if hm < 21:
        return "戌"
    return "亥"


def _branch_index(branch: str) -> int:
    return HOUR_BRANCHES.index(branch)


def _nayin_wuxing(ganzhi: str) -> str:
    for ganzhi_set, wuxing in NAYIN_WUXING_MAP.items():
        if ganzhi in ganzhi_set:
            return wuxing
    return ""


def _year_yinyang(year_gan: str) -> str:
    return "阳" if year_gan in {"甲", "丙", "戊", "庚", "壬"} else "阴"


def _yin_start_stem_index(year_gan: str) -> int:
    stem_num = HEAVENLY_STEMS.index(year_gan) + 1
    return (stem_num * 2) % 10


def _step_to_yin_index(step: int) -> int:
    if step == 0:
        return 0
    if step > 0:
        return (step - 1) % 12
    return (-(abs(step) - 1)) % 12


def _normalize_count_1_to_12(step: int) -> int:
    """将任意步数折算为以寅宫为 1 的 1..12 计数。"""
    return ((step - 1) % 12) + 1


def _count_from_yin_clockwise(step: int) -> str:
    normalized = _normalize_count_1_to_12(step)
    return PALACE_BRANCHES_FROM_YIN[normalized - 1]


def _count_from_yin_counterclockwise(step: int) -> str:
    normalized = _normalize_count_1_to_12(step)
    return PALACE_BRANCHES_FROM_YIN[(1 - normalized) % 12]


def _rotate_branch(branch: str, offset: int) -> str:
    idx = PALACE_BRANCHES_FROM_YIN.index(branch)
    return PALACE_BRANCHES_FROM_YIN[(idx + offset) % 12]


def _add_star(
    target: Dict[str, List[str]],
    star_positions: Dict[str, str],
    star_name: str,
    branch: str,
):
    star_positions[star_name] = branch
    target.setdefault(branch, []).append(star_name)


def _calc_brightness(stars: List[str], branch: str) -> Dict[str, str]:
    result = {}
    for star in stars:
        result[star] = STAR_BRIGHTNESS_BY_BRANCH.get(star, {}).get(branch, "未定义")
    return result


def _branch_window(true_dt: datetime) -> Tuple[datetime, datetime]:
    branch = _hour_to_branch(true_dt.hour, true_dt.minute)
    if branch == "子":
        if true_dt.hour >= 23:
            start_dt = true_dt.replace(hour=23, minute=0, second=0, microsecond=0)
            end_dt = start_dt + timedelta(hours=2)
        else:
            end_dt = true_dt.replace(hour=1, minute=0, second=0, microsecond=0)
            start_dt = end_dt - timedelta(hours=2)
        return start_dt, end_dt

    branch_index = HOUR_BRANCHES.index(branch)
    start_hour = branch_index * 2 - 1
    start_dt = true_dt.replace(hour=start_hour, minute=0, second=0, microsecond=0)
    end_dt = start_dt + timedelta(hours=2)
    return start_dt, end_dt


def _iter_true_minutes(start_dt: datetime, end_dt: datetime) -> List[datetime]:
    current = start_dt
    points = []
    while current <= end_dt:
        points.append(current)
        current += timedelta(minutes=1)
    return points


def _reference_input_signature(payload: Dict[str, Any]) -> Tuple[Any, ...]:
    return tuple(payload.get(key) for key in REFERENCE_MATCH_KEYS)


def _find_reference_case(data: ZiweiInput) -> Dict[str, Any]:
    signature = _reference_input_signature(asdict(data))
    for case in REFERENCE_WENMO_CASES:
        if _reference_input_signature(case["input"]) == signature:
            return case
    return {}


def _build_field_mismatches(expected: Dict[str, Any], actual: Dict[str, Any], label: str) -> List[Dict[str, Any]]:
    mismatches = []
    for key, expected_value in expected.items():
        actual_value = actual.get(key)
        if actual_value != expected_value:
            mismatches.append({label: key, "expected": expected_value, "actual": actual_value})
    return mismatches


def _build_transformation_mismatches(expected: Dict[str, Any], actual: Dict[str, Any]) -> List[Dict[str, Any]]:
    mismatches = []
    for hua_name, expected_detail in expected.items():
        actual_detail = actual.get(hua_name)
        if actual_detail is None:
            mismatches.append({"四化": hua_name, "expected": expected_detail, "actual": None})
            continue
        field_mismatches = _build_field_mismatches(expected_detail, actual_detail, "field")
        if field_mismatches:
            mismatches.append({"四化": hua_name, "diffs": field_mismatches})
    return mismatches


def _extract_passed_keys(expected: Dict[str, Any], mismatches: List[Dict[str, Any]], mismatch_key: str) -> List[str]:
    failed = {item[mismatch_key] for item in mismatches}
    return [key for key in expected if key not in failed]


def _extract_passed_transformations(expected: Dict[str, Any], mismatches: List[Dict[str, Any]]) -> List[str]:
    failed = {item["四化"] for item in mismatches}
    return [key for key in expected if key not in failed]


def _build_reference_case_comparison(case: Dict[str, Any], result: ZiweiResult) -> Dict[str, Any]:
    basic = result.basic_info
    palace_map = {palace["宫位"]: palace for palace in result.palaces}
    transformations = result.transformations.get("四化", {})
    boundary_analysis = result.validation.get("时辰边界", {})

    basic_mismatches = _build_field_mismatches(case.get("expected_basic", {}), basic, "field")

    expected_main_stars = case.get("expected_main_stars", {})
    star_mismatches = []
    for palace_name, expected_stars in expected_main_stars.items():
        actual_stars = palace_map.get(palace_name, {}).get("主星", [])
        if actual_stars != expected_stars:
            star_mismatches.append({"palace": palace_name, "expected": expected_stars, "actual": actual_stars})

    transformation_mismatches = _build_transformation_mismatches(case.get("expected_transformations", {}), transformations)
    boundary_mismatches = _build_field_mismatches(case.get("expected_boundary", {}), boundary_analysis, "field")

    mismatch_count = (
        len(basic_mismatches)
        + len(star_mismatches)
        + len(transformation_mismatches)
        + len(boundary_mismatches)
    )
    blocking_items = []
    if basic_mismatches:
        blocking_items.append("basic_fields")
    if star_mismatches:
        blocking_items.append("main_stars")
    if transformation_mismatches:
        blocking_items.append("transformations")
    if boundary_mismatches:
        blocking_items.append("boundary")

    return {
        "name": case["name"],
        "status": "PASS" if mismatch_count == 0 else "FAIL",
        "summary": "All reference assertions passed." if mismatch_count == 0 else f"{mismatch_count} mismatches detected.",
        "mismatch_count": mismatch_count,
        "blocking_items": blocking_items,
        "basic_mismatches": basic_mismatches,
        "star_mismatches": star_mismatches,
        "transformation_mismatches": transformation_mismatches,
        "boundary_mismatches": boundary_mismatches,
        "passed_assertions": {
            "basic_fields": _extract_passed_keys(case.get("expected_basic", {}), basic_mismatches, "field"),
            "main_star_palaces": _extract_passed_keys(expected_main_stars, star_mismatches, "palace"),
            "transformations": _extract_passed_transformations(case.get("expected_transformations", {}), transformation_mismatches),
            "boundary_fields": _extract_passed_keys(case.get("expected_boundary", {}), boundary_mismatches, "field"),
        },
    }


def _build_reference_match_info(data: ZiweiInput, result: ZiweiResult) -> Dict[str, Any]:
    case = _find_reference_case(data)
    if not case:
        return {
            "matched": False,
            "case_name": None,
            "status": "NO_REFERENCE",
            "validated_fields": {},
            "summary": "仅通用规则计算，未命中文墨样本。",
        }

    comparison = _build_reference_case_comparison(case, result)
    return {
        "matched": True,
        "case_name": case["name"],
        "status": comparison["status"],
        "validated_fields": comparison["passed_assertions"],
        "summary": (
            "命中文墨参考盘，关键字段已通过校验。"
            if comparison["status"] == "PASS"
            else "命中文墨参考盘，但仍存在待修正差异。"
        ),
        "comparison": comparison,
    }


def _build_boundary_validation_summary(boundary_analysis: Dict[str, Any], comparison_charts: List[Dict[str, Any]]) -> Dict[str, Any]:
    candidates = []
    field_values = {field: {} for field in CORE_DIFFERENCE_FIELDS}
    for chart in comparison_charts:
        candidate = {
            "time_branch": chart["time_branch"],
            "representative_clock_time": chart["representative_clock_time"],
            "representative_true_solar_time": chart["representative_true_solar_time"],
            "core_fields": {},
        }
        for field in CORE_DIFFERENCE_FIELDS:
            value = chart["basic_info"].get(field)
            candidate["core_fields"][field] = value
            field_values[field][chart["time_branch"]] = value
        candidates.append(candidate)

    differing_fields = [
        field
        for field, branch_map in field_values.items()
        if len({value for value in branch_map.values()}) > 1
    ]
    return {
        "near_boundary": boundary_analysis["near_boundary"],
        "crosses_time_branch": boundary_analysis["should_generate_double_chart"],
        "candidate_branches": boundary_analysis["candidate_branches"],
        "candidate_core_fields": candidates,
        "differing_fields": differing_fields,
    }


def analyze_time_boundary(data: ZiweiInput) -> Dict[str, Any]:
    """分析输入时间是否贴近时辰边界，以及在给定误差范围内是否跨时辰。"""
    input_dt = datetime.strptime(f"{data.birth_date} {data.birth_time}", "%Y-%m-%d %H:%M")
    correction = _true_solar_delta(input_dt, data.longitude, data.time_is_true_solar)
    delta_minutes = correction["delta_minutes"]
    true_dt = input_dt + timedelta(minutes=delta_minutes)
    start_dt, end_dt = _branch_window(true_dt)
    minutes_from_start = int((true_dt - start_dt).total_seconds() // 60)
    minutes_to_end = int((end_dt - true_dt).total_seconds() // 60)
    nearest_boundary_minutes = min(minutes_from_start, minutes_to_end)

    uncertainty = max(0, int(data.time_accuracy_minutes))
    lower_clock_dt = input_dt - timedelta(minutes=uncertainty)
    upper_clock_dt = input_dt + timedelta(minutes=uncertainty)
    lower_true_dt = lower_clock_dt + timedelta(minutes=delta_minutes)
    upper_true_dt = upper_clock_dt + timedelta(minutes=delta_minutes)

    branch_segments: Dict[str, Dict[str, datetime]] = {}
    for probe_dt in _iter_true_minutes(lower_true_dt, upper_true_dt):
        branch = _hour_to_branch(probe_dt.hour, probe_dt.minute)
        if branch not in branch_segments:
            branch_segments[branch] = {"start_true": probe_dt, "end_true": probe_dt}
        else:
            branch_segments[branch]["end_true"] = probe_dt

    candidate_branches = list(branch_segments.keys())
    near_boundary = nearest_boundary_minutes <= max(0, int(data.boundary_threshold_minutes))
    should_generate_double_chart = len(candidate_branches) > 1

    if should_generate_double_chart:
        status = "BOUNDARY_SENSITIVE"
    elif near_boundary:
        status = "NEAR_BOUNDARY"
    else:
        status = "STABLE"

    representative_times = []
    for branch, segment in branch_segments.items():
        midpoint_true = segment["start_true"] + (segment["end_true"] - segment["start_true"]) / 2
        representative_clock = midpoint_true - timedelta(minutes=delta_minutes)
        representative_times.append(
            {
                "time_branch": branch,
                "representative_clock_time": representative_clock.strftime("%Y-%m-%d %H:%M"),
                "representative_true_solar_time": midpoint_true.strftime("%Y-%m-%d %H:%M"),
            }
        )

    return {
        "status": status,
        "clock_time": input_dt.strftime("%Y-%m-%d %H:%M"),
        "true_solar_time": true_dt.strftime("%Y-%m-%d %H:%M"),
        "input_is_true_solar": data.time_is_true_solar,
        "longitude_delta_minutes": correction["longitude_delta_minutes"],
        "equation_of_time_minutes": correction["equation_of_time_minutes"],
        "delta_minutes": delta_minutes,
        "current_time_branch": _hour_to_branch(true_dt.hour, true_dt.minute),
        "time_accuracy_minutes": uncertainty,
        "boundary_threshold_minutes": int(data.boundary_threshold_minutes),
        "minutes_from_branch_start": minutes_from_start,
        "minutes_to_branch_end": minutes_to_end,
        "nearest_boundary_minutes": nearest_boundary_minutes,
        "near_boundary": near_boundary,
        "candidate_branches": candidate_branches,
        "should_generate_double_chart": should_generate_double_chart,
        "window_clock_time": {
            "start": lower_clock_dt.strftime("%Y-%m-%d %H:%M"),
            "end": upper_clock_dt.strftime("%Y-%m-%d %H:%M"),
        },
        "window_true_solar_time": {
            "start": lower_true_dt.strftime("%Y-%m-%d %H:%M"),
            "end": upper_true_dt.strftime("%Y-%m-%d %H:%M"),
        },
        "representative_times": representative_times,
        "message": (
            "输入时间误差范围已跨时辰，建议双盘并看。"
            if should_generate_double_chart
            else "输入时间贴近时辰边界，建议结合生平信息复核。"
            if near_boundary
            else "输入时间离时辰边界较远。"
        ),
    }


def apply_true_solar_time(
    birth_date: str,
    birth_time: str,
    longitude: float = BEIJING_LONGITUDE,
    already_true_solar: bool = False,
) -> Dict[str, Any]:
    """按经度 + 时差方程进行真太阳时近似校正（以东八区 120E 为基准）。"""
    dt = datetime.strptime(f"{birth_date} {birth_time}", "%Y-%m-%d %H:%M")
    correction = _true_solar_delta(dt, longitude, already_true_solar)
    delta_minutes = correction["delta_minutes"]
    true_dt = dt + timedelta(minutes=delta_minutes)
    return {
        "input_date": birth_date,
        "input_time": birth_time,
        "longitude": longitude,
        "input_is_true_solar": already_true_solar,
        "longitude_delta_minutes": correction["longitude_delta_minutes"],
        "equation_of_time_minutes": correction["equation_of_time_minutes"],
        "delta_minutes": delta_minutes,
        "true_solar_datetime": true_dt,
        "true_solar_time": true_dt.strftime("%Y-%m-%d %H:%M"),
        "time_branch": _hour_to_branch(true_dt.hour, true_dt.minute),
        "status": "OK",
    }


def calc_ming_shen_gong(lunar_month: int, hour_branch_index: int) -> Dict[str, Any]:
    """命宫：寅起正月顺数到月，再逆数到时；身宫同起点顺数到时。"""
    start_idx = (lunar_month - 1) % 12
    ming_idx = (start_idx - hour_branch_index) % 12
    shen_idx = (start_idx + hour_branch_index) % 12
    return {
        "命宫": PALACE_BRANCHES_FROM_YIN[ming_idx],
        "身宫": PALACE_BRANCHES_FROM_YIN[shen_idx],
        "status": "OK",
    }


def calc_doujun(lunar_month: int, hour_branch_index: int) -> Dict[str, Any]:
    """子斗：从子宫逆数生月，再顺数生时。"""
    zi_idx = EARTHLY_BRANCHES.index("子")
    dou_idx = (zi_idx - (lunar_month - 1) + hour_branch_index) % 12
    return {
        "子斗": EARTHLY_BRANCHES[dou_idx],
        "status": "OK",
        "rule": "子宫逆月顺时",
    }


def build_palace_ganzhi_map(year_gan: str) -> Dict[str, str]:
    """五虎遁起寅首：以出生农历年干推寅宫宫干，顺布十二宫干。"""
    yin_stem_index = _yin_start_stem_index(year_gan)
    palace_ganzhi = {}
    for offset, branch in enumerate(PALACE_BRANCHES_FROM_YIN):
        stem = HEAVENLY_STEMS[(yin_stem_index + offset) % 10]
        palace_ganzhi[branch] = f"{stem}{branch}"
    return palace_ganzhi


def calc_wuxing_ju(ming_gong_ganzhi: str) -> Dict[str, Any]:
    """按命宫干支纳音五行定局。"""
    wuxing = _nayin_wuxing(ming_gong_ganzhi)
    ju_num = {"水": 2, "木": 3, "金": 4, "土": 5, "火": 6}.get(wuxing)
    return {
        "命宫干支": ming_gong_ganzhi,
        "五行局": wuxing,
        "局数": ju_num,
        "局名": WUXING_JU_LABELS.get(wuxing),
        "status": "OK" if wuxing and ju_num else "TODO",
    }


def calc_ziwei_tianfu_positions(lunar_day: int, ju_num: int) -> Dict[str, Any]:
    """
    依公开三合派公式定紫微、天府所在宫。

    规则依据（公开通用公式，未宣称已与文墨天机专有码逐条校验）：
    1. 找到可覆盖生日数的最小局数倍数
    2. 用差数奇偶决定寅宫起顺/逆步数
    3. 同步得到紫微、天府起点
    """
    if not ju_num or lunar_day <= 0:
        return {"status": "TODO", "紫微": None, "天府": None}

    quotient = lunar_day // ju_num
    remainder = lunar_day % ju_num
    multiplier = quotient + (1 if remainder > 0 else 0)
    difference = multiplier * ju_num - lunar_day
    step = ((-1) ** difference) * difference + multiplier
    normalized_step = _normalize_count_1_to_12(step)
    return {
        "status": "OK",
        "公式来源": "公开三合派公式",
        "商": quotient,
        "余": remainder,
        "差": difference,
        "步数": step,
        "折算步数": normalized_step,
        "紫微": _count_from_yin_clockwise(step),
        "天府": _count_from_yin_counterclockwise(step),
    }


def place_main_stars(context: Dict[str, Any]) -> Dict[str, Any]:
    """按紫微/天府两组固定偏移安十四主星。"""
    lunar_day = context["lunar_day"]
    ju_num = context["wuxing_ju"]["局数"]
    positioning = calc_ziwei_tianfu_positions(lunar_day, ju_num)
    if positioning["status"] != "OK":
        return {"status": "TODO", "主星": [], "星位": {}, "定位": positioning}

    star_to_branch: Dict[str, str] = {}
    branch_to_stars: Dict[str, List[str]] = {branch: [] for branch in PALACE_BRANCHES_FROM_YIN}

    ziwei_branch = positioning["紫微"]
    for star, offset in ZIWEI_GROUP_OFFSETS:
        branch = _rotate_branch(ziwei_branch, offset)
        star_to_branch[star] = branch
        branch_to_stars[branch].append(star)

    tianfu_branch = positioning["天府"]
    for star, offset in TIANFU_GROUP_OFFSETS:
        branch = _rotate_branch(tianfu_branch, offset)
        star_to_branch[star] = branch
        branch_to_stars[branch].append(star)

    return {
        "status": "PARTIAL_VERIFIED",
        "说明": "主星安星按公开三合派公式实现，尚未逐例校验到文墨天机 C5FYC。",
        "定位": positioning,
        "星位": star_to_branch,
        "主星": branch_to_stars,
    }


def place_assist_stars(context: Dict[str, Any]) -> Dict[str, Any]:
    """
    第一、二批辅星/煞曜安星。

    规则依据：公开常用三合派安星诀，当前作为文墨对齐的可试用实现，后续继续用样本盘校准。
    """
    lunar_month = context["lunar_month"]
    lunar_day = context["lunar_day"]
    hour_branch_index = context["hour_branch_index"]
    year_gan = context["year_gan"]
    year_branch = context["year_branch"]
    day_xunkong = context["day_xunkong"]

    assist_branch_map: Dict[str, List[str]] = {branch: [] for branch in PALACE_BRANCHES_FROM_YIN}
    shensha_branch_map: Dict[str, List[str]] = {branch: [] for branch in PALACE_BRANCHES_FROM_YIN}
    star_positions: Dict[str, str] = {}

    # 左辅右弼：月系星
    _add_star(assist_branch_map, star_positions, "左辅", _rotate_branch("辰", lunar_month - 1))
    _add_star(assist_branch_map, star_positions, "右弼", _rotate_branch("戌", -(lunar_month - 1)))

    # 文昌文曲：时系星
    _add_star(assist_branch_map, star_positions, "文昌", _rotate_branch("戌", -hour_branch_index))
    _add_star(assist_branch_map, star_positions, "文曲", _rotate_branch("辰", hour_branch_index))

    # 天魁天钺：年干系星
    tiankui_branch, tianyue_branch = TIANKUI_TIANYUE_BY_YEAR_STEM[year_gan]
    _add_star(assist_branch_map, star_positions, "天魁", tiankui_branch)
    _add_star(assist_branch_map, star_positions, "天钺", tianyue_branch)

    # 禄存 / 羊陀：年干系星
    lucun_branch = LUCUN_BY_YEAR_STEM[year_gan]
    _add_star(assist_branch_map, star_positions, "禄存", lucun_branch)
    _add_star(shensha_branch_map, star_positions, "擎羊", _rotate_branch(lucun_branch, 1))
    _add_star(shensha_branch_map, star_positions, "陀罗", _rotate_branch(lucun_branch, -1))

    # 天马：年支系星
    _add_star(assist_branch_map, star_positions, "天马", TIANMA_BY_YEAR_BRANCH[year_branch])

    # 天空：生年支顺数的前一位
    _add_star(shensha_branch_map, star_positions, "天空", _rotate_branch(year_branch, -1))

    # 火铃：先按年支定子时起点，再顺数至生时
    huoxing_start, lingxing_start = HUOLING_STARTS_BY_YEAR_BRANCH[year_branch]
    _add_star(assist_branch_map, star_positions, "火星", _rotate_branch(huoxing_start, hour_branch_index))
    _add_star(assist_branch_map, star_positions, "铃星", _rotate_branch(lingxing_start, hour_branch_index))

    # 地空地劫：亥宫起子时
    _add_star(assist_branch_map, star_positions, "地劫", _rotate_branch("亥", hour_branch_index))
    _add_star(assist_branch_map, star_positions, "地空", _rotate_branch("亥", -hour_branch_index))

    # 红鸾天喜：卯宫起子逆数，天喜对宫
    hongluan_branch = _rotate_branch("卯", -_branch_index(year_branch))
    _add_star(assist_branch_map, star_positions, "红鸾", hongluan_branch)
    _add_star(assist_branch_map, star_positions, "天喜", _rotate_branch(hongluan_branch, 6))

    # 三台八座：由左右起初一
    left_fu_branch = star_positions["左辅"]
    right_bi_branch = star_positions["右弼"]
    _add_star(assist_branch_map, star_positions, "三台", _rotate_branch(left_fu_branch, lunar_day - 1))
    _add_star(assist_branch_map, star_positions, "八座", _rotate_branch(right_bi_branch, -(lunar_day - 1)))

    # 恩光天贵：由昌曲起初一，顺行至生日再退一步
    wenchang_branch = star_positions["文昌"]
    wenqu_branch = star_positions["文曲"]
    _add_star(assist_branch_map, star_positions, "恩光", _rotate_branch(wenchang_branch, lunar_day - 2))
    _add_star(assist_branch_map, star_positions, "天贵", _rotate_branch(wenqu_branch, lunar_day - 2))

    # 将星华盖：年支组
    _add_star(shensha_branch_map, star_positions, "将星", JIANGXING_BY_YEAR_BRANCH[year_branch])
    _add_star(shensha_branch_map, star_positions, "华盖", HUAGAI_BY_YEAR_BRANCH[year_branch])

    # 截空：年干组双宫
    for branch in JIEKONG_BY_YEAR_STEM[year_gan]:
        _add_star(shensha_branch_map, star_positions, "截空", branch)

    # 旬空：按日旬空双宫
    for branch in [item for item in day_xunkong if item in EARTHLY_BRANCHES]:
        _add_star(shensha_branch_map, star_positions, "旬空", branch)

    return {
        "status": "PARTIAL_VERIFIED",
        "辅星": assist_branch_map,
        "神煞": shensha_branch_map,
        "星位": star_positions,
        "已实现": [
            "左辅", "右弼", "文昌", "文曲", "天魁", "天钺", "禄存", "擎羊", "陀罗", "天马", "天空",
            "火星", "铃星", "地空", "地劫", "红鸾", "天喜", "三台", "八座", "恩光", "天贵", "将星", "华盖", "截空", "旬空",
        ],
        "说明": "第一、二批辅星/煞曜按公开三合派安星诀实现，待继续用文墨天机样本盘校准。",
    }


def apply_si_hua(year_gan: str, star_positions: Dict[str, str]) -> Dict[str, Any]:
    """文墨天机默认四化表。"""
    table = SI_HUA_TABLE.get(year_gan, {})
    detailed = {}
    for hua, star in table.items():
        detailed[hua] = {
            "星曜": star,
            "宫支": star_positions.get(star),
            "状态": "LOCATED" if star_positions.get(star) else "STAR_NOT_PLACED_YET",
        }
    return {
        "天干": year_gan,
        "四化": detailed,
        "status": "OK" if table else "TODO",
    }


def calc_ming_shen_zhu(ming_branch: str, year_branch: str) -> Dict[str, Any]:
    return {
        "命主": MING_ZHU_TABLE.get(ming_branch),
        "身主": SHEN_ZHU_TABLE.get(year_branch),
        "status": "PARTIAL_VERIFIED",
        "说明": "命主/身主按公开通用对照表实现，待继续用文墨天机命例校准。",
    }


def build_palace_roles(ming_branch: str) -> Dict[str, str]:
    """命宫起命，逆时针布十二宫。"""
    ming_idx = PALACE_BRANCHES_FROM_YIN.index(ming_branch)
    branch_to_role = {}
    for offset, role in enumerate(PALACE_NAME_SEQUENCE):
        branch = PALACE_BRANCHES_FROM_YIN[(ming_idx - offset) % 12]
        branch_to_role[branch] = role
    return branch_to_role


def build_palaces(
    ming_shen: Dict[str, Any],
    palace_ganzhi_map: Dict[str, str],
    main_star_info: Dict[str, Any],
    assist_star_info: Dict[str, Any],
    sihua_info: Dict[str, Any],
) -> List[Dict[str, Any]]:
    palace_roles = build_palace_roles(ming_shen["命宫"])
    palaces = []

    for branch in PALACE_OUTPUT_ORDER:
        role = palace_roles[branch]
        stars = main_star_info["主星"].get(branch, [])
        assist = assist_star_info["辅星"].get(branch, []) if assist_star_info["status"] != "TODO" else []
        shensha = assist_star_info["神煞"].get(branch, []) if assist_star_info["status"] != "TODO" else []
        sihua_list = []
        for hua_name, detail in sihua_info["四化"].items():
            if detail["宫支"] == branch:
                sihua_list.append({"化": hua_name, "星曜": detail["星曜"]})

        palaces.append(
            {
                "宫支": branch,
                "宫位": role,
                "宫干": palace_ganzhi_map[branch][0],
                "宫位干支": palace_ganzhi_map[branch],
                "主星": stars,
                "辅星": assist,
                "神煞": shensha,
                "星曜亮度": {
                    "主星": _calc_brightness(stars, branch),
                    "辅星": _calc_brightness(assist, branch),
                },
                "四化": sihua_list,
                "身宫": branch == ming_shen["身宫"],
            }
        )

    return palaces


def validate_against_wenmo(context: Dict[str, Any]) -> Dict[str, Any]:
    shen_role = build_palace_roles(context["ming_shen"]["命宫"])[context["ming_shen"]["身宫"]]
    main_star_info = context["main_star_info"]
    assist_star_info = context["assist_star_info"]
    sihua = context["sihua"]
    wuxing_ju = context["wuxing_ju"]
    ming_shen_zhu = context["ming_shen_zhu"]
    legacy_validation = {
        "真太阳时": "OK",
        "时辰地支": "OK",
        "命宫": "OK",
        "身宫": "OK" if shen_role in SHEN_GONG_ALLOWED else "CHECK_REQUIRED",
        "命宫干支": "OK" if context["ming_gong_ganzhi"] else "TODO",
        "五行局": "OK" if wuxing_ju["status"] == "OK" else "TODO",
        "主星安星": main_star_info["status"],
        "四化": "OK" if sihua["status"] == "OK" else "TODO",
        "命主": ming_shen_zhu["status"],
        "身主": ming_shen_zhu["status"],
        "子斗": context["doujun"]["status"],
        "辅星神煞": assist_star_info["status"],
        "亮度": "PARTIAL_VERIFIED",
        "文墨C5FYC逐盘校验": "UNVERIFIED",
        "风险提示": [
            "主星安星按公开三合派公式实现，尚未逐条验证文墨天机基础版 C5FYC。",
            "前两批辅星/煞曜已实现，但仍需更多文墨样本盘校准。",
            "亮度框架已接入，但目前只覆盖十四主星及部分辅曜，仍需继续补齐与校准。",
            "更多神煞体系仍未实现。",
        ],
    }
    legacy_validation["time_calendar"] = {
        "status": "OK",
        "details": {
            "真太阳时": legacy_validation["真太阳时"],
            "时辰地支": legacy_validation["时辰地支"],
        },
        "risks": [],
    }
    legacy_validation["core_fields"] = {
        "status": "PARTIAL_VERIFIED" if ming_shen_zhu["status"] != "OK" else "OK",
        "details": {
            "命宫": legacy_validation["命宫"],
            "身宫": legacy_validation["身宫"],
            "命宫干支": legacy_validation["命宫干支"],
            "五行局": legacy_validation["五行局"],
            "命主": legacy_validation["命主"],
            "身主": legacy_validation["身主"],
            "子斗": legacy_validation["子斗"],
        },
        "risks": [
            "命主、身主、子斗目前仍以公开规则和样本回归校准，未覆盖大样本文墨验盘。"
        ],
    }
    legacy_validation["main_stars"] = {
        "status": main_star_info["status"],
        "details": {
            "主星安星": legacy_validation["主星安星"],
            "定位": main_star_info.get("定位"),
        },
        "risks": [main_star_info.get("说明")] if main_star_info.get("说明") else [],
    }
    legacy_validation["transformations"] = {
        "status": legacy_validation["四化"],
        "details": sihua,
        "risks": ["四化已纳入主星与前两批辅星定位；尚未实现的星曜仍可能显示 STAR_NOT_PLACED_YET。"] if sihua["status"] == "OK" else [],
    }
    legacy_validation["boundary"] = {
        "status": "PENDING_RUNTIME_ANALYSIS",
        "details": {},
        "risks": ["需在 generate_ziwei_chart() 运行时附加边界分析。"],
    }
    legacy_validation["assist_stars"] = {
        "status": assist_star_info["status"],
        "details": assist_star_info,
        "risks": [assist_star_info.get("说明")] if assist_star_info.get("说明") else [],
    }
    legacy_validation["brightness"] = {
        "status": "PARTIAL_VERIFIED",
        "details": {
            "source": "公开中州派/三合派常用星曜亮度表",
            "implemented_stars": sorted(STAR_BRIGHTNESS_BY_BRANCH.keys()),
        },
        "risks": [
            "当前已覆盖十四主星及部分辅曜亮度；未覆盖星曜将显示“未定义”。",
            "亮度表尚未逐例校验到文墨天机基础版 C5FYC。",
        ],
    }
    return legacy_validation


def _generate_ziwei_chart_core(data: ZiweiInput) -> ZiweiResult:
    """生成文墨天机对齐版紫微结果（当前为可试盘版）。"""
    from lunar_python import Solar

    true_solar = apply_true_solar_time(
        data.birth_date,
        data.birth_time,
        data.longitude,
        data.time_is_true_solar,
    )
    true_dt = true_solar["true_solar_datetime"]
    solar = Solar(true_dt.year, true_dt.month, true_dt.day, true_dt.hour, true_dt.minute, 0)
    lunar = solar.getLunar()

    raw_month = lunar.getMonth()
    lunar_month = abs(raw_month)
    lunar_day = lunar.getDay()
    # 闰月按文墨天机/紫微斗数全书规则：初一-十五归本月，十六-末归下月
    if raw_month < 0 and lunar_day > 15:
        lunar_month = lunar_month + 1 if lunar_month < 12 else 1
    year_ganzhi = lunar.getYearInGanZhi()
    month_ganzhi = lunar.getMonthInGanZhiExact()
    day_ganzhi = lunar.getDayInGanZhiExact2()
    day_xunkong = lunar.getDayXunKongExact2() if hasattr(lunar, "getDayXunKongExact2") else lunar.getDayXunKongExact()
    time_ganzhi = lunar.getTimeInGanZhi()
    year_gan = lunar.getYearGan()
    year_branch = lunar.getYearZhi()
    hour_branch = true_solar["time_branch"]
    hour_branch_index = _branch_index(hour_branch)

    ming_shen = calc_ming_shen_gong(lunar_month, hour_branch_index)
    doujun = calc_doujun(lunar_month, hour_branch_index)
    palace_ganzhi_map = build_palace_ganzhi_map(year_gan)
    ming_gong_ganzhi = palace_ganzhi_map[ming_shen["命宫"]]
    wuxing_ju = calc_wuxing_ju(ming_gong_ganzhi)
    main_star_info = place_main_stars(
        {
            "lunar_day": lunar_day,
            "wuxing_ju": wuxing_ju,
        }
    )
    assist_star_info = place_assist_stars(
        {
            "lunar_month": lunar_month,
            "lunar_day": lunar_day,
            "hour_branch_index": hour_branch_index,
            "year_gan": year_gan,
            "year_branch": year_branch,
            "day_xunkong": day_xunkong,
        }
    )
    ming_shen_zhu = calc_ming_shen_zhu(ming_shen["命宫"], year_branch)
    all_star_positions = {}
    all_star_positions.update(main_star_info.get("星位", {}))
    all_star_positions.update(assist_star_info.get("星位", {}))
    sihua = apply_si_hua(year_gan, all_star_positions)
    palaces = build_palaces(ming_shen, palace_ganzhi_map, main_star_info, assist_star_info, sihua)
    palace_map = {palace["宫位"]: palace for palace in palaces}

    shen_role = build_palace_roles(ming_shen["命宫"])[ming_shen["身宫"]]
    validation = validate_against_wenmo(
        {
            "ming_shen": ming_shen,
            "doujun": doujun,
            "ming_gong_ganzhi": ming_gong_ganzhi,
            "wuxing_ju": wuxing_ju,
            "main_star_info": main_star_info,
            "assist_star_info": assist_star_info,
            "ming_shen_zhu": ming_shen_zhu,
            "sihua": sihua,
        }
    )

    basic_info = {
        "gender": data.gender,
        "birth_date": data.birth_date,
        "birth_time": data.birth_time,
        "place": data.place,
        "longitude": data.longitude,
        "anxing_code": ANXING_CODE,
        "true_solar_time": true_solar["true_solar_time"],
        "time_correction": {
            "input_is_true_solar": true_solar["input_is_true_solar"],
            "longitude_delta_minutes": true_solar["longitude_delta_minutes"],
            "equation_of_time_minutes": true_solar["equation_of_time_minutes"],
            "delta_minutes": true_solar["delta_minutes"],
        },
        "time_branch": hour_branch,
        "lunar_date": f"{lunar.getYearInChinese()}年{lunar.getMonthInChinese()}月{lunar.getDayInChinese()}",
        "lunar_month": lunar_month,
        "lunar_day": lunar_day,
        "year_ganzhi": year_ganzhi,
        "month_ganzhi": month_ganzhi,
        "day_ganzhi": day_ganzhi,
        "day_xunkong": day_xunkong,
        "time_ganzhi": time_ganzhi,
        "命局": f"{_year_yinyang(year_gan)}{data.gender}{wuxing_ju['局名']}",
        "命宫": ming_shen["命宫"],
        "身宫": ming_shen["身宫"],
        "身宫所属宫位": shen_role,
        "命宫干支": ming_gong_ganzhi,
        "五行局": wuxing_ju["五行局"],
        "局数": wuxing_ju["局数"],
        "局名": wuxing_ju["局名"],
        "命主": ming_shen_zhu["命主"],
        "身主": ming_shen_zhu["身主"],
        "子斗": doujun["子斗"],
        "规则来源": {
            "命宫干支": "农历年干五虎遁起寅首 + 宫支顺布",
            "五行局": "命宫干支纳音",
            "主星安星": main_star_info.get("说明"),
            "命主身主": ming_shen_zhu["说明"],
        },
    }

    return ZiweiResult(
        version="wenmo-rebuild-phase2.0",
        anxing_code=ANXING_CODE,
        status="TRIAL_READY",
        message=(
            "已实现真太阳时、时辰换算、命宫/身宫、子斗、命宫干支、五行局、命主/身主、"
            "十四主星安星、前两批辅星/煞曜、亮度框架与四化；更多神煞与文墨天机逐盘校验仍待完成。"
        ),
        basic_info=basic_info,
        palaces=palaces,
        palace_map=palace_map,
        transformations=sihua,
        validation=validation,
    )


def generate_ziwei_chart(data: ZiweiInput) -> ZiweiResult:
    """常规排盘入口，附带时辰边界分析。"""
    result = _generate_ziwei_chart_core(data)
    boundary_analysis = analyze_time_boundary(data)
    result.basic_info["time_accuracy_minutes"] = data.time_accuracy_minutes
    result.basic_info["boundary_threshold_minutes"] = data.boundary_threshold_minutes
    result.validation["时辰边界"] = boundary_analysis
    result.validation["boundary"] = {
        "status": boundary_analysis["status"],
        "details": boundary_analysis,
        "risks": (
            ["输入时间误差范围已跨时辰，建议启用双盘模式。"]
            if boundary_analysis["status"] == "BOUNDARY_SENSITIVE"
            else ["输入时间贴近时辰边界，建议结合生平信息复核。"]
            if boundary_analysis["status"] == "NEAR_BOUNDARY"
            else []
        ),
    }
    reference_match = _build_reference_match_info(data, result)
    result.validation["reference_match"] = reference_match
    result.basic_info["reference_case_name"] = reference_match["case_name"]
    if boundary_analysis["status"] == "BOUNDARY_SENSITIVE":
        result.message += " 当前输入时间误差范围已跨时辰，建议启用双盘模式。"
    elif boundary_analysis["status"] == "NEAR_BOUNDARY":
        result.message += " 当前输入时间贴近时辰边界，建议结合生平信息复核。"
    if reference_match["matched"] and reference_match["status"] == "PASS":
        result.validation["文墨C5FYC逐盘校验"] = "PASS"
    elif reference_match["matched"]:
        result.validation["文墨C5FYC逐盘校验"] = "FAIL"
    return result


def generate_ziwei_chart_with_boundary_support(data: ZiweiInput) -> Dict[str, Any]:
    """
    边界双盘模式：
    - 常规返回主盘
    - 若输入误差范围跨时辰，则额外返回候选时辰对照盘
    """
    boundary_analysis = analyze_time_boundary(data)
    primary_chart = generate_ziwei_chart(data)
    comparison_charts = []

    if boundary_analysis["should_generate_double_chart"]:
        for sample in boundary_analysis["representative_times"]:
            clock_date, clock_time = sample["representative_clock_time"].split(" ")
            comparison_input = ZiweiInput(
                gender=data.gender,
                birth_date=clock_date,
                birth_time=clock_time,
                longitude=data.longitude,
                place=data.place,
                time_accuracy_minutes=0,
                boundary_threshold_minutes=data.boundary_threshold_minutes,
            )
            chart = _generate_ziwei_chart_core(comparison_input)
            comparison_charts.append(
                {
                    "time_branch": sample["time_branch"],
                    "representative_clock_time": sample["representative_clock_time"],
                    "representative_true_solar_time": sample["representative_true_solar_time"],
                    "basic_info": chart.basic_info,
                    "palaces": chart.palaces,
                    "transformations": chart.transformations,
                }
            )

    validation_summary = _build_boundary_validation_summary(boundary_analysis, comparison_charts)
    return {
        "mode": "DOUBLE_CHART" if comparison_charts else "SINGLE_CHART",
        "boundary_analysis": boundary_analysis,
        "validation_summary": validation_summary,
        "primary_chart": asdict(primary_chart),
        "comparison_charts": comparison_charts,
    }


def run_reference_selfcheck() -> Dict[str, Any]:
    """使用已人工转录的文墨天机参考盘做回归校验。"""
    case_results = []
    mismatch_count = 0
    blocking_items = []

    for case in REFERENCE_WENMO_CASES:
        result = generate_ziwei_chart(ZiweiInput(**case["input"]))
        comparison = _build_reference_case_comparison(case, result)
        case_results.append(comparison)
        mismatch_count += comparison["mismatch_count"]
        blocking_items.extend(f"{case['name']}:{item}" for item in comparison["blocking_items"])

    passed = sum(1 for item in case_results if item["status"] == "PASS")
    total = len(case_results)
    summary = f"{passed}/{total} reference cases passed"
    return {
        "status": "PASS" if mismatch_count == 0 else "PARTIAL",
        "summary": summary,
        "case_results": case_results,
        "mismatch_count": mismatch_count,
        "blocking_items": blocking_items,
        "cases": case_results,
    }


if __name__ == "__main__":
    sample = ZiweiInput(gender="男", birth_date="1985-08-10", birth_time="15:00")
    result = generate_ziwei_chart(sample)
    print(asdict(result))
    print(run_reference_selfcheck())
