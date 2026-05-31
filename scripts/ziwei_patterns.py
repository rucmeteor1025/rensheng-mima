#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
紫微斗数格局识别 — Python 版

来源：移植自 https://github.com/Renhuai123/ziwei-doushu/blob/main/lib/ziwei/patterns.ts
（MIT 协议，倪海厦《天纪》体系 + 紫微斗数全书/全集 出处的 43 个经典格局）

设计原则：
1. 古书条件优先：每个格局列 "必须 / 加分 / 破格" 三层结构
2. 三合派立场：不使用宫干自化、大限四化、来因宫等飞星派工具
3. 庙旺利陷：用 brightness（bright=庙旺、normal=得利平、dim=陷不）
4. 三方四正会照：命宫 + 财帛 + 官禄 + 迁移
5. 夹宫：命宫前后两宫

入口：
    detect_patterns(result: ZiweiResult) -> List[Pattern]
"""
from __future__ import annotations

from dataclasses import dataclass, field, asdict
from typing import Any, Dict, List, Optional, Set


# ============================================================
# 常量
# ============================================================

BRANCHES = ["子", "丑", "寅", "卯", "辰", "巳", "午", "未", "申", "酉", "戌", "亥"]
BRANCH_IDX = {b: i for i, b in enumerate(BRANCHES)}

SHA_NAMES = ['擎羊', '陀罗', '火星', '铃星', '地空', '地劫']
SHA_HARD = ['擎羊', '陀罗', '火星', '铃星']   # 四煞
SHA_KONG = ['地空', '地劫']                  # 空劫
ZUO_YOU = ['左辅', '右弼']
CHANG_QU = ['文昌', '文曲']
KUI_YUE = ['天魁', '天钺']

MAJOR_STARS = {'紫微', '天机', '太阳', '武曲', '天同', '廉贞',
               '天府', '太阴', '贪狼', '巨门', '天相', '天梁', '七杀', '破军'}
SHA_STARS_SET = {'擎羊', '陀罗', '火星', '铃星', '地空', '地劫',
                 '天空', '旬空', '截路', '大耗', '天使', '天伤'}
LUCKY_STARS_SET = {'文昌', '文曲', '左辅', '右弼', '天魁', '天钺',
                   '禄存', '天马', '天官', '天福', '天才', '天寿',
                   '三台', '八座', '恩光', '天贵', '台辅',
                   '龙池', '凤阁', '红鸾', '天喜', '孤辰', '寡宿'}

BRIGHT_VALUES = {'庙', '旺'}
DIM_VALUES = {'陷', '不'}


# ============================================================
# 数据模型
# ============================================================

@dataclass
class Star:
    name: str
    type: str  # 'major' | 'lucky' | 'sha' | 'minor'
    brightness: Optional[str] = None  # 'bright' | 'normal' | 'dim'
    sihua: Optional[str] = None  # '禄' | '权' | '科' | '忌'


@dataclass
class Palace:
    branch: int                # 0-11
    branch_name: str           # "子"
    name: str                  # "命宫"
    stars: List[Star] = field(default_factory=list)
    is_body: bool = False


@dataclass
class Chart:
    ming_branch: int           # 命宫地支索引
    shen_branch: int           # 身宫地支索引
    palaces: List[Palace]
    year_sihua: Dict[str, str] # {"太阳": "禄", ...}  星 -> 化


@dataclass
class PatternCondition:
    required: List[str] = field(default_factory=list)
    bonus: List[str] = field(default_factory=list)
    breaking: List[str] = field(default_factory=list)


@dataclass
class Pattern:
    name: str
    level: str  # 'excellent' | 'good' | 'neutral' | 'caution'
    description: str
    palaces: List[str] = field(default_factory=list)
    conditions: Optional[PatternCondition] = None
    source: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        d = asdict(self)
        if d.get('conditions') is None:
            d.pop('conditions', None)
        return d


# ============================================================
# Adapter: 虾神算 ZiweiResult → Chart
# ============================================================

def _classify_star(name: str) -> str:
    if name in MAJOR_STARS: return 'major'
    if name in SHA_STARS_SET: return 'sha'
    if name in LUCKY_STARS_SET: return 'lucky'
    return 'minor'


def _map_brightness(b: Optional[str]) -> Optional[str]:
    if not b: return None
    if b in BRIGHT_VALUES: return 'bright'
    if b in DIM_VALUES: return 'dim'
    return 'normal'


def from_xiashensuan_result(result) -> Chart:
    """虾神算 ZiweiResult 或 dict（primary_chart）→ patterns 内部 Chart 模型"""
    # 统一从 dict 或 dataclass 取字段
    if hasattr(result, 'basic_info'):
        basic_info = result.basic_info
        palaces_raw = result.palaces
        transformations = result.transformations
    else:
        basic_info = result['basic_info']
        palaces_raw = result['palaces']
        transformations = result['transformations']

    # 生年四化：星 -> 化
    year_sihua: Dict[str, str] = {}
    for hua, detail in transformations.get('四化', {}).items():
        if detail.get('状态') == 'LOCATED' and detail.get('星曜'):
            year_sihua[detail['星曜']] = hua

    palaces: List[Palace] = []
    for p in palaces_raw:
        branch_name = p['宫支']
        if branch_name not in BRANCH_IDX:
            continue
        bidx = BRANCH_IDX[branch_name]
        bright_major = p.get('星曜亮度', {}).get('主星', {}) or {}
        bright_assist = p.get('星曜亮度', {}).get('辅星', {}) or {}

        stars: List[Star] = []
        for sname in p.get('主星', []):
            stars.append(Star(
                name=sname, type='major',
                brightness=_map_brightness(bright_major.get(sname)),
                sihua=year_sihua.get(sname),
            ))
        for sname in p.get('辅星', []):
            stars.append(Star(
                name=sname, type=_classify_star(sname),
                brightness=_map_brightness(bright_assist.get(sname)),
                sihua=year_sihua.get(sname),
            ))
        for sname in p.get('神煞', []):
            stars.append(Star(
                name=sname, type=_classify_star(sname),
                sihua=year_sihua.get(sname),
            ))

        palaces.append(Palace(
            branch=bidx, branch_name=branch_name,
            name=p['宫位'], stars=stars, is_body=bool(p.get('身宫')),
        ))

    # 追加生年四化作为"化禄/化权/化科/化忌"虚拟星，便于 sanFangAllStars 直接匹配
    for hua, detail in transformations.get('四化', {}).items():
        if detail.get('状态') != 'LOCATED': continue
        target = detail.get('宫支')
        if target not in BRANCH_IDX: continue
        for p in palaces:
            if p.branch_name == target:
                p.stars.append(Star(name=f'化{hua}', type='minor'))
                break

    ming_branch = BRANCH_IDX[basic_info['命宫']]
    shen_branch = BRANCH_IDX[basic_info['身宫']]
    return Chart(
        ming_branch=ming_branch, shen_branch=shen_branch,
        palaces=palaces, year_sihua=year_sihua,
    )


# ============================================================
# 辅助函数（patterns.ts L44-101 移植）
# ============================================================

def _wrap(b: int) -> int:
    return (b % 12 + 12) % 12


def get_palace_by_branch(chart: Chart, branch: int) -> Optional[Palace]:
    branch = _wrap(branch)
    return next((p for p in chart.palaces if p.branch == branch), None)


def get_san_fang_palaces(chart: Chart) -> List[Palace]:
    m = chart.ming_branch
    branches = {m, _wrap(m + 4), _wrap(m + 8), _wrap(m + 6)}
    return [p for p in chart.palaces if p.branch in branches]


def is_in_san_fang(chart: Chart, branch: int) -> bool:
    m = chart.ming_branch
    return _wrap(branch) in {m, _wrap(m + 4), _wrap(m + 8), _wrap(m + 6)}


def get_dui_gong(chart: Chart, branch: int) -> Optional[Palace]:
    return get_palace_by_branch(chart, branch + 6)


def get_jia_palaces(chart: Chart, branch: int) -> Dict[str, Optional[Palace]]:
    return {
        'prev': get_palace_by_branch(chart, branch + 11),
        'next': get_palace_by_branch(chart, branch + 1),
    }


def san_fang_all_stars(chart: Chart) -> Set[str]:
    out: Set[str] = set()
    for p in get_san_fang_palaces(chart):
        for s in p.stars:
            out.add(s.name)
    return out


def san_fang_sha_count(chart: Chart, names: List[str] = SHA_HARD) -> int:
    return sum(sha_count_in_palace(p, names) for p in get_san_fang_palaces(chart))


def find_star_palace(chart: Chart, star_name: str) -> Optional[Palace]:
    return next((p for p in chart.palaces
                 if any(s.name == star_name for s in p.stars)), None)


def has_star(palace: Palace, star_name: str) -> bool:
    return any(s.name == star_name for s in palace.stars)


def find_star(palace: Palace, star_name: str) -> Optional[Star]:
    return next((s for s in palace.stars if s.name == star_name), None)


def sha_count_in_palace(palace: Palace, names: List[str] = SHA_HARD) -> int:
    return sum(1 for s in palace.stars if s.name in names)


def has_sha_in_palace(palace: Palace, names: List[str] = SHA_NAMES) -> bool:
    return any(s.name in names for s in palace.stars)


def is_bright(palace: Palace, star_name: str) -> bool:
    s = find_star(palace, star_name)
    return bool(s and s.brightness == 'bright')


def is_dim(palace: Palace, star_name: str) -> bool:
    s = find_star(palace, star_name)
    return bool(s and s.brightness == 'dim')


def get_star_sihua(palace: Palace, star_name: str) -> Optional[str]:
    s = find_star(palace, star_name)
    return s.sihua if s else None


def get_major_star_names(palace: Palace) -> List[str]:
    return [s.name for s in palace.stars if s.type == 'major']


# ============================================================
# 入口（detector 函数在下方分段追加）
# ============================================================

def detect_patterns(result_or_chart) -> List[Pattern]:
    """
    主入口：接 ZiweiResult 或 Chart，返回识别到的格局列表
    """
    if isinstance(result_or_chart, Chart):
        chart = result_or_chart
    else:
        chart = from_xiashensuan_result(result_or_chart)

    ming = get_palace_by_branch(chart, chart.ming_branch)
    patterns: List[Pattern] = []
    if not ming:
        return patterns

    # 43 个 detector 按 ziwei-doushu 原顺序调用
    for fn in _DETECTORS:
        try:
            fn(chart, ming, patterns)
        except Exception as e:
            # 某个 detector 抛错不影响其他
            continue
    return patterns


# 占位，真正的 detector 列表在文件末尾用 _register 填充
_DETECTORS: List = []


def _register(fn):
    """detector 注册装饰器"""
    _DETECTORS.append(fn)
    return fn


# =============================================================
# 第 1 批：上格 (8) + 中格 (7) = 15 个 detector
# =============================================================

@_register
def detect_jun_chen_qing_hui(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """君臣庆会：紫微入命，左辅右弼同会"""
    if not has_star(ming, '紫微'): return
    sanfang = san_fang_all_stars(chart)
    if '左辅' not in sanfang or '右弼' not in sanfang: return
    required = ['紫微入命', '左辅右弼同会三方四正']
    bonus, breaking = [], []
    if '文昌' in sanfang or '文曲' in sanfang: bonus.append('再会文昌或文曲')
    if '天魁' in sanfang or '天钺' in sanfang: bonus.append('魁钺贵人加照')
    if get_star_sihua(ming, '紫微') == '权': bonus.append('紫微化权')
    if san_fang_sha_count(chart, SHA_KONG) >= 2: breaking.append('地空地劫双夹会照（紫微忌空劫）')
    patterns.append(Pattern(
        name='君臣庆会',
        level='good' if breaking else 'excellent',
        description='紫微入命，左辅右弼同会，帝王得贤臣辅佐，主大富大贵、统御之命。一生贵人不绝，宜走政商高位、跨界领袖之途。',
        palaces=['命宫'],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·君臣庆会格》',
    ))


@_register
def detect_zi_fu(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """紫府同宫"""
    ziwei = find_star_palace(chart, '紫微')
    tianfu = find_star_palace(chart, '天府')
    if not ziwei or not tianfu or ziwei.branch != tianfu.branch: return
    in_ming = ziwei.branch == chart.ming_branch
    required = ['紫微天府同入命宫'] if in_ming else ['紫微天府同宫（不在命宫，会照减力）']
    bonus, breaking = [], []
    sanfang = san_fang_all_stars(chart)
    if '左辅' in sanfang and '右弼' in sanfang: bonus.append('左辅右弼同会')
    if '文昌' in sanfang or '文曲' in sanfang: bonus.append('再会昌曲')
    if has_sha_in_palace(ziwei, SHA_KONG): breaking.append('紫府宫坐空劫（破紫府之贵气）')
    if sha_count_in_palace(ziwei, SHA_HARD) >= 2: breaking.append('紫府宫见双煞同坐')
    patterns.append(Pattern(
        name='紫府同宫',
        level='excellent' if in_ming and not breaking else 'good',
        description=('紫微天府同入命宫，帝相并临，尊贵之命。主品行端正、衣食无忧、有领导才能，宜担任要职。需要左右辅弼来配合方为完整大格。'
                     if in_ming else '紫微天府同宫但未坐命，主一生有贵人贵气依托，但本身不一定大富贵，需看会照吉煞而定。'),
        palaces=[ziwei.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·紫府同宫格》',
    ))


@_register
def detect_fu_xiang_chao_yuan(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """府相朝垣"""
    tianfu = find_star_palace(chart, '天府')
    tianxiang = find_star_palace(chart, '天相')
    if not tianfu or not tianxiang: return
    if not is_in_san_fang(chart, tianfu.branch) or not is_in_san_fang(chart, tianxiang.branch): return
    if tianfu.branch == chart.ming_branch and tianxiang.branch == chart.ming_branch: return
    if tianfu.branch == tianxiang.branch: return
    required = ['天府坐命三方', '天相坐命三方', '两星不同宫']
    bonus, breaking = [], []
    if has_star(ming, '禄存') or has_star(ming, '化禄'): bonus.append('命宫见禄')
    if '左辅' in san_fang_all_stars(chart): bonus.append('再会左辅')
    if has_sha_in_palace(ming, SHA_HARD): breaking.append('命宫坐煞星')
    if san_fang_sha_count(chart, SHA_HARD) >= 3: breaking.append('三方四正煞星过多')
    patterns.append(Pattern(
        name='府相朝垣',
        level='good' if breaking else 'excellent',
        description='天府天相分守命宫三方四正，文武并济、权印双辉，主一生衣食丰足、地位崇高。古书云"府相朝垣千钟食禄"，常见于政界、企业管理者。',
        palaces=[tianfu.name, tianxiang.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·府相朝垣格》',
    ))


@_register
def detect_yang_liang_chang_lu(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """阳梁昌禄"""
    sanfang = san_fang_all_stars(chart)
    if not all(s in sanfang for s in ['太阳', '天梁', '文昌', '禄存']): return
    sun = find_star_palace(chart, '太阳')
    liang = find_star_palace(chart, '天梁')
    required = ['太阳会命宫三方', '天梁会命宫三方', '文昌会命宫三方', '禄存会命宫三方']
    bonus, breaking = [], []
    if sun and is_bright(sun, '太阳'): bonus.append('太阳庙旺')
    if liang and is_bright(liang, '天梁'): bonus.append('天梁庙旺')
    if '化科' in sanfang: bonus.append('再会化科')
    if sun and is_dim(sun, '太阳'): breaking.append('太阳落陷（阳梁失辉）')
    if san_fang_sha_count(chart, SHA_HARD) >= 2: breaking.append('三方煞重')
    patterns.append(Pattern(
        name='阳梁昌禄',
        level='good' if breaking else 'excellent',
        description='太阳、天梁、文昌、禄存四星齐会命宫三方，号称"科举之星"，主清贵显达、考运极佳，宜走学术、文教、研究、专业认证之路，一生功名易就。',
        palaces=[sun.name if sun else '', liang.name if liang else ''],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·阳梁昌禄格》',
    ))


@_register
def detect_huo_tan_ling_tan(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """火贪格 / 铃贪格"""
    tan = find_star_palace(chart, '贪狼')
    if not tan: return
    huo = find_star_palace(chart, '火星')
    ling = find_star_palace(chart, '铃星')
    for sha_name, sha_palace in [('火星', huo), ('铃星', ling)]:
        if not sha_palace: continue
        b = tan.branch
        same_or_trine = (b == sha_palace.branch
                         or _wrap(b + 4) == sha_palace.branch
                         or _wrap(b + 8) == sha_palace.branch
                         or _wrap(b + 6) == sha_palace.branch)
        if not same_or_trine: continue
        if not is_in_san_fang(chart, tan.branch): continue
        same = tan.branch == sha_palace.branch
        required = [f'贪狼{"同宫" if same else "会照"}{sha_name}', '贪狼会照命宫三方']
        bonus, breaking = [], []
        if is_bright(tan, '贪狼'): bonus.append('贪狼庙旺')
        sihua = get_star_sihua(tan, '贪狼')
        if sihua in ('禄', '权'): bonus.append('贪狼化禄/化权')
        if has_sha_in_palace(tan, ['擎羊', '陀罗']): breaking.append('贪狼宫又见羊陀（破横发之力）')
        if has_sha_in_palace(tan, SHA_KONG): breaking.append('贪狼遇空劫（财来财去）')
        patterns.append(Pattern(
            name='火贪格' if sha_name == '火星' else '铃贪格',
            level='good' if breaking else 'excellent',
            description=f'贪狼遇{sha_name}{"同宫" if same else "三方会照"}，主突发横财、突如其来的机遇。古书云"贪狼遇火铃，必发横财"，但来得快去得也快，宜见好就收。'
                        + ('本盘破格条件已触发，发力打折。' if breaking else ''),
            palaces=[tan.name, sha_palace.name],
            conditions=PatternCondition(required, bonus, breaking),
            source='《紫微斗数骨髓赋》',
        ))


@_register
def detect_wu_tan(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """武贪格"""
    wu = find_star_palace(chart, '武曲')
    tan = find_star_palace(chart, '贪狼')
    if not wu or not tan: return
    same_or_oppose = wu.branch == tan.branch or _wrap(wu.branch + 6) == tan.branch
    if not same_or_oppose: return
    if not is_in_san_fang(chart, wu.branch) and not is_in_san_fang(chart, tan.branch): return
    required = [
        '武曲贪狼同宫（丑/未）' if wu.branch == tan.branch else '武曲贪狼对宫拱照',
        '会照命宫三方',
    ]
    bonus, breaking = [], []
    sanfang = san_fang_all_stars(chart)
    if '火星' in sanfang or '铃星' in sanfang: bonus.append('再遇火星/铃星（火贪/铃贪叠加）')
    if get_star_sihua(wu, '武曲') == '禄': bonus.append('武曲化禄')
    if has_sha_in_palace(wu, ['擎羊', '陀罗']): breaking.append('武贪宫见羊陀')
    if has_sha_in_palace(wu, SHA_KONG): breaking.append('武贪宫遇空劫')
    patterns.append(Pattern(
        name='武贪格',
        level='good' if breaking else 'excellent',
        description='武曲贪狼会命，财星与桃花欲望星交辉，古书云"武贪不发少年人"——三十岁后方能厚积薄发。主中年以后大富大贵，财源由人脉、应酬、欲望管理而来，适合金融、投机、销售、娱乐业。',
        palaces=[wu.name, tan.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数骨髓赋》',
    ))


@_register
def detect_sha_po_lang(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """杀破狼"""
    sanfang = san_fang_all_stars(chart)
    has = [s for s in ['七杀', '破军', '贪狼'] if s in sanfang]
    if len(has) < 3: return
    required = ['七杀、破军、贪狼三星齐入命宫三方四正']
    bonus, breaking = [], []
    if '化禄' in sanfang or '化权' in sanfang: bonus.append('三方有化禄或化权（动得有力）')
    if '左辅' in sanfang and '右弼' in sanfang: bonus.append('辅弼同会（变动中得贵人）')
    if san_fang_sha_count(chart, SHA_HARD) >= 3: breaking.append('煞星过重（动而无成）')
    if has_sha_in_palace(ming, SHA_KONG): breaking.append('命坐空劫（动得辛苦）')
    palaces_names = [p.name for p in get_san_fang_palaces(chart)
                     if get_major_star_names(p) and get_major_star_names(p)[0] in has]
    patterns.append(Pattern(
        name='杀破狼',
        level='caution' if breaking else 'good',
        description='七杀、破军、贪狼三星会命，开创闯荡之命格。一生变动多、不甘平凡，宜创业、军警、业务、销售。中年后才能稳定守成，年轻时易因冲动失利。',
        palaces=palaces_names,
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·杀破狼》',
    ))


@_register
def detect_ji_yue_tong_liang(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """机月同梁（四星齐）"""
    sanfang = san_fang_all_stars(chart)
    has = [s for s in ['天机', '太阴', '天同', '天梁'] if s in sanfang]
    if len(has) < 4: return
    required = ['天机、太阴、天同、天梁四星齐入命宫三方四正']
    bonus, breaking = [], []
    if '文昌' in sanfang or '文曲' in sanfang: bonus.append('再会昌曲')
    if '化科' in sanfang: bonus.append('再会化科')
    if san_fang_sha_count(chart, SHA_HARD) >= 3: breaking.append('煞星过多（机月同梁忌煞）')
    if has_sha_in_palace(ming, SHA_HARD): breaking.append('命宫坐煞')
    palaces_names = [p.name for p in get_san_fang_palaces(chart)
                     if any(s in get_major_star_names(p) for s in has)]
    patterns.append(Pattern(
        name='机月同梁',
        level='good' if breaking else 'excellent',
        description='天机太阴天同天梁四星齐入命迁财官，文质彬彬、聪慧善谋。最适合公职、学术、文艺、医疗、服务等需稳定累积的行业，不宜大冒险大投机。',
        palaces=palaces_names,
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·机月同梁格》',
    ))


@_register
def detect_lian_xiang(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """廉贞天相同宫"""
    lian = find_star_palace(chart, '廉贞')
    xiang = find_star_palace(chart, '天相')
    if not lian or not xiang or lian.branch != xiang.branch: return
    in_ming = lian.branch == chart.ming_branch
    required = ['廉贞天相同宫']
    bonus, breaking = [], []
    if has_star(lian, '禄存') or get_star_sihua(lian, '廉贞') == '禄': bonus.append('见禄存或廉贞化禄')
    if '左辅' in san_fang_all_stars(chart): bonus.append('左辅会照')
    if has_sha_in_palace(lian, ['擎羊']): breaking.append('廉相宫坐擎羊（廉杀羊倾向）')
    if get_star_sihua(lian, '廉贞') == '忌': breaking.append('廉贞化忌')
    patterns.append(Pattern(
        name='廉贞天相格',
        level='caution' if breaking else ('good' if in_ming else 'neutral'),
        description='廉贞天相同宫，印绶格局，主秉公处事、清廉之名，宜任公职、行政管理、法务、企划。怕见擎羊化忌，则反主官非。',
        palaces=[lian.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书》',
    ))


@_register
def detect_wu_qi_sha(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """武曲七杀同宫"""
    wu = find_star_palace(chart, '武曲')
    qi = find_star_palace(chart, '七杀')
    if not wu or not qi or wu.branch != qi.branch: return
    in_ming = wu.branch == chart.ming_branch
    required = ['武曲七杀同宫']
    bonus, breaking = [], []
    sihua = get_star_sihua(wu, '武曲')
    if sihua == '权': bonus.append('武曲化权')
    if sihua == '禄': bonus.append('武曲化禄')
    if sihua == '忌': breaking.append('武曲化忌（武曲化忌为财劫之兆）')
    if has_sha_in_palace(wu, ['擎羊', '陀罗', '火星', '铃星']): breaking.append('武杀宫煞星过多')
    patterns.append(Pattern(
        name='武曲七杀',
        level='caution' if breaking else ('excellent' if in_ming else 'good'),
        description='武曲七杀同宫，将星配财星，主果决刚毅、理财能力强，适合金融、军警、创业。但忌见化忌煞星，否则凶险。一生奋斗、积财但操心。',
        palaces=[wu.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书》',
    ))


@_register
def detect_tong_liang(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """天同天梁同宫"""
    tong = find_star_palace(chart, '天同')
    liang = find_star_palace(chart, '天梁')
    if not tong or not liang or tong.branch != liang.branch: return
    required = ['天同天梁同宫']
    bonus, breaking = [], []
    if '文昌' in san_fang_all_stars(chart): bonus.append('文昌会照')
    if get_star_sihua(tong, '天同') == '禄': bonus.append('天同化禄')
    if has_sha_in_palace(tong, SHA_HARD): breaking.append('煞星同坐')
    patterns.append(Pattern(
        name='天同天梁格',
        level='neutral' if breaking else 'good',
        description='天同天梁同宫，福星与荫星共会，主宽厚和善、乐于助人，宜医疗、教育、宗教、社会公益。但偏温和保守，难成大富大贵之局。',
        palaces=[tong.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书》',
    ))


@_register
def detect_ri_yue_tong_gong(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """日月同宫（丑/未）"""
    sun = find_star_palace(chart, '太阳')
    moon = find_star_palace(chart, '太阴')
    if not sun or not moon or sun.branch != moon.branch: return
    if sun.branch not in (1, 7): return
    in_ming = sun.branch == chart.ming_branch
    required = [f'太阳太阴同入{BRANCHES[sun.branch]}宫']
    bonus, breaking = [], []
    if sun.branch == 7: bonus.append('未宫日月同辉（古书云未宫日月双美）')
    sanfang = san_fang_all_stars(chart)
    if '文昌' in sanfang and '文曲' in sanfang: bonus.append('昌曲会照')
    if has_sha_in_palace(sun, SHA_HARD): breaking.append('日月宫煞星同坐')
    patterns.append(Pattern(
        name='日月同宫',
        level='good' if breaking else ('excellent' if in_ming else 'good'),
        description=f'太阳太阴于{BRANCHES[sun.branch]}宫同宫，阴阳平衡，文武兼备。主异性缘佳、事业顺遂、名声远播。'
                    + ('未宫日月双美尤佳。' if sun.branch == 7 else '丑宫日月同宫力量较平。'),
        palaces=[sun.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书》',
    ))


@_register
def detect_ri_yue_jia_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """日月夹命"""
    jia = get_jia_palaces(chart, chart.ming_branch)
    prev, nxt = jia['prev'], jia['next']
    if not prev or not nxt: return
    p_sun, p_moon = has_star(prev, '太阳'), has_star(prev, '太阴')
    n_sun, n_moon = has_star(nxt, '太阳'), has_star(nxt, '太阴')
    if not ((p_sun and n_moon) or (p_moon and n_sun)): return
    sun_palace = prev if p_sun else nxt
    moon_palace = prev if p_moon else nxt
    required = ['太阳太阴分居命宫前后两宫']
    bonus, breaking = [], []
    if is_bright(sun_palace, '太阳'): bonus.append('太阳庙旺')
    if is_bright(moon_palace, '太阴'): bonus.append('太阴庙旺')
    if is_dim(sun_palace, '太阳') or is_dim(moon_palace, '太阴'): breaking.append('日月落陷（夹命无光）')
    patterns.append(Pattern(
        name='日月夹命',
        level='good' if breaking else 'excellent',
        description='太阳太阴分居命宫两侧夹照，光明磊落，一生贵人相助，事业蓬勃。男主官贵，女主旺夫兴家。日月须不落陷方为真夹。',
        palaces=[sun_palace.name, moon_palace.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·日月夹命》',
    ))


@_register
def detect_ju_ri_tong_gong(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """巨日同宫（寅/申）"""
    ju = find_star_palace(chart, '巨门')
    sun = find_star_palace(chart, '太阳')
    if not ju or not sun or ju.branch != sun.branch: return
    if ju.branch not in (2, 8): return
    in_ming = ju.branch == chart.ming_branch
    required = [f'巨门太阳同入{BRANCHES[ju.branch]}宫']
    bonus, breaking = [], []
    if ju.branch == 2: bonus.append('寅宫太阳庙旺，巨门得日光化解是非')
    sihua = get_star_sihua(ju, '巨门')
    if sihua in ('禄', '权'): bonus.append('巨门化禄/化权（口才生财）')
    if sihua == '忌': breaking.append('巨门化忌（口舌官非）')
    if ju.branch == 8: breaking.append('申宫太阳偏西，巨门暗曜更显')
    level = 'caution' if breaking else ('excellent' if (in_ming and ju.branch == 2) else 'good')
    patterns.append(Pattern(
        name='巨日同宫',
        level=level,
        description=f'巨门太阳同{BRANCHES[ju.branch]}宫，太阳化解巨门暗曜，主以口才、传媒、外语、专业立业。寅宫为佳，申宫力减。怕巨门化忌则官非。',
        palaces=[ju.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书·巨日同宫》',
    ))


@_register
def detect_shi_zhong_yin_yu(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """石中隐玉：巨门入命子午"""
    if not has_star(ming, '巨门'): return
    if ming.branch not in (0, 6): return
    required = [f'巨门入命于{BRANCHES[ming.branch]}宫']
    bonus, breaking = [], []
    sihua = get_star_sihua(ming, '巨门')
    if sihua in ('禄', '权'): bonus.append('巨门化禄/化权')
    if '文昌' in san_fang_all_stars(chart): bonus.append('文昌会照（石中隐玉得明）')
    if sihua == '忌': breaking.append('巨门化忌（玉藏深泥）')
    if has_sha_in_palace(ming, SHA_HARD): breaking.append('命坐煞星')
    patterns.append(Pattern(
        name='石中隐玉',
        level='caution' if breaking else 'excellent',
        description='巨门坐命子午，外表平凡而内蕴才学。早年默默无闻、中年方显贵气，宜走专业、研究、口才、传媒。需有禄权或文昌相助方能"凿石见玉"。',
        palaces=['命宫'],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数骨髓赋·石中隐玉》',
    ))


# =============================================================
# 第 2 批：中格剩余 (2) + 助力格 (6) + 恶格 (8) = 16 个 detector
# =============================================================

@_register
def detect_ming_zhu_chu_hai(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """明珠出海：命在未空宫，对宫丑日月同度"""
    if ming.branch != 7: return
    if len(get_major_star_names(ming)) > 0: return
    dui = get_dui_gong(chart, ming.branch)
    if not dui: return
    if not has_star(dui, '太阳') or not has_star(dui, '太阴'): return
    required = ['命宫在未为空宫', '对宫丑宫为太阳太阴同度']
    bonus, breaking = [], []
    sanfang = san_fang_all_stars(chart)
    if '文昌' in sanfang or '文曲' in sanfang: bonus.append('再会昌曲')
    if '左辅' in sanfang or '右弼' in sanfang: bonus.append('辅弼相助')
    if san_fang_sha_count(chart, SHA_HARD) >= 2: breaking.append('煞星会照（珠光黯淡）')
    patterns.append(Pattern(
        name='明珠出海',
        level='good' if breaking else 'excellent',
        description='命未空宫，对宫丑宫日月同辉拱照，号"明珠出海"。主出生平凡、后天努力出头，宜远赴他乡、学术研究或大公司高位，主大富大贵。',
        palaces=['命宫', dui.name],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全集·明珠出海》',
    ))


@_register
def detect_ziwei_in_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """紫微独坐入命"""
    if not has_star(ming, '紫微') or has_star(ming, '天府'): return
    required = ['紫微独坐命宫（无天府同坐）']
    bonus, breaking = [], []
    sanfang = san_fang_all_stars(chart)
    if '左辅' in sanfang and '右弼' in sanfang: bonus.append('左辅右弼同会')
    if '文昌' in sanfang and '文曲' in sanfang: bonus.append('文昌文曲同会')
    if '左辅' not in sanfang and '右弼' not in sanfang: breaking.append('无辅弼（孤君无臣）')
    if has_sha_in_palace(ming, SHA_KONG): breaking.append('紫微遇空劫（古书最忌）')
    level = 'caution' if breaking else ('excellent' if bonus else 'good')
    patterns.append(Pattern(
        name='紫微入命',
        level=level,
        description='紫微独坐命宫，帝王之星，自尊心强、有领导魅力。但紫微最忌"在野孤君"——若无左右辅弼相会，反成孤高自傲、易招毁谤。',
        palaces=['命宫'],
        conditions=PatternCondition(required, bonus, breaking),
        source='《紫微斗数全书》',
    ))


@_register
def detect_fu_bi_jia_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """辅弼夹命"""
    jia = get_jia_palaces(chart, chart.ming_branch)
    prev, nxt = jia['prev'], jia['next']
    if not prev or not nxt: return
    pz, py = has_star(prev, '左辅'), has_star(prev, '右弼')
    nz, ny = has_star(nxt, '左辅'), has_star(nxt, '右弼')
    if not ((pz and ny) or (py and nz)): return
    required = ['左辅右弼分居命宫前后两宫']
    bonus = []
    sanfang = san_fang_all_stars(chart)
    if '天魁' in sanfang or '天钺' in sanfang: bonus.append('再会魁钺')
    patterns.append(Pattern(
        name='辅弼夹命',
        level='excellent',
        description='左辅右弼夹命，一生贵人不断、逢凶化吉。适合走仕途、大企业管理，有贵人提携之命。古书云"左辅右弼，终身福厚"。',
        palaces=['命宫', prev.name, nxt.name],
        conditions=PatternCondition(required, bonus),
        source='《紫微斗数全书·辅弼夹命》',
    ))


@_register
def detect_chang_qu_jia_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """昌曲夹命"""
    jia = get_jia_palaces(chart, chart.ming_branch)
    prev, nxt = jia['prev'], jia['next']
    if not prev or not nxt: return
    pc, pq = has_star(prev, '文昌'), has_star(prev, '文曲')
    nc, nq = has_star(nxt, '文昌'), has_star(nxt, '文曲')
    if not ((pc and nq) or (pq and nc)): return
    patterns.append(Pattern(
        name='昌曲夹命',
        level='excellent',
        description='文昌文曲夹命宫，主聪明俊秀、文采斐然，宜走文教、学术、艺术、写作。古书云"昌曲夹命主科甲"，最利考运。',
        palaces=['命宫', prev.name, nxt.name],
        conditions=PatternCondition(['文昌文曲分居命宫前后两宫']),
        source='《紫微斗数全书》',
    ))


@_register
def detect_kui_yue_jia_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """魁钺夹命"""
    jia = get_jia_palaces(chart, chart.ming_branch)
    prev, nxt = jia['prev'], jia['next']
    if not prev or not nxt: return
    ok_a = has_star(prev, '天魁') and has_star(nxt, '天钺')
    ok_b = has_star(prev, '天钺') and has_star(nxt, '天魁')
    if not ok_a and not ok_b: return
    patterns.append(Pattern(
        name='魁钺夹命',
        level='good',
        description='天魁天钺夹命，男称天乙、女称玉堂，一生贵人提携。考试、求职、关键时刻常有意外贵人相助。',
        palaces=['命宫', prev.name, nxt.name],
        conditions=PatternCondition(['天魁天钺分居命宫前后两宫']),
        source='《紫微斗数全书》',
    ))


@_register
def detect_shuang_lu_chao_yuan(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """双禄朝垣：化禄+禄存同会三方"""
    sanfang = get_san_fang_palaces(chart)
    hua_lu = any(s.sihua == '禄' for p in sanfang for s in p.stars)
    lu_cun = any(has_star(p, '禄存') for p in sanfang)
    if not (hua_lu and lu_cun): return
    breaking = ['命坐空劫（双禄遇空，财来财去）'] if has_sha_in_palace(ming, SHA_KONG) else []
    patterns.append(Pattern(
        name='双禄朝垣',
        level='excellent',
        description='化禄、禄存同会命宫三方四正，财源涌动、衣食丰足。古书云"双禄朝垣，富比陶朱"，主一生不愁财，多有正财横财兼得。',
        palaces=[p.name for p in sanfang],
        conditions=PatternCondition(
            required=['化禄会照三方四正', '禄存会照三方四正'],
            breaking=breaking,
        ),
        source='《紫微斗数全书·双禄朝垣》',
    ))


@_register
def detect_san_qi_jia_hui(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """三奇加会：禄权科齐会三方"""
    sanfang = get_san_fang_palaces(chart)
    lu = quan = ke = False
    for p in sanfang:
        for s in p.stars:
            if s.sihua == '禄': lu = True
            if s.sihua == '权': quan = True
            if s.sihua == '科': ke = True
    if not (lu and quan and ke): return
    patterns.append(Pattern(
        name='三奇加会',
        level='excellent',
        description='化禄、化权、化科三吉化齐会命宫三方四正，号称"三奇加会"。主一生功名、财富、贵人三全，是紫微斗数最高吉格之一。',
        palaces=[p.name for p in sanfang],
        conditions=PatternCondition(['化禄、化权、化科三吉化齐会命宫三方四正']),
        source='《紫微斗数全书·三奇加会》',
    ))


@_register
def detect_hua_lu_ru_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """化禄入命"""
    hua_lu_star = next((s for s in ming.stars if s.sihua == '禄' and s.type == 'major'), None)
    if not hua_lu_star: return
    name = hua_lu_star.name
    detail = ('武曲化禄属正财，宜实业、金融。' if name == '武曲'
              else '太阴化禄属阴财、不动产。' if name == '太阴'
              else '贪狼化禄属人脉财、桃花财。' if name == '贪狼' else '')
    patterns.append(Pattern(
        name=f'{name}化禄入命',
        level='good',
        description=f'{name}化禄坐命，主生财顺利、人缘佳、机缘多。{detail}',
        palaces=['命宫'],
        conditions=PatternCondition([f'{name}化禄坐命宫']),
        source='《紫微斗数全书》',
    ))


@_register
def detect_hua_ji_ru_ming_qian(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """化忌入命/迁"""
    qian_branch = _wrap(chart.ming_branch + 6)
    for palace in chart.palaces:
        if palace.branch != chart.ming_branch and palace.branch != qian_branch: continue
        ji_star = next((s for s in palace.stars if s.sihua == '忌' and s.type == 'major'), None)
        if not ji_star: continue
        in_ming = palace.branch == chart.ming_branch
        desc = (f'{ji_star.name}化忌坐命宫，需留意自身固执、心理障碍或健康隐患，凡事退一步思考。化忌不一定坏，代表此星能量需要特别关注。'
                if in_ming
                else f'{ji_star.name}化忌坐迁移宫，外出、远行、人际关系易有波折，宜守不宜动。')
        patterns.append(Pattern(
            name=f'{ji_star.name}化忌入{"命" if in_ming else "迁"}',
            level='caution',
            description=desc,
            palaces=[palace.name],
            conditions=PatternCondition([f'{ji_star.name}化忌坐{"命" if in_ming else "迁"}宫']),
            source='《紫微斗数全书》',
        ))


@_register
def detect_yang_tuo_jia_ji(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """羊陀夹忌：化忌坐命被羊陀夹"""
    for palace in chart.palaces:
        ji_star = next((s for s in palace.stars if s.sihua == '忌'), None)
        if not ji_star: continue
        if palace.branch != chart.ming_branch: continue
        jia = get_jia_palaces(chart, palace.branch)
        prev, nxt = jia['prev'], jia['next']
        if not prev or not nxt: continue
        ok = (has_star(prev, '擎羊') and has_star(nxt, '陀罗')) \
             or (has_star(prev, '陀罗') and has_star(nxt, '擎羊'))
        if not ok: continue
        patterns.append(Pattern(
            name='羊陀夹忌',
            level='caution',
            description='化忌坐命，左右擎羊陀罗夹命，古书云"羊陀夹忌为败局"，主一生劳碌奔波、坎坷不顺、身心俱疲。需以德行修养与积极做事化解，凡事谨慎为上。',
            palaces=['命宫', prev.name, nxt.name],
            conditions=PatternCondition(['化忌坐命', '擎羊陀罗分居命宫前后两宫']),
            source='《紫微斗数骨髓赋·羊陀夹忌》',
        ))
        return


@_register
def detect_huo_ling_jia_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """火铃夹命"""
    jia = get_jia_palaces(chart, chart.ming_branch)
    prev, nxt = jia['prev'], jia['next']
    if not prev or not nxt: return
    ok_a = has_star(prev, '火星') and has_star(nxt, '铃星')
    ok_b = has_star(prev, '铃星') and has_star(nxt, '火星')
    if not ok_a and not ok_b: return
    patterns.append(Pattern(
        name='火铃夹命',
        level='caution',
        description='火星铃星分居命宫前后两宫夹命，主性急、易冲动、突发意外或纠纷。需培养耐性、避免冲动决策。',
        palaces=['命宫', prev.name, nxt.name],
        conditions=PatternCondition(['火星铃星分居命宫前后两宫']),
        source='《紫微斗数全书》',
    ))


@_register
def detect_kong_jie_jia_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """空劫夹命"""
    jia = get_jia_palaces(chart, chart.ming_branch)
    prev, nxt = jia['prev'], jia['next']
    if not prev or not nxt: return
    ok_a = has_star(prev, '地空') and has_star(nxt, '地劫')
    ok_b = has_star(prev, '地劫') and has_star(nxt, '地空')
    if not ok_a and not ok_b: return
    patterns.append(Pattern(
        name='空劫夹命',
        level='caution',
        description='地空地劫夹命，主财来财去、思想脱俗、易遁入宗教哲学。古书云"空劫夹命，财不聚"。宜技艺、宗教、研究等不重物质之业。',
        palaces=['命宫', prev.name, nxt.name],
        conditions=PatternCondition(['地空地劫分居命宫前后两宫']),
        source='《紫微斗数全书》',
    ))


@_register
def detect_lian_sha_yang(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """廉杀羊"""
    sanfang = san_fang_all_stars(chart)
    if not (all(s in sanfang for s in ['廉贞', '七杀', '擎羊'])): return
    patterns.append(Pattern(
        name='廉杀羊',
        level='caution',
        description='廉贞、七杀、擎羊三星会照命宫三方，古书警示之凶格。主血光、官非、意外。本命有此格不必惊慌，但流年大限再触发时需特别谨慎驾驶、避免冲突、注意手术风险。',
        palaces=['命宫'],
        conditions=PatternCondition(['廉贞、七杀、擎羊三星会照三方四正']),
        source='《紫微斗数全书·廉杀羊》',
    ))


@_register
def detect_ju_huo_yang(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """巨火羊"""
    sanfang = san_fang_all_stars(chart)
    if not (all(s in sanfang for s in ['巨门', '火星', '擎羊'])): return
    patterns.append(Pattern(
        name='巨火羊',
        level='caution',
        description='巨门、火星、擎羊三星会照，古书云"巨火羊，终身缢死"——古时凶格。现代理解为：易因口舌、激烈冲突而招大祸。需修身养性、慎言慎行，避免极端情绪。',
        palaces=['命宫'],
        conditions=PatternCondition(['巨门、火星、擎羊三星会照三方四正']),
        source='《紫微斗数骨髓赋·巨火羊》',
    ))


@_register
def detect_ling_chang_tuo_wu(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """铃昌陀武"""
    sanfang = san_fang_all_stars(chart)
    if not (all(s in sanfang for s in ['铃星', '文昌', '陀罗', '武曲'])): return
    patterns.append(Pattern(
        name='铃昌陀武',
        level='caution',
        description='铃星、文昌、陀罗、武曲四星齐会，古书云"铃昌陀武，限至投河"——古时大凶格。本命有此组合本身不必恐慌，但流年大限触发时需高度警觉重大决策、情绪起伏、水边活动。',
        palaces=['命宫'],
        conditions=PatternCondition(['铃星、文昌、陀罗、武曲四星会照三方四正']),
        source='《紫微斗数骨髓赋·铃昌陀武》',
    ))


@_register
def detect_ma_tou_dai_jian(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """马头带箭：擎羊在午宫坐命"""
    if ming.branch != 6: return
    if not has_star(ming, '擎羊'): return
    required = ['擎羊于午宫坐命']
    bonus = []
    sanfang = san_fang_all_stars(chart)
    if '七杀' in sanfang or '破军' in sanfang: bonus.append('再会七杀或破军（武职大贵）')
    if '天魁' in sanfang or '天钺' in sanfang: bonus.append('魁钺加照')
    patterns.append(Pattern(
        name='马头带箭',
        level='good' if bonus else 'caution',
        description='擎羊于午宫坐命，号"马头带箭"。古书云"威镇边疆"——主刚毅果决、有冲杀之力，宜军警武职、运动员、外科医师。但同时主危险与意外，需配合杀破狼或贵人方为大格，否则反主血光。',
        palaces=['命宫'],
        conditions=PatternCondition(required, bonus),
        source='《紫微斗数骨髓赋·马头带箭》',
    ))


# =============================================================
# 第 3 批：基础格局 = 12 个 detector（提升识别覆盖率）
# =============================================================

@_register
def detect_lu_cun_shou_shen(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """禄存守命/身"""
    lc_palace = find_star_palace(chart, '禄存')
    if not lc_palace: return
    in_ming = lc_palace.branch == chart.ming_branch
    in_shen = lc_palace.branch == chart.shen_branch
    if not in_ming and not in_shen: return
    name = '禄存守命' if in_ming else '禄存守身'
    desc = ('禄存坐命，主一生衣食无忧、财禄稳定。性格保守，善积累，但羊陀夹禄须防小人。最宜配化禄、左辅右弼方为大格。'
            if in_ming
            else '禄存入身宫，主中年后财源稳定、得禄自享。倪师说「禄存入身，财气近身」——配偶或事业方向能带来稳定财禄。')
    patterns.append(Pattern(
        name=name, level='good', description=desc,
        palaces=['命宫' if in_ming else '身宫'],
        conditions=PatternCondition([f'禄存入{"命宫" if in_ming else "身宫"}']),
        source='《紫微斗数全书·禄存星》',
    ))


@_register
def detect_tian_ma_ru_ming(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """天马入命/迁"""
    tm_palace = find_star_palace(chart, '天马')
    if not tm_palace: return
    in_ming = tm_palace.branch == chart.ming_branch
    in_qian = tm_palace.branch == _wrap(chart.ming_branch + 6)
    if not in_ming and not in_qian: return
    name = '天马入命' if in_ming else '天马在迁'
    desc = ('天马坐命，主一生奔波、动中得财，宜走商旅、外勤、跨界发展。倪师说「天马入命，无禄不发」——若再会禄存或化禄即「禄马交驰」之富格。'
            if in_ming
            else '天马在迁移宫，主外出有利、远行得财，宜异乡发展。配化禄主异地生财，配煞星则旅途多波折。')
    patterns.append(Pattern(
        name=name, level='neutral', description=desc,
        palaces=[tm_palace.name],
        conditions=PatternCondition([f'天马入{"命宫" if in_ming else "迁移宫"}']),
        source='《紫微斗数全书·天马星》',
    ))


@_register
def detect_hua_lu_ru_cai(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """化禄入财"""
    cai = next((p for p in chart.palaces if p.name in ('财帛宫', '财帛')), None)
    if not cai: return
    lu_star = next((s for s in cai.stars if s.type == 'major' and s.sihua == '禄'), None)
    if not lu_star: return
    patterns.append(Pattern(
        name='化禄入财',
        level='good',
        description=f'{lu_star.name}化禄入财帛宫，主财源畅通、收入稳定。倪师讲化禄是「正财」象征——这个化禄星所代表的能力（{lu_star.name}的核心特质）是你赚钱的主轴。配禄存或天马则财源更广。',
        palaces=['财帛宫'],
        conditions=PatternCondition([f'{lu_star.name}化禄入财帛宫']),
        source='《紫微斗数全书·四化论》',
    ))


@_register
def detect_hua_quan_ru_guan(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """化权入官"""
    guan = next((p for p in chart.palaces if p.name in ('官禄宫', '官禄')), None)
    if not guan: return
    quan_star = next((s for s in guan.stars if s.type == 'major' and s.sihua == '权'), None)
    if not quan_star: return
    patterns.append(Pattern(
        name='化权入官',
        level='good',
        description=f'{quan_star.name}化权入官禄宫，主事业有掌控力、能担当独当一面的职位。化权代表权力与执行力——{quan_star.name}化权说明你在事业上能成为决策者或核心执行者，宜走管理或技术权威路线。',
        palaces=['官禄宫'],
        conditions=PatternCondition([f'{quan_star.name}化权入官禄宫']),
        source='《紫微斗数全书·四化论》',
    ))


@_register
def detect_hua_ke_ru_ming_shen(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """化科入命/身"""
    shen = next((p for p in chart.palaces if p.branch == chart.shen_branch), None)
    candidates = [ming] + ([shen] if shen and shen.branch != ming.branch else [])
    for p in candidates:
        ke_star = next((s for s in p.stars if s.type == 'major' and s.sihua == '科'), None)
        if not ke_star: continue
        is_ming = p.branch == chart.ming_branch
        patterns.append(Pattern(
            name='化科入命' if is_ming else '化科入身',
            level='good',
            description=f'{ke_star.name}化科入{"命" if is_ming else "身"}宫，主名声、文书、学术运。倪师讲化科是「贵人星」——{ke_star.name}化科带来的是被人看重的特质，宜从事文书、教育、研究、咨询、文创等"以名取利"的方向。',
            palaces=['命宫' if is_ming else '身宫'],
            conditions=PatternCondition([f'{ke_star.name}化科入{"命宫" if is_ming else "身宫"}']),
            source='《紫微斗数全书·四化论》',
        ))
        return


@_register
def detect_ji_yue_tong_liang_partial(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """机月同梁三星会（降级版）"""
    sanfang = san_fang_all_stars(chart)
    has = [s for s in ['天机', '太阴', '天同', '天梁'] if s in sanfang]
    if len(has) != 3: return
    missing = [s for s in ['天机', '太阴', '天同', '天梁'] if s not in sanfang]
    palaces_names = [p.name for p in get_san_fang_palaces(chart)
                     if any(s in get_major_star_names(p) for s in has)]
    patterns.append(Pattern(
        name='机月同梁三星会',
        level='neutral',
        description=f'三方四正会齐{"、".join(has)}，差{"、".join(missing)}未会。机月同梁不全格，文质带谋，但稳定度不如四星齐。仍宜公职、教研、医疗、服务等需要积累与稳定的行业，关键看缺位星与四化的配合。',
        palaces=palaces_names,
        conditions=PatternCondition([f'三方四正会{"、".join(has)}（机月同梁缺{"、".join(missing)}）']),
        source='《紫微斗数全书·机月同梁格》（降级版）',
    ))


@_register
def detect_chang_qu_tong_hui(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """昌曲同会"""
    sanfang = san_fang_all_stars(chart)
    if '文昌' not in sanfang or '文曲' not in sanfang: return
    in_ming = has_star(ming, '文昌') and has_star(ming, '文曲')
    desc = ('文昌文曲同入命宫，主聪明俊秀、文采斐然，宜文学、教育、写作、咨询。最忌化忌——昌曲化忌主文书契约暗亏。'
            if in_ming
            else '文昌文曲同会三方四正，主才华横溢、口才文笔俱佳。宜走需要表达与文采的行业，化科加持则名声大显。')
    patterns.append(Pattern(
        name='昌曲坐命' if in_ming else '昌曲同会',
        level='good',
        description=desc,
        palaces=['命宫'],
        conditions=PatternCondition(['文昌、文曲同会命宫三方四正']),
        source='《紫微斗数全书·文星论》',
    ))


@_register
def detect_fu_bi_tong_hui(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """辅弼同会"""
    sanfang = san_fang_all_stars(chart)
    if '左辅' not in sanfang or '右弼' not in sanfang: return
    patterns.append(Pattern(
        name='辅弼同会',
        level='good',
        description='左辅右弼同会命宫三方四正，主一生贵人不绝、人缘极佳。最宜领导岗位与团队合作型工作。倪师说「辅弼夹命，平生贵人多」——你不是单打独斗的命，要善用人际网络。',
        palaces=['命宫'],
        conditions=PatternCondition(['左辅、右弼同会命宫三方四正']),
        source='《紫微斗数全书·辅弼论》',
    ))


@_register
def detect_kui_yue_tong_hui(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """魁钺同会"""
    sanfang = san_fang_all_stars(chart)
    if '天魁' not in sanfang or '天钺' not in sanfang: return
    patterns.append(Pattern(
        name='魁钺同会',
        level='good',
        description='天魁天钺同会命宫三方四正，主"天乙贵人"加持，关键时刻总有贵人提携。倪师说「魁钺夹命，必为贵人」——遇到困难时身边会出现得力相助者，宜主动维护人脉。',
        palaces=['命宫'],
        conditions=PatternCondition(['天魁、天钺同会命宫三方四正']),
        source='《紫微斗数全书·魁钺论》',
    ))


@_register
def detect_ke_quan_shuang_hui(chart: Chart, ming: Palace, patterns: List[Pattern]):
    """科权双会"""
    sf_palaces = get_san_fang_palaces(chart)
    has_ke = any(s.type == 'major' and s.sihua == '科' for p in sf_palaces for s in p.stars)
    has_quan = any(s.type == 'major' and s.sihua == '权' for p in sf_palaces for s in p.stars)
    if not (has_ke and has_quan): return
    patterns.append(Pattern(
        name='科权双会',
        level='good',
        description='化科 + 化权 同会三方四正，主名权双美——既有学识/名声（科），又有掌控力（权），宜走"专业权威"路线（如医生、律师、教授、技术骨干），名利双收且根基扎实。',
        palaces=['命宫'],
        conditions=PatternCondition(['化科、化权同会命宫三方四正']),
        source='《紫微斗数全书·四化会照》',
    ))


