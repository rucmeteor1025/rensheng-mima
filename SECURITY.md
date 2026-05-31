# Security Policy

## Reporting

Please open a private security advisory or contact the maintainer privately for vulnerabilities involving:

- exposure of birth records or generated reports
- path traversal or local file disclosure
- unsafe upload/parsing behavior
- payment or order-state bypasses in future production integrations

Do not include real personal data in public issues.

## Current Security Model

The current web service is a local MVP. It stores reports only in process memory and does not implement login, persistent storage, or real payment callbacks.

Before production deployment, the project needs:

- authenticated access
- encrypted persistence
- payment callback verification
- production logging with redaction
- rate limiting
- a stronger input-validation layer

