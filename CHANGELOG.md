# Changelog

## 0.3.0 - Versioned JSON Schema output contracts

- Added 4 JSON Schema contracts under `xiashensuan_core/schemas/` (bazi / ziwei / fusion / web_summary), draft-07, versioned `1.0.0`
- Added `scripts/schema_contract_tests.py` (dependency-free validator) wired into CI
- Contracts validated against both `life` and `professional` engine outputs on synthetic samples
- Closes #2

## 0.2.0 - Synthetic fixtures + public parser regression

- Added deterministic synthetic Wenmo chart fixtures (3 cases, no real user data)
- Added `scripts/gen_synthetic_fixtures.py` generator with `--verify` re-parse check
- Added `scripts/wenmo_synthetic_tests.py` regression suite wired into CI
- Manifest now carries synthetic entries with parse expectations (birth, true solar time, four-hua stars)

## 0.1.0 - Local MVP

- Added BaZi and Zi Wei computation entry point
- Added Wenmo-compatible parser support for private local regression
- Added Zi Wei pattern detectors
- Added local web MVP with React/Vite source and static fallback
- Added privacy-first OSS packaging with no real case records

