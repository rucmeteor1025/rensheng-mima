"""Professional Ziwei renderer."""

from typing import Any, Dict, List


KEY_PALACES = ["命宫", "身宫", "官禄宫", "财帛宫", "夫妻宫", "福德宫", "迁移宫", "疾厄宫"]

STAR_THEMES = {
    "紫微": "主导、统筹、责任、格局",
    "天机": "学习、机变、策划、思考",
    "太阳": "外放、名声、照拂、行动",
    "武曲": "执行、财务、纪律、硬实力",
    "天同": "人和、安适、情绪、福气",
    "廉贞": "原则、边界、审美、秩序",
    "天府": "稳定、库藏、承接、组织",
    "太阴": "细腻、积累、资源、感受",
    "贪狼": "表达、欲望、人缘、才艺",
    "巨门": "辨析、表达、口舌、质疑",
    "天相": "协调、体面、制度、辅助",
    "天梁": "庇护、原则、长辈、修正",
    "七杀": "突破、决断、压力、竞争",
    "破军": "变革、破旧、重组、冒险",
    "文昌": "学习、表达、考试、文书",
    "文曲": "表达、审美、才艺、细节",
    "左辅": "助力、配合、贵人、补位",
    "右弼": "助力、协调、贵人、补位",
    "天魁": "提携、机会、贵助、抬举",
    "天钺": "提携、机会、贵助、抬举",
    "禄存": "资源、守成、积累、稳定",
    "天马": "流动、奔波、迁移、变化",
    "擎羊": "冲突、锋芒、压力、破耗",
    "陀罗": "拖延、牵扯、阻滞、慢耗",
    "火星": "急迫、爆发、突发、火气",
    "铃星": "警讯、焦躁、突发、反复",
    "地空": "落空、抽离、取舍、虚耗",
    "地劫": "损耗、断裂、破财、取舍",
    "红鸾": "缘分、喜气、人缘、感受",
    "天喜": "喜庆、助缘、活络、人和",
    "天贵": "抬举、贵助、机会、体面",
    "恩光": "照拂、善缘、缓冲、润泽",
    "三台": "阶梯、抬升、次第、助推",
    "八座": "承托、体面、稳定、座次",
    "台辅": "辅助、托举、协作、补位",
    "凤阁": "文采、仪态、表达、审美",
    "天姚": "魅力、人缘、活跃、吸引",
    "天福": "福分、缓和、照应、安定",
    "天官": "名分、规制、职位、体面",
    "封诰": "认可、名分、资质、文书",
    "天寿": "持久、耐性、积累、修养",
}

PALACE_TOPICS = {
    "命宫": "性格底色、自我定位与人生起手式",
    "兄弟宫": "同辈、同学、伙伴与竞争关系",
    "夫妻宫": "亲密关系、婚恋取向与深度合作",
    "子女宫": "作品、表达、后续结果与照顾责任",
    "财帛宫": "钱财路径、资源落袋与现实承接",
    "疾厄宫": "身体反应、压力承接与消耗模式",
    "迁移宫": "外部环境、出行迁动与平台变化",
    "交友宫": "圈层、人脉、团队与外部资源",
    "官禄宫": "学业事业、职责位置与成事路径",
    "田宅宫": "家庭空间、资产稳定与安全感",
    "福德宫": "精神状态、心气、内耗与幸福感",
    "父母宫": "长辈、规则、支持系统与上级缘分",
}

HUA_MEANINGS = {
    "禄": "资源入口、机会与顺手处",
    "权": "责任、掌控、压力与必须出面处",
    "科": "名声、认可、文书与缓冲处",
    "忌": "牵扯、代价、心结与反复处",
}


def _palace_map(ziwei_section: Dict[str, Any]) -> Dict[str, Dict[str, Any]]:
    return {palace["宫位"]: palace for palace in ziwei_section.get("十二宫", [])}


def _stars(palace: Dict[str, Any]) -> str:
    stars = palace.get("主星", []) + palace.get("辅星", [])
    return "、".join(stars) if stars else "空宫待参"


def _theme_words(stars: List[str], limit: int = 6) -> str:
    words: List[str] = []
    for star in stars:
        for word in STAR_THEMES.get(star, "").split("、"):
            if word and word not in words:
                words.append(word)
    return "、".join(words[:limit]) if words else "待结合全盘细参"


def _palace_theme(palace: Dict[str, Any]) -> str:
    return _theme_words(palace.get("主星", []) + palace.get("辅星", []))


def _palace_line(palace: Dict[str, Any]) -> str:
    hua = palace.get("四化", [])
    hua_text = ""
    if hua:
        hua_text = "；四化：" + "、".join(f"{item.get('星曜')}化{item.get('化')}" for item in hua)
    shen_text = "；身宫在此" if palace.get("身宫") else ""
    return f"{palace.get('宫位')}在{palace.get('宫支')}，见{_stars(palace)}{hua_text}{shen_text}。"


def _palace_evidence(palaces: Dict[str, Dict[str, Any]], palace_name: str) -> str:
    palace = palaces.get(palace_name)
    if not palace:
        return f"{palace_name}资料待补。"
    return (
        f"{palace_name}：{_palace_line(palace)}"
        f"关键词为{_palace_theme(palace)}，主看{PALACE_TOPICS.get(palace_name, '该宫主题')}。"
    )


def _domain_block(
    palaces: Dict[str, Dict[str, Any]],
    evidence_palaces: List[str],
    judgment: str,
    advice: str,
) -> Dict[str, Any]:
    return {
        "盘面依据": [_palace_evidence(palaces, name) for name in evidence_palaces],
        "判断": judgment,
        "建议": advice,
    }


def _four_hua_line(ziwei_section: Dict[str, Any]) -> str:
    four_hua = ziwei_section.get("四化", {})
    if not four_hua:
        return "四化线索待补。"
    return "、".join(
        f"{detail.get('星曜')}化{name}落{detail.get('宫支')}，状态{detail.get('状态')}"
        for name, detail in four_hua.items()
    )


def _four_hua_target_lines(ziwei_section: Dict[str, Any]) -> List[str]:
    branch_map = {palace.get("宫支"): palace.get("宫位") for palace in ziwei_section.get("十二宫", [])}
    lines = []
    for hua_name in ["禄", "权", "科", "忌"]:
        detail = ziwei_section.get("四化", {}).get(hua_name, {})
        star = detail.get("星曜", "")
        palace_name = branch_map.get(detail.get("宫支"), detail.get("宫支", "待定"))
        if star:
            lines.append(f"{star}化{hua_name}落{palace_name}，主{HUA_MEANINGS.get(hua_name, '应事线索')}。")
    return lines


def _palace_reading(palace: Dict[str, Any]) -> str:
    palace_name = palace.get("宫位", "该宫")
    return (
        f"{palace_name}见{_stars(palace)}，主题偏{_palace_theme(palace)}，"
        f"对应{PALACE_TOPICS.get(palace_name, '该宫主题')}。"
    )


def _line_for_palace(palaces: Dict[str, Dict[str, Any]], palace_name: str) -> str:
    palace = palaces.get(palace_name)
    if not palace:
        return f"{palace_name}资料待补。"
    return _palace_reading(palace)


def _key_palace_lines(ziwei_section: Dict[str, Any]) -> List[str]:
    palaces = _palace_map(ziwei_section)
    basic = ziwei_section.get("基础信息", {})
    lines = []
    for name in KEY_PALACES:
        if name == "身宫":
            shen_role = basic.get("身宫所属宫位", "")
            palace = palaces.get(shen_role)
            if palace:
                lines.append(f"身宫落{shen_role}：{_palace_line(palace)}")
            continue
        palace = palaces.get(name)
        if palace:
            lines.append(_palace_line(palace))
    return lines


def _stage_reminders(wenmo_chart: Dict[str, Any]) -> Dict[str, Any]:
    if not wenmo_chart or wenmo_chart.get("状态") != "OK":
        return {
            "置信等级": "低（结构提示）：当前未接入可解析的大限文字盘，不做流年事件判断。",
            "说明": "当前未接入可解析的大限文字盘，阶段判断先以命身、官财福夫妻迁移主轴为准。",
        }

    wenmo_palaces = wenmo_chart.get("十二宫", {})
    liunian_age_map = _liunian_age_map(wenmo_palaces)
    reminders = []
    theme_index: Dict[str, List[str]] = {}
    for item in wenmo_chart.get("大限序列", [])[:8]:
        palace_name = item.get("宫位", "")
        age = item.get("年龄", "")
        palace = wenmo_palaces.get(palace_name, {})
        stars = "、".join(palace.get("主星", []) + palace.get("辅星", [])) or "空宫待参"
        liunian = palace.get("流年", [])
        liunian_text = f"；该宫重复触发年龄可关注 {', '.join(str(num) for num in liunian[:5])} 虚岁" if liunian else ""
        reminders.append(
            f"{age}走{palace_name}，主{PALACE_TOPICS.get(palace_name, '该宫主题')}；盘面见{stars}{liunian_text}。"
        )
        theme_index[f"{age}（{palace_name}）"] = _liunian_lines_for_range(
            item.get("起始年龄"),
            item.get("结束年龄"),
            liunian_age_map,
            wenmo_palaces,
        )

    return {
        "置信等级": "低（结构提示）：仅根据文墨文字盘的大限宫位与流年落宫生成，用来定位年份主题，不做吉凶与具体事件判断。",
        "前八步大限": reminders,
        "流年主题索引": theme_index,
        "说明": "这里先按文墨文字盘提供的大限宫位、宫内星曜和流年落宫做主题索引；若要精确到事件性质，仍需补齐大限四化、流年四化、流月流日或真实事件校准。",
    }


def _liunian_age_map(wenmo_palaces: Dict[str, Dict[str, Any]]) -> Dict[int, str]:
    age_map: Dict[int, str] = {}
    for palace_name, palace in wenmo_palaces.items():
        for age in palace.get("流年", []):
            if isinstance(age, int):
                age_map[age] = palace_name
    return age_map


def _liunian_lines_for_range(
    start_age: int,
    end_age: int,
    age_map: Dict[int, str],
    wenmo_palaces: Dict[str, Dict[str, Any]],
) -> List[str]:
    if not isinstance(start_age, int) or not isinstance(end_age, int):
        return ["该步大限缺少起止年龄，暂不展开逐岁流年。"]

    lines = []
    missing_count = 0
    for age in range(start_age, end_age + 1):
        palace_name = age_map.get(age, "")
        if not palace_name:
            missing_count += 1
            continue
        palace = wenmo_palaces.get(palace_name, {})
        stars = "、".join(palace.get("主星", []) + palace.get("辅星", [])) or "空宫待参"
        lines.append(
            f"{age}虚岁：主题落{palace_name}，提示关注{PALACE_TOPICS.get(palace_name, '该宫主题')}；盘面见{stars}。"
        )

    if missing_count:
        lines.append(f"该步大限另有 {missing_count} 个年龄未在当前文字盘流年字段中列出，暂不强行细断。")
    if not lines:
        lines.append(f"{start_age}~{end_age}虚岁：当前文字盘未提供该段逐岁流年宫位。")
    return lines


def _body_analysis(ziwei_section: Dict[str, Any], wenmo_chart: Dict[str, Any] = None) -> Dict[str, Any]:
    palaces = _palace_map(ziwei_section)
    basic = ziwei_section.get("基础信息", {})
    ming = palaces.get("命宫", {})
    shen_role = basic.get("身宫所属宫位", "")
    shen = palaces.get(shen_role, {})
    hua_lines = _four_hua_target_lines(ziwei_section)
    hua_text = " ".join(hua_lines) if hua_lines else "四化落点待补。"

    return {
        "专业正文口径": {
            "阅读顺序": [
                "先以命宫定性格底色，再以身宫定现实发力点。",
                "专题判断以本命宫位、三方联动和四化落点为主，不按单颗星曜直接下结论。",
                "阶段提醒只保留大限与流年落宫的主题索引，不扩写成具体年份事件。",
            ],
            "边界": "以下正文用于增强紫微专业版的本命与专题表达；流年部分仍保持低置信结构提示。",
        },
        "命身总论": {
            "盘面依据": [
                _palace_evidence(palaces, "命宫"),
                _palace_evidence(palaces, shen_role) if shen_role else "身宫所属宫位待补。",
                hua_text,
            ],
            "判断": (
                f"命宫见{_stars(ming)}，人格底色偏{_palace_theme(ming)}；身宫落{shen_role}，"
                f"后天发力点落在{PALACE_TOPICS.get(shen_role, '身宫对应主题')}。"
                "这张盘不宜只看单宫吉凶，而要看命宫定性、身宫定用，四化再定应事方向。"
            ),
            "建议": "先顺命身主轴建立稳定节奏，再把四化牵动处当成重点课题处理。",
        },
        "性格气质": _domain_block(
            palaces,
            ["命宫", "福德宫", "迁移宫"],
            "性格判断看命宫的外显气质，也看福德宫的内在心气；迁移宫则说明人在外部环境中会被怎样带动。",
            "表达自己时抓住核心原则，遇到环境变化先稳住内在节奏，再决定是否推进。",
        ),
        "事业学业": _domain_block(
            palaces,
            ["官禄宫", "迁移宫", "福德宫"],
            "学业与事业不是只看职位或成绩，而是看能力结构、平台变化和长期心力能否接得住。",
            "适合把目标拆成可执行路径；若迁移或福德见耗，先处理环境与精力管理，再谈强攻突破。",
        ),
        "财运资源": _domain_block(
            palaces,
            ["财帛宫", "官禄宫", "田宅宫"],
            "财运要回扣成事路径和资源承接，能不能赚钱、能不能落袋、能不能守住，是三件不同的事。",
            "重大资源选择宜看现金流、责任边界和长期稳定性，不把短期机会等同于真正积累。",
        ),
        "感情婚姻": _domain_block(
            palaces,
            ["夫妻宫", "福德宫", "交友宫"],
            "关系判断不能只看缘分强弱，还要看内在安全感、圈层牵引和现实节奏是否能对上。",
            "亲密关系里先讲边界和节奏，再讲承诺；当外部压力进入关系，要分清现实问题和情绪问题。",
        ),
        "健康状态": _domain_block(
            palaces,
            ["疾厄宫", "福德宫", "迁移宫"],
            "这里不作医学结论，只看身心压力如何反映到作息、情绪、恢复力和外部奔波上。",
            "若长期疲惫、焦虑或身体不适，应以专业医疗意见为准；命理建议只用于节奏管理和风险提醒。",
        ),
        "阶段提醒": _stage_reminders(wenmo_chart),
    }


def build_ziwei_professional_output(
    ziwei_section: Dict[str, Any],
    wenmo_chart: Dict[str, Any] = None,
    wenmo_comparison: Dict[str, Any] = None,
) -> Dict[str, Any]:
    basic = ziwei_section.get("基础信息", {})
    ming = ziwei_section.get("重点宫位", {}).get("命宫", {})
    shen_role = basic.get("身宫所属宫位", "")
    validation = ziwei_section.get("校验", {})
    reference = validation.get("reference_match", {})
    boundary = validation.get("boundary", {})

    data_source = "虾神算自排盘"
    if wenmo_chart and wenmo_chart.get("状态") == "OK":
        data_source = "文墨天机文字盘 + 虾神算自排盘交叉校验"

    return {
        "模式": "紫微斗数专业版",
        "数据源": data_source,
        "命盘信息": {
            "安星码": ziwei_section.get("安星码"),
            "状态": ziwei_section.get("状态"),
            "性别": basic.get("gender"),
            "公历": f"{basic.get('birth_date')} {basic.get('birth_time')}",
            "真太阳时": basic.get("true_solar_time"),
            "农历": basic.get("lunar_date"),
            "命局": basic.get("命局"),
            "命宫": basic.get("命宫"),
            "身宫": f"{basic.get('身宫')}（{shen_role}）",
            "命主身主": f"{basic.get('命主')}/{basic.get('身主')}",
            "子斗": basic.get("子斗"),
        },
        "总断": (
            f"此盘先看命宫，命宫见{_stars(ming)}，定人物主气质；再看身宫落{shen_role}，"
            "定后天真正发力与被牵动的位置。专业断盘不宜逐宫念稿，要先抓命身主轴，再看官财福夫妻迁移如何联动。"
        ),
        "命身主轴": [
            f"命宫：{_palace_line(ming)}" if ming else "命宫资料待补。",
            f"身宫：后天重心落{shen_role}，现实发力与压力承接多从此处展开。",
        ],
        "正文分析": _body_analysis(ziwei_section, wenmo_chart),
        "关键宫位": _key_palace_lines(ziwei_section),
        "四化流向": _four_hua_line(ziwei_section),
        "专题判断": {
            "事业": "先看官禄宫，再联动迁移宫与福德宫；事业不是只看职位，而是看能否承接责任、平台变化与长期心力。",
            "财运": "先看财帛宫，再联动官禄宫与田宅宫；财不是只看机会，而是看路径、落袋和守成。",
            "感情": "先看夫妻宫，再联动福德宫与迁移宫；关系不是只看缘分，而是看现实节奏与内在安全感。",
            "状态": "先看福德宫与疾厄宫；真正的趋避重点，是不要让精神内耗拖垮判断和行动。",
        },
        "校验": {
            "时辰边界": boundary.get("status"),
            "文墨参考盘": reference.get("status", validation.get("文墨C5FYC逐盘校验", "UNVERIFIED")),
            "文墨文字盘比对": wenmo_comparison or {"状态": "NOT_PROVIDED"},
            "说明": "当前紫微引擎为 TRIAL_READY；命中文墨样本时可看 reference_match，未命中时仍需保留校准边界。",
        },
        "文墨文字盘摘要": wenmo_chart if wenmo_chart else None,
        "趋避建议": {
            "事业": "顺命身主轴发力，少在不属于主线的位置硬耗。",
            "关系": "夫妻宫只是一端，还要看福德与迁移，避免把现实压力误读成单纯感情问题。",
            "状态": "福德与疾厄若见耗，先调节睡眠、节奏和情绪出口，再谈强攻突破。",
        },
        "声明": "命理为参考，趋吉避凶为目的；重大事项仍需结合现实信息理性决策。",
    }
