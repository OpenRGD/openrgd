# OpenRGD Governance

OpenRGD is an open project. The goal of governance is to make changes understandable, reviewable and welcoming — not bureaucratic.

## Principles

1. **Evidence over assumption.** Explain why a normative change is needed.
2. **Dream boldly, label maturity honestly.** Targets and experiments are welcome when they are not presented as completed guarantees.
3. **Humans approve normative changes.** AI tools may help design, code, test and review; maintainers remain accountable.
4. **Keep the core understandable.** New complexity should earn its place.
5. **Safety-affecting changes fail closed.** Ambiguity must not silently become permission to actuate.

## How changes enter the project

Small fixes can use a normal pull request. Changes to the standard, compatibility boundaries, safety objectives or major architecture should open an RFC or clearly explain the decision in the pull request.

`main` is protected and changes are merged through reviewed pull requests with required CI checks.

## Maturity

OpenRGD uses simple maturity language:

- **stable** — intended for normal use within the declared version;
- **experimental** — implemented or specified but still evolving;
- **candidate** — proposed cross-component contract awaiting promotion;
- **target** — an engineering objective to measure toward;
- **proposal** — an idea not yet committed as implementation.

Presence in the repository is not enough to turn a target into a guarantee.

## Community

Good RFCs do not need to be formal essays. A useful contribution explains the problem, the proposed change, evidence or examples, compatibility impact and how we can test it.

See `CONTRIBUTING.md` and `ENTHUSIAST.md` to get involved.
