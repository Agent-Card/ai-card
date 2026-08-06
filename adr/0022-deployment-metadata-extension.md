# ADR-0022: Deployment Metadata as an Official Extension

## Status
Accepted

## Date
2026-08-05

## Context
[Issue #64](https://github.com/Agent-Card/ai-catalog/issues/64)
observes that a Catalog Entry conflates *identity* ("what the agent is")
with *instance* ("where it lives"). The entry's `identifier` names a
single logical artifact, and its `url` names a single entry point — yet
the same logical agent is routinely deployed many times: across
environments (development, staging, production), across release channels
(stable, beta, LTS, edge), and across regions (us-east, eu-west) that
carry differing data-residency and compliance constraints.

Enterprise consumers need to discover and select among these deployments
deterministically: an EU client must reach an EU instance subject to
GDPR, a test harness must reach staging, and shadow-testing a pre-release
release channel must be possible — all while the artifact keeps a single
logical identity. The
core entry schema, which is intentionally closed (see
[ADR-0012](0012-extensibility-via-metadata.md)), has no place to express
this, and there is no interoperable convention for it today.

## Decision
Deployment metadata is defined as an **official extension**, registered
at the extension key
`https://ai-catalog.org/extensions/deployment`, and carried in the
entry's `extensions` map. It is **not** added as a native `instances`
field on the entry.

The extension value is a JSON object with a REQUIRED, non-empty
`instances` array. Each Instance object carries:

- `instanceId` (REQUIRED, string) — stable identifier, unique within the
  entry.
- `url` (REQUIRED, string) — entry-point URL for this instance.
- `environment` (OPTIONAL, string) — e.g. `production`, `staging`,
  `development`.
- `releaseChannel` (OPTIONAL, string) — release maturity track, orthogonal
  to `environment`; e.g. `stable`, `beta`, `LTS`, `EDGE`.
- `region` (OPTIONAL, string) — e.g. `us-east-1`, `eu-west-1`.
- `dataResidency` (OPTIONAL, array of strings) — jurisdictions where data
  is stored or processed.
- `compliance` (OPTIONAL, array of strings) — compliance regimes the
  instance conforms to.
- `description` (OPTIONAL, string) — human-readable label.

The entry's top-level `url` remains the DEFAULT entry point for the
artifact, and one instance `url` SHOULD equal it. Each instance is an
alternative endpoint for the SAME logical artifact (same `identifier`);
instances are deployments, not distinct artifacts. A consumer that does
not understand the key MUST ignore it and fall back to the entry `url`; a
consumer that does understand it MAY select an instance matching its
policy and, if none matches, SHOULD NOT fall back to a non-conforming
instance. All identifiers use the `urn:air` format mandated by
[ADR-0015](0015-agent-identifier-naming.md).

## Rationale
- Keeps the core entry schema closed and stable, consistent with the
  closed-core philosophy of
  [ADR-0012](0012-extensibility-via-metadata.md); a not-yet-universal
  need does not force a change to the core.
- Consumers that do not recognize the key ignore it safely and fall back
  to the entry `url`, guaranteed by the existing `extensions` rule.
- The extension can evolve independently without requiring a major
  version bump of the specification.
- Aligns with the precedent already set by the Metadata official
  extension (`https://ai-catalog.org/extensions/metadata`).

## Alternatives Considered
- **Native `instances` field on the entry** — Rejected. It bloats the
  closed core for a need that is not universal and reopens the schema
  evolution problem ADR-0012 was written to avoid.
- **Separate curated catalogs per compliance regime** — Rejected as
  inflexible (per the issue's own analysis): it multiplies catalogs,
  duplicates identity, and cannot express a single logical artifact with
  many deployments.
- **Freeform vendor metadata** — Rejected. Ad-hoc, per-vendor keys give
  no interoperability, so no consumer could select instances
  deterministically across producers.

## Consequences
- Instance selection becomes deterministic and interoperable across
  producers and consumers.
- The metadata is advisory. It is unsigned unless carried in a Trust
  Manifest's `extensions`, and MUST NOT be treated as a security control
  on its own; `dataResidency` and `compliance` are producer assertions
  that a consumer needing assurance verifies via the Trust Manifest
  (attestations), not via this extension.
- The official extensions registry gains one entry:
  `https://ai-catalog.org/extensions/deployment`.
