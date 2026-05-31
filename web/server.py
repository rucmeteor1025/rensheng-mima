#!/usr/bin/env python3
# -*- coding: utf-8 -*-
"""
XiaShenSuan local web MVP.

This service is a local-first web entry point. Reports are stored only in
process memory in the MVP implementation and are cleared when the service exits.
"""

import json
import sys
import traceback
import uuid
from datetime import datetime
from http.server import BaseHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from typing import Any, Dict, Tuple
from urllib.parse import urlparse


WEB_ROOT = Path(__file__).resolve().parent
PROJECT_ROOT = WEB_ROOT.parent
STATIC_ROOT = WEB_ROOT / "static"
FRONTEND_DIST = WEB_ROOT / "frontend" / "dist"
DEFAULT_HOST = "127.0.0.1"
DEFAULT_PORT = 8765

if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))
scripts_path = PROJECT_ROOT / "scripts"
if str(scripts_path) not in sys.path:
    sys.path.insert(0, str(scripts_path))

from scripts.xiashensuan import full_xiashensuan_analysis  # noqa: E402


REPORT_STORE: Dict[str, Dict[str, Any]] = {}


def _json_response(handler: BaseHTTPRequestHandler, status: int, payload: Dict[str, Any]) -> None:
    body = json.dumps(payload, ensure_ascii=False, indent=2).encode("utf-8")
    handler.send_response(status)
    handler.send_header("Content-Type", "application/json; charset=utf-8")
    handler.send_header("Cache-Control", "no-store")
    handler.send_header("Content-Length", str(len(body)))
    handler.end_headers()
    handler.wfile.write(body)


def _read_json(handler: BaseHTTPRequestHandler) -> Tuple[Dict[str, Any], str]:
    try:
        length = int(handler.headers.get("Content-Length", "0"))
    except ValueError:
        return {}, "请求长度不正确"
    if length <= 0:
        return {}, "请求体为空"
    if length > 64 * 1024:
        return {}, "请求过大"
    raw = handler.rfile.read(length)
    try:
        return json.loads(raw.decode("utf-8")), ""
    except json.JSONDecodeError:
        return {}, "请求体不是有效 JSON"


def _as_int(value: Any, field: str, low: int, high: int) -> int:
    try:
        number = int(value)
    except (TypeError, ValueError):
        raise ValueError(f"{field} 需要是数字")
    if number < low or number > high:
        raise ValueError(f"{field} 需要在 {low}-{high} 之间")
    return number


def _normalize_gender(value: Any) -> str:
    gender = str(value or "").strip()
    if gender in {"男", "男性", "male", "M", "m"}:
        return "男"
    if gender in {"女", "女性", "female", "F", "f"}:
        return "女"
    raise ValueError("性别请选择男或女")


def _normalize_focus(value: Any) -> str:
    focus = str(value or "full").strip()
    allowed = {"full", "career", "relationship", "wealth"}
    if focus not in allowed:
        raise ValueError("分析主题不正确")
    return focus


def _safe_text(value: Any, default: str = "") -> str:
    text = str(value or default).strip()
    return text[:80]


def _pick_path(data: Dict[str, Any], *keys: str, default: Any = "") -> Any:
    current: Any = data
    for key in keys:
        if not isinstance(current, dict):
            return default
        current = current.get(key)
    return default if current is None else current


def _build_summary(result: Dict[str, Any]) -> Dict[str, Any]:
    styled = result.get("风格化输出", {})
    life_lines = []
    if isinstance(styled, dict):
        life_output = styled.get("生活版")
        if isinstance(life_output, dict):
            for key in ("总论", "性格气质", "事业财运", "感情关系", "状态健康", "阶段运势", "收束"):
                value = life_output.get(key)
                if value:
                    life_lines.append({"title": key, "text": str(value)})
        elif isinstance(life_output, str):
            life_lines.append({"title": "总论", "text": life_output})
        main_output = styled.get("命理主输出")
        if isinstance(main_output, dict):
            for key in ("整体判断", "性格气质", "事业与财运", "感情与婚姻", "健康与状态", "当前运势", "总结"):
                value = main_output.get(key)
                if value:
                    life_lines.append({"title": key, "text": str(value)})

    if not life_lines:
        fusion_main = _pick_path(result, "融合判断", "主轴", default="")
        if fusion_main:
            life_lines.append({"title": "主轴", "text": str(fusion_main)})

    if not life_lines:
        bazi_simple = _pick_path(result, "八字命理", "简批", "核心", default="")
        if bazi_simple:
            life_lines.append({"title": "核心", "text": str(bazi_simple)})

    free_lines = life_lines[:3]
    paid_lines = life_lines[3:]
    recommendations = _pick_path(styled, "命理主输出", "建议", default={})
    if not recommendations:
        recommendations = result.get("融合判断", {}).get("建议", {})
    if isinstance(recommendations, dict):
        for key, value in recommendations.items():
            if len(free_lines) < 3:
                free_lines.append({"title": key, "text": str(value)})
            else:
                paid_lines.append({"title": key, "text": str(value)})

    basic = result.get("基础信息", {})
    bazi = result.get("八字命理", {})
    ziwei = result.get("紫微斗数", {})

    return {
        "basic": {
            "birthTime": basic.get("出生时间", ""),
            "lunar": basic.get("农历", ""),
            "gender": basic.get("性别", ""),
            "place": basic.get("出生地", ""),
            "mode": _pick_path(result, "输出架构", "当前模式名称", default="生活版"),
            "version": "人生密码 Web MVP",
        },
        "chart": {
            "bazi": bazi.get("八字", ""),
            "dayMaster": _pick_path(bazi, "日主", "日主", default=""),
            "strength": _pick_path(bazi, "日主", "身强弱", default=""),
            "useful": _pick_path(bazi, "日主", "喜用神", default=""),
            "mingStar": _pick_path(ziwei, "重点宫位", "命宫", "主星", default=[]),
            "shenPalace": _pick_path(ziwei, "基础信息", "身宫所属宫位", default=""),
        },
        "free": free_lines,
        "paidPreview": paid_lines[:5],
        "disclaimer": "仅供参考，理性决策；不替代医疗、法律、投资等专业建议。",
    }


def _calculate(payload: Dict[str, Any]) -> Dict[str, Any]:
    birth_time = {
        "year": _as_int(payload.get("year"), "出生年", 1900, 2100),
        "month": _as_int(payload.get("month"), "出生月", 1, 12),
        "day": _as_int(payload.get("day"), "出生日", 1, 31),
        "hour": _as_int(payload.get("hour"), "出生小时", 0, 23),
        "minute": _as_int(payload.get("minute", 0), "出生分钟", 0, 59),
    }
    gender = _normalize_gender(payload.get("gender"))
    focus = _normalize_focus(payload.get("focus"))
    place = _safe_text(payload.get("place"), "北京") or "北京"
    mbti = _safe_text(payload.get("mbti"))
    blood_type = _safe_text(payload.get("bloodType"))
    mode = "professional" if focus != "full" else "life"

    result = full_xiashensuan_analysis(
        birth_time=birth_time,
        gender=gender,
        place=place,
        mode=mode,
        focus=focus,
        mbti=mbti or None,
        blood_type=blood_type or None,
        modules="all",
        output_mode="fusion",
        target_year=datetime.now().year,
    )
    report_id = uuid.uuid4().hex[:16]
    REPORT_STORE[report_id] = {
        "createdAt": datetime.now().isoformat(timespec="seconds"),
        "input": {
            "gender": gender,
            "place": place,
            "focus": focus,
            "birthTime": birth_time,
            "hasMbti": bool(mbti),
            "hasBloodType": bool(blood_type),
        },
        "summary": _build_summary(result),
        "full": result,
    }
    return {
        "ok": True,
        "reportId": report_id,
        "summary": REPORT_STORE[report_id]["summary"],
        "privacy": {
            "storage": "当前本地 MVP 只存在内存里；服务重启后自动清空。",
            "deleteEndpoint": f"/api/report/{report_id}",
        },
    }


class XiashensuanHandler(BaseHTTPRequestHandler):
    server_version = "XiashensuanWebMVP/0.1"

    def log_message(self, fmt: str, *args: Any) -> None:
        sys.stderr.write("[%s] %s\n" % (self.log_date_time_string(), fmt % args))

    def do_GET(self) -> None:
        path = urlparse(self.path).path
        if FRONTEND_DIST.exists():
            candidate = (FRONTEND_DIST / path.lstrip("/")).resolve()
            if candidate.is_file() and FRONTEND_DIST.resolve() in candidate.parents:
                self._send_file(candidate, _content_type(candidate))
                return
            if path == "/" or path in {"/index.html", "/analysis", "/checkout", "/pricing", "/privacy", "/about"}:
                self._send_file(FRONTEND_DIST / "index.html", "text/html; charset=utf-8")
                return
        if path in {"/", "/index.html", "/analysis", "/checkout", "/pricing", "/privacy", "/about"}:
            self._send_file(STATIC_ROOT / "index.html", "text/html; charset=utf-8")
            return
        if path == "/static/styles.css":
            self._send_file(STATIC_ROOT / "styles.css", "text/css; charset=utf-8")
            return
        if path == "/static/app.js":
            self._send_file(STATIC_ROOT / "app.js", "application/javascript; charset=utf-8")
            return
        if path.startswith("/api/report/"):
            report_id = path.rsplit("/", 1)[-1]
            report = REPORT_STORE.get(report_id)
            if not report:
                _json_response(self, 404, {"ok": False, "error": "报告不存在或已删除"})
                return
            _json_response(self, 200, {"ok": True, "reportId": report_id, "report": report["full"]})
            return
        _json_response(self, 404, {"ok": False, "error": "未找到页面"})

    def do_POST(self) -> None:
        path = urlparse(self.path).path
        if path != "/api/calculate":
            _json_response(self, 404, {"ok": False, "error": "未找到接口"})
            return
        payload, error = _read_json(self)
        if error:
            _json_response(self, 400, {"ok": False, "error": error})
            return
        try:
            _json_response(self, 200, _calculate(payload))
        except Exception as exc:
            traceback.print_exc()
            _json_response(self, 400, {"ok": False, "error": str(exc)})

    def do_DELETE(self) -> None:
        path = urlparse(self.path).path
        if not path.startswith("/api/report/"):
            _json_response(self, 404, {"ok": False, "error": "未找到接口"})
            return
        report_id = path.rsplit("/", 1)[-1]
        existed = REPORT_STORE.pop(report_id, None) is not None
        _json_response(self, 200, {"ok": True, "deleted": existed})

    def _send_file(self, path: Path, content_type: str) -> None:
        if not path.exists():
            _json_response(self, 404, {"ok": False, "error": "文件不存在"})
            return
        body = path.read_bytes()
        self.send_response(200)
        self.send_header("Content-Type", content_type)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)


def _content_type(path: Path) -> str:
    suffix = path.suffix.lower()
    if suffix == ".html":
        return "text/html; charset=utf-8"
    if suffix == ".js":
        return "application/javascript; charset=utf-8"
    if suffix == ".css":
        return "text/css; charset=utf-8"
    if suffix == ".svg":
        return "image/svg+xml"
    if suffix == ".png":
        return "image/png"
    if suffix == ".jpg" or suffix == ".jpeg":
        return "image/jpeg"
    if suffix == ".webp":
        return "image/webp"
    if suffix == ".ico":
        return "image/x-icon"
    return "application/octet-stream"


def main() -> None:
    host = sys.argv[1] if len(sys.argv) > 1 else DEFAULT_HOST
    port = int(sys.argv[2]) if len(sys.argv) > 2 else DEFAULT_PORT
    server = ThreadingHTTPServer((host, port), XiashensuanHandler)
    print(f"人生密码网页端 MVP 已启动：http://{host}:{port}")
    print(f"加载主仓：{PROJECT_ROOT}")
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n已停止")


if __name__ == "__main__":
    main()
