# ADR-0016: displayName Is Optional on a Catalog Entry

## Status
Proposed

## Date
2026-06-18 (Proposed)

## Context
A Catalog Entry is a thin pointer: it carries an `identifier`, a `mediaType`, and exactly one of `url` or `data` locating the full artifact. `displayName` (a human-readable name for the artifact) is a REQUIRED member of every Catalog Entry, and is listed among the required-at-minimum members of a Minimal Catalog (Level 1).

For the card-shaped artifact types this spec calls out by media type, a human-readable name already lives inside the referenced artifact:

- An **A2A Agent Card** has a REQUIRED, human-readable `name`.
- An **MCP Server Card** carries a human-readable `title` (and a required human-readable `description`); its `name` is a reverse-DNS machine identifier.

Requiring `displayName` on the entry therefore forces every catalog publisher to copy a value that already exists in the document the client is about to fetch, and to keep the two in sync indefinitely. When they drift, a consumer is left with two conflicting human-readable names and no principled way to pick.

Not all artifacts self-name, however. Opaque artifacts referenced by a catalog — a raw dataset (`application/parquet`), a model blob, a skill bundle (`application/agentskill+zip`), or a nested catalog — have no embedded canonical name. For those, the entry is the only place a human-readable name can live.

## Decision
`displayName` is an **OPTIONAL** member of a Catalog Entry, not a required one, and is removed from the Minimal Catalog (Level 1) required-at-minimum set.

Guidance: a publisher SHOULD set `displayName` only when the referenced artifact does not already carry its own canonical human-readable name. When the artifact does carry one, that artifact is the authoritative source and `displayName` SHOULD be omitted. When `displayName` is present and disagrees with a name carried by the referenced artifact, consumers SHOULD treat the artifact's own name as authoritative.

This decision concerns only the Catalog Entry. `displayName` on `HostInfo` and `Publisher` is unchanged — those name the catalog host and publishing organization, which is genuinely catalog-authored metadata with no other home.

## Rationale
- For self-naming artifacts (A2A Agent Cards, MCP Server Cards), requiring an entry-level name guarantees permanent duplication and a standing sync burden.
- Keeping the name authoritative at its source keeps it fresh and avoids the "two conflicting names" failure mode.
- The entry stays a thin pointer, consistent with the catalog's role as a lightweight directory of links (ADR-0013: authoring/discovery format).
- The field is preserved (not removed) so opaque, nameless artifacts still have a place to carry a human-readable name.
- Mirrors the project's existing "optional, not mandatory" posture for discovery mechanics (ADR-0011).

## Alternatives Considered
- **Keep `displayName` required.** The strongest argument is browsing UX: a UI listing N entries shouldn't have to fetch N artifacts just to show names. Rejected as a permanent duplication/sync cost; the optional form still lets any publisher populate `displayName` on every entry when a self-describing list view is wanted — it just isn't forced on card-backed entries.
- **Remove `displayName` from the entry entirely.** Rejected because opaque artifacts (datasets, model blobs, skill bundles, nested catalogs) embed no self-describing name and would be left nameless in a catalog.

## Open Question
An MCP Server Card's `title` is itself OPTIONAL. The guidance above is keyed on whether the artifact *carries a canonical name*, not on its media type: if a referenced Server Card omits `title`, the entry SHOULD keep `displayName` so the artifact is not left with only a reverse-DNS identifier and a prose description.

## Meeting Reference
Slated for discussion at the 2026-06-18 AI Catalog bi-weekly working-group call; this ADR records the proposal ahead of that discussion. Update the Status and Date (and note who raised concerns and the agreed outcome, as in ADR-0011) once the working group ratifies it.
