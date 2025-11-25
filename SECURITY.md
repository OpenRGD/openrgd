# Security Policy

OpenRGD defines the "Cognitive BIOS" for physical machines. Vulnerabilities in this standard—whether in the CLI toolchain or the semantic logic—can lead to physical harm. We take this responsibility with extreme seriousness.

## 🛡️ Reporting a Vulnerability

**DO NOT** report security issues via public GitHub Issues.

If you believe you have found a vulnerability in the OpenRGD Standard, the CLI, or any reference implementation, please report it via our dedicated security portal:

👉 **[https://vulnerabilities.openrgd.org](https://vulnerabilities.openrgd.org)**

If the portal is inaccessible, you may email the Security Stewardship Council directly at:
🔒 **security@openrgd.org**

### What to Report
We accept reports regarding:
* **Cognitive Bypasses:** Logic flaws in `02_operation` or `04_volition` that allow an AI to ignore safety constraints.
* **Integrity Failures:** Methods to bypass the `verify-twins` check or spoof the `kernel.jsonc` signature.
* **Toolchain Exploits:** Code execution or injection vulnerabilities in the `rgd` CLI or Bridge modules.
* **Privilege Escalation:** Flaws in the `02_operation/oversight_interface.jsonc` role definitions.

---

## 📦 Supported Versions

Security patches are prioritized for the current stable release and the immediate previous version.

| Version | Status | Security Updates |
| :--- | :--- | :--- |
| **v0.x (Alpha)** | **Active** | **Critical Only** |
| v0.0.x | EOL | No |

---

## ⏳ Disclosure Policy (Responsible Disclosure)

We adhere to a standard **90-day disclosure deadline**:
1.  Upon receiving a report via `vulnerabilities.openrgd.org`, the relevant Domain Maintainer (e.g., the *Volition Architect* for ethics bypasses) will triage the issue within 48 hours.
2.  We will work with you to verify and fix the vulnerability.
3.  Once fixed, we will publish a **Security Advisory** on the vulnerabilities portal and issue a new release.
4.  We will publicly acknowledge your contribution (unless you request anonymity).

## 🔑 PGP Key
For sensitive email communication, please use our PGP public key available at:
`https://openrgd.org/.well-known/openrgd_public_key.asc`

The fingerprint is:
`F642 B5CE FF72 F477 FAC3 AD66 5C55 7CA1 6AD3 D115`