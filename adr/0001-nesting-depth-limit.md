# ADR-0001: Maximum Catalog Nesting Depth of 4

**Status:** Proposed

**Date:** 2026-04-03

**Authors:** Darrel Miller

## Context

The AI Catalog specification allows entries with `mediaType`
`application/ai-catalog+json` to reference or embed other catalogs,
creating hierarchical structures. Without a recommended depth limit,
implementations risk unbounded recursion, fetch amplification, and
denial-of-service vulnerabilities.

We need to pick a concrete number to RECOMMEND as the maximum nesting
depth. The number must balance real-world organizational needs against
security, performance, and comprehensibility.

## Decision

The specification RECOMMENDS a maximum nesting depth of **4**.

## Rationale

### Precedent: npm dependency tree (depth 3)

The npm package manager originally allowed unbounded nesting of
`node_modules` directories. In practice, dependency trees regularly
exceeded 10 levels deep, causing:

- Windows path length failures (`MAX_PATH` = 260 characters)
- Duplicate copies of the same package at different depths
- Unmanageable directory structures

npm v3 (2015) fundamentally redesigned its algorithm to **flatten the
tree**, effectively capping meaningful nesting at roughly 3 levels. This
was one of the most impactful breaking changes in the Node.js ecosystem,
driven entirely by the pain of deep nesting.

### Our fourth level: multi-artifact packaging

A catalog hierarchy of 3 levels covers the organizational use case:

| Depth | Example |
|-------|---------|
| 1 | Enterprise catalog |
| 2 | Department catalog (Finance, Engineering, ML) |
| 3 | Team or product catalog |

The fourth level accommodates multi-artifact packaging — a single
catalog entry with a `publisher` that contains a nested catalog of
related artifacts (e.g., an A2A agent + MCP server + dataset). This is
the analog of an npm package's internal dependency list: it sits at the
leaf of the organizational tree.

```
Enterprise (1)
  └── Finance Department (2)
        └── Trading Team (3)
              └── Trading Suite: [A2A Agent, MCP Server, Dataset] (4)
```

### Why not deeper?

- **Fetch amplification:** Each level is a network request. With a
  branching factor of 10, depth 4 = 10,000 potential fetches; depth 8 =
  100,000,000.
- **Comprehensibility:** If a catalog hierarchy cannot be drawn on a
  whiteboard, it is too deep for humans to reason about.
- **Security surface:** Each hop is a potential MITM or DNS rebinding
  target. Fewer hops = smaller attack surface.
- **DNS CNAME precedent:** RFC 1034 §5.3.2 limits CNAME chains to 8,
  but that is widely considered too generous — most resolvers bail at
  5-6 in practice.

### Why not shallower?

A limit of 3 would force organizations to choose between hierarchy and
packaging — they could not have both. The fourth level specifically
enables the multi-artifact packaging use case without conflating it with
organizational structure.

## Consequences

- Implementations SHOULD enforce a depth limit of 4.
- Implementations MAY support deeper nesting but SHOULD document their
  limit.
- Catalog authors whose hierarchy exceeds 4 levels should restructure
  rather than rely on deeper nesting.
- The spec text uses RECOMMENDED (not MUST) to allow flexibility for
  edge cases while establishing a clear norm.
