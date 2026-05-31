"""Fusion engine for multi-module XiaShenSuan output."""

from typing import Any, Dict, List


BASE_WEIGHTS = {
    "bazi": 0.35,
    "ziwei": 0.35,
    "mbti": 0.15,
    "zodiac": 0.10,
    "blood": 0.05,
}

MODULE_NAMES = {
    "bazi": "八字",
    "ziwei": "紫微斗数",
    "mbti": "MBTI",
    "zodiac": "星座",
    "blood": "血型",
}


def _ok(module_result: Dict[str, Any]) -> bool:
    return bool(module_result and module_result.get("状态") == "OK")


def _normalize_weights(enabled_modules: List[str]) -> Dict[str, float]:
    total = sum(BASE_WEIGHTS.get(module, 0) for module in enabled_modules)
    if not total:
        return {}
    return {
        MODULE_NAMES[module]: round(BASE_WEIGHTS[module] / total, 3)
        for module in enabled_modules
        if module in BASE_WEIGHTS
    }


def build_personality_complement(
    enabled_modules: List[str],
    mbti: Dict[str, Any] = None,
    zodiac: Dict[str, Any] = None,
    blood: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build a layered personality supplement from MBTI, zodiac and blood type."""
    layers: List[Dict[str, Any]] = []
    suggestions: List[str] = []

    if "mbti" in enabled_modules and _ok(mbti):
        layers.append(
            {
                "模块": "MBTI",
                "层级": mbti.get("补充层级", "行为策略层"),
                "结论": mbti.get("人格补充画像", {}).get("核心画像", mbti.get("特点")),
                "用于解释": "决策方式、协作方式、压力反应和关系边界。",
            }
        )
        suggestions.append(mbti.get("人格补充画像", {}).get("压力管理", mbti.get("恢复建议", "")))

    if "zodiac" in enabled_modules and _ok(zodiac):
        layers.append(
            {
                "模块": "星座",
                "层级": zodiac.get("补充层级", "外显气质与情绪表达层"),
                "结论": zodiac.get("人格补充画像", {}).get("外显气质", zodiac.get("特点")),
                "用于解释": "外显气质、情绪表达、第一印象和恢复空间。",
            }
        )
        suggestions.append(zodiac.get("人格补充画像", {}).get("恢复建议", ""))

    if "blood" in enabled_modules and _ok(blood):
        layers.append(
            {
                "模块": "血型",
                "层级": blood.get("补充层级", "民俗相处风格层"),
                "结论": blood.get("人格补充画像", {}).get("相处节奏", blood.get("特点")),
                "用于解释": "相处节奏、协作习惯和低权重民俗风格提示。",
            }
        )
        suggestions.append(blood.get("人格补充画像", {}).get("关系提醒", blood.get("关系建议", "")))

    if not layers:
        return {
            "状态": "EMPTY",
            "说明": "当前未启用有效人格补充模块。",
        }

    return {
        "状态": "OK",
        "版本": "personality-complement-v1",
        "定位": "人格补充模块：解释行为、表达、相处节奏，不替代八字与紫微的结构判断。",
        "启用层级": layers,
        "融合规则": [
            "MBTI优先解释行为策略和压力反应。",
            "星座优先解释外显气质和情绪表达。",
            "血型只作低权重相处风格提示。",
            "三者与八字/紫微冲突时，命理结构定主轴，人格模块解释表现方式。",
        ],
        "综合建议": [item for item in suggestions if item],
        "边界": "人格补充模块不单独判断事业成败、婚恋吉凶、财富高低或具体年份事件。",
    }


def build_core_mingli_fusion(
    bazi: Dict[str, Any] = None,
    ziwei: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build the equal-weight fusion protocol for Bazi and Ziwei."""
    if not bazi or not ziwei:
        return {
            "状态": "EMPTY",
            "说明": "八字与紫微未同时启用，暂不生成核心命理融合。",
        }

    bazi_interface = bazi.get("融合接口", {})
    bazi_prof = bazi.get("专业分析", {})
    ziwei_basic = ziwei.get("基础信息", {})
    ziwei_four_hua = ziwei.get("四化", {})
    hua_text = "、".join(
        f"{detail.get('星曜')}化{name}落{detail.get('宫支')}"
        for name, detail in ziwei_four_hua.items()
        if isinstance(detail, dict)
    )
    ziwei_axis = (
        f"命宫{ziwei_basic.get('命宫', '待定')}，身宫落{ziwei_basic.get('身宫所属宫位', '待定')}，"
        f"四化为{hua_text or '待补'}。"
    )
    bazi_strength = bazi_prof.get("旺衰判断", {})
    bazi_useful = bazi_prof.get("用神策略", {})

    agreements = [
        "八字负责底层气势、五行旺衰、十神结构与大运承压。",
        "紫微负责命身主轴、宫位场景、三方四正与四化落点。",
    ]
    if bazi_interface.get("当前阶段", {}).get("大运"):
        agreements.append(
            f"八字当前大运主轴为{bazi_interface['当前阶段']['大运'].get('主轴', '待定')}，可与紫微身宫/官财福夫妻宫联动看阶段主题。"
        )
    if ziwei_basic.get("身宫所属宫位"):
        agreements.append(f"紫微身宫落{ziwei_basic.get('身宫所属宫位')}，用于定位现实发力与压力承接场景。")

    return {
        "状态": "OK",
        "版本": "core-mingli-fusion-v1",
        "核心权重": {"八字": 0.5, "紫微斗数": 0.5},
        "分工": {
            "八字": "定底层气势、日主旺衰、十神结构、喜忌方向、大运阶段。",
            "紫微斗数": "定命身主轴、宫位场景、四化牵引、现实应事位置。",
        },
        "八字主轴": bazi_interface.get("主轴摘要", ""),
        "紫微主轴": ziwei_axis,
        "一致信号": agreements,
        "冲突解释": [
            "八字旺而紫微宫位受压：说明有承压底子，但应事场景存在阻滞，宜看具体宫位化忌或煞曜。",
            "八字弱而紫微宫位有力：说明机会场景存在，但承接力要靠环境、资源和节奏托底。",
            "八字喜忌与紫微四化方向不一致：八字先定能不能承接，紫微再定事情落在哪个生活领域。",
        ],
        "专业边界": [
            bazi_useful.get("边界", ""),
            "紫微流年当前仍保持主题索引，不扩写具体事件。",
            "核心命理融合不是简单投票；两者一致提高置信，冲突时拆成承压能力与应事场景分别解释。",
        ],
        "融合结论": "八字与紫微在核心层并列同权：八字看气，紫微看象；八字看能量承接，紫微看场景落点。",
        "置信说明": f"八字结构判断为{bazi_strength.get('结构判断', '待定')}；需继续用真实事件校准提高事件级判断。",
    }


def build_fusion_report(
    enabled_modules: List[str],
    bazi: Dict[str, Any] = None,
    ziwei: Dict[str, Any] = None,
    mbti: Dict[str, Any] = None,
    zodiac: Dict[str, Any] = None,
    blood: Dict[str, Any] = None,
) -> Dict[str, Any]:
    """Build a concise fusion layer with explicit weights and conflict rules."""
    weights = _normalize_weights(enabled_modules)
    personality = build_personality_complement(enabled_modules, mbti=mbti, zodiac=zodiac, blood=blood)
    core_fusion = build_core_mingli_fusion(bazi=bazi, ziwei=ziwei)
    agreements: List[str] = []
    conflicts: List[str] = []

    if bazi and ziwei and {"bazi", "ziwei"}.issubset(enabled_modules):
        professional = bazi.get("专业分析", {})
        strength = professional.get("旺衰判断", {}) if isinstance(professional, dict) else {}
        basic = ziwei.get("基础信息", {})
        agreements.append(
            f"八字先看底层气势：{strength.get('结构判断') or bazi.get('日主', {}).get('身强弱', '待定')}；"
            f"紫微再看人生结构：身宫落{basic.get('身宫所属宫位', '待定')}。"
        )
    if _ok(mbti) and "mbti" in enabled_modules:
        agreements.append(f"MBTI补行为策略：{mbti.get('代号')}，重点看决策、协作和压力反应。")
    if _ok(zodiac) and "zodiac" in enabled_modules:
        agreements.append(f"星座补情绪表达：{zodiac.get('星座')}，外显气质偏{zodiac.get('特点')}。")
    if _ok(blood) and "blood" in enabled_modules:
        agreements.append(f"血型补相处节奏：{blood.get('类型')}，只作低权重民俗风格参考。")

    if {"bazi", "ziwei", "mbti"}.issubset(enabled_modules):
        conflicts.append("若命理结构与MBTI行为描述不一致，优先按八字/紫微定底层结构，MBTI解释外在行为策略。")
    if {"zodiac", "blood"}.intersection(enabled_modules):
        conflicts.append("星座与血型只解释表达习惯和体验感，不作为事业、婚恋、财富重大判断的主依据。")

    if not agreements:
        agreements.append("当前启用模块较少，先保留单项判断，不强行做大融合。")

    return {
        "版本": "fusion-v1",
        "启用模块": [MODULE_NAMES.get(module, module) for module in enabled_modules],
        "权重": weights,
        "核心命理融合": core_fusion,
        "人格补充": personality,
        "一致结论": agreements,
        "冲突解释": conflicts,
        "最终画像": "命理模块负责结构与周期，人格模块负责表达与行为；融合时先定底层，再解释外显。",
        "行动建议": {
            "事业": "先看命理里的事业结构和阶段节奏，再用MBTI补执行方式。",
            "感情": "先看夫妻宫、关系宫与八字关系倾向，再用MBTI/星座解释表达差异。",
            "状态": "先看福德、疾厄与五行失衡，再用人格模块补压力反应和恢复方式。",
        },
        "边界": "融合分析是分层解释，不是简单投票；低权重模块不推翻高权重结构判断。",
    }
