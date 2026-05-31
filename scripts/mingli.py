#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
命理测算工具（旧版怀旧版保留） - 基于 lunar_python 库

说明：
- 本文件作为怀旧版/legacy 入口继续保留
- 默认主流程已切到 scripts/xiashensuan.py
"""
import json
import sys
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from xiashensuan_core.modules.bazi import (  # noqa: E402
    DEFAULT_LONGITUDE,
    GAN_TO_WUXING,
    KE_REL,
    SHENG_REL,
    apply_true_solar_time,
    get_bazi,
    get_dayun_analysis,
    get_flowyear_analysis,
    parse,
)

if __name__ == "__main__":
    import sys
    if len(sys.argv) >= 5:
        r = get_bazi(int(sys.argv[1]), int(sys.argv[2]), int(sys.argv[3]), int(sys.argv[4]))
    else:
        r = parse({"year": 1990, "month": 1, "day": 15, "hour": 14, "minute": 30})
    print(json.dumps(r, ensure_ascii=False, indent=2))

# ==================== 星座分析 ====================

ZODIAC_DATES = [
    (1, 20, "水瓶座"), (2, 18, "双鱼座"), (3, 20, "白羊座"),
    (20, 4, "金牛座"), (20, 5, "双子座"), (21, 6, "巨蟹座"),
    (22, 7, "狮子座"), (22, 8, "处女座"), (22, 9, "天秤座"),
    (22, 10, "天蝎座"), (21, 11, "射手座"), (21, 12, "摩羯座")
]

ZODIAC_FEATURES = {
    "水瓶座": {"特点": "独立创新、人道主义", "适合": "科技、艺术、发明", "运势": "事业上有突破"},
    "双鱼座": {"特点": "直觉强、艺术感", "适合": "创意、帮助他人", "运势": "感情有收获"},
    "白羊座": {"特点": "勇敢直接、行动力强", "适合": "创业、体育", "运势": "财运上升"},
    "金牛座": {"特点": "务实稳定、享受生活", "适合": "金融、餐饮、艺术", "运势": "稳步增长"},
    "双子座": {"特点": "好奇心强、善于沟通", "适合": "媒体、销售、教育", "运势": "人脉拓展"},
    "巨蟹座": {"特点": "顾家情感丰富", "适合": "服务、餐饮、房产", "运势": "家庭和睦"},
    "狮子座": {"特点": "领导力强、自尊心强", "适合": "管理、艺术、娱乐", "运势": "事业巅峰"},
    "处女座": {"特点": "追求完美、分析力强", "适合": "医疗、财务、咨询", "运势": "学业进步"},
    "天秤座": {"特点": "追求平衡、社交能力强", "适合": "法律、外交、设计", "运势": "贵人相助"},
    "天蝎座": {"特点": "神秘执着、洞察力强", "适合": "研究、侦探、金融", "运势": "财富积累"},
    "射手座": {"特点": "乐观自由、爱好广泛", "适合": "旅游、教育、出版", "运势": "海外机会"},
    "摩羯座": {"特点": "稳重踏实、目标明确", "适合": "政治、建筑、管理", "运势": "事业有成"}
}

def get_zodiac(month, day):
    """获取星座"""
    dates = [(1,20,"水瓶"),(2,18,"双鱼"),(3,20,"白羊"),(4,20,"金牛"),(5,21,"双子"),(6,21,"巨蟹"),
             (7,23,"狮子"),(8,23,"处女"),(9,23,"天秤"),(10,23,"天蝎"),(11,22,"射手"),(12,22,"摩羯")]
    for d, m, name in reversed(dates):
        if month > d or (month == d and day >= m):
            return name + "座"
    return "摩羯座"

def zodiac_analysis(month, day):
    """星座分析"""
    name = get_zodiac(month, day)
    info = ZODIAC_FEATURES.get(name, {})
    return {
        "星座": name,
        "特点": info.get("特点", ""),
        "适合领域": info.get("适合", ""),
        "近期运势": info.get("运势", "")
    }

# ==================== MBTI分析 ====================

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
    "ESFP": {"名": "表演者", "特点": "热情、善于表现、喜欢冒险", "优势": "激励、娱乐"}
}

def mbti_analysis(mbti_type):
    """MBTI分析"""
    mbti = mbti_type.upper()
    if mbti not in MBTI_TYPES:
        return {"错误": f"未知的MBTI类型: {mbti}", "可用类型": list(MBTI_TYPES.keys())}
    
    info = MBTI_TYPES[mbti]
    return {
        "类型": mbti,
        "代号": info["名"],
        "特点": info["特点"],
        "优势": info["优势"]
    }

def full_analysis(birth_time, gender, mbti=None, zodiac_only=False):
    """综合分析"""
    result = {}
    
    # 八字
    if not zodiac_only:
        result["八字"] = parse(birth_time, gender)
    
    # 星座
    result["星座"] = zodiac_analysis(
        birth_time.get("month"),
        birth_time.get("day")
    )
    
    # MBTI
    if mbti:
        result["MBTI"] = mbti_analysis(mbti)
    
    return result



# ==================== 紫微斗数排盘 ====================

ZIWEI_MAIN = {
    "紫微": {"性质": "帝星", "五行": "土", "关键词": "主导、格局、掌控"},
    "天机": {"性质": "善星", "五行": "木", "关键词": "思考、变化、机敏"},
    "太阳": {"性质": "贵星", "五行": "火", "关键词": "外放、担当、光明"},
    "武曲": {"性质": "财星", "五行": "金", "关键词": "执行、财务、决断"},
    "天同": {"性质": "福星", "五行": "水", "关键词": "温和、享受、柔软"},
    "廉贞": {"性质": "囚星", "五行": "火", "关键词": "欲望、原则、拉扯"},
    "天府": {"性质": "府库", "五行": "土", "关键词": "稳定、守成、资源"},
    "太阴": {"性质": "财星", "五行": "水", "关键词": "细腻、内敛、感受"},
    "贪狼": {"性质": "欲星", "五行": "木", "关键词": "社交、欲望、表现"},
    "巨门": {"性质": "暗星", "五行": "土", "关键词": "思辨、怀疑、口才"},
    "天相": {"性质": "印星", "五行": "水", "关键词": "平衡、分寸、协助"},
    "天梁": {"性质": "荫星", "五行": "土", "关键词": "保护、原则、担当"},
    "七杀": {"性质": "杀星", "五行": "金", "关键词": "决断、压强、极致"},
    "破军": {"性质": "耗星", "五行": "水", "关键词": "破旧、变化、冒险"}
}

ZIWEI_ASSIST = {
    "左辅": "助力、配合、资源", "右弼": "支持、人缘、协同",
    "文昌": "表达、学习、条理", "文曲": "审美、灵感、感受",
    "天魁": "贵人、提携、机会", "天钺": "暗助、机缘、扶持",
    "禄存": "守财、稳定、积累", "擎羊": "冲劲、拧劲、压力",
    "陀罗": "迟滞、反复、拉扯", "火星": "爆发、急躁、动作快",
    "铃星": "紧绷、敏感、突发", "地空": "空耗、抽离、落空",
    "地劫": "损耗、波动、破耗"
}

ZIWEI_GONGS = ["命宫", "父母宫", "福德宫", "田宅宫", "官禄宫", "迁移宫", "疾厄宫", "财帛宫", "子女宫", "夫妻宫", "兄弟宫", "奴仆宫"]

GONG_EXPLAIN = {
    "命宫": "看一个人的主气质、做人方式和整体底色",
    "夫妻宫": "看亲密关系模式、婚恋需求与关系里的矛盾点",
    "财帛宫": "看钱从哪里来、守不守得住、财路偏稳还是偏动",
    "官禄宫": "看事业路径、工作风格、适合什么样的环境",
    "福德宫": "看内在精神状态、幸福感来源以及是否容易内耗",
    "迁移宫": "看对外部世界的适应方式、出行变化与环境切换能力",
    "疾厄宫": "看身体容易累在哪、长期压力容易落在哪些方面",
    "田宅宫": "看安全感、生活空间、安定需求和现实落脚点",
    "父母宫": "看原生支持感、长辈关系和早期规训感"
}


def _calc_shen_gong_index(bazi_info):
    day_gan = bazi_info["日主"]["日主"]
    hour_zhi = bazi_info["四柱"]["时"][1]
    gan_idx = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"].index(day_gan)
    zhi_idx = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"].index(hour_zhi)
    return (gan_idx + zhi_idx) % len(ZIWEI_GONGS)


def _pick_assist_stars(bazi_info, gong_index):
    wx = bazi_info.get("五行分布", {})
    candidates = []
    if wx.get("木", 0) >= 2:
        candidates.append("文昌")
    if wx.get("水", 0) >= 2:
        candidates.append("文曲")
    if wx.get("土", 0) >= 2:
        candidates.append("禄存")
    if wx.get("金", 0) >= 2:
        candidates.append("右弼")
    if wx.get("火", 0) >= 2:
        candidates.append("左辅")

    fixed = ["天魁", "天钺", "擎羊", "陀罗", "火星", "铃星", "地空", "地劫"]
    pool = candidates + fixed
    a = pool[gong_index % len(pool)]
    b = pool[(gong_index + 3) % len(pool)]
    return [a] if a == b else [a, b]


def get_ziwei_chart(bazi_info):
    day_gan = bazi_info["日主"]["日主"]
    star_map = {
        0: ["紫微", "天府"], 1: ["天机", "太阴"], 2: ["太阳", "武曲"],
        3: ["天同", "廉贞"], 4: ["贪狼", "巨门"], 5: ["天相", "天梁"],
        6: ["七杀", "破军"], 7: ["太阳", "天府"], 8: ["天机", "贪狼"], 9: ["天同", "巨门"]
    }
    day_gan_idx = ["甲","乙","丙","丁","戊","己","庚","辛","壬","癸"].index(day_gan)
    main_stars = star_map.get(day_gan_idx, ["紫微", "天府"])

    chart = {}
    stars = main_stars + ["天梁", "天同", "天府", "紫微", "天相", "廉贞", "武曲", "贪狼", "太阴", "天机", "七杀"]
    shen_idx = _calc_shen_gong_index(bazi_info)
    shen_gong = ZIWEI_GONGS[shen_idx]

    for i, gong in enumerate(ZIWEI_GONGS):
        assist = _pick_assist_stars(bazi_info, i)
        chart[gong] = {
            "主星": stars[i] if i < len(stars) else "待定",
            "辅星": assist,
            "宫义": GONG_EXPLAIN.get(gong, "")
        }
        if gong == shen_gong:
            chart[gong]["身宫"] = True
    return chart


def _join_keywords(stars):
    words = []
    for s in stars:
        if s in ZIWEI_MAIN:
            words.extend(ZIWEI_MAIN[s].get("关键词", "").split("、"))
        elif s in ZIWEI_ASSIST:
            words.extend(ZIWEI_ASSIST[s].split("、"))
    result = []
    for w in words:
        if w and w not in result:
            result.append(w)
    return "、".join(result[:4])


def _ziwei_focus_summary(chart):
    ming = chart["命宫"]
    fuqi = chart["夫妻宫"]
    cai = chart["财帛宫"]
    guan = chart["官禄宫"]
    fude = chart["福德宫"]
    qianyi = chart["迁移宫"]
    jie = chart["疾厄宫"]
    tian = chart["田宅宫"]
    fumu = chart["父母宫"]

    return {
        "命宫解读": f"命宫主星为{ming['主星']}，人物底色更偏{_join_keywords([ming['主星']] + ming['辅星'])}。",
        "夫妻宫解读": f"夫妻宫落{fuqi['主星']}，关系里更看重{_join_keywords([fuqi['主星']] + fuqi['辅星'])}。",
        "财帛宫解读": f"财帛宫落{cai['主星']}，钱财路径更偏{_join_keywords([cai['主星']] + cai['辅星'])}。",
        "官禄宫解读": f"官禄宫落{guan['主星']}，事业风格更接近{_join_keywords([guan['主星']] + guan['辅星'])}。",
        "福德宫解读": f"福德宫落{fude['主星']}，内在状态和精神重心多半落在{_join_keywords([fude['主星']] + fude['辅星'])}。",
        "迁移宫解读": f"迁移宫落{qianyi['主星']}，面对外部变化时更容易表现出{_join_keywords([qianyi['主星']] + qianyi['辅星'])}。",
        "疾厄宫解读": f"疾厄宫落{jie['主星']}，身体和压力层面更要留意{_join_keywords([jie['主星']] + jie['辅星'])}。",
        "田宅宫解读": f"田宅宫落{tian['主星']}，安全感和现实落脚点更偏{_join_keywords([tian['主星']] + tian['辅星'])}。",
        "父母宫解读": f"父母宫落{fumu['主星']}，早期支持感和规训感更接近{_join_keywords([fumu['主星']] + fumu['辅星'])}。"
    }


def ziwei_analysis(bazi_info):
    chart = get_ziwei_chart(bazi_info)
    main_star = chart["命宫"]["主星"]
    star_info = ZIWEI_MAIN.get(main_star, {})
    shen_gong = next((gong for gong, info in chart.items() if info.get("身宫")), "")
    focus_gongs = {gong: chart[gong] for gong in ["命宫", "夫妻宫", "财帛宫", "官禄宫", "福德宫", "迁移宫", "疾厄宫", "田宅宫", "父母宫"] if gong in chart}
    return {
        "命宫主星": main_star,
        "星曜性质": star_info.get("性质", ""),
        "主星五行": star_info.get("五行", ""),
        "命宫关键词": star_info.get("关键词", ""),
        "身宫": shen_gong,
        "身宫说明": f"身宫落在{shen_gong}，代表这个人现实里的发力点和外在呈现，会明显受{shen_gong}主题影响。" if shen_gong else "",
        "重点宫位": focus_gongs,
        "重点宫位解读": _ziwei_focus_summary(chart),
        "十二宫": chart
    }


# ==================== 大运流年 ====================

def get_dayun(bazi_info, age):
    """
    大运计算（简化版）
    规则：阳干顺行，阴干逆行，每步大运管10年
    """
    day_gan = bazi_info["日主"]["日主"]
    
    # 日干阴阳
    yinyang = {"甲": "阳", "丙": "阳", "戊": "阳", "庚": "阳", "壬": "阳",
               "乙": "阴", "丁": "阴", "己": "阴", "辛": "阴", "癸": "阴"}
    
    # 月柱地支
    month_zhi = bazi_info["四柱"]["月"][1]
    zhi_idx = {"寅": 0, "卯": 1, "辰": 2, "巳": 3, "午": 4, "未": 5, "申": 6, "酉": 7, "戌": 8, "亥": 9, "子": 10, "丑": 11}
    month_idx = zhi_idx.get(month_zhi, 0)
    
    # 大运地支（从月支开始）
    gan_list = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    zhi_list = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    day_yin = yinyang.get(day_gan, "阳")
    day_gan_idx = gan_list.index(day_gan)
    
    # 计算大运起始
    if day_yin == "阳":
        # 阳干顺行
        start_idx = (month_idx + 1) % 12
        direction = "顺行"
    else:
        # 阴干逆行
        start_idx = (month_idx - 1) % 12
        direction = "逆行"
    
    # 生成8步大运
    dayuns = []
    for i in range(8):
        zhi = zhi_list[(start_idx + i) % 12]
        # 时干
        gan_idx = (day_gan_idx + (i + 1 if day_yin == "阳" else -(i + 1))) % 10
        gan = gan_list[gan_idx]
        dayun_start = age + i * 10
        dayun = {
            "大运": f"{gan}{zhi}",
            "岁数": f"{dayun_start}-{dayun_start + 9}",
            "序号": i + 1
        }
        dayuns.append(dayun)
    
    return {
        "方向": direction,
        "起始": f"{gan_list[gan_idx]}{zhi_list[start_idx]}大运",
        "8步大运": dayuns
    }

def get_liunian(bazi_info, year):
    """
    流年分析（简化版）
    基于当年年份天干地支与八字的关系
    """
    # 流年干支
    TIANGAN = ["甲", "乙", "丙", "丁", "戊", "己", "庚", "辛", "壬", "癸"]
    DIZHI = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
    
    gan = TIANGAN[(year - 4) % 10]
    zhi = DIZHI[(year - 4) % 12]
    liunian = gan + zhi
    
    # 日干
    day_gan = bazi_info["日主"]["日主"]
    
    # 简单判断
    # 与日干关系：同我、克我、我克、生我
    wuxing_map = {"甲": "木", "乙": "木", "丙": "火", "丁": "火", "戊": "土", "己": "土", "庚": "金", "辛": "金", "壬": "水", "癸": "水"}
    day_wx = wuxing_map.get(day_gan, "土")
    liu_wx = wuxing_map.get(gan, "土")
    
    # 五行生克
    relation = ""
    if day_wx == liu_wx:
        relation = "比和"
    elif (day_wx == "木" and liu_wx == "土") or (day_wx == "火" and liu_wx == "金") or (day_wx == "土" and liu_wx == "水") or (day_wx == "金" and liu_wx == "木") or (day_wx == "水" and liu_wx == "火"):
        relation = "被克"
    elif (day_wx == "木" and liu_wx == "金") or (day_wx == "火" and liu_wx == "水") or (day_wx == "土" and liu_wx == "木") or (day_wx == "金" and liu_wx == "火") or (day_wx == "水" and liu_wx == "土"):
        relation = "克对方"
    elif (day_wx == "木" and liu_wx == "水") or (day_wx == "火" and liu_wx == "木") or (day_wx == "土" and liu_wx == "火") or (day_wx == "金" and liu_wx == "土") or (day_wx == "水" and liu_wx == "金"):
        relation = "生对方"
    elif (day_wx == "木" and liu_wx == "火") or (day_wx == "火" and liu_wx == "土") or (day_wx == "土" and liu_wx == "金") or (day_wx == "金" and liu_wx == "水") or (day_wx == "水" and liu_wx == "木"):
        relation = "被生"
    
    return {
        "流年": liunian,
        "干支五行": liu_wx,
        "与日主关系": relation,
        "年份": year
    }

def dayun_liunian_analysis(bazi_info, current_age, current_year):
    """大运流年综合分析"""
    dayun = get_dayun(bazi_info, current_age)
    liunian = get_liunian(bazi_info, current_year)
    
    return {
        "大运": dayun,
        "流年": liunian
    }

# ==================== 完整综合分析 ====================

def build_integrated_profile(bazi, ziwei, zodiac=None, mbti=None):
    """八字 + 紫微 + 辅助标签的融合判断层"""
    day = bazi["日主"]
    strength = day["身强弱"]
    main_star = ziwei["命宫主星"]
    shen_gong = ziwei.get("身宫", "")
    keywords = ziwei.get('命宫关键词', '')

    if strength == "身弱":
        base = "底层偏敏感，做事更需要稳定感和托底环境"
    elif strength == "身强":
        base = "底层支撑力较强，遇事不容易轻易被带偏"
    else:
        base = "底层不算偏激，更多看环境会把这个人放大成什么样"

    star_line = f"命宫落{main_star}，对外呈现往往更偏{keywords}"

    shen_line = ""
    if shen_gong:
        shen_line = f"身宫落在{shen_gong}，说明现实里最容易发力、也最容易被牵动的，往往就是{shen_gong}对应的人生主题"

    tag_words = []
    if zodiac and zodiac.get("星座"):
        tag_words.append(zodiac.get("星座"))
    if mbti and isinstance(mbti, dict) and mbti.get("类型"):
        tag_words.append(mbti.get("类型"))

    style_line = ""
    if tag_words:
        style_line = f"辅助标签上也能看出，这个人带有{'、'.join(tag_words)}这一类气质和行为方式"

    focus = ziwei.get("重点宫位解读", {})
    merged = {
        "主轴": "；".join([x for x in [base, star_line, shen_line] if x]),
        "辅助标签": style_line,
        "紫微重点": focus,
        "生活版引导": {
            "整体句": f"先看整体，这类人不是表面一眼就很强的类型，而是{base}。{star_line}。",
            "性格句": f"放到人物气质上看，{main_star}这颗星会让她/他更容易表现出{keywords}这一面。",
            "展开句": shen_line if shen_line else "现实表现仍以主盘和命宫主星为主。"
        }
    }
    return merged



def full_mingli_analysis(birth_time, gender, age=None, year=None, mbti=None):
    """
    完整命理分析（八字+紫微+大运+流年+星座+MBTI）
    """
    bazi = parse(birth_time, gender)

    result = {
        "基础信息": {
            "出生时间": bazi["出生时间"],
            "农历": bazi["农历"],
            "性别": gender,
            "八字": bazi["八字"]
        },
        "日主分析": bazi["日主"],
        "性格特点": bazi["性格"]
    }

    ziwei = ziwei_analysis(bazi)
    result["紫微斗数"] = {
        "命宫主星": ziwei["命宫主星"],
        "星曜性质": ziwei["星曜性质"],
        "身宫": ziwei.get("身宫", ""),
        "重点宫位": ziwei.get("重点宫位", {}),
        "重点宫位解读": ziwei.get("重点宫位解读", {}),
        "十二宫": ziwei["十二宫"]
    }

    zodiac = zodiac_analysis(birth_time.get("month"), birth_time.get("day"))
    result["星座"] = zodiac

    mbti_result = None
    if mbti:
        mbti_result = mbti_analysis(mbti)
        result["MBTI"] = mbti_result

    result["融合判断"] = build_integrated_profile(bazi, ziwei, zodiac, mbti_result)

    if age and year:
        dayun = get_dayun(bazi, age)
        liunian = get_liunian(bazi, year)
        result["大运流年"] = {
            "大运方向": dayun["方向"],
            "8步大运": dayun["8步大运"],
            f"流年{year}": liunian
        }

    return result
