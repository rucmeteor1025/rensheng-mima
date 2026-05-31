"""Bazi calculation and professional enhancement layer."""

import math
from datetime import datetime, timedelta
from typing import Any, Dict, List, Tuple


EARTH_ROTATION_MIN_PER_DEGREE = 4
DEFAULT_LONGITUDE = 116.4

GAN_TO_WUXING = {
    "甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土",
    "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水",
}

GAN_YINYANG = {
    "甲": "阳", "丙": "阳", "戊": "阳", "庚": "阳", "壬": "阳",
    "乙": "阴", "丁": "阴", "己": "阴", "辛": "阴", "癸": "阴",
}

SHENG_REL = {"木": "火", "火": "土", "土": "金", "金": "水", "水": "木"}
KE_REL = {"木": "土", "火": "金", "土": "水", "金": "木", "水": "火"}

BRANCH_TO_WUXING = {
    "寅": "木", "卯": "木", "巳": "火", "午": "火",
    "申": "金", "酉": "金", "亥": "水", "子": "水",
    "辰": "土", "戌": "土", "丑": "土", "未": "土",
}

BRANCH_HIDDEN_STEMS = {
    "子": ["癸"],
    "丑": ["己", "癸", "辛"],
    "寅": ["甲", "丙", "戊"],
    "卯": ["乙"],
    "辰": ["戊", "乙", "癸"],
    "巳": ["丙", "戊", "庚"],
    "午": ["丁", "己"],
    "未": ["己", "丁", "乙"],
    "申": ["庚", "壬", "戊"],
    "酉": ["辛"],
    "戌": ["戊", "辛", "丁"],
    "亥": ["壬", "甲"],
}

HIDDEN_STEM_WEIGHTS = [0.6, 0.3, 0.1]
PILLAR_NAMES = ["年", "月", "日", "时"]

TEN_GOD_GROUP = {
    "比肩": "比劫",
    "劫财": "比劫",
    "食神": "食伤",
    "伤官": "食伤",
    "正财": "财星",
    "偏财": "财星",
    "正官": "官杀",
    "七杀": "官杀",
    "正印": "印星",
    "偏印": "印星",
    "日主": "日主",
}

GROUP_TOPIC = {
    "比劫": "自我意志、竞争关系、同辈协作与资源分配",
    "食伤": "表达输出、作品成果、技能释放与规则摩擦",
    "财星": "现实资源、钱财路径、经营交换与结果兑现",
    "官杀": "责任位置、规则压力、秩序建立与外部要求",
    "印星": "学习吸收、贵人支持、系统托底与恢复沉淀",
}


def _equation_of_time_minutes(dt: datetime) -> int:
    """近似计算时差方程（分钟），用于贴近文墨真太阳时口径。"""
    day_of_year = dt.timetuple().tm_yday
    b = math.radians((360 / 365) * (day_of_year - 81))
    eot = 9.87 * math.sin(2 * b) - 7.53 * math.cos(b) - 1.5 * math.sin(b)
    return round(eot)


def apply_true_solar_time(year, month, day, hour, minute=0, longitude=DEFAULT_LONGITUDE):
    """按经度 + 时差方程进行真太阳时近似校正。"""
    dt = datetime(year, month, day, hour, minute)
    longitude_delta = round((longitude - 120.0) * EARTH_ROTATION_MIN_PER_DEGREE)
    eot_delta = _equation_of_time_minutes(dt)
    delta_minutes = longitude_delta + eot_delta
    true_dt = dt + timedelta(minutes=delta_minutes)
    return {
        "input_datetime": dt,
        "longitude": longitude,
        "longitude_delta_minutes": longitude_delta,
        "equation_of_time_minutes": eot_delta,
        "delta_minutes": delta_minutes,
        "true_solar_datetime": true_dt,
        "true_solar_time": true_dt.strftime("%Y-%m-%d %H:%M"),
    }


def get_bazi(year, month, day, hour, minute=0, longitude=DEFAULT_LONGITUDE):
    """八字排盘（真太阳时校正版）。"""
    from lunar_python import Solar

    true_solar = apply_true_solar_time(year, month, day, hour, minute, longitude)
    true_dt = true_solar["true_solar_datetime"]
    solar = Solar(true_dt.year, true_dt.month, true_dt.day, true_dt.hour, true_dt.minute, 0)
    lunar = solar.getLunar()
    sz = lunar.getEightChar()

    day_gan = sz.getDay()[0]
    sz_hour = sz.getTime()
    bazi_text = f"{sz.getYear()} {sz.getMonth()} {sz.getDay()} {sz_hour}"

    wx = {"木": 0, "火": 0, "土": 0, "金": 0, "水": 0}
    for char in bazi_text.replace(" ", ""):
        if char in "甲乙寅卯":
            wx["木"] += 1
        elif char in "丙丁巳午":
            wx["火"] += 1
        elif char in "戊己辰戌丑未":
            wx["土"] += 1
        elif char in "庚辛申酉":
            wx["金"] += 1
        elif char in "壬癸亥子":
            wx["水"] += 1

    day_wuxing = GAN_TO_WUXING[day_gan]
    if wx[day_wuxing] >= 3:
        strength = "身强"
        yongshen = "官杀、财星"
    elif wx[day_wuxing] <= 1:
        strength = "身弱"
        yongshen = "印星、比劫"
    else:
        strength = "中和"
        yongshen = "平衡"

    char_map = {
        "甲": "正直有领导力", "乙": "柔和适应力强", "丙": "热情直接冲动",
        "丁": "温柔细腻", "戊": "稳重务实", "己": "忠厚包容",
        "庚": "刚毅果断", "辛": "追求完美", "壬": "聪明灵活变通", "癸": "浪漫温柔",
    }

    return {
        "八字": bazi_text,
        "四柱": {"年": sz.getYear(), "月": sz.getMonth(), "日": sz.getDay(), "时": sz_hour},
        "日主": {
            "日主": day_gan,
            "五行": day_wuxing,
            "身强弱": strength,
            "喜用神": yongshen,
        },
        "五行分布": wx,
        "性格": char_map.get(day_gan, "待分析"),
        "农历": f"{lunar.getYearInChinese()}年 {lunar.getMonthInChinese()}月 {lunar.getDayInChinese()}",
        "出生时间": f"{year}-{month:02d}-{day:02d} {hour:02d}:{minute:02d}",
        "真太阳时": true_solar["true_solar_time"],
        "时间校正": {
            "经度": longitude,
            "经度修正分钟": true_solar["longitude_delta_minutes"],
            "时差方程分钟": true_solar["equation_of_time_minutes"],
            "总校正分钟": true_solar["delta_minutes"],
        },
    }


def _broad_ten_god(day_gan: str, other_gan: str) -> str:
    dm = GAN_TO_WUXING[day_gan]
    ow = GAN_TO_WUXING[other_gan]
    if ow == dm:
        return "比劫"
    if SHENG_REL[dm] == ow:
        return "食伤"
    if KE_REL[dm] == ow:
        return "财星"
    if KE_REL[ow] == dm:
        return "官杀"
    if SHENG_REL[ow] == dm:
        return "印星"
    return "平"


def _year_focus_by_tengod(tengod: str) -> Dict[str, Any]:
    mapping = {
        "比劫": {
            "年度主轴": "自我意志、竞争关系、资源分配重新洗牌",
            "机会": ["适合主动争取机会", "适合重建人脉与合作边界"],
            "风险": ["容易因好胜或义气带来资源消耗", "合作关系里容易有分配矛盾"],
        },
        "食伤": {
            "年度主轴": "表达、输出、创意、项目落地",
            "机会": ["适合做内容、方案、产品、表达型工作", "适合把想法变现"],
            "风险": ["容易说多做少", "与规则、上级、制度产生摩擦"],
        },
        "财星": {
            "年度主轴": "财务、资源、交易、结果导向",
            "机会": ["更容易碰到钱和资源", "适合推进成交、经营、合作"],
            "风险": ["容易因钱和现实压力变大", "投资、支出、关系中的现实矛盾更明显"],
        },
        "官杀": {
            "年度主轴": "责任、位置、规则、压力、抬升",
            "机会": ["有机会拿位置、扛责任、做成事", "适合建立秩序和长期结构"],
            "风险": ["压力偏大", "容易情绪紧绷、关系变硬"],
        },
        "印星": {
            "年度主轴": "学习、恢复、支持、沉淀、修复",
            "机会": ["适合学习、考证、积累、修复状态", "适合借贵人和系统支持提升自己"],
            "风险": ["容易想得多、动得少", "可能保守、拖延、错过窗口"],
        },
    }
    return mapping.get(tengod, {"年度主轴": "平衡调整", "机会": [], "风险": []})


def get_dayun_analysis(birth_time, gender="男", target_year=None, longitude=DEFAULT_LONGITUDE):
    from lunar_python import Solar

    if target_year is None:
        target_year = datetime.now().year

    true_solar = apply_true_solar_time(
        birth_time.get("year"),
        birth_time.get("month"),
        birth_time.get("day"),
        birth_time.get("hour", 12),
        birth_time.get("minute", 0),
        longitude,
    )
    true_dt = true_solar["true_solar_datetime"]
    solar = Solar(true_dt.year, true_dt.month, true_dt.day, true_dt.hour, true_dt.minute, 0)
    lunar = solar.getLunar()
    ec = lunar.getEightChar()
    natal = get_bazi(
        birth_time.get("year"),
        birth_time.get("month"),
        birth_time.get("day"),
        birth_time.get("hour", 12),
        birth_time.get("minute", 0),
        longitude,
    )
    day_gan = natal["日主"]["日主"]
    is_male = 1 if gender == "男" else 0
    yun = ec.getYun(is_male)
    current_age = target_year - birth_time.get("year")

    dayun_list = yun.getDaYun()[1:]
    current_dayun = None
    for item in dayun_list:
        if item.getStartYear() <= target_year <= item.getEndYear():
            current_dayun = item
            break

    if current_dayun is None:
        if target_year < dayun_list[0].getStartYear():
            current_dayun = dayun_list[0]
        else:
            current_dayun = dayun_list[-1]

    dayun_gz = current_dayun.getGanZhi()
    ten_god = _broad_ten_god(day_gan, dayun_gz[0])
    focus = _year_focus_by_tengod(ten_god)
    return {
        "大运": dayun_gz,
        "起运": {
            "起运年": yun.getStartSolar().getYear(),
            "起运月": yun.getStartMonth(),
            "起运日": yun.getStartDay(),
            "起运公历": yun.getStartSolar().toYmdHms(),
        },
        "当前年龄": current_age,
        "当前大运": {
            "干支": dayun_gz,
            "起始年龄": current_dayun.getStartAge(),
            "结束年龄": current_dayun.getEndAge(),
            "起始年份": current_dayun.getStartYear(),
            "结束年份": current_dayun.getEndYear(),
            "十神": ten_god,
            "主轴": focus["年度主轴"],
            "机会点": focus["机会"],
            "风险点": focus["风险"],
        },
        "说明": "当前为八字大运骨架版，当前大运优先按底层库给出的起止年份判定，年龄仅作展示，不作为切运主依据。",
    }


def get_flowyear_analysis(birth_time, gender="男", target_year=None, longitude=DEFAULT_LONGITUDE):
    from lunar_python import Solar

    if target_year is None:
        target_year = datetime.now().year

    natal = get_bazi(
        birth_time.get("year"),
        birth_time.get("month"),
        birth_time.get("day"),
        birth_time.get("hour", 12),
        birth_time.get("minute", 0),
        longitude,
    )
    dayun = get_dayun_analysis(birth_time, gender, target_year, longitude)
    target_solar = Solar(target_year, 6, 30, 12, 0, 0)
    target_lunar = target_solar.getLunar()
    target_year_gz = target_lunar.getEightChar().getYear()
    year_gan = target_year_gz[0]
    year_zhi = target_year_gz[1]
    day_gan = natal["日主"]["日主"]
    ten_god = _broad_ten_god(day_gan, year_gan)
    focus = _year_focus_by_tengod(ten_god)

    relation_flags = []
    natal_branches = [natal["四柱"][k][1] for k in ["年", "月", "日", "时"]]
    if year_zhi in natal_branches:
        relation_flags.append("流年地支与原局重复，主题会被放大，事情更容易落到现实层面。")
    if year_gan == day_gan:
        relation_flags.append("流年天干与日主同气，自我意志、个人决定和主观能动性会更强。")
    if ten_god == dayun["当前大运"]["十神"]:
        relation_flags.append("流年十神与当前大运十神同向，年度主题会被进一步放大。")

    return {
        "流年": target_year,
        "流年干支": target_year_gz,
        "流年十神": ten_god,
        "当前大运": dayun["当前大运"]["干支"],
        "大运主轴": dayun["当前大运"]["主轴"],
        "年度主轴": focus["年度主轴"],
        "机会点": focus["机会"],
        "风险点": focus["风险"],
        "关系提示": relation_flags,
        "事业": "今年事业重点偏“%s”，当前大运主轴是“%s”，要看是顺势推进还是顺势守成。" % (focus["年度主轴"], dayun["当前大运"]["主轴"]),
        "财运": "若流年落财星/官杀主题，财更偏现实结果和资源兑现；若落比劫/食伤主题，需防钱来钱去、冲动投入。",
        "感情": "感情会受年度主轴牵动：财星/官杀年更偏现实落地，食伤/比劫年更容易因表达、边界和节奏起波动。",
        "说明": "当前为八字流年骨架版，已接入大运主轴，侧重阶段判断，不作为极细事件断语。",
    }


def parse(birth_time, gender="男", longitude=DEFAULT_LONGITUDE):
    """Build the base Bazi profile used by legacy and V2 flows."""
    result = get_bazi(
        birth_time.get("year"),
        birth_time.get("month"),
        birth_time.get("day"),
        birth_time.get("hour", 12),
        birth_time.get("minute", 0),
        longitude,
    )
    result["性别"] = gender

    dm = result["日主"]
    result["简批"] = {
        "核心": f"日主{dm['日主']}（{dm['五行']}），{dm['身强弱']}，喜{dm['喜用神']}",
        "性格": result["性格"],
    }
    result["大运骨架"] = get_dayun_analysis(birth_time, gender, longitude=longitude)
    result["流年骨架"] = get_flowyear_analysis(birth_time, gender, longitude=longitude)
    return result


def _split_pillar(pillar: str) -> Tuple[str, str]:
    text = (pillar or "").strip()
    if len(text) < 2:
        return "", ""
    return text[0], text[1]


def _generating_element(element: str) -> str:
    for source, target in SHENG_REL.items():
        if target == element:
            return source
    return ""


def _controlling_element(element: str) -> str:
    for source, target in KE_REL.items():
        if target == element:
            return source
    return ""


def exact_ten_god(day_gan: str, other_gan: str) -> str:
    """Return the precise ten-god name between day stem and another heavenly stem."""
    if not day_gan or not other_gan or day_gan not in GAN_TO_WUXING or other_gan not in GAN_TO_WUXING:
        return "待定"
    day_element = GAN_TO_WUXING[day_gan]
    other_element = GAN_TO_WUXING[other_gan]
    same_polarity = GAN_YINYANG[day_gan] == GAN_YINYANG[other_gan]

    if other_element == day_element:
        return "比肩" if same_polarity else "劫财"
    if SHENG_REL[day_element] == other_element:
        return "食神" if same_polarity else "伤官"
    if KE_REL[day_element] == other_element:
        return "偏财" if same_polarity else "正财"
    if KE_REL[other_element] == day_element:
        return "七杀" if same_polarity else "正官"
    if SHENG_REL[other_element] == day_element:
        return "偏印" if same_polarity else "正印"
    return "待定"


def _ten_god_group(ten_god: str) -> str:
    return TEN_GOD_GROUP.get(ten_god, "待定")


def _pillar_ten_gods(pillars: Dict[str, str], day_gan: str) -> Dict[str, Any]:
    heavenly = {}
    hidden = {}
    for name in PILLAR_NAMES:
        gan, branch = _split_pillar(pillars.get(name, ""))
        ten_god = "日主" if name == "日" else exact_ten_god(day_gan, gan)
        heavenly[name] = {
            "天干": gan,
            "五行": GAN_TO_WUXING.get(gan, ""),
            "阴阳": GAN_YINYANG.get(gan, ""),
            "十神": ten_god,
            "十神组": _ten_god_group(ten_god),
        }
        hidden_items = []
        for idx, stem in enumerate(BRANCH_HIDDEN_STEMS.get(branch, [])):
            hidden_ten_god = exact_ten_god(day_gan, stem)
            hidden_items.append(
                {
                    "藏干": stem,
                    "五行": GAN_TO_WUXING.get(stem, ""),
                    "权重": HIDDEN_STEM_WEIGHTS[idx] if idx < len(HIDDEN_STEM_WEIGHTS) else 0.1,
                    "十神": hidden_ten_god,
                    "十神组": _ten_god_group(hidden_ten_god),
                }
            )
        hidden[name] = {
            "地支": branch,
            "主气五行": BRANCH_TO_WUXING.get(branch, ""),
            "藏干": hidden_items,
        }
    return {"天干十神": heavenly, "地支藏干十神": hidden}


def _weighted_wuxing(pillars: Dict[str, str]) -> Dict[str, Any]:
    scores = {"木": 0.0, "火": 0.0, "土": 0.0, "金": 0.0, "水": 0.0}
    for pillar in pillars.values():
        gan, branch = _split_pillar(pillar)
        if gan in GAN_TO_WUXING:
            scores[GAN_TO_WUXING[gan]] += 1.0
        for idx, stem in enumerate(BRANCH_HIDDEN_STEMS.get(branch, [])):
            weight = HIDDEN_STEM_WEIGHTS[idx] if idx < len(HIDDEN_STEM_WEIGHTS) else 0.1
            if stem in GAN_TO_WUXING:
                scores[GAN_TO_WUXING[stem]] += weight

    ranked = sorted(scores.items(), key=lambda item: item[1], reverse=True)
    rounded = {key: round(value, 2) for key, value in scores.items()}
    return {
        "加权五行": rounded,
        "最旺": ranked[0][0] if ranked else "",
        "最弱": ranked[-1][0] if ranked else "",
        "说明": "天干按 1.0 计，地支藏干按主气/中气/余气加权，作为结构参考，不替代人工格局细判。",
    }


def _season_support(pillars: Dict[str, str], day_element: str) -> Dict[str, str]:
    month_branch = _split_pillar(pillars.get("月", ""))[1]
    month_element = BRANCH_TO_WUXING.get(month_branch, "")
    if not month_branch or not month_element:
        relation = "待定"
        description = "月令资料不足，暂不强断得令。"
    elif month_element == day_element:
        relation = "得令"
        description = "月令与日主同气，日主根气有力。"
    elif SHENG_REL.get(month_element) == day_element:
        relation = "得生"
        description = "月令生扶日主，命局有印气托底。"
    elif SHENG_REL.get(day_element) == month_element:
        relation = "泄气"
        description = "日主生月令，气容易向表达、输出或事务消耗处走。"
    elif KE_REL.get(day_element) == month_element:
        relation = "耗气"
        description = "日主克月令，现实资源与财务交换会牵动精力。"
    elif KE_REL.get(month_element) == day_element:
        relation = "受制"
        description = "月令克日主，外部规则、压力或责任感较早压到身上。"
    else:
        relation = "平衡"
        description = "月令与日主不构成单边强弱，需回看全局通关。"

    return {
        "月支": month_branch,
        "月令五行": month_element,
        "与日主关系": relation,
        "判断": description,
    }


def _strength_assessment(bazi: Dict[str, Any], weighted: Dict[str, Any], season: Dict[str, str]) -> Dict[str, Any]:
    day = bazi.get("日主", {})
    day_element = day.get("五行", "")
    scores = weighted.get("加权五行", {})
    total = sum(scores.values()) or 1.0
    self_score = scores.get(day_element, 0)
    support_score = scores.get(_generating_element(day_element), 0)
    output_score = scores.get(SHENG_REL.get(day_element, ""), 0)
    wealth_score = scores.get(KE_REL.get(day_element, ""), 0)
    officer_score = scores.get(_controlling_element(day_element), 0)
    support_ratio = round((self_score + support_score) / total, 3)
    pressure_ratio = round((output_score + wealth_score + officer_score) / total, 3)

    season_relation = season.get("与日主关系")
    if season_relation in {"得令", "得生"}:
        structured = "偏强" if support_ratio >= 0.42 else "中和偏强"
    elif season_relation in {"泄气", "耗气", "受制"}:
        if support_ratio <= 0.34 or pressure_ratio >= support_ratio * 0.95:
            structured = "偏弱"
        else:
            structured = "中和偏弱"
    elif support_ratio >= 0.52:
        structured = "偏强"
    elif support_ratio <= 0.32:
        structured = "偏弱"
    else:
        structured = "中和"

    return {
        "原始判断": day.get("身强弱", ""),
        "结构判断": structured,
        "扶身比例": support_ratio,
        "耗泄克比例": pressure_ratio,
        "依据": [
            f"日主五行{day_element}，自党得分 {round(self_score, 2)}，生扶得分 {round(support_score, 2)}。",
            f"输出得分 {round(output_score, 2)}，财星得分 {round(wealth_score, 2)}，官杀得分 {round(officer_score, 2)}。",
            season.get("判断", ""),
        ],
        "说明": "结构判断用于提升专业表达；旧字段保留原始简判，避免破坏既有调用。",
    }


def _useful_god_strategy(day: Dict[str, Any], strength: Dict[str, Any]) -> Dict[str, Any]:
    old_strength = day.get("身强弱", "")
    structured = strength.get("结构判断", "")
    base = old_strength or structured
    if "强" in base or structured == "偏强":
        strategy = "宜用财官食伤疏导与成事，重点在把自身力量导向责任、结果与输出。"
        avoid = "忌比劫再旺而争夺资源，也忌只凭主观硬推。"
    elif "弱" in base or structured == "偏弱":
        strategy = "宜用印比扶身，重点在学习、系统支持、贵人托底与自我恢复。"
        avoid = "忌财官压力过早压身，未稳先扩容易透支。"
    else:
        strategy = "宜先取平衡，随大运流年决定是扶身、泄秀还是承财官。"
        avoid = "忌把单一喜忌用到底，阶段不同取法应不同。"

    return {
        "原始喜用": day.get("喜用神", ""),
        "结构取向": strategy,
        "忌讳": avoid,
        "边界": "喜用神先按旺衰和月令取大方向；特殊格局、调候、通关仍需结合全盘人工校验。",
    }


def _topic_mapping(ten_gods: Dict[str, Any], strength: Dict[str, Any]) -> Dict[str, str]:
    heavenly = ten_gods.get("天干十神", {})
    groups = []
    for item in heavenly.values():
        group = item.get("十神组")
        if group and group not in {"日主", "待定"} and group not in groups:
            groups.append(group)
    group_text = "、".join(groups) if groups else "待结合藏干与大运"
    return {
        "事业": f"事业先看官杀、印星与食伤的组合；当前明透十神见{group_text}，再结合紫微官禄宫定具体路径。",
        "财运": "财运先看财星是否能被日主承接，再看官禄路径是否能把资源落袋。",
        "感情": "感情不只看财官，还要看日主强弱能否承压，以及现实责任是否过早介入关系。",
        "状态": f"状态看扶身比例与月令关系；当前结构判断为{strength.get('结构判断', '待定')}，先处理精力承接。",
    }


def _strength_category(strength: Dict[str, Any]) -> str:
    label = strength.get("结构判断", "")
    if "强" in label:
        return "strong"
    if "弱" in label:
        return "weak"
    return "balanced"


def _group_scores(ten_gods: Dict[str, Any]) -> Dict[str, float]:
    scores: Dict[str, float] = {}
    for item in ten_gods.get("天干十神", {}).values():
        group = item.get("十神组")
        if group and group not in {"日主", "待定"}:
            scores[group] = scores.get(group, 0.0) + 1.0
    for branch in ten_gods.get("地支藏干十神", {}).values():
        for item in branch.get("藏干", []):
            group = item.get("十神组")
            if group and group not in {"日主", "待定"}:
                scores[group] = scores.get(group, 0.0) + float(item.get("权重", 0.0))
    return {key: round(value, 2) for key, value in sorted(scores.items(), key=lambda item: item[1], reverse=True)}


def _dominant_groups_text(group_scores: Dict[str, float]) -> str:
    if not group_scores:
        return "十神主轴待结合大运细看"
    names = list(group_scores.keys())[:3]
    return "、".join(f"{name}{group_scores[name]}" for name in names)


def _body_block(evidence: str, judgment: str, advice: str) -> Dict[str, str]:
    return {
        "盘面依据": evidence,
        "判断": judgment,
        "建议": advice,
    }


def _strength_body(day: Dict[str, Any], strength: Dict[str, Any], useful: Dict[str, Any], season: Dict[str, Any]) -> Dict[str, str]:
    day_text = f"{day.get('日主', '')}{day.get('五行', '')}".strip() or "日主待定"
    category = _strength_category(strength)
    evidence = (
        f"{day_text}，月令关系为{season.get('与日主关系', '待定')}；"
        f"扶身比例{strength.get('扶身比例', '待定')}，耗泄克比例{strength.get('耗泄克比例', '待定')}。"
    )
    if category == "strong":
        judgment = "命局底气不薄，成事不怕担事，真正的问题在于力量要有出口，不能只靠主观硬推。"
    elif category == "weak":
        judgment = "命局更看环境、系统与支持，先稳住底盘，再谈扩张，越急越容易透支。"
    else:
        judgment = "命局不走极端，成败更看阶段节奏、取舍顺序和外部位置是否配合。"
    return _body_block(evidence, judgment, useful.get("结构取向", "先按结构取向调平，再结合大运看取舍。"))


def _ten_god_body(group_scores: Dict[str, float], ten_gods: Dict[str, Any]) -> Dict[str, str]:
    heavenly = ten_gods.get("天干十神", {})
    heavenly_text = "、".join(
        f"{pillar}{item.get('天干', '')}{item.get('十神', '')}"
        for pillar, item in heavenly.items()
        if item.get("十神") and item.get("十神") != "日主"
    ) or "天干透出不明显"
    dominant = _dominant_groups_text(group_scores)
    top_group = next(iter(group_scores), "")
    if top_group == "官杀":
        judgment = "主轴偏责任、规则、位置与压力承接，适合在有秩序、有考核、有长期结果的结构里成事。"
    elif top_group == "财星":
        judgment = "主轴偏资源、现实、经营与兑现，做判断时容易先被结果、成本和收益牵引。"
    elif top_group == "食伤":
        judgment = "主轴偏表达、输出、技术和作品，优势在把能力释放出来，但要防和规则硬碰。"
    elif top_group == "印星":
        judgment = "主轴偏学习、吸收、托底和恢复，越有系统支持，越容易把能力沉淀成长期资产。"
    elif top_group == "比劫":
        judgment = "主轴偏自我意志、竞争和同辈关系，靠心气能起势，但也要防资源分散和意气用事。"
    else:
        judgment = "十神主轴不单边，不能只抓一个标签，要结合旺衰、大运和现实场景判断。"
    return _body_block(
        f"天干见{heavenly_text}；十神组加权主轴为{dominant}。",
        judgment,
        "十神只定问题类型，不直接断吉凶；要把它落到事业、关系、财务和状态的具体场景里看。",
    )


def _career_wealth_body(topics: Dict[str, str], strength: Dict[str, Any], useful: Dict[str, Any]) -> Dict[str, str]:
    category = _strength_category(strength)
    if category == "strong":
        judgment = "事业财运宜把自身能力导向责任、结果和输出，越能建立规则与交付闭环，越容易见成果。"
    elif category == "weak":
        judgment = "事业财运不宜未稳先扩，先找平台、资质、贵人与稳定现金流，再谈更大的承担。"
    else:
        judgment = "事业财运重在平衡节奏，适合边做边校准，不宜一条路径押到底。"
    return _body_block(
        f"{topics.get('事业', '')} {topics.get('财运', '')}".strip(),
        judgment,
        useful.get("结构取向", "先按命局承接能力安排事业与财务节奏。"),
    )


def _relationship_body(topics: Dict[str, str], strength: Dict[str, Any]) -> Dict[str, str]:
    category = _strength_category(strength)
    if category == "strong":
        judgment = "关系里容易有主见，也容易把现实标准放得比较重；适合找能共同承担、边界清楚的人。"
        advice = "少用控制感换安全感，把规则说清楚，比反复试探更有利。"
    elif category == "weak":
        judgment = "关系里更需要被承托和稳定回应，若现实压力过早压进关系，容易先耗状态。"
        advice = "先看对方是否能给稳定支持，不要只被短期热度或现实条件牵着走。"
    else:
        judgment = "关系成败不在单一强弱，而在双方节奏、责任分配和情绪恢复能力是否协调。"
        advice = "遇到关系拉扯时，先分清是情绪问题、现实问题，还是责任边界问题。"
    return _body_block(topics.get("感情", "感情需结合财官、旺衰与现实责任同看。"), judgment, advice)


def _health_body(topics: Dict[str, str], weighted: Dict[str, Any], strength: Dict[str, Any]) -> Dict[str, str]:
    weakest = weighted.get("最弱", "待定")
    strongest = weighted.get("最旺", "待定")
    category = _strength_category(strength)
    if category == "strong":
        judgment = "状态问题多半不是扛不住，而是长期绷着、消耗过重，容易把压力压成身体反应。"
    elif category == "weak":
        judgment = "状态问题更怕连续透支，恢复、睡眠、饮食和支持系统比短期冲刺更重要。"
    else:
        judgment = "状态起伏多与节奏有关，工作、情绪和身体不能长期失衡。"
    return _body_block(
        f"五行最旺为{strongest}，最弱为{weakest}；{topics.get('状态', '')}",
        judgment,
        "健康相关只做命理倾向参考；若有具体不适，应以专业医疗检查和医生意见为准。",
    )


def _dayun_body(bazi: Dict[str, Any]) -> Dict[str, str]:
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    annual = bazi.get("流年骨架", {})
    evidence = (
        f"当前大运{dayun.get('干支', '待补')}，主轴为{dayun.get('主轴', '阶段调整')}；"
        f"当前流年{annual.get('流年干支', '待补')}，年度主轴为{annual.get('年度主轴', '阶段主题')}。"
    )
    judgment = "大运看十年左右的承压方向，流年只做阶段主题提示，不直接扩写成具体事件。"
    advice = "先把大运主轴当作阶段策略，再结合现实选择验证；未做历史事件校准前，不把流年写成确定事件。"
    return _body_block(evidence, judgment, advice)


def build_bazi_body_analysis(
    bazi: Dict[str, Any],
    ten_gods: Dict[str, Any],
    weighted: Dict[str, Any],
    season: Dict[str, Any],
    strength: Dict[str, Any],
    useful: Dict[str, Any],
    topics: Dict[str, str],
) -> Dict[str, Any]:
    day = bazi.get("日主", {})
    group_scores = _group_scores(ten_gods)
    day_text = f"{day.get('日主', '')}{day.get('五行', '')}".strip() or "日主待定"
    return {
        "专业正文口径": {
            "主判断来源": "节气四柱、日主旺衰、月令得气、精细十神、地支藏干、五行强度与大运骨架。",
            "输出边界": "八字正文用于判断底层气势、承接能力与主题倾向；流年仍为阶段主题提示，不做具体事件断语。",
            "融合定位": "八字定气势与承接能力；紫微斗数定宫位落点与人生场景。",
        },
        "命局总论": _body_block(
            f"四柱为{bazi.get('八字', '待补')}；{day_text}日主，结构判断为{strength.get('结构判断', '待定')}；十神主轴为{_dominant_groups_text(group_scores)}。",
            "这张八字先看日主能不能承接，再看十神把力推到哪里；不宜只用身强身弱一句话收掉。",
            useful.get("结构取向", "先稳住命局主轴，再结合大运决定取舍。"),
        ),
        "日主旺衰": _strength_body(day, strength, useful, season),
        "十神主轴": _ten_god_body(group_scores, ten_gods),
        "事业财运": _career_wealth_body(topics, strength, useful),
        "感情婚姻": _relationship_body(topics, strength),
        "健康状态": _health_body(topics, weighted, strength),
        "大运阶段": _dayun_body(bazi),
    }


def build_bazi_professional_profile(bazi: Dict[str, Any]) -> Dict[str, Any]:
    pillars = bazi.get("四柱", {})
    day_gan = bazi.get("日主", {}).get("日主", "")
    day_element = bazi.get("日主", {}).get("五行", "")
    ten_gods = _pillar_ten_gods(pillars, day_gan)
    weighted = _weighted_wuxing(pillars)
    season = _season_support(pillars, day_element)
    strength = _strength_assessment(bazi, weighted, season)
    useful = _useful_god_strategy(bazi.get("日主", {}), strength)
    topics = _topic_mapping(ten_gods, strength)
    body = build_bazi_body_analysis(bazi, ten_gods, weighted, season, strength, useful, topics)

    return {
        "版本": "bazi-professional-v1",
        "排盘口径": {
            "历法": "默认公历钟表时间输入，由 lunar_python 按节气四柱排盘。",
            "保留字段": "旧版八字、日主、五行分布、简批、大运骨架、流年骨架均保留。",
            "增强字段": "新增精细十神、地支藏干、加权五行、月令得气、旺衰依据与用神策略。",
        },
        "四柱": pillars,
        "日主": bazi.get("日主", {}),
        "十神明细": ten_gods,
        "五行强度": weighted,
        "月令得气": season,
        "旺衰判断": strength,
        "用神策略": useful,
        "专题映射": topics,
        "正文分析": body,
        "准确边界": "四柱排盘可程序化校验；旺衰、格局、调候、通关属于专业判断层，当前先给结构化依据，不做未经校准的绝对断语。",
    }


def build_bazi_fusion_interface(bazi: Dict[str, Any], professional: Dict[str, Any]) -> Dict[str, Any]:
    day = bazi.get("日主", {})
    strength = professional.get("旺衰判断", {})
    useful = professional.get("用神策略", {})
    dayun = bazi.get("大运骨架", {}).get("当前大运", {})
    annual = bazi.get("流年骨架", {})
    return {
        "状态": "OK",
        "核心权重建议": 0.5,
        "负责层级": "底层气势、五行旺衰、十神结构、大运主轴与现实承压能力。",
        "口径优先级": "报告与融合优先使用专业分析；旧日主、喜用神等字段仅作基础排盘和兼容兜底。",
        "主轴摘要": (
            f"日主{day.get('日主', '')}{day.get('五行', '')}，"
            f"结构判断{strength.get('结构判断', '')}（旧版简判：{day.get('身强弱', '')}）；"
            f"当前大运主轴为{dayun.get('主轴', '待补')}。"
        ),
        "融合抓手": [
            "用八字定底层气势与喜忌方向。",
            "用紫微定人生宫位结构、命身主轴与四化落点。",
            "两者一致时提高结论置信；两者冲突时，八字定承压能力，紫微定应事场景。",
        ],
        "风险边界": useful.get("边界", ""),
        "当前阶段": {
            "大运": dayun,
            "流年": {
                "干支": annual.get("流年干支", ""),
                "主轴": annual.get("年度主轴", ""),
                "说明": "八字流年仍为阶段主题提示，不做具体事件断语。",
            },
        },
    }


def enhance_bazi_profile(bazi: Dict[str, Any]) -> Dict[str, Any]:
    """Attach professional Bazi structures while preserving legacy fields."""
    result = dict(bazi)
    professional = build_bazi_professional_profile(result)
    result["专业分析"] = professional
    result["融合接口"] = build_bazi_fusion_interface(result, professional)
    return result
