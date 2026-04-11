# ADR-0002: Defer Dependency Expression Between Entries

**Status:** Accepted

**Date:** 2026-04-02

**Participants:** Darrel Miller (Microsoft), Sam Betts (Cisco),
Junjie Bu (Google), Luca Muscariello (Cisco)

## Context

During the discussion of how to represent multi-artifact packages (e.g.,
an agent skill that requires an MCP server), Sam Betts proposed adding a
`dependencies` field on catalog entries. This would allow an entry to
declare that it depends on other entries to function.

However, the group identified significant complexity:

1. **AND vs. OR relationships.** When an agent supports both MCP and A2A
   protocols, those entries represent alternatives (OR) — the client
   picks one. When a skill requires an MCP server, that is a hard
   dependency (AND) — both must be deployed. Expressing both
   relationships requires additional semantics.

2. **Ambiguity within nested catalogs.** If a nested catalog contains an
   MCP entry and an A2A entry, are they alternatives or co-requisites?
   The catalog alone cannot distinguish these cases without additional
   annotation (e.g., an `artifactType` or `isBundle` flag).

3. **Downstream protocols may own this.** Luca Muscariello noted that
   dependency semantics may belong in the downstream artifact formats
   (e.g., the MCP server card itself could declare its dependencies)
   rather than in the catalog envelope.

4. **Scope creep risk.** Junjie Bu argued that the catalog should remain
   a simple index and that complex dependency management belongs in
   dynamic registries, not static catalogs.

## Decision

Defer any notion of describing dependencies between catalog entries.
The catalog remains a flat (or nested) index without dependency
semantics.

## Rationale

- Adding dependency support requires resolving the AND/OR ambiguity
  first, which is a non-trivial design problem.
- Darrel Miller observed that the "bundle" concept is really just a unit
  of acquisition: a nested catalog with a `publisher` already signals
  "these items were published as a set." This covers the primary
  packaging use case without explicit dependency syntax.
- The group reached consensus that implementation experience should
  drive whether and how dependencies are added, rather than
  specifying them prematurely.

## Consequences

- Entries cannot express "I require entry X" or "I am an alternative
  to entry Y" within the catalog format.
- Multi-protocol agents are represented as a nested catalog entry; the
  OR semantics are implied by the structure and left to client
  interpretation.
- If dependencies become necessary, a future ADR should address:
  - A `dependencies` array (with AND semantics) on catalog entries
  - A mechanism for OR relationships (possibly via nested catalogs
    or a `relationship` annotation)
  - Alignment with how OCI expresses dependencies (referrers/layers)
