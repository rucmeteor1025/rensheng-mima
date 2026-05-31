# Privacy Policy for the Public OSS Project

人生密码 treats birth information and generated reports as highly sensitive personal data.

The public repository must not contain:

- real names
- exact real birth records tied to a person
- private reports
- screenshots of private reports
- chat logs, sessions, tokens, cookies, API keys, or local agent state

The local MVP currently stores generated reports in memory only. When the process exits, reports are cleared.

If you run private regression tests, keep fixtures under `private_records/`; this path is ignored by Git.

