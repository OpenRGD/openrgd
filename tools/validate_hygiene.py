#!/usr/bin/env python3
"""Fail closed on tracked secrets, generated debris and unclassified AI-era claims."""

from __future__ import annotations

import collections
import json
import re
import subprocess
import sys
from pathlib import Path, PurePosixPath
from typing import Iterable

ROOT = Path(__file__).resolve().parents[1]

FORBIDDEN_EXACT_PATHS = {
    ".env",
    "Dockerfile",
    "ENTHUSIAST.md",
    "GUIDE_DOCKER.md",
    "MAINTENANCE.md",
    "ONBOARDING.md",
    "PLUGIN_GUIDE.md",
    "plugins.toml",
    "src/openrgd/commands/plugins.py",
    "src/openrgd/core/command_registry.py",
    "src/openrgd/core/plugins_policy.py",
    "src/rgd_schema.jsonc",
}
FORBIDDEN_PREFIXES = (
    "plugins/",
    "assets/branding/proposal/",
)
GENERATED_PARTS = {
    "__pycache__",
    ".pytest_cache",
    ".mypy_cache",
    ".ruff_cache",
    "build",
    "dist",
}
BINARY_SUFFIXES = {
    ".7z",
    ".a",
    ".avi",
    ".bin",
    ".bmp",
    ".class",
    ".dll",
    ".dylib",
    ".exe",
    ".gif",
    ".gz",
    ".ico",
    ".jar",
    ".jpeg",
    ".jpg",
    ".mp3",
    ".mp4",
    ".o",
    ".pdf",
    ".png",
    ".pyc",
    ".rar",
    ".so",
    ".tar",
    ".tgz",
    ".whl",
    ".woff",
    ".woff2",
    ".xz",
    ".zip",
}
SECRET_PATTERNS = (
    ("openai_api_key", re.compile(r"\bsk-(?:proj-|svcacct-)?[A-Za-z0-9_-]{20,}\b")),
    ("github_token", re.compile(r"\bgh[pousr]_[A-Za-z0-9]{20,}\b")),
    ("aws_access_key", re.compile(r"\bAKIA[0-9A-Z]{16}\b")),
    ("slack_token", re.compile(r"\bxox[baprs]-[A-Za-z0-9-]{20,}\b")),
    (
        "private_key",
        re.compile(r"-----BEGIN (?:RSA |EC |OPENSSH |DSA )?PRIVATE KEY-----"),
    ),
)
SECRET_ASSIGNMENT = re.compile(
    r"""(?im)^\s*
    (?P<name>
        OPENAI_API_KEY|
        ANTHROPIC_API_KEY|
        GOOGLE_API_KEY|
        GITHUB_TOKEN|
        GH_TOKEN|
        AWS_SECRET_ACCESS_KEY|
        AZURE_OPENAI_API_KEY|
        DATABASE_URL|
        SUPABASE_SERVICE_ROLE_KEY
    )
    \s*[:=]\s*
    ["']?(?P<value>[^\s"'#]+)
    """,
    re.VERBOSE,
)
PLACEHOLDER_MARKERS = (
    "${",
    "<",
    "changeme",
    "example",
    "placeholder",
    "replace",
    "test-only",
    "your_",
    "your-",
)
UNVERIFIED_CONTACT_DOMAIN = "@openrgd" + ".org"
UNVERIFIED_URL_DOMAIN = "openrgd" + ".org"
LOCAL_PATH_PATTERNS = (
    re.compile(r"(?<![A-Za-z0-9_])/home/[A-Za-z0-9._-]+/"),
    re.compile(r"(?<![A-Za-z0-9_])" + "/mnt" + r"/data/"),
    re.compile(r"(?i)\b[A-Z]:\\Users\\[^\\\r\n]+\\"),
)


class HygieneError(ValueError):
    """Raised when repository hygiene invariants are violated."""


def tracked_paths() -> list[str]:
    result = subprocess.run(
        ["git", "ls-files", "-z"],
        cwd=ROOT,
        check=True,
        capture_output=True,
    )
    return sorted(
        item.decode("utf-8")
        for item in result.stdout.split(b"\0")
        if item
    )


def is_forbidden_secret_path(path: str) -> bool:
    pure = PurePosixPath(path)
    name = pure.name
    if name == ".env":
        return True
    if name.startswith(".env.") and name not in {".env.example", ".env.template"}:
        return True
    if name in {"id_rsa", "id_ed25519"}:
        return True
    if name.startswith(("id_rsa.", "id_ed25519.")):
        return True
    if pure.suffix.lower() in {".key", ".p12", ".pfx", ".pem"}:
        return True
    lower = name.lower()
    return (
        lower.startswith("credentials")
        and lower.endswith(".json")
    ) or (
        lower.startswith("service-account")
        and lower.endswith(".json")
    )


def is_generated_path(path: str) -> bool:
    pure = PurePosixPath(path)
    if any(part in GENERATED_PARTS or part.endswith(".egg-info") for part in pure.parts):
        return True
    return pure.suffix.lower() in {".pyc", ".pyo"}


def should_scan_text(path: str) -> bool:
    pure = PurePosixPath(path)
    if pure.suffix.lower() in BINARY_SUFFIXES:
        return False
    local = ROOT / path
    return local.is_file() and local.stat().st_size <= 2_000_000


def is_placeholder(value: str) -> bool:
    normalized = value.strip().lower()
    return not normalized or any(marker in normalized for marker in PLACEHOLDER_MARKERS)


def active_contact_scope(path: str) -> bool:
    excluded = (
        "docs/history/",
        "docs/reconciliation/",
        "spec/",
        "standard/",
        "src/openrgd/seeds/",
    )
    return not path.startswith(excluded)


def local_path_scope(path: str) -> bool:
    excluded = (
        "docs/history/",
        "docs/reconciliation/",
        "spec/",
        "standard/",
        "src/openrgd/seeds/",
    )
    return not path.startswith(excluded)


def scan_tracked_files(paths: Iterable[str]) -> list[str]:
    errors: list[str] = []
    for path in paths:
        if path in FORBIDDEN_EXACT_PATHS:
            errors.append(f"obsolete or unaccepted active surface is tracked: {path}")
        if path.startswith(FORBIDDEN_PREFIXES):
            errors.append(f"obsolete or unaccepted active tree is tracked: {path}")
        if is_forbidden_secret_path(path):
            errors.append(f"secret-bearing filename is tracked: {path}")
        if is_generated_path(path):
            errors.append(f"generated artifact is tracked: {path}")
        if not should_scan_text(path):
            continue

        try:
            text = (ROOT / path).read_text(encoding="utf-8")
        except UnicodeDecodeError:
            continue

        for pattern_id, pattern in SECRET_PATTERNS:
            if pattern.search(text):
                errors.append(f"possible {pattern_id} material in tracked file: {path}")

        for match in SECRET_ASSIGNMENT.finditer(text):
            if not is_placeholder(match.group("value")):
                errors.append(
                    f"non-placeholder secret assignment for "
                    f"{match.group('name')} in tracked file: {path}"
                )

        if active_contact_scope(path):
            if UNVERIFIED_CONTACT_DOMAIN in text or (
                UNVERIFIED_URL_DOMAIN in text
                and "github.com/OpenRGD/openrgd" not in text
            ):
                errors.append(
                    f"unverified OpenRGD contact/domain assertion outside "
                    f"the registered draft-spec scope: {path}"
                )

        if local_path_scope(path):
            for pattern in LOCAL_PATH_PATTERNS:
                if pattern.search(text):
                    errors.append(f"machine-local absolute path in active file: {path}")
                    break
    return errors


def validate_spec_content_registry() -> list[str]:
    registry_path = ROOT / "docs/reconciliation/SPEC_CONTENT_HYGIENE.json"
    if not registry_path.is_file():
        return ["missing SPEC_CONTENT_HYGIENE.json"]
    registry = json.loads(registry_path.read_text(encoding="utf-8"))
    if registry.get("stable_standard_release_blocking") is not True:
        return ["known draft assertions must block a stable standard release"]
    if registry.get("merge_blocking_for_reconciliation_pr_1") is not False:
        return ["draft assertion registry has ambiguous merge behavior"]

    spec_files = sorted((ROOT / "spec").rglob("*.jsonc"))
    texts = {
        path.relative_to(ROOT).as_posix(): path.read_text(encoding="utf-8")
        for path in spec_files
    }
    combined = "\n".join(texts.values())
    errors: list[str] = []

    expected_contacts = collections.Counter()
    for item in registry.get("registered_contact_literals", []):
        literal = str(item["literal"])
        count = int(item["expected_count"])
        expected_contacts[literal] += count
        actual = combined.count(literal)
        if actual != count:
            errors.append(
                f"registered contact count drifted for {literal!r}: "
                f"expected {count}, found {actual}"
            )

    actual_contacts = collections.Counter(re.findall(r'mailto:[^"\s]+', combined))
    if actual_contacts != expected_contacts:
        unregistered = actual_contacts - expected_contacts
        missing = expected_contacts - actual_contacts
        if unregistered:
            errors.append(
                "unregistered specification contact assertions: "
                + ", ".join(
                    f"{value!r} x{count}"
                    for value, count in sorted(unregistered.items())
                )
            )
        if missing:
            errors.append(
                "registered specification contacts disappeared without registry update: "
                + ", ".join(
                    f"{value!r} x{count}"
                    for value, count in sorted(missing.items())
                )
            )

    for item in registry.get("registered_assertion_literals", []):
        literal = str(item["literal"])
        count = int(item["expected_count"])
        actual = combined.count(literal)
        if actual != count:
            errors.append(
                f"registered draft assertion count drifted for {literal!r}: "
                f"expected {count}, found {actual}"
            )

    return errors


def main() -> int:
    try:
        paths = tracked_paths()
        errors = scan_tracked_files(paths)
        errors.extend(validate_spec_content_registry())
    except (
        HygieneError,
        FileNotFoundError,
        KeyError,
        TypeError,
        ValueError,
        json.JSONDecodeError,
        subprocess.CalledProcessError,
    ) as exc:
        print(f"FAIL: {exc}", file=sys.stderr)
        return 1

    if errors:
        for error in errors:
            print(f"FAIL: {error}", file=sys.stderr)
        return 1

    print(
        "PASS: repository hygiene; no tracked secret paths or token patterns; "
        "obsolete AI-generated surfaces absent; draft spec assertions registered"
    )
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
