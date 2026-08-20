# ADR-0023: Lifecycle Metadata as an Official Extension

## Status
Accepted

## Date
2026-08-06

## Context
[Issue #65](https://github.com/Agent-Card/ai-catalog/issues/65)
observes that the specification has no way to communicate an artifact's
software-lifecycle state at discovery time. An entry carries `version`
(which revision this is) and `updatedAt` (when the entry last changed),
but nothing that expresses *where that revision sits in its lifecycle*:
whether it is a preview, generally available, deprecated with a scheduled
end-of-life, or already retired — nor how a consumer should move off it.

Agents evolve. A v1 agent is superseded by a breaking v2; an endpoint is
scheduled for shutdown; a successor is published with a migration guide.
Without lifecycle metadata at discovery time a consumer cannot distinguish
a current artifact from a deprecated one, cannot learn an end-of-life date
before committing to an integration, and cannot discover the recommended
replacement. The core entry schema, which is intentionally closed (see
[ADR-0012](0012-extensibility-via-metadata.md)), has no place to express
this, and there is no interoperable convention for it today.

## Decision
Lifecycle metadata is defined as an **official extension**, registered at
the extension key `https://ai-catalog.org/extensions/lifecycle`, and
carried in the entry's `extensions` map. It is **not** added as a native
`lifecycle` field on the entry.

The extension value is a JSON object with these OPTIONAL members:

- `status` (string) — the lifecycle state; open text, with RECOMMENDED
  values `preview`, `active`, `deprecated`, and `retired`. Every
  recommended value denotes a version a consumer can actually reach: a
  catalog entry exists because the artifact is discoverable, so a
  not-yet-released ("planned") state is deliberately excluded — an
  unreleased version has no consumable endpoint to list.
- `releaseDate` (string) — ISO 8601 date/date-time the version was
  released, distinct from the entry's `updatedAt`.
- `deprecated` (object) — deprecation detail, present when `status` is
  `deprecated` or `retired`. It carries:
  - `replacedBy` (string) — the `identifier` of the successor artifact,
    subject to the same naming rule as a Catalog Entry's `identifier`
    (`urn:air` HIGHLY RECOMMENDED, and MUST be used for open or federated
    systems).
  - `deprecationDate` (string) — ISO 8601 date/date-time of deprecation.
  - `endOfLifeDate` (string) — ISO 8601 date/date-time after which the
    version is retired.
  - `breakingChanges` (array of strings) — human-readable breaking-change
    descriptions.
  - `migrationGuide` (string) — URL to migration documentation.

Lifecycle metadata describes the artifact **version** identified by the
entry, not the logical artifact as a whole: within a multi-version listing
(see the specification's Multi-Version Entries), a v1 entry MAY be
`deprecated` while the v2 entry is `active`. A consumer that does not
understand the key MUST ignore it; a consumer that does understand it MAY
filter or rank entries by lifecycle state (e.g. exclude `retired`, warn on
`deprecated`, prefer the `replacedBy` successor) and MAY still choose a
deprecated artifact deliberately. All identifiers use the `urn:air` format
mandated by [ADR-0015](0015-agent-identifier-naming.md).

`status` is intentionally open text rather than a closed enum, consistent
with how the specification treats `type` and `identifier`. Because it is
open text, a consumer MUST NOT reject an entry for an unrecognized status,
but it also MUST NOT silently discard the value and treat the artifact as
unqualified — that fails open, since a value such as `sunset` may signal a
retirement the consumer would then miss. A consumer SHOULD interpret an
unrecognized value against the recommended states (an agent consumer can
do so semantically) and, when it cannot, treat the artifact conservatively
rather than assume it is `active`. This preserves the spec's open-text
extensibility while making unrecognized values fail safe rather than fail
open.

## Rationale
- Keeps the core entry schema closed and stable, consistent with the
  closed-core philosophy of
  [ADR-0012](0012-extensibility-via-metadata.md); a not-yet-universal
  need does not force a change to the core.
- Consumers that do not recognize the key ignore it safely and treat the
  entry as any other, guaranteed by the existing `extensions` rule.
- The extension can evolve independently without requiring a major version
  bump of the specification.
- Aligns with the precedent already set by the Metadata official extension
  (`https://ai-catalog.org/extensions/metadata`).

## Alternatives Considered
- **Native `lifecycle` field on the entry** (as the original issue
  proposed) — Rejected. It bloats the closed core for a need that is not
  universal and reopens the schema evolution problem ADR-0012 was written
  to avoid.
- **Overloading `version`/`updatedAt` with a status convention** —
  Rejected. Those fields have defined, distinct semantics; encoding
  lifecycle state into them would be ambiguous and non-interoperable.
- **Freeform vendor metadata** — Rejected. Ad-hoc, per-vendor keys give no
  interoperability, so no consumer could filter deprecated artifacts or
  discover successors deterministically across producers.

## Consequences
- Deprecation and retirement become discoverable and actionable before a
  consumer commits to an integration; migration paths are advertised at
  discovery time.
- The metadata is advisory. It is unsigned unless carried in a Trust
  Manifest's `extensions`, and MUST NOT be treated as a security or
  support guarantee on its own; the dates and successor reference are
  producer assertions a consumer needing assurance corroborates out of
  band.
- The official extensions registry gains one entry:
  `https://ai-catalog.org/extensions/lifecycle`.
