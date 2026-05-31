"""Parser for Wenmo Tianji text charts.

The adapter is intentionally conservative: it extracts stable fields from text
reports and keeps the original palace lines for human review.
"""

import re
from typing import Any, Dict, List


MAIN_STARS = {
    "紫微",
    "天机",
    "太阳",
    "武曲",
    "天同",
    "廉贞",
    "天府",
    "太阴",
    "贪狼",
    "巨门",
    "天相",
    "天梁",
    "七杀",
    "破军",
}
PALACE_NAMES = {
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
}
GANZHI_RE = r"[甲乙丙丁戊己庚辛壬癸][子丑寅卯辰巳午未申酉戌亥]"
BRANCH_RE = r"[子丑寅卯辰巳午未申酉戌亥]"
BRIGHTNESS_MARKS = {"庙", "旺", "得", "利", "平", "闲", "陷"}
HUA_MAP = {"禄": "禄", "权": "权", "科": "科", "忌": "忌"}
PALACE_LINE_RE = re.compile(r"^\s*(?:[-*]\s*)?\*\*(?P<name>[^*]+宫)\*\*\s*[:：]\s*(?P<raw>.+?)\s*$")
TREE_PALACE_HEADER_RE = re.compile(
    rf"^\s*[│┃\s]*(?:[├└]─?)?\s*(?P<name>[\u4e00-\u9fff\s]+宫)"
    rf"\[(?P<ganzhi>{GANZHI_RE})\](?P<flags>(?:\[[^\]]+\])*)\s*$"
)
TREE_FIELD_RE = re.compile(
    r"^\s*[│┃\s]*(?:[├└]─?)?\s*(?P<label>主星|辅星|小星|大限|小限|流年|限流叠宫|"
    r"岁前星|将前星|十二长生|太岁煞禄)\s*[:：]\s*(?P<value>.+?)\s*$"
)
TREE_BASIC_FIELD_RE = re.compile(
    r"^\s*[│┃\s]*(?:[├└]─?)?\s*(?P<label>性别|地理经度|钟表时间|真太阳时|"
    r"农历时间|节气四柱|非节气四柱|五行局数)\s*[:：]\s*(?P<value>.+?)\s*$"
)
DAYUN_LINE_RE = re.compile(
    r"^\s*(?:[-*]\s*)?(?P<start>\d+)\s*[~－-]\s*(?P<end>\d+)\s*虚岁\s*[:：]\s*"
    r"(?P<palace>[^（\n]+?)(?:（(?P<note>[^）]+)）)?\s*$"
)
AGE_RANGE_RE = re.compile(r"(?P<start>\d+)\s*[~－-]\s*(?P<end>\d+)\s*虚岁")
MARK_RE = re.compile(r"\[(?P<mark>[^\]]+)\]")
ANXING_RE = re.compile(r"安星码\s*(?:\*\*)?\s*[:：]\s*([A-Za-z0-9]+)", re.I)
DATETIME_RE = re.compile(r"(?P<year>\d{4})[-/](?P<month>\d{1,2})[-/](?P<day>\d{1,2})\s+(?P<hour>\d{1,2}):(?P<minute>\d{1,2})")


def _extract_markdown_field(text: str, label: str) -> str:
    pattern = rf"(?:^|\n)\s*(?:[-*]\s*)?\*\*{re.escape(label)}\*\*\s*[:：]\s*([^\n]+)"
    match = re.search(pattern, text)
    if not match:
        return ""
    value = match.group(1).strip()
    value = re.split(r"[；;]\s*\*\*[^*]+\*\*\s*[:：]", value, maxsplit=1)[0]
    return value.strip()


def _extract_inline_field(text: str, label: str) -> str:
    pattern = rf"\*\*{re.escape(label)}\*\*\s*[:：]\s*([^；;\n]+)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _extract_plain_field(text: str, label: str) -> str:
    pattern = rf"{re.escape(label)}\s*[:：]\s*([^；;\n]+)"
    match = re.search(pattern, text)
    return match.group(1).strip() if match else ""


def _clean_star_name(raw: str) -> str:
    cleaned = re.sub(r"\[.*?\]", "", raw)
    cleaned = re.sub(r"（.*?）", "", cleaned)
    cleaned = cleaned.strip(" ，,;；")
    return cleaned


def _parse_datetime_text(raw: str) -> Dict[str, Any]:
    raw = (raw or "").strip()
    match = DATETIME_RE.search(raw)
    if not match:
        return {
            "原文": raw,
            "标准时间": "",
            "日期": "",
            "时间": "",
            "year": None,
            "month": None,
            "day": None,
            "hour": None,
            "minute": None,
        }
    year = int(match.group("year"))
    month = int(match.group("month"))
    day = int(match.group("day"))
    hour = int(match.group("hour"))
    minute = int(match.group("minute"))
    date = f"{year:04d}-{month:02d}-{day:02d}"
    time = f"{hour:02d}:{minute:02d}"
    return {
        "原文": raw,
        "标准时间": f"{date} {time}",
        "日期": date,
        "时间": time,
        "year": year,
        "month": month,
        "day": day,
        "hour": hour,
        "minute": minute,
    }


def _infer_calendar(raw: str) -> str:
    if re.search(r"农历|阴历", raw or ""):
        return "农历"
    return "公历"


def _normalize_palace_name(name: str) -> str:
    return re.sub(r"\s+", "", name)


def _extract_hua_marks(piece: str) -> List[Dict[str, str]]:
    marks = []
    for mark in MARK_RE.findall(piece):
        if mark.startswith("生年") and mark[-1:] in HUA_MAP:
            marks.append({"化": mark[-1], "类型": "生年", "符号": "", "原文标记": mark})
        elif len(mark) >= 2 and mark[0] in {"↑", "↓"} and mark[-1] in HUA_MAP:
            marks.append({"化": mark[-1], "类型": "飞化", "符号": mark[0], "原文标记": mark})
    return marks


def _parse_star_details(raw: str) -> List[Dict[str, Any]]:
    pieces = re.split(r"\s*(?:\+|,|，)\s*", raw)
    stars: List[Dict[str, Any]] = []
    for piece in pieces:
        piece = piece.strip()
        if not piece or _clean_star_name(piece) in {"空宫", "无"}:
            continue
        name = _clean_star_name(piece)
        if not name:
            continue
        bracket_marks = MARK_RE.findall(piece)
        brightness = next((mark for mark in bracket_marks if mark in BRIGHTNESS_MARKS), "")
        hua_marks = _extract_hua_marks(piece)
        extra_marks = [
            mark
            for mark in bracket_marks
            if mark != brightness and mark not in {hua["原文标记"] for hua in hua_marks}
        ]
        stars.append(
            {
                "星曜": name,
                "类别": "主星" if name in MAIN_STARS else "辅星",
                "亮度": brightness,
                "四化": hua_marks,
                "附加标记": extra_marks,
                "原文": piece,
            }
        )
    return stars


def _build_transformations(star_details: List[Dict[str, Any]]) -> List[Dict[str, str]]:
    transformations = []
    for detail in star_details:
        for hua in detail.get("四化", []):
            transformations.append(
                {
                    "星曜": detail["星曜"],
                    "化": hua["化"],
                    "类型": hua["类型"],
                    "符号": hua["符号"],
                    "原文标记": hua["原文标记"],
                    "原文": detail["原文"],
                }
            )
    return transformations


def _parse_stars(raw: str) -> List[str]:
    stars: List[str] = []
    for detail in _parse_star_details(raw):
        name = detail["星曜"]
        if name and name not in stars:
            stars.append(name)
    return stars


def _split_palace_star_part(raw: str) -> Dict[str, str]:
    match = re.match(
        rf"^\s*(?P<ganzhi>{GANZHI_RE})(?P<flag_text>(?:（[^）]+）)?)\s*[，,]\s*(?P<stars>.+?)\s*$",
        raw,
    )
    if match:
        return {
            "宫干支": match.group("ganzhi"),
            "标记原文": match.group("flag_text") or "",
            "星曜原文": match.group("stars").strip(),
        }
    if "，" in raw:
        return {"宫干支": "", "标记原文": "", "星曜原文": raw.split("，", 1)[1].strip()}
    if "," in raw:
        return {"宫干支": "", "标记原文": "", "星曜原文": raw.split(",", 1)[1].strip()}
    return {"宫干支": "", "标记原文": "", "星曜原文": raw.strip()}


def _parse_palace_line(name: str, raw: str) -> Dict[str, Any]:
    split = _split_palace_star_part(raw)
    ganzhi = split["宫干支"] or (re.search(GANZHI_RE, raw).group(0) if re.search(GANZHI_RE, raw) else "")
    star_part = split["星曜原文"].replace("（身宫）", "").replace("（来因宫）", "")
    star_details = _parse_star_details(star_part)
    transformations = _build_transformations(star_details)
    palace_flags = {
        "空宫": "空宫" in raw,
        "身宫": "身宫" in raw,
        "来因宫": "来因宫" in raw,
    }
    return {
        "宫位": name,
        "宫干支": ganzhi,
        "宫支": ganzhi[1] if ganzhi else "",
        "星曜": [detail["星曜"] for detail in star_details],
        "主星": [detail["星曜"] for detail in star_details if detail["类别"] == "主星"],
        "辅星": [detail["星曜"] for detail in star_details if detail["类别"] == "辅星"],
        "星曜详情": star_details,
        "四化线索": transformations,
        "标记": palace_flags,
        "原文": raw,
    }


def _extract_palaces(text: str) -> Dict[str, Dict[str, Any]]:
    palaces: Dict[str, Dict[str, Any]] = {}
    for line in text.splitlines():
        match = PALACE_LINE_RE.match(line)
        if not match:
            continue
        name = match.group("name").strip()
        raw = match.group("raw").strip()
        if name in PALACE_NAMES:
            palaces[name] = _parse_palace_line(name, raw)
    return palaces


def _parse_age_list(raw: str) -> List[int]:
    return [int(piece) for piece in re.findall(r"\d+", raw or "")]


def _parse_age_range(raw: str) -> Dict[str, Any]:
    match = AGE_RANGE_RE.search(raw or "")
    if not match:
        return {"年龄": raw.strip() if raw else ""}
    start = int(match.group("start"))
    end = int(match.group("end"))
    return {"年龄": f"{start}~{end}虚岁", "起始年龄": start, "结束年龄": end}


def _append_unique(target: List[str], values: List[str]) -> None:
    for value in values:
        if value and value not in target:
            target.append(value)


def _new_tree_palace(name: str, ganzhi: str, flags: List[str], raw: str) -> Dict[str, Any]:
    return {
        "宫位": name,
        "宫干支": ganzhi,
        "宫支": ganzhi[1] if ganzhi else "",
        "星曜": [],
        "主星": [],
        "辅星": [],
        "小星": [],
        "星曜详情": [],
        "四化线索": [],
        "标记": {
            "空宫": False,
            "身宫": "身宫" in flags,
            "来因宫": "来因" in flags or "来因宫" in flags,
        },
        "神煞": {},
        "大限": {},
        "小限": [],
        "流年": [],
        "限流叠宫": "",
        "原文": raw,
    }


def _extract_tree_basic_fields(text: str) -> Dict[str, str]:
    fields = {}
    for line in text.splitlines():
        match = TREE_BASIC_FIELD_RE.match(line)
        if match:
            fields[match.group("label")] = match.group("value").strip()
    return fields


def _extract_tree_palaces(text: str) -> Dict[str, Dict[str, Any]]:
    palaces: Dict[str, Dict[str, Any]] = {}
    current: Dict[str, Any] = {}
    for line in text.splitlines():
        header_match = TREE_PALACE_HEADER_RE.match(line)
        if header_match:
            name = _normalize_palace_name(header_match.group("name"))
            if name not in PALACE_NAMES:
                current = {}
                continue
            flags = MARK_RE.findall(header_match.group("flags") or "")
            current = _new_tree_palace(name, header_match.group("ganzhi"), flags, line.strip())
            palaces[name] = current
            continue

        if not current:
            continue
        field_match = TREE_FIELD_RE.match(line)
        if not field_match:
            continue
        label = field_match.group("label")
        value = field_match.group("value").strip()
        if label in {"主星", "辅星", "小星"}:
            details = _parse_star_details(value)
            names = [detail["星曜"] for detail in details]
            if label == "主星":
                current["主星"] = names
                if not names:
                    current["标记"]["空宫"] = True
            elif label == "辅星":
                current["辅星"] = names
            else:
                current["小星"] = names
            current["星曜详情"].extend(details)
            _append_unique(current["星曜"], names)
            current["四化线索"].extend(_build_transformations(details))
        elif label == "大限":
            current["大限"] = _parse_age_range(value)
        elif label in {"小限", "流年"}:
            current[label] = _parse_age_list(value)
        elif label == "限流叠宫":
            current["限流叠宫"] = value
        else:
            current["神煞"][label] = value
    return palaces


def _extract_tree_dayun(palaces: Dict[str, Dict[str, Any]]) -> List[Dict[str, Any]]:
    rows = []
    for palace_name, palace in palaces.items():
        dayun = palace.get("大限", {})
        if not dayun.get("年龄"):
            continue
        rows.append(
            {
                **dayun,
                "宫位": palace_name,
                "宫干支": palace.get("宫干支", ""),
                "标记": [
                    mark
                    for mark, enabled in palace.get("标记", {}).items()
                    if enabled and mark in {"身宫", "来因宫"}
                ],
                "原文": palace.get("原文", ""),
            }
        )
    return sorted(rows, key=lambda item: item.get("起始年龄", 999))


def _extract_dayun(text: str) -> List[Dict[str, str]]:
    rows = []
    for line in text.splitlines():
        match = DAYUN_LINE_RE.match(line)
        if not match:
            continue
        note = (match.group("note") or "").strip()
        note_parts = [part.strip() for part in re.split(r"[，,]", note) if part.strip()]
        ganzhi = note_parts[0] if note_parts and re.fullmatch(GANZHI_RE, note_parts[0]) else ""
        markers = note_parts[1:] if ganzhi else note_parts
        rows.append(
            {
                "年龄": f"{match.group('start')}~{match.group('end')}虚岁",
                "起始年龄": int(match.group("start")),
                "结束年龄": int(match.group("end")),
                "宫位": match.group("palace").strip(),
                "宫干支": ganzhi,
                "标记": markers,
                "原文": line.strip(),
            }
        )
    return rows


def _parse_shengong_summary(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    match = re.match(rf"^\s*(?P<branch>{BRANCH_RE})?（(?P<inside>[^）]+)）\s*$", raw)
    if not match:
        return {"原文": raw}
    inside_parts = [part.strip() for part in re.split(r"[，,]", match.group("inside"), maxsplit=1)]
    palace = inside_parts[0] if inside_parts else ""
    star_part = inside_parts[1] if len(inside_parts) > 1 else ""
    return {
        "宫支": match.group("branch") or "",
        "所属宫位": palace,
        "星曜": _parse_stars(star_part),
        "星曜详情": _parse_star_details(star_part),
        "原文": raw,
    }


def _parse_laiyin_summary(raw: str) -> Dict[str, Any]:
    if not raw:
        return {}
    match = re.match(r"^\s*(?P<palace>[^（]+宫)（(?P<inside>[^）]+)）\s*$", raw)
    if not match:
        return {"原文": raw}
    inside_parts = [part.strip() for part in re.split(r"[，,]", match.group("inside"), maxsplit=1)]
    ganzhi = inside_parts[0] if inside_parts else ""
    star_part = inside_parts[1] if len(inside_parts) > 1 else ""
    palace = _parse_palace_line(match.group("palace"), f"{ganzhi}，{star_part}") if star_part else {}
    return {
        "宫位": match.group("palace"),
        "宫干支": ganzhi if re.fullmatch(GANZHI_RE, ganzhi) else "",
        "宫支": ganzhi[1] if re.fullmatch(GANZHI_RE, ganzhi) else "",
        "星曜": palace.get("星曜", []),
        "星曜详情": palace.get("星曜详情", []),
        "四化线索": palace.get("四化线索", []),
        "原文": raw,
    }


def parse_wenmo_text(text: str) -> Dict[str, Any]:
    raw_text = text or ""
    markdown_palaces = _extract_palaces(raw_text)
    tree_palaces = _extract_tree_palaces(raw_text)
    palaces = {**markdown_palaces, **tree_palaces}
    dayun = _extract_dayun(raw_text) or _extract_tree_dayun(palaces)
    tree_basic = _extract_tree_basic_fields(raw_text)
    mingzhu_line = (
        _extract_inline_field(raw_text, "命主")
        or _extract_markdown_field(raw_text, "命主")
        or _extract_plain_field(raw_text, "命主")
    )
    shenzhu = _extract_inline_field(raw_text, "身主") or _extract_plain_field(raw_text, "身主")
    doujun = _extract_inline_field(raw_text, "子年斗君") or _extract_plain_field(raw_text, "子年斗君")
    shengong = _extract_markdown_field(raw_text, "身宫") or _extract_inline_field(raw_text, "身宫")
    laiyin = _extract_markdown_field(raw_text, "来因宫")
    anxing = ANXING_RE.search(raw_text)
    true_solar_match = re.search(r"真太阳时\*\*：?([^\n]+)", raw_text)
    birth_match = re.search(r"出生\*\*：?([^\n]+)", raw_text)
    longitude_match = re.search(r"出生地经度\*\*：?([^\n]+)", raw_text)
    birth_raw = (
        birth_match.group(1).strip()
        if birth_match
        else _extract_markdown_field(raw_text, "出生") or tree_basic.get("钟表时间", "")
    )
    true_solar_raw = (
        true_solar_match.group(1).strip()
        if true_solar_match
        else _extract_markdown_field(raw_text, "真太阳时") or tree_basic.get("真太阳时", "")
    )
    birth_time_detail = _parse_datetime_text(birth_raw)
    true_solar_detail = _parse_datetime_text(true_solar_raw)
    if not shengong:
        shengong_palace = next((palace for palace in palaces.values() if palace.get("标记", {}).get("身宫")), {})
        shengong = _extract_plain_field(raw_text, "身宫")
        if shengong_palace and shengong:
            shengong = f"{shengong}（{shengong_palace.get('宫位')}，{'+'.join(shengong_palace.get('主星', [])) or '空宫'}）"
    if not laiyin:
        laiyin_palace = next((palace for palace in palaces.values() if palace.get("标记", {}).get("来因宫")), {})
        if laiyin_palace:
            stars = " + ".join(laiyin_palace.get("主星", []) + laiyin_palace.get("辅星", []))
            laiyin = f"{laiyin_palace.get('宫位')}（{laiyin_palace.get('宫干支')}，{stars or '空宫'}）"
    four_hua = [
        {**item, "宫位": palace_name}
        for palace_name, palace in palaces.items()
        for item in palace.get("四化线索", [])
    ]

    return {
        "状态": "OK" if palaces else "NO_PALACE_DATA",
        "数据源": "文墨天机文字版",
        "解析版本": "wenmo-text-structured-v2",
        "安星码": anxing.group(1) if anxing else "",
        "基础信息": {
            "昵称": _extract_markdown_field(raw_text, "昵称"),
            "性别": _extract_markdown_field(raw_text, "性别") or tree_basic.get("性别", ""),
            "出生": birth_raw,
            "出生原文": birth_raw,
            "历法": _infer_calendar(birth_raw),
            "钟表时间": tree_basic.get("钟表时间", "") or birth_raw,
            "出生标准时间": birth_time_detail["标准时间"],
            "出生日期": birth_time_detail["日期"],
            "出生时间": birth_time_detail["时间"],
            "出生地经度": (
                longitude_match.group(1).strip()
                if longitude_match
                else _extract_markdown_field(raw_text, "出生地经度") or tree_basic.get("地理经度", "")
            ),
            "真太阳时": true_solar_raw,
            "真太阳时原文": true_solar_raw,
            "真太阳标准时间": true_solar_detail["标准时间"],
            "真太阳日期": true_solar_detail["日期"],
            "真太阳时间": true_solar_detail["时间"],
            "时间来源格式": "API_TREE" if tree_palaces else "MARKDOWN_TEXT",
            "农历": _extract_markdown_field(raw_text, "农历") or tree_basic.get("农历时间", ""),
            "八字": _extract_markdown_field(raw_text, "八字") or tree_basic.get("节气四柱", ""),
            "五行局": _extract_markdown_field(raw_text, "五行局") or tree_basic.get("五行局数", ""),
            "命主": mingzhu_line,
            "身主": shenzhu,
            "子年斗君": doujun,
            "身宫": shengong,
            "身宫详情": _parse_shengong_summary(shengong),
            "来因宫": laiyin,
            "来因宫详情": _parse_laiyin_summary(laiyin),
        },
        "十二宫": palaces,
        "四化线索": four_hua,
        "宫位标记": {name: palace.get("标记", {}) for name, palace in palaces.items()},
        "大限序列": dayun,
        "解析完整度": {
            "宫位数": len(palaces),
            "是否完整十二宫": len(palaces) == 12,
            "四化线索数": len(four_hua),
            "大限数": len(dayun),
            "格式": "API_TREE" if tree_palaces else "MARKDOWN_TEXT",
        },
        "解析说明": "当前为结构化解析器，已提取宫位星曜、亮度、四化、身宫/来因宫标记与大限序列；原文仍保留用于人工复核。",
    }


def compare_wenmo_with_ziwei(wenmo_chart: Dict[str, Any], ziwei_section: Dict[str, Any]) -> Dict[str, Any]:
    if not wenmo_chart or wenmo_chart.get("状态") != "OK":
        return {"状态": "SKIPPED", "说明": "未提供可解析的文墨文字盘。"}

    basic = ziwei_section.get("基础信息", {})
    ziwei_palaces = {palace["宫位"]: palace for palace in ziwei_section.get("十二宫", [])}
    mismatches = []
    matched = []

    field_pairs = [
        ("五行局", wenmo_chart["基础信息"].get("五行局", ""), basic.get("局名", "")),
        ("命主", wenmo_chart["基础信息"].get("命主", ""), basic.get("命主", "")),
        ("身主", wenmo_chart["基础信息"].get("身主", ""), basic.get("身主", "")),
        ("子年斗君", wenmo_chart["基础信息"].get("子年斗君", ""), basic.get("子斗", "")),
    ]
    for field, wenmo_value, local_value in field_pairs:
        if not wenmo_value:
            continue
        if str(local_value) and str(local_value) in str(wenmo_value):
            matched.append(field)
        else:
            mismatches.append({"字段": field, "文墨": wenmo_value, "虾神算": local_value})

    for palace_name, wenmo_palace in wenmo_chart.get("十二宫", {}).items():
        local_palace = ziwei_palaces.get(palace_name)
        if not local_palace:
            continue
        local_stars = {_clean_star_name(name) for name in local_palace.get("主星", []) + local_palace.get("辅星", [])}
        wenmo_compare_stars = wenmo_palace.get("主星", []) + wenmo_palace.get("辅星", [])
        if not wenmo_compare_stars:
            wenmo_compare_stars = wenmo_palace.get("星曜", [])
        wenmo_stars = {_clean_star_name(name) for name in wenmo_compare_stars}
        local_stars.discard("")
        wenmo_stars.discard("")
        if wenmo_stars and wenmo_stars.issubset(local_stars):
            matched.append(f"{palace_name}星曜")
        elif wenmo_stars:
            mismatches.append(
                {
                    "字段": f"{palace_name}星曜",
                    "文墨": sorted(wenmo_stars),
                    "虾神算": sorted(local_stars),
                }
            )

    return {
        "状态": "PASS" if not mismatches else "DIFF",
        "一致项": matched,
        "差异项": mismatches,
        "一致数": len(matched),
        "差异数": len(mismatches),
        "说明": "文墨文字盘解析结果与虾神算自排盘的基础字段和宫位星曜做轻量比对。",
    }
