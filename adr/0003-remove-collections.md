# ADR-0003: Remove Top-Level Collections in Favor of Catalog Entries

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Sam Betts (Cisco),
Junjie Bu (Google), Luca Muscariello (Cisco)

## Context

The spec had two separate mechanisms for catalog hierarchy:

1. **`entries[]`** — catalog entries that could reference nested catalogs
   (called "bundles") with `mediaType: application/ai-catalog+json`
2. **`collections[]`** — a top-level array of Collection Reference
   objects pointing to child catalogs

Sam Betts observed that these "felt like they were the wrong way around."
Collections and bundles both ultimately point to child catalogs, but with
different semantics (organization vs. dependency) and at different
structural positions (top-level array vs. entry).

## Decision

Remove the top-level `collections` array entirely. Catalog hierarchy is
achieved exclusively through entries with `mediaType` set to
`application/ai-catalog+json`.

## Rationale

- A Collection Reference was essentially a catalog entry without
  identity or trust metadata. Making it a full catalog entry gives it
  an `identifier`, optional `trustManifest`, and `publisher` — strictly
  more capable.
- One mechanism instead of two reduces cognitive load for authors and
  consumers.
- Sam Betts: "collections goes away, and what you're left with is
  entries that can be catalogues, which are downstream catalogues."
- Consensus was unanimous; no objections raised.

## Consequences

- The `CollectionRef` type is removed from the schema.
- The `collections` member is removed from the top-level AI Catalog
  object.
- All hierarchy is expressed through `entries[]`, using the catalog
  media type.
- Clients filter entries by `mediaType` to distinguish catalog pointers
  from leaf artifacts.
