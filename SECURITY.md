# Security Policy

## Supported security scope

The current repository contains a draft standard and a non-actuating alpha toolchain. It does not provide a production physical runtime or certify any robot for safe operation.

Security fixes are applied to the active reconciliation/main lineage. Historical files under `docs/history/` are evidence and are not supported implementations.

## Reporting a vulnerability

Do not publish exploitable details in a public issue.

Use GitHub private vulnerability reporting when it is available for this repository. Otherwise email:

```text
rfc@openrgd.org
```

Use the subject prefix:

```text
[SECURITY] OpenRGD
```

Include:

- affected commit, tag or file;
- impact and preconditions;
- minimal reproduction evidence;
- whether physical hardware, middleware or an external Body Adapter is involved;
- any known safe mitigation;
- whether disclosure could create immediate physical risk.

Do not include secrets, personal data or unnecessary chain-of-thought transcripts.

## Physical-safety reports

A vulnerability involving actuation must also be reported to the responsible embodied-runtime or Body Adapter repository once that implementation is identified.

Do not reproduce a suspected actuation vulnerability on live hardware unless the system is isolated, independently supervised and the test is necessary to establish the issue. Prefer simulation, static fixtures and fail-closed reproduction.

The canonical repository cannot authorize hardware execution and must not be treated as a safety certification authority.

## Supply-chain reports

Report unexpected changes to:

- canonical source-tree hashes;
- release tags;
- CI workflows;
- generated artifacts or checksums;
- dependency resolution;
- signing or provenance metadata.

A SHA-256 digest demonstrates content identity, not trusted authorship.

## Public disclosure

A public advisory or issue should be created only after a safe fix or mitigation is available, or when coordinated disclosure is no longer possible. The public record should distinguish confirmed facts, affected versions and unresolved risk.
