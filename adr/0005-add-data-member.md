# ADR-0005: Add `data` Member for Inline Artifact Content

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Sam Betts (Cisco),
Junjie Bu (Google), Luca Muscariello (Cisco)

## Context

After removing inline nested catalogs (bundles), the group discussed
whether catalog entries should support embedding artifact content
directly. Junjie Bu argued this is needed for dynamic registries: "when
a registry dynamically queries, it will return the same AI catalog
format, but it will have embedded data, because you don't want to say,
oh, this is only all the URLs, they have to grab the actual agent card
data."

The discussion centered on naming: Darrel asked "Do we prefer the word
inline over embedded?" Junjie suggested "protocol" (as in protocol
data), but Sam Betts proposed "data" and Luca Muscariello immediately
agreed: "Data."

## Decision

Add a `data` member as a oneOf with `url` on catalog entries. An entry
MUST contain exactly one of `url` (reference) or `data` (inline
content). The field name is `data`.

## Rationale

- `data` is concise, unambiguous, and avoids overloaded terms like
  "inline" or "embedded."
- The oneOf constraint with `url` keeps entries simple: every entry
  points to or contains exactly one artifact.
- Junjie's registry use case is compelling: a registry API returning
  AI Catalog format should be able to include full artifact content
  without requiring a second fetch.
- Darrel noted that supporting `data` technically makes the catalog an
  "envelope" for artifact content. The group accepted this tradeoff
  for the registry use case.

## Alternatives Considered

- **`inline`** — the original field name. Rejected as less intuitive.
- **`embedded`** — considered but "data" was preferred as shorter.
- **`protocol`** — suggested by Junjie Bu but too narrow in meaning.
- **URL-only (no inline)** — Junjie initially suggested removing inline
  entirely but then argued for keeping it for registry responses.

## Consequences

- Catalog entries have a `url | data` choice for artifact content.
- Consumers MUST handle both forms.
- The `data` value's structure is opaque to the catalog spec — it is
  determined by the entry's `mediaType`.
