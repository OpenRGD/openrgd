# Annual Maintenance & Renewal Rituals

This document defines the mandatory administrative and technical tasks that must be performed **once per year** (typically in January) to ensure the continuity, security, and legal health of the OpenRGD project.

> **Goal:** To signal to the world (and the machines) that the standard is alive, governed, and secure.

---

## 🛡️ 1. Security Infrastructure (CRITICAL)

These tasks prevents security warnings and ensures researchers can still contact us.

- [ ] **Renew `security.txt` Expiry**
    * **Why:** The RFC 9116 standard requires an `Expires` field. If expired, security researchers may assume the project is abandoned.
    * **Action:** Update the date in `.well-known/security.txt` to one year in the future.
    * **Command:** `Expires: 2026-01-01T00:00:00.000Z` -> `2027...`

- [ ] **Review PGP/GPG Keys**
    * **Why:** Keys may expire or algorithms may become weak.
    * **Action:** Check the expiration date of the key `security@openrgd.org`.
    * **Command:** `gpg --list-keys`
    * **If expiring:** Extend the expiry date (`gpg --edit-key ... expire`) and upload the new public key to the website.

- [ ] **Audit Maintainer Access**
    * **Action:** Review the list of people with "Write" access to the GitHub repository and "Publish" access to PyPI.
    * **Rule:** Remove anyone who has been inactive for >12 months or moved to a conflict-of-interest role.

---

## ⚖️ 2. Legal & Copyright

- [ ] **Update Copyright Year**
    * **Action:** Update the year in the `NOTICE` file and the website footer.
    * **Format:** `Copyright © 2025-2026 OpenRGD Foundation`.
    * *Note:* You do not need to update the header of every single source file unless you modified that specific file, but updating the global `NOTICE` is mandatory.

- [ ] **License Dependency Check**
    * **Action:** Verify that no new dependencies have been added with incompatible licenses (e.g., GPL if we want to stay MIT).

---

## 🗺️ 3. Roadmap & Vision

- [ ] **Archive Completed Milestones**
    * **Action:** Move completed items from `ROADMAP.md` to `CHANGELOG.md`.

- [ ] **Update the "North Star"**
    * **Action:** Add the high-level goals for the new year in `ROADMAP.md`.
    * **Context:** Is "Phase 2" finished? Are we moving to "Standardization"?

---

## 🏗️ 4. Technical Hygiene

- [ ] **Dependency Upgrade**
    * **Action:** Run a security audit on Python dependencies.
    * **Command:** `pip list --outdated` or `pip-audit`.
    * **Task:** Upgrade `typer`, `rich`, or `pydantic` if major versions are available, and verify `rgd check` still passes.

- [ ] **Deprecated Features Cleanup**
    * **Action:** If a feature was marked "Deprecated" in the previous major version, remove it now from the codebase.

---

## 📢 5. Community Signal

- [ ] **"State of the Union" Post**
    * **Action:** Publish a short post on GitHub Discussions or the Blog.
    * **Content:** "OpenRGD is entering year X. Here is what we achieved, here is where we are going."

---

*Checklist last updated: 2025-11-25*