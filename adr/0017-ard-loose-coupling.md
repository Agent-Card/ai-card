# ADR-0017: Loose Coupling of ARD and AI-Catalog

## Status
Accepted

## Date
2026-07-02 (Discussed), 2026-07-09 (Agreed)

**Participants:** Darrel Miller, David Soria Parra, Jeffrey Damick, Jonathan Hefner, Junjie Bu, Luca Muscariello, Mariano Gonzalez, Martin Ristov, Pamela Dingle, Ramanathan Guha, Ramiz Polić, Sam Betts, Tadas Antanavicius

## Context
The AI-Catalog specification defines a lightweight format for agentic artifact discovery. Recently, a significant debate emerged regarding how to handle extensibility and vendor-specific fields. A proposal was made (Issue #58) to use a JSON-LD inspired `@context` mechanism to map prefix-based fields (e.g. `okf:type`) to absolute IRIs, replacing the nested `metadata` / `extensions` approach.

While ARD (Agentic Resource Discovery) spec group strongly advocated for `@context` to support rich, federated metadata returned from various domains (such as TechSoup and SEC databases, which already heavily utilize semantic web standards like schema.org), there was strong opposition from AI-Catalog TSC members. 

The primary concerns from the AI-Catalog perspective were:
1. **Scope:** AI-Catalog entries are meant to act as "least common denominator" pointers/leaves, not as rich data envelopes.
2. **Complexity:** Introducing `@context` and dynamic keys could complicate rigid bindings (e.g., gRPC protojson) and introduce perceived JSON-LD processing baggage.

After extensive discussions in the July 2 and July 9, 2026 working group meetings, the team concluded that the requirements of the two projects are fundamentally different. ARD requires the ability to aggregate rich, namespaced descriptions of resources directly in the discovery payload, while AI-Catalog requires strict, minimal schema definitions.

## Decision
AI-Catalog will proceed without native `@context` support and will instead rely on simpler mechanisms (such as an `extensions` map) for minimal extensions. ARD will evolve its data model independently to fully support the rich, namespaced metadata and semantic schemas required for comprehensive, web-scale agentic resource discovery.

## Rationale
- **Preserves Core Visions:** Allows AI-Catalog to remain a lightweight, strictly-typed "thin pointer" registry format.
- **Unblocks Innovation:** Frees ARD to adopt flexible semantic descriptors (JSON-LD / `@context`, schema.org) necessary for advanced discovery and LLM context building without forcing these complex requirements onto all AI-Catalog implementations.
- **Development Velocity:** Prevents the specifications from blocking each other due to conflicting data model requirements, allowing both groups to iterate rapidly.

