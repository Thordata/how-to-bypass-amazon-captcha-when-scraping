# Security & responsible use

## Educational purpose

This repository is provided **strictly for educational and research purposes**. It demonstrates how Amazon CAPTCHA is triggered and detected, and why manual bypass techniques do not scale. It is **not** a tool for evading anti-bot protections in production.

## Compliance is your responsibility

When accessing any third-party website (including Amazon), you are solely responsible for complying with that website's **Terms of Service**, **robots.txt** rules, and all **applicable laws and regulations** in your jurisdiction.

- Do **not** use these examples to overload, damage, or disrupt target sites.
- Do **not** use them where automated access is **prohibited by contract or law**.
- For commercial or large-scale usage, use a compliant managed solution and seek legal advice if unsure.

The authors and Thordata do **not** provide legal advice and are **not liable** for any misuse of this code.

## Reporting a vulnerability

Found a security issue in the **code in this repository** (e.g., the detection logic, CLI, or docs site scripts)? Please report it responsibly:

1. **Do not** open a public GitHub issue for security vulnerabilities.
2. Email **support@thordata.com** with a description and, if possible, a proof of concept.
3. Allow a reasonable response window before any disclosure.

Please note: reports about Amazon's anti-bot behavior, or requests to help bypass specific protections, are **out of scope** and will not receive a response.

## Credential safety

The Thordata examples read credentials from environment variables / a `.env` file. `.env` is gitignored — never commit real tokens. If you accidentally commit credentials, rotate them immediately in the Thordata dashboard.
