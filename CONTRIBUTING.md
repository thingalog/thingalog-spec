# Contributing to catdef

catdef is an open standard for machine-enhanceable descriptors of real-world objects and catalogs. This document describes how changes to the specification are proposed, reviewed, and accepted.

## Governance

catdef is stewarded independently of any single implementation. The standard exists to enable interoperability between runtimes — browser-only L1 readers, lightweight L2 servers, full-graph L3 platforms, and L4 hosting platforms — not to codify any one product's schema.

**Implementations do not own the spec.** Thingalog, PXMemo, dangerstorm, partner-branded renderers, and any future catdef runtime are equal citizens from the spec's perspective. Each is a consumer. Each can propose changes. No one gets unilateral authorship.

## The change-request process

Changes to the specification follow a structured process:

### 1. Propose

Open a GitHub issue or pull request describing:

- **What the change is** — new field type, new attribute, new conformance requirement, clarification, etc.
- **Why it's needed** — concrete use case, ideally with an implementation that would adopt it
- **How it affects existing catdefs** — backward compatibility, migration story, impact on v1.x readers
- **Which conformance level it targets** — L1 (universal), L2 (server), L3 (graph), L4 (platform)

### 2. Discuss

Proposals are discussed openly. Expect questions about:

- Is this a spec concern or an implementation detail? (Most things are implementation details.)
- Does this generalize beyond the proposing implementation?
- Can it be expressed via the existing [extension namespace](CATDEF_SPEC.md#extension-namespace) (`x.<domain>.<identifier>`) instead?
- Does it obligate runtimes to add significant complexity? (Raise the conformance bar.)

### 3. Prototype

For non-trivial changes, a prototype in at least one implementation is required before the change is merged into the main spec. The prototype proves the change is buildable and catches edge cases before they become spec text.

### 4. Merge

Changes are merged when:

- Prototype demonstrates feasibility
- Conformance tests (if applicable) are written and passing
- Documentation is complete — main spec + examples + changelog entry
- No unresolved blocking objections from maintainers

### 5. Version

- **Patch (1.x.y)** — documentation clarifications, no schema changes
- **Minor (1.x.0)** — new optional fields, new field types, new settings. Old catdefs remain valid. Old runtimes gracefully ignore new fields.
- **Major (x.0.0)** — breaking changes to required fields or semantics. Runtime MUST check major version before rendering.

Version bumps happen at the end of a release cycle, not per-change.

## What NOT to propose

- **Implementation-specific features.** "How Thingalog does X" belongs in Thingalog's codebase, not the spec. If every runtime would do it differently, it's not spec-worthy.
- **Features that belong in the extension namespace.** If your use case can be expressed via `x.<domain>.<field>`, use that. The extension namespace exists precisely so the core spec stays lean.
- **Wishlist items without a concrete use case.** "Wouldn't it be cool if..." without an implementation that would adopt it gets deferred.
- **Changes that break L1 conformance.** The browser-only minimal tier is sacred. If your change requires a server, it belongs at L2+.

## What SHOULD be proposed

- **Gaps discovered during implementation.** If a real runtime hits a case the spec doesn't cover, that's spec feedback.
- **Interoperability issues.** Two implementations reading the same catdef differently → spec ambiguity.
- **New field types with cross-implementation demand.** If three unrelated runtimes all invent the same extension, it's time to promote it.
- **Conformance test additions.** More tests = more interoperability confidence.
- **Clarifications, corrections, typos.** Always welcome.

## Conformance test suite

The test suite in [conformance/](conformance/) is the practical expression of the standard. A change to the spec that doesn't come with test coverage isn't really part of the spec. Contributions to the test suite are as valuable as contributions to the spec text.

**The test suite is the standard.**

## Implementer roles

If you're building a catdef runtime, you're welcome to:

- Propose changes through the process above
- Add conformance tests
- Publish a conformance report showing which tests your implementation passes
- List your runtime in the implementations directory

You are NOT welcome to:

- Extend the core spec unilaterally in your implementation (use the extension namespace)
- Claim "catdef compliant" if you don't pass the test suite
- Use the catdef name/branding for a fork

## License

catdef is MIT licensed. Build whatever you want. If it passes the tests, it's catdef.

## Contact

File issues and PRs on this repository. Structured feedback at [catdef.org/feedback](https://catdef.org/feedback).
