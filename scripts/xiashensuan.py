#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
虾神算 V2 主流程入口。

说明：
- 默认综合命理入口切到新版
- 旧版 mingli.py 作为怀旧版保留，不参与默认主流程切换
- 新版紫微默认接入 ziwei_wenmo.py
"""

import argparse
import json
import re
import sys
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from mingli import (
    GONG_EXPLAIN,
    ZIWEI_ASSIST,
    ZIWEI_MAIN,
    build_integrated_profile,
)
from xiashensuan_core.adapters.wenmo_text import compare_wenmo_with_ziwei, parse_wenmo_text
from xiashensuan_core.fusion import build_fusion_report, build_personality_complement
from xiashensuan_core.modules.bazi import enhance_bazi_profile, get_dayun_analysis, get_flowyear_analysis, parse
from xiashensuan_core.modules.blood import blood_type_analysis
from xiashensuan_core.modules.mbti import mbti_analysis
from xiashensuan_core.modules.zodiac import zodiac_analysis
from xiashensuan_core.renderers.report_text import build_report_text
from xiashensuan_core.renderers.ziwei import build_ziwei_professional_output
from xiashensuan_core.router import build_route
from ziwei_wenmo import ZiweiInput, generate_ziwei_chart_with_boundary_support
from ziwei_patterns import detect_patterns as _detect_ziwei_patterns


DEFAULT_ENTRY = "scripts/xiashensuan.py"
LEGACY_ENTRY = "scripts/mingli.py"
ZIWEI_ENGINE = "scripts/ziwei_wenmo.py"
DEFAULT_PLACE = "北京"
DEFAULT_LONGITUDE = 116.4
DEFAULT_MODE = "life"
DEFAULT_FOCUS = "full"
FOCUS_PALACES = ["命宫", "夫妻宫", "财帛宫", "官禄宫", "福德宫", "迁移宫", "疾厄宫", "田宅宫", "父母宫"]
BRANCH_SEQUENCE = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_TO_WUXING = {
    "子": "水",
    "丑": "土",
    "寅": "木",
    "卯": "木",
    "辰": "土",
    "巳": "火",
    "午": "火",
    "未": "土",
    "申": "金",
    "酉": "金",
    "戌": "土",
    "亥": "水",
}
WUXING_GENERATES = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
WUXING_CONTROLS = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}
PALACE_IMPACT_LABELS = {
    "命宫": "自己这条主线",
    "兄弟宫": "同辈、伙伴与竞争关系",
    "夫妻宫": "亲密关系与深度合作",
    "子女宫": "输出、作品、后续结果",
    "财帛宫": "钱、资源与落袋能力",
    "疾厄宫": "身心消耗与压力承接",
    "迁移宫": "外部环境、流动与见机",
    "交友宫": "圈层、人脉、团队与合作资源",
    "官禄宫": "事业位置、职责与工作结构",
    "田宅宫": "安身立命、空间与稳定感",
    "福德宫": "心气、精神状态与内在幸福感",
    "父母宫": "长辈、规训与支持系统",
}
THEMATIC_LINKAGES = {
    "事业联动": ["官禄宫", "财帛宫", "迁移宫", "福德宫"],
    "感情联动": ["夫妻宫", "福德宫", "迁移宫", "交友宫"],
    "财运联动": ["财帛宫", "官禄宫", "田宅宫", "福德宫"],
}
THEMATIC_TOPICS = {
    "事业专题": {
        "linkage": "事业联动",
        "focus": "这条专题不单看职位高低，更看结构、平台切换与内在承压能不能同步。",
    },
    "感情专题": {
        "linkage": "感情联动",
        "focus": "这条专题不单看有没有缘分，更看关系能不能承受现实节奏与内在安全感的波动。",
    },
    "财运专题": {
        "linkage": "财运联动",
        "focus": "这条专题不单看赚不赚钱，更看路径、承接、守成与稳定感能不能一起兜住。",
    },
}
FOCUS_TOPIC_MAP = {
    "career": {"topic": "事业专题", "linkage": "事业联动", "judgment": "事业判断", "guidance": "事业趋避"},
    "relationship": {"topic": "感情专题", "linkage": "感情联动", "judgment": "感情判断", "guidance": "感情趋避"},
    "wealth": {"topic": "财运专题", "linkage": "财运联动", "judgment": "财运判断", "guidance": "财运趋避"},
}

STAR_KEYWORDS = {
    **{name: detail["关键词"] for name, detail in ZIWEI_MAIN.items()},
    **ZIWEI_ASSIST,
    "天马": "机动、奔波、变化",
    "天空": "抽离、空转、留白",
    "红鸾": "缘分、心动、喜气",
    "天喜": "喜庆、助缘、活络",
    "三台": "阶梯、抬升、助推",
    "八座": "体面、承托、稳场",
    "恩光": "照拂、善缘、润泽",
    "天贵": "提携、贵助、抬举",
    "将星": "主导、调度、领头",
    "华盖": "清高、专注、独处",
    "截空": "截断、落空、悬置",
    "旬空": "空缺、延后、虚化",
}


def _normalize_mode(mode: str) -> str:
    aliases = {
        "life": "life",
        "生活版": "life",
        "default": "life",
        "professional": "professional",
        "专业版": "professional",
        "pro": "professional",
    }
    normalized = aliases.get((mode or DEFAULT_MODE).strip().lower(), aliases.get(mode, None))
    if normalized:
        return normalized
    raise ValueError(f"不支持的输出模式: {mode}")


def _normalize_focus(focus: str) -> str:
    aliases = {
        "full": "full",
        "all": "full",
        "全部": "full",
        "完整": "full",
        "career": "career",
        "事业": "career",
        "事业专题": "career",
        "job": "career",
        "work": "career",
        "relationship": "relationship",
        "感情": "relationship",
        "关系": "relationship",
        "婚恋": "relationship",
        "感情专题": "relationship",
        "wealth": "wealth",
        "财运": "wealth",
        "财富": "wealth",
        "财务": "wealth",
        "财运专题": "wealth",
    }
    key = (focus or DEFAULT_FOCUS).strip()
    normalized = aliases.get(key.lower(), aliases.get(key, None))
    if normalized:
        return normalized
    raise ValueError(f"不支持的专题焦点: {focus}")


def _build_birth_time(year: int, month: int, day: int, hour: int, minute: int) -> Dict[str, int]:
    return {
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
    }


def _join_keywords(stars: List[str]) -> str:
    words: List[str] = []
    for star in stars:
        raw = STAR_KEYWORDS.get(star, "")
        for word in raw.split("、"):
            if word and word not in words:
                words.append(word)
    return "、".join(words[:4])


def _index_palaces(palaces: List[Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {palace["宫位"]: palace for palace in palaces}


def _extract_focus_palaces(palace_map: Dict[str, Dict[str, Any]]) -> Dict[str, Dict[str, Any]]:
    return {name: palace_map[name] for name in FOCUS_PALACES if name in palace_map}


def _describe_palace(palace: Dict[str, Any]) -> str:
    stars = palace.get("主星", []) + palace.get("辅星", [])
    keywords = _join_keywords(stars) or "待继续结合全盘确认"
    sihua = palace.get("四化", [])
    sihua_text = ""
    if sihua:
        sihua_text = "，并带" + "、".join(f"{item['星曜']}化{item['化']}" for item in sihua)
    return f"主轴更偏{keywords}{sihua_text}。"


def _build_focus_summary(palace_map: Dict[str, Dict[str, Any]]) -> Dict[str, str]:
    summary = {}
    for palace_name, palace in _extract_focus_palaces(palace_map).items():
        meaning = GONG_EXPLAIN.get(palace_name, "")
        prefix = f"{meaning}。" if meaning else ""
        summary[palace_name] = prefix + _describe_palace(palace)
    return summary


def _build_legacy_compatible_ziwei(primary_chart: Dict[str, Any]) -> Dict[str, Any]:
    palace_map = primary_chart["palace_map"]
    ming_palace = palace_map["命宫"]
    ming_stars = ming_palace.get("主星", [])
    ming_assist = ming_palace.get("辅星", [])
    return {
        "命宫主星": "、".join(ming_stars) if ming_stars else "待定",
        "命宫关键词": _join_keywords(ming_stars + ming_assist),
        "身宫": primary_chart["basic_info"].get("身宫所属宫位", ""),
        "重点宫位解读": _build_focus_summary(palace_map),
    }


def _build_ziwei_section(primary_chart: Dict[str, Any]) -> Dict[str, Any]:
    palace_map = primary_chart["palace_map"]
    try:
        patterns = [p.to_dict() for p in _detect_ziwei_patterns(primary_chart)]
    except Exception:
        patterns = []
    return {
        "版本": primary_chart["version"],
        "状态": primary_chart["status"],
        "安星码": primary_chart["anxing_code"],
        "说明": primary_chart["message"],
        "基础信息": primary_chart["basic_info"],
        "重点宫位": _extract_focus_palaces(palace_map),
        "重点宫位解读": _build_focus_summary(palace_map),
        "十二宫": primary_chart["palaces"],
        "四化": primary_chart["transformations"].get("四化", {}),
        "格局": patterns,
        "校验": primary_chart["validation"],
    }


def _bazi_day(bazi: Dict[str, Any]) -> Dict[str, Any]:
    return bazi.get("日主", {})


def _bazi_professional(bazi: Dict[str, Any]) -> Dict[str, Any]:
    return bazi.get("专业分析", {}) if isinstance(bazi.get("专业分析"), dict) else {}


def _bazi_strength_label(bazi: Dict[str, Any]) -> str:
    professional = _bazi_professional(bazi)
    strength = professional.get("旺衰判断", {})
    day = _bazi_day(bazi)
    if isinstance(strength, dict):
        return strength.get("结构判断") or strength.get("原始判断") or day.get("身强弱", "待定")
    return day.get("身强弱", "待定")


def _bazi_strength_category(bazi: Dict[str, Any]) -> str:
    strength = _bazi_strength_label(bazi)
    if "强" in strength:
        return "strong"
    if "弱" in strength:
        return "weak"
    return "balanced"


def _bazi_useful_strategy(bazi: Dict[str, Any]) -> str:
    professional = _bazi_professional(bazi)
    useful = professional.get("用神策略", {})
    day = _bazi_day(bazi)
    if isinstance(useful, dict):
        return useful.get("结构取向") or useful.get("原始喜用") or day.get("喜用神", "待定")
    return day.get("喜用神", "待定")


def _bazi_legacy_yongshen(bazi: Dict[str, Any]) -> str:
    professional = _bazi_professional(bazi)
    useful = professional.get("用神策略", {})
    if isinstance(useful, dict):
        return useful.get("原始喜用") or _bazi_day(bazi).get("喜用神", "")
    return _bazi_day(bazi).get("喜用神", "")


_PATTERN_LEVEL_ORDER = {'excellent': 0, 'good': 1, 'neutral': 2, 'caution': 3}
_PATTERN_LEVEL_LABEL = {'excellent': '上吉', 'good': '吉格', 'neutral': '中性', 'caution': '需注意'}


def _summarize_top_patterns(patterns: List[Dict[str, Any]], top_n: int = 3) -> str:
    if not patterns:
        return ""
    sorted_ps = sorted(
        patterns,
        key=lambda p: _PATTERN_LEVEL_ORDER.get(p.get('level', ''), 9),
    )
    lines: List[str] = []
    for p in sorted_ps[:top_n]:
        label = _PATTERN_LEVEL_LABEL.get(p.get('level', ''), '')
        name = p.get('name', '')
        desc = (p.get('description') or '').split('。', 1)[0]
        source = p.get('source') or ''
        suffix = f"（{source}）" if source else ''
        lines.append(f"【{label}】{name}：{desc}。{suffix}")
    # 破格警示：把所有触发的 breaking 条件提一下
    breakings: List[str] = []
    for p in sorted_ps[:top_n]:
        cond = p.get('conditions') or {}
        for b in cond.get('breaking', []) or []:
            breakings.append(f"{p.get('name','')} → {b}")
    if breakings:
        lines.append("破格提示：" + "；".join(breakings))
    return "\n".join(lines)


def _build_recommendations(bazi: Dict[str, Any], ziwei_section: Dict[str, Any]) -> Dict[str, str]:
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    annual = bazi.get("流年骨架", {})
    boundary = ziwei_section["校验"].get("boundary", {})
    career = f"事业上顺着“{dayun.get('主轴', '当前主轴')}”发力，少在无效消耗里硬撑。"
    relation = f"感情上更要看真实需求，不要只在表面节奏上互相误解。夫妻宫主题当前偏{_describe_palace(ziwei_section['重点宫位']['夫妻宫'])}"
    state = f"状态上先顾住{_bazi_strength_label(bazi)}这条底层节奏；今年主轴偏“{annual.get('年度主轴', '阶段调整')}”。"
    if boundary.get("status") in {"NEAR_BOUNDARY", "BOUNDARY_SENSITIVE"}:
        state += " 这张盘贴近时辰边界，遇到关键判断最好双盘并看。"
    out = {
        "事业上": career,
        "感情上": relation,
        "状态上": state,
    }
    patterns_summary = _summarize_top_patterns(ziwei_section.get("格局", []) or [])
    if patterns_summary:
        out["格局亮点"] = patterns_summary
    return out


def _palace_keywords(palace: Dict[str, Any], fallback: str = "这条线") -> str:
    stars = palace.get("主星", []) + palace.get("辅星", [])
    keywords = _join_keywords(stars)
    return keywords or fallback


def _life_base_tone(bazi: Dict[str, Any]) -> str:
    strength = _bazi_strength_category(bazi)
    if strength == "strong":
        return "底层是能扛事的，很多时候不是没能力，而是容易把力气耗在不值得的地方"
    if strength == "weak":
        return "底层更需要稳定感和托底环境，不是不能成事，而是成事更看环境和节奏"
    return "底层不算极端，很多事成败不在天赋够不够，而在节奏有没有踩对"


def _life_overall_line(
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    guide: Dict[str, Any],
) -> str:
    ming_palace = ziwei_section["重点宫位"]["命宫"]
    ming_keywords = _palace_keywords(ming_palace, "人物底色")
    return (
        f"先看整体，你这类人不是表面上那种一路猛冲、靠气势赢的人，"
        f"而是{_life_base_tone(bazi)}。"
        f" 命宫这边又把你外面那层样子，往{ming_keywords}这一路推，"
        f"所以别人第一眼看你，往往会先看到这一面。"
    )


def _life_personality_line(
    ziwei_section: Dict[str, Any],
    guide: Dict[str, Any],
    zodiac: Dict[str, Any],
    mbti_result: Dict[str, Any],
) -> str:
    basic = ziwei_section["基础信息"]
    ming_palace = ziwei_section["重点宫位"]["命宫"]
    ming_keywords = _palace_keywords(ming_palace, "个人气质")
    shen_role = basic["身宫所属宫位"]
    text = (
        f"你不是外面看起来那样简单。"
        f" 表面上给人的感觉更偏{ming_keywords}，"
        f"但真正把你整个人往前推的，往往是{shen_role}这条线。"
        f" 也就是说，你不是没有别的可能，只是现实里更容易把力气放在{shen_role}对应的人生主题上。"
    )
    if zodiac.get("星座"):
        text += f" 再加上{zodiac['星座']}这层外显气质，别人会更容易先感受到你外面的那层样子。"
    if mbti_result and mbti_result.get("类型"):
        text += f" 如果再叠上{mbti_result['类型']}这一类行为风格，就更容易出现“外面这样看你，里面其实不是那回事”的感觉。"
    return text


def _life_career_line(ziwei_section: Dict[str, Any]) -> str:
    guan = ziwei_section["重点宫位"]["官禄宫"]
    cai = ziwei_section["重点宫位"]["财帛宫"]
    guan_keywords = _palace_keywords(guan, "做事方式")
    cai_keywords = _palace_keywords(cai, "财路节奏")
    return (
        f"事业上你真正适合的，不是一味拼体力、拼情绪，而是走{guan_keywords}这一路。"
        f" 你值钱的地方，往往不在一时爆发，而在能不能把事情稳住、理顺、慢慢坐实。"
        f" 财运也是一样，你的问题通常不在没机会，而在机会来了之后，能不能按{cai_keywords}这条路把结果接住。"
    )


def _life_relationship_line(ziwei_section: Dict[str, Any]) -> str:
    spouse = ziwei_section["重点宫位"]["夫妻宫"]
    spouse_keywords = _palace_keywords(spouse, "关系节奏")
    return (
        f"感情上你真正要的，不只是有人陪，而是关系能不能稳、能不能懂、能不能让你心里不别扭。"
        f" 你在关系里最怕的，不是没人爱，而是节奏乱、拉扯多、情绪一直悬着。"
        f" 所以这条线最后还是会回到{spouse_keywords}这几个字上。"
    )


def _life_health_line(ziwei_section: Dict[str, Any]) -> str:
    fude = ziwei_section["重点宫位"]["福德宫"]
    jie = ziwei_section["重点宫位"]["疾厄宫"]
    fude_keywords = _palace_keywords(fude, "内在状态")
    jie_keywords = _palace_keywords(jie, "身体反应")
    return (
        f"状态上你最怕的不是忙，而是心里一直松不下来。"
        f" 你很多问题不是外面一眼看得见的，而是内里那根弦一直绷着。"
        f" 一旦绷久了，身体很多时候就会替情绪说话，所以{fude_keywords}和{jie_keywords}这两条线都要顾。"
    )


def _life_luck_line(bazi: Dict[str, Any], ziwei_section: Dict[str, Any]) -> str:
    annual = bazi.get("流年骨架", {})
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    boundary = ziwei_section["校验"].get("boundary", {})
    text = (
        f"放到当前阶段看，你现在的主轴偏“{annual.get('年度主轴', '阶段调整')}”，"
        f"而大运又在“{dayun.get('主轴', '阶段主轴')}”这条线上。"
        f" 这就说明，眼下真正考验你的，不只是机会来没来，而是你能不能稳住自己的节奏，把事情接稳。"
    )
    if boundary.get("status") in {"NEAR_BOUNDARY", "BOUNDARY_SENSITIVE"}:
        text += " 另外这张盘本身又贴近时辰边界，真要细断，最好把双盘一起参照。"
    return text


def _life_summary_line(bazi: Dict[str, Any], ziwei_section: Dict[str, Any]) -> str:
    basic = ziwei_section["基础信息"]
    return (
        f"总结一句，这类命不是靠乱冲赢，而是靠判断、节奏和定力赢。"
        f" 你的优势在于{_bazi_strength_label(bazi)}带来的底层支撑，"
        f"真正需要注意的，是别让{basic['身宫所属宫位']}这条线把你拖进内耗。"
        " 如果能把心气稳住，把力气用在对的地方，越往后通常越能看出后劲。"
    )


def _stars_label(palace: Dict[str, Any]) -> str:
    stars = palace.get("主星", [])
    return "、".join(stars) if stars else "空曜待参"


def _professional_yongshen_line(bazi: Dict[str, Any]) -> str:
    strategy = _bazi_useful_strategy(bazi)
    yongshen = f"{strategy} {_bazi_legacy_yongshen(bazi)}"
    if "官杀" in yongshen or "财星" in yongshen:
        return "用神偏官杀财星，翻成白话，就是越在讲规则、讲结果、讲兑现的环境里，越容易把本事坐实。"
    if "印星" in yongshen or "比劫" in yongshen:
        return "用神偏印比，翻成白话，就是先补底盘、先借支持、先稳住自己，比一味往前冲更要紧。"
    return "此命喜忌不算偏锋，真正要紧的是顺势调平，不可偏执走一头。"


def _professional_strength_line(bazi: Dict[str, Any]) -> str:
    day = _bazi_day(bazi)
    strength = _bazi_strength_label(bazi)
    category = _bazi_strength_category(bazi)
    day_master = day.get("日主", "")
    wuxing = day.get("五行", "")
    if category == "strong":
        return f"日主{day_master}{wuxing}，结构判断{strength}，主气在己身，主见不弱，宜泄宜克。翻成白话，不怕事多，怕的是力气使偏。"
    if category == "weak":
        return f"日主{day_master}{wuxing}，结构判断{strength}，根气重在外援，宜扶宜生。翻成白话，不是不能成事，而是成事更讲环境与托举。"
    return f"日主{day_master}{wuxing}，结构判断{strength}，命局不走极端。翻成白话，成败更看阶段节奏和外部位置。"


def _professional_month_root_line(bazi: Dict[str, Any]) -> str:
    month_pillar = bazi["四柱"]["月"]
    month_branch = month_pillar[1]
    month_wuxing = BRANCH_TO_WUXING.get(month_branch, "")
    day_wuxing = bazi["日主"]["五行"]
    if month_wuxing == day_wuxing:
        relation = "月令与日主同气，主根气不虚，遇事不至一碰就散。"
    elif WUXING_GENERATES.get(month_wuxing) == day_wuxing:
        relation = "月令生日主，属印气暗扶，这种命遇到对的人和对的环境，往往能被托起来。"
    elif WUXING_GENERATES.get(day_wuxing) == month_wuxing:
        relation = "日主泄于月令，主气外放，做事容易把力气先用出去。"
    elif WUXING_CONTROLS.get(month_wuxing) == day_wuxing:
        relation = "月令制日主，现实规矩和外部压力感会更早压到身上。"
    elif WUXING_CONTROLS.get(day_wuxing) == month_wuxing:
        relation = "日主克月令，财气牵引偏重，很多决定容易先被现实问题推着走。"
    else:
        relation = "月令与日主关系不算偏锋，真正决定成败的还是后天运势与所处位置。"
    return f"月令在{month_branch}，五行属{month_wuxing}。{relation}"


def _professional_tengod_axis_line(bazi: Dict[str, Any]) -> str:
    yongshen = f"{_bazi_useful_strategy(bazi)} {_bazi_legacy_yongshen(bazi)}"
    if "官杀" in yongshen and "财星" in yongshen:
        return "命局十神主轴偏官财，主题落在责任、位置、结果与兑现。说得更直白一点，就是越现实、越见真章。"
    if "官杀" in yongshen:
        return "命局十神主轴偏官杀，讲的是规矩、位置、承担与压力。走好了是成事，走偏了就是绷得太紧。"
    if "财星" in yongshen:
        return "命局十神主轴偏财，讲的是资源、现实、得失与交换。成败多半跟判断现实轻重有关。"
    if "印星" in yongshen and "比劫" in yongshen:
        return "命局十神主轴偏印比，讲的是托底、恢复、自持与积累。先稳自己，再谈往外发。"
    if "印星" in yongshen:
        return "命局十神主轴偏印，遇事宜先蓄势、先得支持，不可一上来就硬碰硬。"
    if "比劫" in yongshen:
        return "命局十神主轴偏比劫，主自我意志重，成事靠心气，败也容易败在太凭一口气。"
    return "命局十神主轴不算单边，真正起作用的，还是盘里几条主线怎么彼此牵引。"


def _professional_imbalance_line(bazi: Dict[str, Any]) -> str:
    wuxing = bazi.get("五行分布", {})
    ordered = sorted(wuxing.items(), key=lambda item: item[1], reverse=True)
    strongest, strongest_count = ordered[0]
    weakest, weakest_count = ordered[-1]
    if strongest_count - weakest_count >= 2:
        return f"五行分布里{strongest}气偏旺，{weakest}气偏弱。命里最怕的不是没机会，而是强处过强、弱处一直补不上。"
    return "五行分布不算一头独大，命局失衡点不在偏枯，而在阶段性节奏一乱就容易把优势打散。"


def _professional_geju_center_line(bazi: Dict[str, Any], ziwei_section: Dict[str, Any]) -> str:
    shen_role = ziwei_section["基础信息"]["身宫所属宫位"]
    return (
        f"格局重心不只在八字本身，还被紫微的{shen_role}一路牵动。"
        f" 所以这命看似只是性格问题，实则很多关键选择，最后都会落到{shen_role}对应的人生课题上。"
    )


def _professional_ming_shen_line(ziwei_section: Dict[str, Any]) -> str:
    basic = ziwei_section["基础信息"]
    ming_palace = ziwei_section["重点宫位"]["命宫"]
    ming_stars = _stars_label(ming_palace)
    shen_role = basic["身宫所属宫位"]
    keywords = _join_keywords(ming_palace.get("主星", []) + ming_palace.get("辅星", [])) or "格局主轴"
    return (
        f"命宫见{ming_stars}，身宫落{shen_role}。此盘先天气质偏{keywords}，后天真正发力，多半落在{shen_role}这一条线上。"
    )


def _professional_branch_to_palace_map(ziwei_section: Dict[str, Any]) -> Dict[str, str]:
    return {palace["宫支"]: palace["宫位"] for palace in ziwei_section["十二宫"]}


def _professional_full_palace_map(ziwei_section: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {palace["宫位"]: palace for palace in ziwei_section["十二宫"]}


def _professional_branch_hua_target_line(ziwei_section: Dict[str, Any]) -> str:
    branch_map = _professional_branch_to_palace_map(ziwei_section)
    pieces = []
    for hua_name in ["禄", "权", "科", "忌"]:
        detail = ziwei_section["四化"].get(hua_name, {})
        branch = detail.get("宫支")
        palace_name = branch_map.get(branch, "待定宫位")
        pieces.append(f"{detail.get('星曜', '待补')}化{hua_name}落{palace_name}")
    return "、".join(pieces)


def _professional_sanfang_sizheng_set(ziwei_section: Dict[str, Any], palace_name: str) -> List[Dict[str, Any]]:
    palace_map = _professional_full_palace_map(ziwei_section)
    target = palace_map[palace_name]
    idx = BRANCH_SEQUENCE.index(target["宫支"])
    branches = [
        BRANCH_SEQUENCE[idx],
        BRANCH_SEQUENCE[(idx + 4) % 12],
        BRANCH_SEQUENCE[(idx + 8) % 12],
        BRANCH_SEQUENCE[(idx + 6) % 12],
    ]
    branch_lookup = {palace["宫支"]: palace for palace in ziwei_section["十二宫"]}
    return [branch_lookup[branch] for branch in branches if branch in branch_lookup]


def _professional_linkage_line(ziwei_section: Dict[str, Any], label: str) -> str:
    palace_map = _professional_full_palace_map(ziwei_section)
    palaces = [palace_map[name] for name in THEMATIC_LINKAGES[label]]
    pieces = [f"{palace['宫位']}见{_stars_label(palace)}" for palace in palaces]
    if label == "事业联动":
        tail = "说明事业成不成，不只看职位高低，还要看财路、环境和心气能不能一起跟上。"
    elif label == "感情联动":
        tail = "说明关系成败不只看对象本身，也看自己内里状态、环境变化与圈层牵引。"
    else:
        tail = "说明财运不是单看赚钱能力，还要看事业位置、承接结构和安全感能不能兜住。"
    return "；".join(pieces) + "。" + tail


def _professional_linkage_triplet(ziwei_section: Dict[str, Any], label: str) -> Dict[str, str]:
    palace_map = _professional_full_palace_map(ziwei_section)

    if label == "事业联动":
        guan = palace_map["官禄宫"]
        cai = palace_map["财帛宫"]
        qian = palace_map["迁移宫"]
        fu = palace_map["福德宫"]
        return {
            "主因": (
                f"主因在官禄与财帛这条线。官禄宫见{_stars_label(guan)}，说明做事路径、职责结构与位置感是根；"
                f"财帛宫见{_stars_label(cai)}，说明最后能不能把事做成钱、把资源收成结果，也是一道硬门槛。"
            ),
            "触发条件": (
                f"触发条件多半落在迁移与福德。迁移宫见{_stars_label(qian)}，外部环境、平台变化、项目切换一动，事业题目就会被推出来；"
                f"福德宫见{_stars_label(fu)}，心气稳不稳、内里耗不耗，会直接决定这条事业线能不能持续发力。"
            ),
            "风险点": (
                f"风险点在于官财能起而福德失守，容易出现位置先上去了，但承接、节奏与内耗没有一起跟上的情况。"
                f" 若{_palace_keywords(fu, '心气')}长期失衡，事业判断就容易变形。"
            ),
        }

    if label == "感情联动":
        spouse = palace_map["夫妻宫"]
        fu = palace_map["福德宫"]
        qian = palace_map["迁移宫"]
        jiaoyou = palace_map["交友宫"]
        return {
            "主因": (
                f"主因在夫妻与福德。夫妻宫见{_stars_label(spouse)}，这是你对亲密关系与合作关系的基本取向；"
                f"福德宫见{_stars_label(fu)}，说明真正决定关系能不能稳住的，往往不是表面互动，而是内在安全感与心气节奏。"
            ),
            "触发条件": (
                f"触发条件常落在迁移与交友。迁移宫见{_stars_label(qian)}，环境一变、距离一拉、现实条件一调整，关系问题就更容易浮出来；"
                f"交友宫见{_stars_label(jiaoyou)}，圈层、人脉、合作关系也会把人带进来，或把原有关系推向重新判断。"
            ),
            "风险点": (
                f"风险点在于内里还没稳，关系已经先进入现实拉扯。"
                f" 若{_palace_keywords(spouse, '关系主题')}与{_palace_keywords(fu, '心气')}互相顶住，就容易出现想靠近又难真正安下来的局面。"
            ),
        }

    cai = palace_map["财帛宫"]
    guan = palace_map["官禄宫"]
    tian = palace_map["田宅宫"]
    fu = palace_map["福德宫"]
    return {
        "主因": (
            f"主因在财帛与官禄。财帛宫见{_stars_label(cai)}，先看钱从哪里来、能不能落袋；"
            f"官禄宫见{_stars_label(guan)}，再看事业位置和职责结构，能不能给财路提供稳定来源。"
        ),
        "触发条件": (
            f"触发条件多半落在田宅与福德。田宅宫见{_stars_label(tian)}，说明稳定感、资产观念、安身立命的基础一旦变化，财运决策就会跟着变；"
            f"福德宫见{_stars_label(fu)}，说明能不能守财、持续承接，最终还要看心态和节奏。"
        ),
        "风险点": (
            f"风险点在于只盯财帛宫，不看官禄、田宅与福德能不能一起兜住。"
            f" 若{_palace_keywords(cai, '财路')}起得快、{_palace_keywords(fu, '心气')}却跟不上，就容易出现有机会却留不住结果的情况。"
        ),
    }


def _professional_hua_implications(ziwei_section: Dict[str, Any]) -> Dict[str, str]:
    branch_map = _professional_branch_to_palace_map(ziwei_section)
    prefixes = {
        "禄": "资源与机会更容易起在",
        "权": "责任、掌控与压力多半压在",
        "科": "名声、体面与抬举更容易显在",
        "忌": "最容易起牵扯、绊脚与心结的地方在",
    }
    result = {}
    for hua_name in ["禄", "权", "科", "忌"]:
        detail = ziwei_section["四化"].get(hua_name, {})
        palace_name = branch_map.get(detail.get("宫支"), "待定宫位")
        impact = PALACE_IMPACT_LABELS.get(palace_name, "该宫主题")
        result[hua_name] = f"{detail.get('星曜', '待补')}化{hua_name}落{palace_name}，{prefixes[hua_name]}{impact}。"
    return result


def _professional_hua_layered_implications(
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
) -> Dict[str, Dict[str, str]]:
    branch_map = _professional_branch_to_palace_map(ziwei_section)
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    dayun_axis = dayun.get("主轴", "阶段结构")
    long_term_prefixes = {
        "禄": "本命长期看，这颗化禄会把资源入口、贵人牵引与现实机会持续往",
        "权": "本命长期看，这颗化权会把责任、主导权与必须出面担结果的题目长期压在",
        "科": "本命长期看，这颗化科会把名声、体面、被看见与被认可的加分，长期落在",
        "忌": "本命长期看，这颗化忌会把反复牵扯、顾虑心结与代价累积，长期系在",
    }
    dayun_prefixes = {
        "禄": "放到当前大运，这颗禄更容易被推成资源重组、机会显化与可兑现的入口，重点仍在",
        "权": "放到当前大运，这颗权更容易被推成位置上肩、职责加码与现实压力，重点仍在",
        "科": "放到当前大运，这颗科更容易被推成名头抬升、口碑加分与被看见，重点仍在",
        "忌": "放到当前大运，这颗忌更容易被推成返工、顾虑、拖拽与不得不处理的旧题，重点仍在",
    }
    result: Dict[str, Dict[str, str]] = {}
    for hua_name in ["禄", "权", "科", "忌"]:
        detail = ziwei_section["四化"].get(hua_name, {})
        palace_name = branch_map.get(detail.get("宫支"), "待定宫位")
        impact = PALACE_IMPACT_LABELS.get(palace_name, "该宫主题")
        result[hua_name] = {
            "本命长期主题": (
                f"{detail.get('星曜', '待补')}化{hua_name}落{palace_name}，"
                f"{long_term_prefixes[hua_name]}{impact}。"
            ),
            "当前大运放大点": (
                f"当前大运主轴在“{dayun_axis}”，"
                f"{dayun_prefixes[hua_name]}{impact}。"
            ),
        }
    return result


def _professional_thematic_palace_line(ziwei_section: Dict[str, Any], label: str) -> str:
    palace_map = _professional_full_palace_map(ziwei_section)
    palaces = [palace_map[name] for name in THEMATIC_LINKAGES[label]]
    return "；".join(f"{palace['宫位']}见{_stars_label(palace)}" for palace in palaces) + "。"


def _professional_thematic_hua_line(
    ziwei_section: Dict[str, Any],
    label: str,
    hua_layered_impacts: Dict[str, Dict[str, str]],
) -> str:
    branch_map = _professional_branch_to_palace_map(ziwei_section)
    relevant_palaces = set(THEMATIC_LINKAGES[label])
    matched = []
    for hua_name in ["禄", "权", "科", "忌"]:
        detail = ziwei_section["四化"].get(hua_name, {})
        palace_name = branch_map.get(detail.get("宫支"), "待定宫位")
        if palace_name in relevant_palaces:
            matched.append(hua_layered_impacts[hua_name]["本命长期主题"].rstrip("。"))
    if matched:
        return "；".join(matched) + "。"
    first = THEMATIC_LINKAGES[label][0]
    second = THEMATIC_LINKAGES[label][1]
    return f"这条专题当前不以四化直接落{first}/{second}为主，更要回到宫位结构本身去看主线。"


def _professional_thematic_dayun_line(bazi: Dict[str, Any], label: str) -> str:
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    annual = bazi.get("流年骨架", {})
    axis = dayun.get("主轴", "阶段结构")
    annual_axis = annual.get("年度主轴", "阶段调整")
    if label == "事业联动":
        tail = "放到事业线上，就是位置、职责、平台与长期承接能力会被放大检验。"
    elif label == "感情联动":
        tail = "放到感情线上，就是关系节奏、现实安排与边界感会更容易被推上桌面。"
    else:
        tail = "放到财运线上，就是资源收口、路径稳定性与守成能力会被更直接地检验。"
    return f"当前大运主轴在“{axis}”，流年题目偏“{annual_axis}”；{tail}"


def _professional_thematic_conclusion(ziwei_section: Dict[str, Any], label: str) -> str:
    palace_map = _professional_full_palace_map(ziwei_section)
    if label == "事业联动":
        return (
            f"事业线最后看的是官禄宫{_stars_label(palace_map['官禄宫'])}能不能把外部机会接成稳定位置，"
            f"以及福德宫{_stars_label(palace_map['福德宫'])}能不能撑住长期输出。"
        )
    if label == "感情联动":
        return (
            f"感情线最后看的是夫妻宫{_stars_label(palace_map['夫妻宫'])}的关系取向，"
            f"能不能和福德宫{_stars_label(palace_map['福德宫'])}的内在节奏对得上。"
        )
    return (
        f"财运线最后看的是财帛宫{_stars_label(palace_map['财帛宫'])}的落袋能力，"
        f"能不能和官禄宫{_stars_label(palace_map['官禄宫'])}、田宅宫{_stars_label(palace_map['田宅宫'])}一起构成可持续结构。"
    )


def _professional_topic_reports(
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    hua_layered_impacts: Dict[str, Dict[str, str]],
) -> Dict[str, Dict[str, str]]:
    triplets = {
        label: _professional_linkage_triplet(ziwei_section, label)
        for label in THEMATIC_LINKAGES
    }
    reports: Dict[str, Dict[str, str]] = {}
    for topic_name, spec in THEMATIC_TOPICS.items():
        label = spec["linkage"]
        reports[topic_name] = {
            "专题主轴": triplets[label]["主因"],
            "关键宫位": _professional_thematic_palace_line(ziwei_section, label),
            "四化牵引": _professional_thematic_hua_line(ziwei_section, label, hua_layered_impacts),
            "当前大运切面": _professional_thematic_dayun_line(bazi, label),
            "风险提示": triplets[label]["风险点"],
            "专题结论": f"{spec['focus']} {_professional_thematic_conclusion(ziwei_section, label)}",
        }
    return reports


def _professional_axis_structure(ziwei_section: Dict[str, Any]) -> str:
    focus_palaces = ziwei_section["重点宫位"]
    guan = focus_palaces["官禄宫"]
    cai = focus_palaces["财帛宫"]
    fu = focus_palaces["福德宫"]
    qian = focus_palaces["迁移宫"]
    fuqi = focus_palaces["夫妻宫"]
    return (
        f"官禄见{_stars_label(guan)}，主做事路径有其章法；"
        f"财帛见{_stars_label(cai)}，财路不单看机会，还看能否把资源收拢；"
        f"福德见{_stars_label(fu)}，内里真正牵动你的，是心气与耗神处；"
        f"迁移见{_stars_label(qian)}，外部环境一动，盘势就容易被带起来；"
        f"夫妻见{_stars_label(fuqi)}，情感与合作关系，也是此盘的重要牵引点。"
    )


def _professional_sanfang_line(ziwei_section: Dict[str, Any]) -> str:
    group = _professional_sanfang_sizheng_set(ziwei_section, "命宫")
    ming = group[0]
    others = "、".join(f"{palace['宫位']}见{_stars_label(palace)}" for palace in group[1:])
    return (
        f"命宫坐{_stars_label(ming)}，三方四正再牵到{others}。"
        " 这种盘不能只看命宫一处，要把命宫本身和旁边几条关键线一起看，盘势才会立体。"
    )


def _professional_realworld_line(ziwei_section: Dict[str, Any]) -> str:
    focus_palaces = ziwei_section["重点宫位"]
    guan = focus_palaces["官禄宫"]
    cai = focus_palaces["财帛宫"]
    fu = focus_palaces["福德宫"]
    spouse = focus_palaces["夫妻宫"]
    qian = focus_palaces["迁移宫"]
    return (
        f"官禄这边见{_stars_label(guan)}，说明事业路子重章法与判断；"
        f"财帛这边见{_stars_label(cai)}，说明财路不只看机会，还看承接与收口；"
        f"福德这边见{_stars_label(fu)}，说明心气与内耗是隐线；"
        f"夫妻这边见{_stars_label(spouse)}，关系与合作会牵动现实取舍；"
        f"迁移这边见{_stars_label(qian)}，外部环境一变，整盘应象就会跟着动。"
    )


def _professional_four_hua_line(ziwei_section: Dict[str, Any]) -> str:
    four_hua = ziwei_section["四化"]
    ordered = []
    for hua_name in ["禄", "权", "科", "忌"]:
        detail = four_hua.get(hua_name, {})
        star = detail.get("星曜", "待补")
        branch = detail.get("宫支", "待定")
        ordered.append(f"{star}化{hua_name}在{branch}")
    return "四化以" + "、".join(ordered) + "为主，重点要看化曜把力推到哪里，而不是只背星名。"


def _professional_hua_flow_line(ziwei_section: Dict[str, Any]) -> str:
    return (
        f"若看四化真正把力推向哪里，当前可抓：{_professional_branch_hua_target_line(ziwei_section)}。"
        " 禄多主资源与机会，权多主责任与掌控，科主名声与抬举，忌则是这张盘最容易绊脚的地方。"
    )


def _professional_total_judgment(
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    integrated: Dict[str, Any],
) -> str:
    basic = ziwei_section["基础信息"]
    return (
        f"总的看，这不是一张走虚名的盘，而是一张要靠位置、节奏与结构成事的盘。"
        f" 八字上结构判断为{_bazi_strength_label(bazi)}，紫微上又由{basic['身宫所属宫位']}牵动现实发力，"
        f"所以命里的关键，从来不是有没有机会，而是机会来了，你站不站得住、接不接得稳。"
    )


def _professional_guidance(bazi: Dict[str, Any], ziwei_section: Dict[str, Any]) -> Dict[str, str]:
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    annual = bazi.get("流年骨架", {})
    boundary = ziwei_section["校验"].get("boundary", {})
    career = f"事业上宜顺当前大运“{dayun.get('主轴', '阶段调整')}”去立位，不宜见机就扑，先立结构再求突破。"
    feeling = "感情上宁可慢断，不宜情绪先行；此盘关系宫会牵动现实选择，择人重节奏与边界。"
    wealth = "财运上先看路径与承接，再看扩张；能不能收口，比一时机会多少更关键。"
    state = f"状态上要防“{annual.get('年度主轴', '阶段压力')}”带来的绷紧。"
    if boundary.get("status") in {"NEAR_BOUNDARY", "BOUNDARY_SENSITIVE"}:
        state += " 此命又贴近时辰边界，若做细断，宜双盘参看。"
    return {
        "事业趋避": career,
        "感情趋避": feeling,
        "财运趋避": wealth,
        "状态趋避": state,
    }


def _professional_opening_line(bazi: Dict[str, Any], ziwei_section: Dict[str, Any]) -> str:
    ming = ziwei_section["重点宫位"]["命宫"]
    shen_role = ziwei_section["基础信息"]["身宫所属宫位"]
    ming_stars = _stars_label(ming)
    strength = _bazi_strength_category(bazi)
    if strength == "strong":
        base = "骨子里不虚，外面未必张扬，但关键时候不至没主心骨"
    elif strength == "weak":
        base = "先天气不足以蛮冲，成局更靠借力、借势、借环境"
    else:
        base = "先天不走极端，很多成败都看时运怎么把这个人推出来"
    return (
        f"此命{base}。命宫坐{ming_stars}，身宫落{shen_role}，"
        "故而不是一眼看去便知深浅的盘，往往越往后看，越能看出内里的主线。"
    )


def _build_life_mode_output(
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    integrated: Dict[str, Any],
    zodiac: Dict[str, Any],
    mbti_result: Dict[str, Any],
) -> Dict[str, Any]:
    guide = integrated.get("生活版引导", {})
    focus = ziwei_section["重点宫位解读"]
    recommendations = _build_recommendations(bazi, ziwei_section)
    return {
        "模式": "生活版",
        "整体判断": _life_overall_line(bazi, ziwei_section, guide),
        "性格气质": _life_personality_line(ziwei_section, guide, zodiac, mbti_result),
        "事业与财运": _life_career_line(ziwei_section),
        "感情与婚姻": _life_relationship_line(ziwei_section),
        "健康与状态": _life_health_line(ziwei_section),
        "当前运势": _life_luck_line(bazi, ziwei_section),
        "建议": recommendations,
        "总结": _life_summary_line(bazi, ziwei_section),
        "盘面支撑": {
            "事业与财运": f"{focus.get('官禄宫', '')} {focus.get('财帛宫', '')}".strip(),
            "感情与婚姻": focus.get("夫妻宫", ""),
            "健康与状态": f"{focus.get('疾厄宫', '')} {focus.get('福德宫', '')}".strip(),
        },
    }


def _build_professional_mode_output(
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    integrated: Dict[str, Any],
    gender: str,
    place: str,
) -> Dict[str, Any]:
    day = bazi["日主"]
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    annual = bazi.get("流年骨架", {})
    basic = ziwei_section["基础信息"]
    focus = ziwei_section["重点宫位解读"]
    four_hua = ziwei_section["四化"]
    four_hua_text = "、".join(f"{detail['星曜']}化{name}在{detail['宫支']}" for name, detail in four_hua.items())
    bazi_professional = bazi.get("专业分析", {})
    guidance = _professional_guidance(bazi, ziwei_section)
    hua_impacts = _professional_hua_implications(ziwei_section)
    hua_layered_impacts = _professional_hua_layered_implications(bazi, ziwei_section)
    topic_reports = _professional_topic_reports(bazi, ziwei_section, hua_layered_impacts)
    return {
        "模式": "专业版",
        "总起断": _professional_opening_line(bazi, ziwei_section),
        "命盘信息": (
            f"{gender}命，出生于{bazi['出生时间']}，地点{place}，真太阳时{basic['true_solar_time']}。"
            f" 八字为{bazi['八字']}，紫微命局为{basic['命局']}，命宫在{basic['命宫']}，身宫在{basic['身宫所属宫位']}。"
        ),
        "八字排盘": {
            "专业分析口径": bazi_professional.get("排盘口径", {}),
            "基础排盘": (
                f"四柱：{bazi['八字']}。日主为{day['日主']}，五行属{day['五行']}，"
                f"结构判断为{_bazi_strength_label(bazi)}；用神策略：{_bazi_useful_strategy(bazi)}"
            ),
            "十神明细": bazi_professional.get("十神明细", {}),
            "五行强度": bazi_professional.get("五行强度", {}),
            "旺衰判断": bazi_professional.get("旺衰判断", {}),
            "用神策略": bazi_professional.get("用神策略", {}),
            "月令与根气": _professional_month_root_line(bazi),
            "十神主轴": _professional_tengod_axis_line(bazi),
            "格局重心": _professional_geju_center_line(bazi, ziwei_section),
            "失衡点": _professional_imbalance_line(bazi),
            "命局结构": f"{_professional_strength_line(bazi)} {_professional_yongshen_line(bazi)}",
            "专题映射": bazi_professional.get("专题映射", {}),
            "正文分析": bazi_professional.get("正文分析", {}),
            "八字结论": (
                f"这类八字，论命不宜只看表面热闹，要看气有没有归处、力有没有用在刀口上。"
                f" 当前大运主轴在“{dayun.get('主轴', '阶段结构')}”，流年又把题目压到“{annual.get('年度主轴', '阶段调整')}”，"
                "说明命势重点在现实承担，不在空转设想。"
            ),
        },
        "紫微斗数排盘": {
            "基础盘面": (
                f"命局：{basic['命局']}；命宫：{basic['命宫']}；身宫：{basic['身宫所属宫位']}；"
                f"命主/身主：{basic['命主']}/{basic['身主']}；四化：{four_hua_text}。"
            ),
            "命宫与身宫": _professional_ming_shen_line(ziwei_section),
            "三方四正": _professional_sanfang_line(ziwei_section),
            "官财福夫妻迁移": _professional_realworld_line(ziwei_section),
            "四化流向": _professional_hua_flow_line(ziwei_section),
            "四化应事": hua_impacts,
            "四化应事分层": hua_layered_impacts,
            "宫位联动": {
                label: _professional_linkage_line(ziwei_section, label)
                for label in THEMATIC_LINKAGES
            },
            "宫位联动三段式": {
                label: _professional_linkage_triplet(ziwei_section, label)
                for label in THEMATIC_LINKAGES
            },
            "专题拆盘": topic_reports,
            "主轴结构": f"{_professional_ming_shen_line(ziwei_section)} {_professional_axis_structure(ziwei_section)} {_professional_four_hua_line(ziwei_section)}",
            "紫微结论": (
                f"此盘若只看单宫，容易看散；若从命、官、财、福、夫妻、迁移一路串下来，"
                f"就会发现人生主轴始终被{basic['身宫所属宫位']}与四化流向牵着走。"
            ),
        },
        "融合判断": {
            "人生主轴": integrated.get("主轴", ""),
            "核心优势": f"优势不在花巧，而在官禄与命身主轴较清，做事能逐步立出自己的位置。{focus.get('官禄宫', '')}",
            "主要矛盾": f"主要矛盾往往不在外部机会少，而在福德与关系宫牵动内耗与取舍。{focus.get('福德宫', '')}",
            "事业判断": f"事业上宜走能立规矩、能担结果、能看长期的位置。{focus.get('官禄宫', '')}",
            "感情判断": f"感情上并非无情，而是有自己的秤。若节奏错了，关系就容易生拉扯。{focus.get('夫妻宫', '')}",
            "财运判断": f"财运不是偏一夜之财，更重路径与承接力。财星能不能落袋，要看人能不能稳住节奏。{focus.get('财帛宫', '')}",
            "盘面依据": "八字定底，命宫身宫定主线，三方四正看结构，四化再看应事落点。",
            "核心命理融合": integrated.get("融合引擎", {}).get("核心命理融合", {}),
            "总断": _professional_total_judgment(bazi, ziwei_section, integrated),
        },
        "大运与流年": {
            "当前大运": (
                f"当前走{dayun.get('干支', '待补')}运，主轴在“{dayun.get('主轴', '阶段调整')}”。"
                f" 这步运看似讲机会，实则更看你能不能把位置坐稳。"
            ),
            "这步运更容易起什么": "更容易起位置、责任、现实事务与长期结构问题，不是只起情绪或表面热闹。",
            "这步运最要防什么": "最要防方向反复、心气过急、位置未稳先求外扩。",
            "当前流年": (
                f"{annual.get('流年干支', '待补')}年主轴在“{annual.get('年度主轴', '阶段调整')}”。"
                f" 官杀之气或财官主题起来时，翻成白话，就是责任、位置、结果都会更压到眼前。"
            ),
            "机会点": annual.get("机会点", []),
            "风险点": annual.get("风险点", []),
            "年度重点": "这一年的重点，不是看热闹多不多，而是看哪些事情真正逼你做取舍、担结果。",
        },
        "趋避建议": guidance,
        "分析备注": "专业版以命理师口吻做结构判断，强调术语之后要能落白话，避免沦为逐宫念稿。",
    }


def _slice_professional_output(style_output: Dict[str, Any], focus: str) -> Dict[str, Any]:
    if focus == "full":
        return style_output

    spec = FOCUS_TOPIC_MAP[focus]
    ziwei_block = style_output["紫微斗数排盘"]
    topic_name = spec["topic"]
    linkage_name = spec["linkage"]
    topic_report = ziwei_block["专题拆盘"][topic_name]
    opening_map = {
        "career": "这一版只聚焦事业线，不展开感情与财运旁支，判断重点放在位置、职责、平台与长期承接。",
        "relationship": "这一版只聚焦感情线，不展开事业与财运旁支，判断重点放在关系节奏、现实条件与内在安全感。",
        "wealth": "这一版只聚焦财运线，不展开事业与感情旁支，判断重点放在路径、收口、守成与稳定结构。",
    }
    closing_map = {
        "career": "事业专题最终看的是，你能不能把机会接成位置，再把位置坐成长期结果。",
        "relationship": "感情专题最终看的是，关系能不能承受现实节奏，而不是只看一时热度。",
        "wealth": "财运专题最终看的是，机会能不能落袋并留住，而不是只看短期进账。",
    }
    return {
        "模式": style_output["模式"],
        "专题模式": focus,
        "当前专题": topic_name,
        "专题引言": opening_map[focus],
        "总起断": style_output["总起断"],
        "命盘信息": style_output["命盘信息"],
        "专题判断": style_output["融合判断"][spec["judgment"]],
        "专题拆盘": {topic_name: topic_report},
        "专题三段式": {linkage_name: ziwei_block["宫位联动三段式"][linkage_name]},
        "四化牵引": topic_report["四化牵引"],
        "当前大运切面": topic_report["当前大运切面"],
        "风险提示": topic_report["风险提示"],
        "趋避建议": {spec["guidance"]: style_output["趋避建议"][spec["guidance"]]},
        "专题收束": closing_map[focus],
        "分析备注": f"专业版当前按{topic_name}聚焦输出；底层仍按全盘计算，只收窄展示层。",
    }


def _build_style_output(
    mode: str,
    focus: str,
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    integrated: Dict[str, Any],
    zodiac: Dict[str, Any],
    mbti_result: Dict[str, Any],
    gender: str,
    place: str,
) -> Dict[str, Any]:
    if mode == "professional":
        return _slice_professional_output(
            _build_professional_mode_output(bazi, ziwei_section, integrated, gender, place),
            focus,
        )
    return _build_life_mode_output(bazi, ziwei_section, integrated, zodiac, mbti_result)


def _build_module_outputs(
    enabled_modules: List[str],
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    zodiac: Dict[str, Any],
    mbti_result: Dict[str, Any],
    blood_result: Dict[str, Any],
) -> Dict[str, Any]:
    outputs: Dict[str, Any] = {}
    if "bazi" in enabled_modules:
        outputs["八字命理"] = bazi
    if "ziwei" in enabled_modules:
        outputs["紫微斗数"] = ziwei_section
    if "mbti" in enabled_modules:
        outputs["MBTI"] = mbti_result or {"状态": "INPUT_REQUIRED", "说明": "未提供 MBTI，模块未参与有效判断。"}
    if "zodiac" in enabled_modules:
        outputs["星座"] = zodiac
    if "blood" in enabled_modules:
        outputs["血型"] = blood_result or {"状态": "INPUT_REQUIRED", "说明": "未提供血型，模块未参与有效判断。"}
    return outputs


def _build_single_module_output(
    enabled_modules: List[str],
    module_outputs: Dict[str, Any],
) -> Dict[str, Any]:
    personality_complement = build_personality_complement(
        enabled_modules,
        mbti=module_outputs.get("MBTI"),
        zodiac=module_outputs.get("星座"),
        blood=module_outputs.get("血型"),
    )
    return {
        "模式": "单项模块版",
        "启用模块": enabled_modules,
        "模块拆解": module_outputs,
        "人格补充画像": personality_complement if personality_complement.get("状态") == "OK" else None,
        "收束": "当前按用户指定模块输出，不强行做全盘融合；若启用人格模块，则作为行为、表达和相处节奏的补充画像。",
        "分析备注": "单项模块版适合只看紫微、八字、MBTI、星座或血型；不把未启用模块塞进正文。",
    }


def _build_routed_style_output(
    output_mode: str,
    enabled_modules: List[str],
    bazi: Dict[str, Any],
    ziwei_section: Dict[str, Any],
    integrated: Dict[str, Any],
    zodiac: Dict[str, Any],
    mbti_result: Dict[str, Any],
    blood_result: Dict[str, Any],
    fusion_report: Dict[str, Any],
    wenmo_chart: Dict[str, Any],
    wenmo_comparison: Dict[str, Any],
    mode: str,
    focus: str,
    gender: str,
    place: str,
) -> Dict[str, Any]:
    module_outputs = _build_module_outputs(enabled_modules, bazi, ziwei_section, zodiac, mbti_result, blood_result)
    core_enabled = {"bazi", "ziwei"}.issubset(set(enabled_modules))
    ziwei_only = enabled_modules == ["ziwei"]
    if ziwei_only and mode == "professional":
        return build_ziwei_professional_output(ziwei_section, wenmo_chart, wenmo_comparison)

    core_style = None
    if core_enabled:
        core_style = _build_style_output(mode, focus, bazi, ziwei_section, integrated, zodiac, mbti_result, gender, place)

    if output_mode == "auto":
        return core_style if core_style else _build_single_module_output(enabled_modules, module_outputs)

    if output_mode == "single":
        return _build_single_module_output(enabled_modules, module_outputs)

    if output_mode == "paired":
        if core_style:
            paired = dict(core_style)
            paired["模块拆解"] = module_outputs
            paired["分析备注"] = f"{paired.get('分析备注', '')} 当前为组合输出，底层模块按用户选择启用。".strip()
            return paired
        return _build_single_module_output(enabled_modules, module_outputs)

    return {
        "模式": "融合版",
        "融合画像": fusion_report,
        "命理主输出": core_style,
        "模块拆解": module_outputs,
        "收束": "融合版先用八字和紫微定结构，再用 MBTI、星座、血型解释行为和表达差异。",
        "分析备注": "融合版不会把所有模块简单相加，而是按权重与适用层级做分层解释。",
    }


def full_xiashensuan_analysis(
    birth_time: Dict[str, int],
    gender: str,
    place: str = DEFAULT_PLACE,
    longitude: float = DEFAULT_LONGITUDE,
    mode: str = DEFAULT_MODE,
    focus: str = DEFAULT_FOCUS,
    mbti: str = None,
    blood_type: str = None,
    modules: str = None,
    output_mode: str = "auto",
    wenmo_text: str = None,
    target_year: int = None,
    time_accuracy_minutes: int = 0,
    boundary_threshold_minutes: int = 15,
) -> Dict[str, Any]:
    """
    新版默认综合命理入口。

    八字与融合判断沿用旧版稳定能力；
    紫微默认接入新版文墨对齐模块。
    """
    normalized_mode = _normalize_mode(mode)
    normalized_focus = _normalize_focus(focus)
    route = build_route(
        raw_modules=modules,
        output_mode=output_mode,
        has_mbti=bool(mbti),
        has_blood_type=bool(blood_type),
    )
    enabled_modules = route["启用模块"]
    wenmo_chart = parse_wenmo_text(wenmo_text) if wenmo_text else None
    effective_longitude = longitude
    ziwei_birth_date = f"{birth_time['year']:04d}-{birth_time['month']:02d}-{birth_time['day']:02d}"
    ziwei_birth_time = f"{birth_time['hour']:02d}:{birth_time['minute']:02d}"
    ziwei_time_is_true_solar = False
    ziwei_time_source = "公历钟表时间+经度校正+时差方程"
    if wenmo_chart and wenmo_chart.get("基础信息", {}).get("真太阳时"):
        true_solar_standard = wenmo_chart["基础信息"].get("真太阳标准时间", "")
        true_solar_text = true_solar_standard or wenmo_chart["基础信息"]["真太阳时"]
        true_match = re.search(r"(\d{4})-(\d{1,2})-(\d{1,2})\s+(\d{1,2}):(\d{1,2})", true_solar_text)
        if true_match:
            ziwei_birth_date = f"{int(true_match.group(1)):04d}-{int(true_match.group(2)):02d}-{int(true_match.group(3)):02d}"
            ziwei_birth_time = f"{int(true_match.group(4)):02d}:{int(true_match.group(5)):02d}"
            effective_longitude = 120.0
            ziwei_time_is_true_solar = True
            ziwei_time_source = "文墨天机真太阳时原文"
    bazi = parse(birth_time, gender, longitude=longitude)
    if target_year is not None:
        bazi["大运骨架"] = get_dayun_analysis(birth_time, gender, target_year, longitude=longitude)
        bazi["流年骨架"] = get_flowyear_analysis(birth_time, gender, target_year, longitude=longitude)
    bazi = enhance_bazi_profile(bazi)

    zodiac = zodiac_analysis(birth_time["month"], birth_time["day"])
    mbti_result = None
    if "mbti" in enabled_modules:
        mbti_result = mbti_analysis(mbti) if mbti else {"状态": "INPUT_REQUIRED", "说明": "未提供 MBTI，模块未参与有效判断。"}
    blood_result = None
    if "blood" in enabled_modules:
        blood_result = blood_type_analysis(blood_type)

    ziwei_input = ZiweiInput(
        gender=gender,
        birth_date=ziwei_birth_date,
        birth_time=ziwei_birth_time,
        longitude=effective_longitude,
        place=place,
        time_accuracy_minutes=time_accuracy_minutes,
        boundary_threshold_minutes=boundary_threshold_minutes,
        time_is_true_solar=ziwei_time_is_true_solar,
    )
    ziwei_package = generate_ziwei_chart_with_boundary_support(ziwei_input)
    primary_chart = ziwei_package["primary_chart"]
    primary_chart["palace_map"] = _index_palaces(primary_chart["palaces"])

    integrated = build_integrated_profile(
        bazi,
        _build_legacy_compatible_ziwei(primary_chart),
        zodiac if "zodiac" in enabled_modules else None,
        mbti_result if mbti_result and mbti_result.get("状态") == "OK" else None,
    )
    ziwei_section = _build_ziwei_section(primary_chart)
    wenmo_comparison = compare_wenmo_with_ziwei(wenmo_chart, ziwei_section) if wenmo_chart else None
    fusion_report = build_fusion_report(
        enabled_modules,
        bazi=bazi if "bazi" in enabled_modules else None,
        ziwei=ziwei_section if "ziwei" in enabled_modules else None,
        mbti=mbti_result,
        zodiac=zodiac if "zodiac" in enabled_modules else None,
        blood=blood_result,
    )
    integrated_with_fusion = dict(integrated)
    integrated_with_fusion["融合引擎"] = fusion_report

    result = {
        "版本": {
            "主流程": "虾神算V2",
            "默认入口": DEFAULT_ENTRY,
            "默认状态": "DEFAULT_ACTIVE",
            "旧版入口": LEGACY_ENTRY,
            "旧版定位": "怀旧版/legacy",
            "紫微引擎": ZIWEI_ENGINE,
        },
        "输出架构": {
            "当前模式": normalized_mode,
            "当前模式名称": "生活版" if normalized_mode == "life" else "专业版",
            "默认模式": DEFAULT_MODE,
            "可用模式": ["life", "professional"],
            "当前专题焦点": normalized_focus,
            "可用专题焦点": ["full", "career", "relationship", "wealth"],
            "专题聚焦生效": normalized_mode == "professional" and normalized_focus != "full",
            "模块路由": route,
            "说明": "同一套盘面数据，按生活版或专业版两种风格输出；专业版可按专题焦点收窄展示层，模块路由决定最终展示层。",
        },
        "基础信息": {
            "出生时间": bazi["出生时间"],
            "农历": bazi["农历"],
            "性别": gender,
            "出生地": place,
            "经度": effective_longitude,
            "紫微时间来源": ziwei_time_source,
            "默认输入": "公历+钟表时间+出生地",
        },
        "八字命理": bazi,
        "紫微斗数": ziwei_section,
        "星座": zodiac,
        "融合判断": integrated_with_fusion,
        "模块输出": _build_module_outputs(enabled_modules, bazi, ziwei_section, zodiac, mbti_result, blood_result),
        "风格化输出": _build_routed_style_output(
            route["输出模式"],
            enabled_modules,
            bazi,
            ziwei_section,
            integrated_with_fusion,
            zodiac,
            mbti_result,
            blood_result,
            fusion_report,
            wenmo_chart,
            wenmo_comparison,
            normalized_mode,
            normalized_focus,
            gender,
            place,
        ),
    }
    if mbti_result:
        result["MBTI"] = mbti_result
    if blood_result:
        result["血型"] = blood_result
    if wenmo_chart:
        result["文墨文字盘"] = {
            "解析": wenmo_chart,
            "交叉校验": wenmo_comparison,
        }
    if ziwei_package["mode"] == "DOUBLE_CHART":
        result["边界双盘"] = ziwei_package
    return result


def _build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="虾神算 V2 默认综合命理入口")
    parser.add_argument("year", type=int, help="公历年")
    parser.add_argument("month", type=int, help="公历月")
    parser.add_argument("day", type=int, help="公历日")
    parser.add_argument("hour", type=int, help="钟表时（24小时）")
    parser.add_argument("--minute", type=int, default=0, help="钟表分")
    parser.add_argument("--gender", default="男", help="性别，默认男")
    parser.add_argument("--mode", default=DEFAULT_MODE, choices=["life", "professional"], help="输出模式，默认 life")
    parser.add_argument(
        "--focus",
        default=DEFAULT_FOCUS,
        help="专业版专题焦点，可选 full/career/relationship/wealth，默认 full",
    )
    parser.add_argument("--place", default=DEFAULT_PLACE, help="出生地，默认北京")
    parser.add_argument("--longitude", type=float, default=DEFAULT_LONGITUDE, help="出生地经度，默认116.4")
    parser.add_argument("--mbti", help="可选 MBTI 类型，例如 INTJ")
    parser.add_argument("--blood-type", help="可选血型，例如 A/B/O/AB")
    parser.add_argument("--modules", help="可选模块列表，例如 ziwei,bazi 或 mbti,zodiac,blood；也支持 core/personality/all")
    parser.add_argument("--wenmo-text-file", help="可选文墨天机文字盘文件路径，用于原盘解析和交叉校验")
    parser.add_argument(
        "--output-mode",
        default="auto",
        choices=["auto", "single", "paired", "fusion"],
        help="展示层模式：auto/single/paired/fusion，默认 auto",
    )
    parser.add_argument("--print-view", default="json", choices=["json", "report"], help="打印视图：json/report，默认 json")
    parser.add_argument("--target-year", type=int, default=datetime.now().year, help="可选目标流年")
    parser.add_argument("--time-accuracy-minutes", type=int, default=0, help="出生时间误差分钟数")
    parser.add_argument("--boundary-threshold-minutes", type=int, default=15, help="边界提醒阈值分钟数")
    return parser


def main() -> None:
    args = _build_parser().parse_args()
    birth_time = _build_birth_time(args.year, args.month, args.day, args.hour, args.minute)
    wenmo_text = None
    if args.wenmo_text_file:
        wenmo_text = Path(args.wenmo_text_file).read_text(encoding="utf-8")
    result = full_xiashensuan_analysis(
        birth_time=birth_time,
        gender=args.gender,
        place=args.place,
        longitude=args.longitude,
        mode=args.mode,
        focus=args.focus,
        mbti=args.mbti,
        blood_type=args.blood_type,
        modules=args.modules,
        output_mode=args.output_mode,
        wenmo_text=wenmo_text,
        target_year=args.target_year,
        time_accuracy_minutes=args.time_accuracy_minutes,
        boundary_threshold_minutes=args.boundary_threshold_minutes,
    )
    if args.print_view == "report":
        print(build_report_text(result), end="")
    else:
        print(json.dumps(result, ensure_ascii=False, indent=2))


if __name__ == "__main__":
    main()
