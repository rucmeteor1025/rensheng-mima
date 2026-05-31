"""Readable text report renderer for CLI output."""

from typing import Any, Dict, List, Tuple


def _present(value: Any) -> bool:
    return value not in (None, "", [], {})


def _first(*values: Any) -> Any:
    for value in values:
        if _present(value):
            return value
    return ""


def _stringify(value: Any) -> str:
    if isinstance(value, list):
        return "、".join(_stringify(item) for item in value if _present(item))
    if isinstance(value, tuple):
        return "、".join(_stringify(item) for item in value if _present(item))
    if isinstance(value, dict):
        parts = []
        for key, item in value.items():
            if _present(item):
                parts.append(f"{key}：{_stringify(item)}")
        return "；".join(parts)
    return str(value)


def _append_section(lines: List[str], title: str, content: Any) -> None:
    if not _present(content):
        return
    lines.append("")
    lines.append(f"## {title}")
    _append_content(lines, content)


def _append_content(lines: List[str], content: Any, heading_level: int = 3) -> None:
    if isinstance(content, str):
        lines.append(content)
        return
    if isinstance(content, list):
        for item in content:
            if _present(item):
                lines.append(f"- {_stringify(item)}")
        return
    if isinstance(content, dict):
        for key, value in content.items():
            if not _present(value) or key == "文墨文字盘摘要":
                continue
            if isinstance(value, dict):
                lines.append("")
                lines.append(f"{'#' * heading_level} {key}")
                _append_content(lines, value, heading_level + 1)
            elif isinstance(value, list):
                lines.append("")
                lines.append(f"{'#' * heading_level} {key}")
                _append_content(lines, value, heading_level + 1)
            else:
                lines.append(f"- {key}：{_stringify(value)}")
        return
    lines.append(_stringify(content))


def _wenmo_basic(result: Dict[str, Any]) -> Dict[str, Any]:
    return (
        result.get("文墨文字盘", {})
        .get("解析", {})
        .get("基础信息", {})
        or {}
    )


def _chart_info_rows(result: Dict[str, Any], styled: Dict[str, Any]) -> List[Tuple[str, Any]]:
    basic = result.get("基础信息", {})
    ziwei = result.get("紫微斗数", {})
    chart = styled.get("命盘信息", {})
    wenmo = _wenmo_basic(result)

    birth_time = _first(
        wenmo.get("出生标准时间"),
        wenmo.get("出生"),
        chart.get("公历"),
        basic.get("出生时间"),
    )
    calendar = wenmo.get("历法", "")
    birth_display = f"{calendar} {birth_time}".strip() if birth_time else ""

    return [
        ("数据源", styled.get("数据源")),
        ("安星码", _first(chart.get("安星码"), ziwei.get("安星码"))),
        ("状态", _first(chart.get("状态"), ziwei.get("状态"))),
        ("性别", _first(wenmo.get("性别"), chart.get("性别"), basic.get("性别"))),
        ("出生", birth_display),
        ("真太阳时", _first(wenmo.get("真太阳标准时间"), wenmo.get("真太阳时"), chart.get("真太阳时"))),
        ("出生地", basic.get("出生地")),
        ("出生地经度", _first(wenmo.get("出生地经度"), wenmo.get("地理经度"), basic.get("经度"))),
        ("农历", _first(wenmo.get("农历时间"), chart.get("农历"), basic.get("农历"))),
        ("节气四柱", wenmo.get("节气四柱")),
        ("非节气四柱", wenmo.get("非节气四柱")),
        ("命局", _first(wenmo.get("五行局数"), wenmo.get("五行局"), chart.get("命局"))),
        ("命宫", chart.get("命宫")),
        ("身宫", chart.get("身宫")),
        ("命主身主", chart.get("命主身主")),
        ("子斗", chart.get("子斗")),
    ]


def _chart_info_lines(result: Dict[str, Any], styled: Dict[str, Any]) -> List[str]:
    return [f"{key}：{_stringify(value)}" for key, value in _chart_info_rows(result, styled) if _present(value)]


def _comparison_summary(validation: Dict[str, Any]) -> Dict[str, Any]:
    comparison = validation.get("文墨文字盘比对", {})
    compact = {
        "时辰边界": validation.get("时辰边界"),
        "文墨参考盘": validation.get("文墨参考盘"),
    }
    if isinstance(comparison, dict):
        compact["文墨文字盘比对"] = (
            f"{comparison.get('状态', 'UNKNOWN')}；"
            f"一致数 {comparison.get('一致数', 0)}；差异数 {comparison.get('差异数', 0)}"
        )
        if comparison.get("差异项"):
            compact["主要差异"] = [
                f"{item.get('字段')}：文墨={_stringify(item.get('文墨'))}；虾神算={_stringify(item.get('虾神算'))}"
                for item in comparison.get("差异项", [])[:5]
            ]
    else:
        compact["文墨文字盘比对"] = comparison
    if validation.get("说明"):
        compact["说明"] = validation["说明"]
    return compact


def _build_ziwei_professional_report(result: Dict[str, Any], styled: Dict[str, Any]) -> str:
    lines = [f"# {styled.get('模式', '紫微斗数专业版')}"]
    data_source = styled.get("数据源")
    if data_source:
        lines.append(f"数据源：{data_source}")

    _append_section(lines, "命盘信息", _chart_info_lines(result, styled))
    _append_section(lines, "总断", styled.get("总断"))
    _append_section(lines, "命身主轴", styled.get("命身主轴"))
    _append_section(lines, "正文分析", styled.get("正文分析"))
    _append_section(lines, "关键宫位", styled.get("关键宫位"))
    _append_section(lines, "四化流向", styled.get("四化流向"))
    _append_section(lines, "专题判断", styled.get("专题判断"))
    _append_section(lines, "趋避建议", styled.get("趋避建议"))
    _append_section(lines, "校验", _comparison_summary(styled.get("校验", {})))
    _append_section(lines, "声明", styled.get("声明"))
    return "\n".join(lines).strip() + "\n"


def _build_standard_report(result: Dict[str, Any], styled: Dict[str, Any]) -> str:
    title = styled.get("模式") or result.get("版本", {}).get("主流程") or "虾神算报告"
    lines = [f"# {title}"]
    _append_section(lines, "基础信息", result.get("基础信息"))

    for key, value in styled.items():
        if key in {"模式", "文墨文字盘摘要"}:
            continue
        _append_section(lines, key, value)

    return "\n".join(lines).strip() + "\n"


def build_report_text(result: Dict[str, Any]) -> str:
    """Build a compact, human-readable report from a full analysis result."""
    styled = result.get("风格化输出", {}) or {}
    if styled.get("模式") == "紫微斗数专业版":
        return _build_ziwei_professional_report(result, styled)
    return _build_standard_report(result, styled)
