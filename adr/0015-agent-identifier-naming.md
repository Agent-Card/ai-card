# ADR 0015: Align Agent Identifier Naming with Proposal

## Status
Proposed

## Date
2026-05-13

## Context
The `ai-catalog` specification originally recommended using URNs or URIs for the `identifier` field in catalog entries, but did not mandate a specific format. This led to inconsistency in examples and potential interoperability issues across different registries and orchestrators.

To ensure global federation and industry-wide interoperability, we need a standardized, secure naming protocol for AI actors.

## Proposal
We will align the agent identifier naming in `ai-catalog.md` with the naming standards proposed in [PR #19](https://github.com/Agent-Card/ai-catalog/pull/19).
The `identifier` field will follow the URN format: `urn:ai:{publisher}:{namespace}:{name}`.
- `publisher`: The domain where the artifact is hosted (e.g., `example.com`).
- `namespace`: Optional segments separated by `:` (e.g., `hr`, `finance`, `finance:agent`, `mcp`, `skill`, `catalog`).
- `name`: The specific name of the artifact.

## Rationale
We propose this URN format for the following reasons:
- **Nomenclature Stability**: The URN acts as an abstract, stable contract. Relocating workloads or changing infrastructure does not break client discovery code.
- **Global Uniqueness**: Domain-anchored URNs guarantee cross-network uniqueness without infrastructure overhead.
- **Separation of Concerns**: It separates the logical name used for discovery and routing from the cryptographic identity used for trust verification. The `identity` field in the `trustManifest` can utilize various security schemas for cryptographic verification (e.g., SPIFFE, DID, DNS), while this URN-based `identifier` provides a consistent and stable naming mechanism that remains constant even if the underlying security infrastructure changes.
- **Interoperability**: Standardizing on this format enables registries to index and search agents consistently.

## Consequences
- **Breaking Change**: Existing catalogs using non-compliant URN formats will need to update their identifiers.
- **Consistency**: All examples and implementations will follow a uniform naming standard.
