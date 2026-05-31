"""Module routing helpers for XiaShenSuan."""

from typing import Any, Dict, Iterable, List


SUPPORTED_MODULES = ("bazi", "ziwei", "mbti", "zodiac", "blood")
DEFAULT_MODULES = ("bazi", "ziwei", "zodiac")
OUTPUT_MODES = ("auto", "single", "paired", "fusion")

MODULE_LABELS = {
    "bazi": "八字命理",
    "ziwei": "紫微斗数",
    "mbti": "MBTI",
    "zodiac": "星座",
    "blood": "血型",
}

MODULE_ALIASES = {
    "八字": "bazi",
    "bazi": "bazi",
    "ziwei": "ziwei",
    "紫微": "ziwei",
    "紫微斗数": "ziwei",
    "mbti": "mbti",
    "MBTI": "mbti",
    "星座": "zodiac",
    "zodiac": "zodiac",
    "blood": "blood",
    "血型": "blood",
}

GROUP_ALIASES = {
    "core": ("bazi", "ziwei"),
    "命理": ("bazi", "ziwei"),
    "personality": ("mbti", "zodiac", "blood"),
    "人格": ("mbti", "zodiac", "blood"),
    "all": SUPPORTED_MODULES,
    "fusion": SUPPORTED_MODULES,
    "全部": SUPPORTED_MODULES,
}


def _unique(items: Iterable[str]) -> List[str]:
    result: List[str] = []
    for item in items:
        if item not in result:
            result.append(item)
    return result


def parse_modules(raw_modules: str, has_mbti: bool = False, has_blood_type: bool = False) -> List[str]:
    if not raw_modules:
        modules = list(DEFAULT_MODULES)
        if has_mbti:
            modules.append("mbti")
        if has_blood_type:
            modules.append("blood")
        return _unique(modules)

    requested: List[str] = []
    for raw in raw_modules.replace("，", ",").split(","):
        token = raw.strip()
        if not token:
            continue
        if token in GROUP_ALIASES:
            requested.extend(GROUP_ALIASES[token])
            continue
        normalized = MODULE_ALIASES.get(token, MODULE_ALIASES.get(token.lower()))
        if not normalized:
            raise ValueError(f"不支持的模块: {token}")
        requested.append(normalized)
    return _unique(requested)


def normalize_output_mode(output_mode: str) -> str:
    mode = (output_mode or "auto").strip().lower()
    aliases = {
        "自动": "auto",
        "单项": "single",
        "单模块": "single",
        "组合": "paired",
        "双项": "paired",
        "融合": "fusion",
    }
    normalized = aliases.get(mode, aliases.get(output_mode, mode))
    if normalized not in OUTPUT_MODES:
        raise ValueError(f"不支持的输出模式: {output_mode}")
    return normalized


def build_route(
    raw_modules: str = None,
    output_mode: str = "auto",
    has_mbti: bool = False,
    has_blood_type: bool = False,
) -> Dict[str, Any]:
    modules = parse_modules(raw_modules, has_mbti=has_mbti, has_blood_type=has_blood_type)
    mode = normalize_output_mode(output_mode)
    return {
        "请求模块": raw_modules or "default",
        "启用模块": modules,
        "启用模块名称": [MODULE_LABELS[item] for item in modules],
        "输出模式": mode,
        "可用模块": list(SUPPORTED_MODULES),
        "说明": "底层仍可复用核心排盘；展示层按启用模块与输出模式裁剪。",
    }

