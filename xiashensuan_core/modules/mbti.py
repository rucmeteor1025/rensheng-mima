"""MBTI personality module."""

from typing import Any, Dict


MBTI_TYPES = {
    "INTJ": {"名": "战略家", "特点": "独立、战略性强、追求效率", "优势": "长远规划、问题解决"},
    "INTP": {"名": "逻辑学家", "特点": "理性、创新、喜欢理论", "优势": "分析能力、创新能力"},
    "ENTJ": {"名": "指挥官", "特点": "领导力强、果断、有执行力", "优势": "决策、组织"},
    "ENTP": {"名": "辩论家", "特点": "创意、善于辩论、思维敏捷", "优势": "创意、沟通"},
    "INFJ": {"名": "提倡者", "特点": "理想主义、有洞察力、追求意义", "优势": "洞察力、毅力"},
    "INFP": {"名": "调停者", "特点": "理想主义、敏感、追求价值", "优势": "创造力、同理心"},
    "ENFJ": {"名": "主人公", "特点": "有感染力、善于激励、自然领袖", "优势": "领导、沟通"},
    "ENFP": {"名": "竞选者", "特点": "热情、创意、善于激励", "优势": "创意、激励他人"},
    "ISTJ": {"名": "物流师", "特点": "可靠、务实、有责任感", "优势": "执行力、可靠性"},
    "ISFJ": {"名": "守卫者", "特点": "忠诚、细心、乐于助人", "优势": "照顾他人、可靠性"},
    "ESTJ": {"名": "总经理", "特点": "有条理、果断、结果导向", "优势": "组织、管理"},
    "ESFJ": {"名": "执政官", "特点": "关心他人、善于组织、社交能力强", "优势": "协调、照顾"},
    "ISTP": {"名": "鉴赏家", "特点": "务实、灵活、善于分析", "优势": "动手能力、分析"},
    "ISFP": {"名": "探险家", "特点": "艺术感、灵活、善于观察", "优势": "艺术、适应力"},
    "ESTP": {"名": "企业家", "特点": "大胆、实际、善于行动", "优势": "行动力、谈判"},
    "ESFP": {"名": "表演者", "特点": "热情、善于表现、喜欢冒险", "优势": "激励、娱乐"},
}

DECISION_STYLE = {
    "T": "决策更看逻辑、效率和边界，遇到压力时容易先找规则与解法。",
    "F": "决策更看关系、价值和感受，遇到压力时容易先照顾人和氛围。",
}

ENERGY_STYLE = {
    "E": "能量更容易从互动、表达和外部反馈中被点燃。",
    "I": "能量更容易从独处、复盘和深度思考中恢复。",
}

STRUCTURE_STYLE = {
    "J": "做事偏计划、收口和确定性，讨厌长期悬而未决。",
    "P": "做事偏开放、探索和弹性，容易在变化里找到新解法。",
}

INFO_STYLE = {
    "S": "信息处理更重事实、经验和可验证细节，适合把复杂问题拆成具体步骤。",
    "N": "信息处理更重趋势、意义和可能性，适合从抽象图景里抓方向。",
}

WORK_STYLE = {
    "SJ": "适合稳定流程、规则执行、复盘校准和长期责任。",
    "SP": "适合现场处理、快速试错、工具化解决和变化场景。",
    "NJ": "适合战略规划、系统搭建、长期目标和复杂问题拆解。",
    "NP": "适合创意探索、概念设计、可能性比较和新路径发现。",
}

RELATION_STYLE = {
    "TJ": "关系里重边界、承诺和可执行规则，适合把责任分工说清楚。",
    "TP": "关系里重自由、逻辑和空间感，适合减少情绪化推拉。",
    "FJ": "关系里重回应、稳定和照顾感，适合建立可持续的沟通节奏。",
    "FP": "关系里重真实、感受和价值一致，适合保留表达弹性与情绪出口。",
}

SUBTYPE_STYLE = {
    "A": "A 型更容易表现为稳定、自主和对外部评价不那么敏感。",
    "T": "T 型更容易表现为自我审视、波动感和对反馈更敏锐。",
}


def _normalize_mbti(raw: str) -> Dict[str, str]:
    value = (raw or "").strip().upper().replace(" ", "")
    if not value:
        return {"base": "", "variant": ""}
    base = value[:4]
    variant = value[5:] if len(value) > 5 and value[4] in {"-", "_"} else ""
    return {"base": base, "variant": variant}


def mbti_analysis(mbti_type: str) -> Dict[str, Any]:
    """Return a structured MBTI profile that can be fused with命理 modules."""
    normalized = _normalize_mbti(mbti_type)
    base = normalized["base"]
    if base not in MBTI_TYPES:
        return {
            "状态": "INVALID",
            "错误": f"未知的MBTI类型: {(mbti_type or '').strip()}",
            "可用类型": list(MBTI_TYPES.keys()),
        }

    info = MBTI_TYPES[base]
    variant = normalized["variant"]
    work_key = f"{base[1]}{base[3]}"
    relation_key = f"{base[2]}{base[3]}"
    subtype_note = SUBTYPE_STYLE.get(variant, "未提供 A/T 亚型时，只按基础四维类型解读。")
    return {
        "状态": "OK",
        "模块定位": "人格补充模块",
        "补充层级": "行为策略层",
        "类型": f"{base}-{variant}" if variant else base,
        "基础类型": base,
        "亚型": variant,
        "代号": info["名"],
        "特点": info["特点"],
        "优势": info["优势"],
        "四维结构": {
            "能量来源": ENERGY_STYLE[base[0]],
            "信息处理": INFO_STYLE[base[1]],
            "决策方式": DECISION_STYLE[base[2]],
            "行动结构": STRUCTURE_STYLE[base[3]],
            "亚型提示": subtype_note,
        },
        "决策方式": DECISION_STYLE[base[2]],
        "能量来源": ENERGY_STYLE[base[0]],
        "信息处理": INFO_STYLE[base[1]],
        "行动结构": STRUCTURE_STYLE[base[3]],
        "协作方式": WORK_STYLE[work_key],
        "关系模式": RELATION_STYLE[relation_key],
        "压力反应": (
            "压力大时，容易把原本的优势用过头："
            f"{base[0]} 维影响恢复方式，{base[1]} 维影响信息焦点，{base[2]} 维影响取舍标准，{base[3]} 维影响行动节奏。"
        ),
        "恢复建议": "先按能量来源恢复基本状态，再用行动结构收口；不要在低能量状态下做高代价承诺。",
        "人格补充画像": {
            "核心画像": f"{base}（{info['名']}）偏{info['特点']}，优势在{info['优势']}。",
            "事业协作": WORK_STYLE[work_key],
            "关系风格": RELATION_STYLE[relation_key],
            "压力管理": "把压力拆成能量、信息、决策、行动四层看，先处理最卡的一层。",
            "成长提醒": "MBTI用于解释行为策略，不用于替代命盘结构、现实能力和真实经历。",
        },
        "融合定位": "人格补充模块 / 行为策略层",
        "权重建议": "中低权重；用于解释做事方式、沟通方式和压力反应，不压过八字与紫微的结构判断。",
        "融合边界": "MBTI可以解释人怎么做选择，但不能单独判断事业成败、婚恋吉凶或财富高低。",
    }
