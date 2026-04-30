# ADR-0004: Eliminate Bundle as a Distinct Concept

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Sam Betts (Cisco),
Junjie Bu (Google), Luca Muscariello (Cisco)

## Context

The spec defined a "bundle" as a catalog entry whose `mediaType` is
`application/ai-catalog+json`, with the semantic that the nested
artifacts are dependent on each other and acquired as a unit. This
created ambiguity: a nested catalog could be either organizational
(hierarchy) or compositional (bundle), and the format had no way to
distinguish them.

Darrel Miller raised the question: "Does that mean we just get rid of
the notion of bundle completely?" and proposed that the publisher field
on a catalog entry is sufficient signal: "If you put a publisher in a
catalog, that would be a signal that that publisher published as a set,
and would make sense to acquire as a set."

## Decision

Eliminate "bundle" as a named concept. An entry with `mediaType`
`application/ai-catalog+json` is simply a nested catalog. An entry that
has a `publisher` may be interpreted by consumers as a set of items that
could be acquired as a unit.

## Rationale

- The distinction between "bundle" and "collection" was confusing and
  Sam Betts noted "the concepts seem to be reversed."
- Darrel Miller: "I think it's a red herring... a consumer can choose
  to download all of the items in that nested catalog and install them
  as a unit. In which case, they've just acquired a bundle."
- The presence of a `publisher` on a nested catalog entry provides
  adequate signal that the contents were published as a coherent set.
- Removing the term reduces spec vocabulary and eliminates a source of
  confusion in the data model.

## Consequences

- No "bundle" terminology, media type, or special semantics in the spec.
- All nested catalog entries are treated uniformly regardless of intent.
- Consumers infer packaging intent from the presence of `publisher` and
  context, not from a structural distinction.
- Future work on explicit dependency semantics (see ADR-0002) may
  revisit whether a more formal packaging concept is needed.
