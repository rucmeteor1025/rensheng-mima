# Contributing

Thanks for considering a contribution to 人生密码 / Rensheng Mima.

## Ground Rules

- Do not commit real birth records, names, private reports, screenshots, logs, tokens, cookies, or agent state.
- Use synthetic or anonymized examples only when they cannot identify a real person.
- Keep rule changes covered by deterministic tests.
- Avoid fear-based, deterministic life advice in user-facing copy.
- Keep medical, legal, financial, and psychological boundaries explicit.

## Development

```bash
pip install -r requirements.txt
python3 -B scripts/ziweiwenmotests.py
python3 -B scripts/xiashensuantests.py
python3 -B scripts/ziwei_patterns_tests.py
```

Frontend:

```bash
cd web/frontend
npm install
npm run build
```

## Pull Requests

Please include:

- what changed
- how it was tested
- whether any fixture or privacy-sensitive data was touched
- screenshots for UI changes

