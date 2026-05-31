# 人生密码 / Rensheng Mima

Local-first Chinese metaphysics computation toolkit and web MVP.

人生密码是一个本地优先的中文命理结构化计算工具。它把八字、紫微斗数、文墨天机兼容文字盘解析、格局识别和融合报告拆成可测试的工程模块，并提供一个 React/Vite 本地网页入口。

> This project is for cultural research, structured rule-engine experiments, and personal reflection. It is not medical, legal, financial, or psychological advice.

## Why This Exists

Traditional Chinese metaphysics tools often mix calculation, interpretation, private records, and product UI in one opaque bundle. 人生密码 tries to make that stack more transparent:

- deterministic chart computation and parser outputs
- privacy-preserving local execution
- fixture-based regression tests
- clear boundaries between rules, renderers, and web UI
- cautious wording with explicit disclaimers

## Features

- BaZi engine with true-solar-time correction, ten-god analysis, weighted five-elements scoring, day-master strength, useful-god strategy, and luck-cycle summaries
- Zi Wei Dou Shu engine using a C5FYC-style rule path, palace maps, major stars, support stars, transformations, and boundary-sensitive double-chart handling
- Wenmo-compatible text parser for private local regression workflows
- Pattern detectors for Zi Wei chart structures
- Fusion layer for BaZi, Zi Wei, MBTI, zodiac, and blood-type modules
- Local web MVP with free summary, mock checkout flow, privacy page, pricing page, and report deletion

## Privacy Boundary

No real user birth records, names, generated reports, private notes, logs, tokens, or agent state are included in this public package.

The public `xiashensuan_core/fixtures/wenmo_cases/manifest.json` is intentionally empty. Maintainers can keep private fixture records locally under `private_records/`, which is ignored by Git.

## Quick Start

```bash
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python3 scripts/xiashensuan.py 1990 1 15 14 --minute 30 --gender 男 --place 北京 --mode life
```

Run the local web MVP:

```bash
python3 web/server.py
```

Open `http://127.0.0.1:8765`.

## Frontend

```bash
cd web/frontend
npm install
npm run build
```

After building, restart `python3 web/server.py`; the server will serve `web/frontend/dist/` first and fall back to `web/static/` if no build exists.

## Tests

```bash
python3 -B scripts/ziweiwenmotests.py
python3 -B scripts/xiashensuantests.py
python3 -B scripts/ziwei_patterns_tests.py
python3 -B scripts/wenmo_text_scan.py --record-dir private_records
```

Private Wenmo fixture tests are skipped when no private fixtures exist.

## Repository Scope

Included:

- rule engines
- local web MVP source
- deterministic tests
- privacy and contribution docs

Excluded:

- real case records
- generated reports
- private agent files
- `.openclaw` or local runtime state
- `node_modules`
- frontend build artifacts

## Roadmap

- Add synthetic public fixtures that do not come from real users
- Split the engine into a proper Python package
- Add typed JSON schema for chart outputs
- Add GitHub Pages demo screenshots
- Add CI coverage for frontend build and backend smoke tests
- Add privacy review checklist for contribution review

## License

MIT.

