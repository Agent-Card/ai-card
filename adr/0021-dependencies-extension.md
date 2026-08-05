# ADR-0021: Entry Dependencies as an Official Extension

## Status
Proposed

## Date
2026-08-05 (Proposed)

## Context
[Issue #63](https://github.com/Agent-Card/ai-catalog/issues/63) (originally
[ards-project/ard-spec#42](https://github.com/ards-project/ard-spec/issues/42))
asks the catalog to describe an artifact's **downstream dependencies**: the
other agents, MCP servers, or datasets it needs to function, and — critically —
the credentials those dependencies require. The motivating use cases are
pre-flight ("can I use this agent — do I hold the credentials its dependencies
need?"), security and compliance planning (user-attributed vs. agent-attributed
access), discovery filtering ("hide agents requiring credentials I don't have"),
and impact analysis ("what breaks if I decommission MCP server X?").

[ADR-0002](0002-defer-entry-dependencies.md) previously **deferred** a
`dependencies` field. It did so for four reasons: (1) the AND-vs-OR ambiguity
(required co-requisites are AND; multi-protocol alternatives are OR); (2) a
nested catalog cannot say whether its members are alternatives or co-requisites;
(3) dependency semantics may belong to the downstream artifact formats; and (4)
scope-creep risk — the catalog should stay a simple index. ADR-0002 explicitly
left the door open: "implementation experience should drive whether and how
dependencies are added."

Two facts have changed the calculus since then:

- The specification now has a first-class, well-defined **extension mechanism**
  ([ADR-0012](0012-extensibility-via-metadata.md)): a closed core schema plus an
  `extensions` map keyed by reverse-DNS or URL, with an "Official Extensions"
  tier under the `https://ai-catalog.org/extensions/` prefix (currently just
  Metadata). This gives us a sanctioned home for capabilities that not every
  catalog needs, *without* enlarging the core.
- The AND/OR modeling problem — ADR-0002's central blocker — has a clean
  resolution once the two relationships are placed on separate structural axes
  (see Decision).

The original proposal predates several current conventions and must be
reconciled: it used `urn:ai:` (now `urn:air:{publisher}:{namespace}:{name}`,
[ADR-0015](0015-agent-identifier-naming.md)), `application/mcp-server+json`
(now `application/mcp-server-card+json`), `minVersion` (a lower bound only),
and `identityType` (which already means something else on Publisher and Trust
Manifest — an identifier *scheme* hint like `did`/`dns`/`spiffe`).

## Decision
Implement [issue #63](https://github.com/Agent-Card/ai-catalog/issues/63) as an **official extension**, not as a core Catalog Entry
field. Register `https://ai-catalog.org/extensions/dependencies` in the
specification's Official Extensions section. This keeps the core schema
minimal and dependency-free — honoring ADR-0002's decision rather than
reversing it — while delivering the capability through the extension point
ADR-0012 established for exactly this purpose.

**No core change, no version bump.** Because the capability rides on the
existing `extensions` map and unrecognized extensions MUST be ignored, the
change is purely additive. A catalog carrying the extension remains a
conformant `specVersion` "1.0" document; no core field, CDDL rule, data-model
diagram entry, or conformance level changes.

**Shape.** The extension value has two OPTIONAL arrays, `required` and
`optional`. Each element is a *Dependency Requirement* that is EITHER a single
Dependency object (the flat, common case) OR a Dependency Group carrying an
`anyOf` array of interchangeable alternatives. A Dependency has a REQUIRED
`identifier` (a `urn:air` reference to another artifact) plus OPTIONAL `type`,
`versionConstraint`, `credentialPropagation`, and `purpose`.

**AND/OR resolution (ADR-0002 concerns 1 & 2).** The two relationships live on
two independent axes so neither field is overloaded:

- **AND** is the outer `required` array — every element is a co-requisite.
- **OR** is the inner `anyOf` group — any one alternative satisfies that one
  slot (e.g. "a vector store: Pinecone *or* pgvector").

This is kept deliberately distinct from the nested-catalog dual-protocol
pattern ([ADR-0004](0004-eliminate-bundle-concept.md)): a nested catalog is
**one** logical artifact with multiple protocol faces; `anyOf` is **different**
artifacts that interchangeably fill a capability slot. Routing OR through
nested catalogs was rejected because it recreates ADR-0002's ambiguity.

**Downstream ownership & scope (ADR-0002 concerns 3 & 4).** The extension
declares *discovery edges* only — references by `identifier`, never embedded
artifacts, and no mandated transitive resolution. The depended-on artifact
still owns its own internal requirements; the catalog does not become a package
manager or resolver. This preserves the thin-pointer posture
([ADR-0013](0013-authoring-vs-distribution-formats.md)) and loose coupling
([ADR-0017](0017-ard-loose-coupling.md)).

**Field reconciliations.**

- `versionConstraint` (not `minVersion`, not `version`): a SemVer *range*
  matcher. `minVersion` is only a floor and cannot express an upper bound
  ("needs v3 but v4 is breaking"), which is exactly the pre-flight
  compatibility question. Reusing `version` would mislead readers into
  treating a range as a concrete literal (and `version` is the multi-version
  uniqueness key).
- `credentialPropagation` (not `identityType`): a distinct field to avoid a
  name collision — `identityType` already means an identifier *scheme* hint
  (`did`/`dns`/`spiffe`) on Publisher and Trust Manifest, whereas this concept
  is credential/audit attribution. Open text with a RECOMMENDED value set
  (`obo`, `agent`, `user`, `none`, lowercase to match existing `identityType`
  casing), matching how the spec treats every other type-ish field. Marked
  **advisory**, never an authoritative security control.

## Rationale
- **Honors ADR-0002 instead of reversing it.** ADR-0002's goal was a simple
  core; an extension keeps the core simple while shipping the capability.
- **Uses the mechanism designed for this.** ADR-0012 created Official
  Extensions precisely so non-universal capabilities need not enter the core.
- **Resolves the real blocker.** The AND/OR ambiguity that stalled ADR-0002 is
  removed by separating the axes (`required` = AND, `anyOf` = OR).
- **Zero-cost to non-adopters.** Additive, ignorable, no version bump; a
  planner that understands the extension gains pre-flight/impact-analysis
  without imposing anything on catalogs that don't.
- **Cross-vendor governance.** Standardizing the shape (rather than leaving it
  to per-vendor `extensions` keys) is what makes cross-platform pre-flight and
  impact analysis interoperable — the concern raised at the end of
  [issue #63](https://github.com/Agent-Card/ai-catalog/issues/63).

## Consequences
- The spec's Official Extensions section gains a **Dependencies Extension**
  subsection (structure, Dependency Requirement, Dependency object, resolution
  semantics, example, and a CDDL block for the extension value). A new Security
  Considerations subsection ("Dependency Confusion and Malicious Dependencies")
  and a note under Catalog Poisoning cover reference substitution, advisory
  hints not being controls, cycle/depth bounds, and topology leakage.
- No change to the core CatalogEntry CDDL, the Data Model diagram, the
  conformance levels, or `specVersion`.
- ADR-0002 is annotated with a forward reference to this ADR but **remains
  Accepted**: its decision (no *core* dependency field) still stands.
- The MCP and Claude-Plugins mapping appendices gain a row noting dependencies
  as catalog-layer extension metadata the native formats do not carry.
- Docs gain an authoring subsection, a consumer pre-flight-check section, a
  dedicated example page, and nav/feature entries.

## Alternatives Considered
- **A core `dependencies` field on Catalog Entry.** Rejected: it re-opens
  ADR-0002's "keep the core simple" decision and forces the capability on every
  catalog reader. The extension delivers the same shape without enlarging the
  core. (If adoption becomes near-universal, ADR-0012 already anticipates
  promoting an official extension to a core field in a future version.)
- **Keeping the proposal's `minVersion`.** Rejected: a lower bound cannot
  express an upper bound, the key compatibility question for pre-flight.
- **Reusing `identityType` for credential propagation.** Rejected: name
  collision with the existing identifier-scheme meaning.
- **Expressing OR via nested catalogs.** Rejected: recreates the exact
  AND/OR ambiguity ADR-0002 flagged; explicit `anyOf` removes it.
- **Always-array `anyOf` (every requirement is a group).** Rejected as verbose
  for the common single-dependency case; the discriminated
  single-Dependency-or-group union keeps the flat case flat.
- **A closed MUST-enum for `credentialPropagation`.** Rejected for now: open
  text with a RECOMMENDED set matches the spec's treatment of `type` and
  `identityType` and leaves room for cases like multi-hop delegation. A future
  ADR MAY tighten it to a registered enum once usage settles.

## Open Questions
- Whether `obo`/`agent`/`user`/`none` are sufficient for real deployments
  (multi-hop delegation, per-tool credential scoping) before this stabilizes.
- Whether the spec should go beyond SHOULD in RECOMMENDING that catalogs
  relying on dependencies for pre-flight decisions carry a catalog-level
  signature, given the extension sits outside the Trust Manifest's signed
  subject.
- Whether OCI / xRegistry substrate bindings need to round-trip the extension
  explicitly, or whether carrying it inline as opaque entry metadata suffices.

## Meeting Reference
Records a proposal ahead of an AI Catalog bi-weekly working-group discussion,
implementing the deferred capability from [ADR-0002](0002-defer-entry-dependencies.md)
via the extension mechanism of [ADR-0012](0012-extensibility-via-metadata.md).
Update the Status and Date (and note who raised concerns and the agreed
outcome) once the working group ratifies it.
