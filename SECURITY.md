# Security Policy

This document describes the security policy for Mastodon Random Facts Bot, including supported versions, vulnerability reporting, scope, and disclosure expectations.

## 📑 Table of Contents

- [Supported Versions](#-supported-versions)
- [Reporting a Vulnerability](#-reporting-a-vulnerability)
- [Scope](#-scope)
- [Disclosure Policy](#-disclosure-policy)

## 🛡️ Supported Versions

Use this table to indicate which project versions currently receive security maintenance.

| Version | Distribution Channel | Supported |
|---------|--------------------|-----------|
| Latest version | GitHub Releases | ✅ |
| Latest version | Source (master branch) | ✅ |
| Preceding versions | Any distribution channel | ❌ |

## 🚨 Reporting a Vulnerability

Please do not disclose suspected vulnerabilities publicly before maintainers have had an opportunity to validate and remediate them.

To report a vulnerability:
- [GitHub Security Advisories](https://github.com/hmlendea/mastodon-random-facts-bot/security/advisories)
- Contact the maintainers directly

## 📌 Scope

The original maintainers are not responsible for changes, modifications, or security issues introduced by downstream forks.

The subsequent report categories are in scope for this repository:
- Vulnerabilities in the application code (mastodon-random-facts-bot.py, dynamic_tags.py, text_replacements.py)
- Dependency vulnerabilities in declared requirements (fake_useragent, Mastodon.py, regex)
- Secret handling issues (Mastodon access token, application secret file)

The subsequent categories are out of scope unless explicitly stated to the contrary:
- Vulnerabilities in the Mastodon API or Mastodon instances
- Vulnerabilities in Python standard library or runtime
- Vulnerabilities in third-party services not directly integrated
- Issues in downstream forks or modified deployments
- Denial-of-service via Mastodon API rate limits

## 📢 Disclosure Policy

This project follows coordinated disclosure:
1. Vulnerabilities are investigated privately.
2. A remediation plan is prepared and validated.
3. Public disclosure is published after a fix, mitigation, or agreed risk decision is available.
4. Credit is attributed in accordance with reporter preference and project policy.