# ADR-0006: Single `url` Value Per Entry (Not an Array)

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Sam Betts (Cisco),
Junjie Bu (Google)

## Context

Sam Betts asked whether `url` could be a list, to handle the case where
"the same card is served from multiple domains." This would allow
entries to declare mirror URLs for redundancy.

## Decision

Keep `url` as a single string value. Do not support an array of URLs.

## Rationale

- Junjie Bu: "I think one-expanding-to-many is durable... let's maybe
  just keep it simple."
- If an artifact is available at multiple URLs, it can be represented as
  multiple entries with the same `identifier`.
- HTTP redirects already solve the availability problem at the transport
  layer.
- Darrel Miller's response — "go redirect" — summarized the consensus.
- Starting with a scalar keeps the schema simple; expanding to an array
  later is a backward-compatible change if needed.

## Consequences

- Each catalog entry has exactly one `url` (or one `data`).
- Mirror/replica scenarios must use separate entries or HTTP redirects.
- A future spec revision could expand `url` to accept an array without
  breaking existing consumers that read only the first value.
