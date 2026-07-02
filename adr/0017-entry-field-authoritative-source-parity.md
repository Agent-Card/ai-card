# ADR-0017: `description` and `version` Follow `displayName`'s Authoritative-Source Rule

## Status
Proposed

## Date
2026-07-02 (Proposed)

## Context
[ADR-0016](0016-displayname-optional.md) made the Catalog Entry `displayName` OPTIONAL and gave it a precise "authoritative-source" rule: a publisher SHOULD set `displayName` only when the referenced artifact does not already carry its own canonical human-readable name; when the artifact does carry one (an A2A Agent Card `name`, an MCP Server Card `title`), that artifact is the authoritative source and `displayName` SHOULD be omitted to avoid a value that drifts out of sync; and when `displayName` *is* present it takes precedence for display. A companion [Resolving an Artifact's Display Name](../specification/ai-catalog.md#resolving-an-artifacts-display-name) section defines the consumer resolution order.

`displayName` is not the only Catalog Entry member that can restate a value the referenced artifact already carries. Two others do, and today they are documented as plain optional fields with no equivalent guidance:

- **`description`** — a short prose description of the artifact. An **A2A Agent Card carries a REQUIRED `description`**, and an **MCP Server Card carries a REQUIRED `description`** ([SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127)). An entry that copies either restates a value that lives, canonically, in the document the consumer is about to fetch.
- **`version`** — the artifact's version. An **A2A Agent Card carries a REQUIRED `version`**, an **MCP Server Card carries a `version`**, and an MCP Registry `server.json` carries a `version`.

This is incoherent: the spec (and the MCP mapping appendix) tells a publisher to omit `displayName` when the Server Card already carries a `title`, while describing `description` and `version` — which have the *same* duplication-and-drift problem against the *same* Server Card — with no such steer. A publisher reading the field list has no reason to treat them differently, so entries end up carrying a copied `description`/`version` that silently drifts from the artifact.

Not every Catalog Entry member has this problem, and the rule should be applied only where it holds (see [Scope](#scope-fields-in-and-out) below).

## Decision
Extend the `displayName` authoritative-source rule (ADR-0016) to the other Catalog Entry members that duplicate a value the referenced artifact carries canonically: **`description`** and **`version`**.

**`description`.** A publisher SHOULD set entry `description` only when the referenced artifact does not already carry its own canonical description. When the artifact does carry one (an A2A Agent Card `description`, an MCP Server Card `description`), that artifact is the authoritative source and entry `description` SHOULD be omitted to avoid duplicating a value that can drift out of sync. When entry `description` *is* present it takes precedence for display: a consumer SHOULD render it as given even when it differs from the artifact's description — this is how a publisher deliberately provides a listing-specific blurb. A new "Resolving an Artifact's Description" section records the consumer resolution order, mirroring "Resolving an Artifact's Display Name".

**`version`.** A publisher SHOULD set entry `version` only when the referenced artifact does not carry its own version, **or** when the entry participates in a multi-version listing. `version` differs from `displayName`/`description` in that it is not merely cosmetic: the combination of `identifier` + `version` is the uniqueness key for [Multi-Version Entries](../specification/ai-catalog.md#multi-version-entries), and consumers sort on it to select the latest. Two consequences follow:

1. When a single entry references an artifact that carries its own version, entry `version` merely restates that value and SHOULD be omitted to avoid drift — the consumer can read the version from the artifact.
2. When a catalog lists multiple versions of the same `identifier`, `version` remains REQUIRED on those entries (unchanged from Multi-Version Entries) because it is doing structural disambiguation, not display.

Unlike `displayName`/`description`, a present entry `version` is **not** an authorial override of the artifact's value: it is used for sorting and version selection, so it SHOULD equal the version the referenced artifact reports. An entry `version` that contradicts the artifact's own version is a publishing error (it breaks latest-selection), not a deliberate override. Consumers MAY surface such a mismatch but SHOULD treat the entry `version`, when present, as authoritative for catalog-level sorting and selection.

This decision concerns only Catalog Entry members. It does not change `displayName` on `HostInfo` / `Publisher`, nor any Trust Manifest field.

## Scope: fields in and out
In scope (duplicate an artifact's canonical value):

- `displayName` — already covered by ADR-0016 (A2A Agent Card `name`, MCP Server Card `title`).
- `description` — A2A Agent Card `description`, MCP Server Card `description`.
- `version` — A2A Agent Card `version`, MCP Server Card `version`, MCP Registry `server.json` `version`.

Deliberately out of scope (no canonical artifact counterpart, or catalog-owned by design):

- `tags` — a discovery aid the catalog author curates for cross-artifact filtering. Card formats do not expose a canonical top-level tag list (A2A tags live per-skill), so there is nothing authoritative to defer to.
- `updatedAt` — records when the *entry* changed; it describes the catalog record, not a value the artifact carries.
- `publisher`, `trustManifest` — the catalog's deliberate value-add (publisher identity and trust), explicitly the information the referenced artifact formats *lack*; the catalog is the authoritative home, so there is nothing to omit. (A2A's `provider` overlaps loosely with `publisher`, but publisher identity is the catalog's trust anchor by design and is intentionally owned here.)
- `metadata` — the open extension point, already governed by the specification's Metadata Extensibility rules, which themselves say to avoid keys that duplicate defined fields.
- `identifier`, `type`, `url` / `data` — required structural fields, not duplicated human-readable values.

## Rationale
- **Consistency.** The same duplication-and-drift argument that made `displayName` optional applies verbatim to `description` and `version`; treating them differently is an inconsistency publishers will trip over.
- **Single authoritative source.** Keeping the value at its source (the referenced card) keeps it fresh and avoids the "two conflicting values, no principled tiebreak" failure mode.
- **Thin entry.** Reinforces the entry-as-thin-pointer posture ([ADR-0013](0013-authoring-vs-distribution-formats.md)): an entry adds the discovery/trust metadata the artifact lacks, rather than mirroring what it already has.
- **Field-appropriate nuance.** `description` is prose and behaves exactly like `displayName` (a present value is a deliberate override). `version` carries structural meaning (uniqueness + sorting), so the rule is adapted: omit the redundant single-entry case, keep it required for multi-version listings, and treat a present value as sort-authoritative rather than a free-form override.

## Consequences
- The spec's `description` and `version` field descriptions gain the SHOULD-omit-when-authoritative / present-takes-precedence language, and a "Resolving an Artifact's Description" section is added next to the display-name one. The MCP mapping-appendix rows for `description` and `version` are aligned with the existing `title`/`displayName` row.
- No schema change: `description` and `version` are already OPTIONAL in the CDDL, so this ADR is guidance only and is not a breaking change.
- Existing catalogs that populate `description` / `version` on every entry remain conformant; the guidance is a SHOULD, and any publisher that wants a self-describing list view may still populate them.
- Consumers gain a defined resolution order for `description`, matching the one they already implement for `displayName`.

## Alternatives Considered
- **Leave `description` / `version` as plain optional fields.** Rejected: it is the status quo that motivated this ADR — the guidance gap is exactly the inconsistency being closed.
- **Apply the identical "present takes precedence as a deliberate override" wording to `version`.** Rejected: a `version` that contradicts the artifact would break Multi-Version selection; version needs the sort-authoritative-but-SHOULD-match framing instead.
- **Generalize into one rule over an open set of "duplicating fields."** Rejected for now as over-abstraction; the concrete set is small (`displayName`, `description`, `version`) and each has enough field-specific nuance to warrant explicit treatment. A future field that duplicates an artifact value should follow this same pattern.

## Open Question
As with ADR-0016's note that a Server Card `title` is itself optional: the guidance keys on whether the artifact *actually carries* the value, not on its media type. If a referenced artifact omits its own `description` (or `version`), the entry SHOULD keep the field so the value is not lost.

## Meeting Reference
Records a proposal ahead of an AI Catalog bi-weekly working-group discussion; drafted as a follow-up to [ADR-0016](0016-displayname-optional.md). Update the Status and Date (and note who raised concerns and the agreed outcome, as in ADR-0011) once the working group ratifies it.
