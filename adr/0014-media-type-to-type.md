# ADR 0014: Move from `mediaType` to `type` with Fixed Set of Values

## Status
Accepted

## Date
2026-04-30

## Context
The `ai-catalog` specification originally used `mediaType` to identify the type of AI artifact in a catalog entry, intending to leverage standard IANA media types. However, in practice, we are using a closed, fixed set of types specific to the AI Catalog ecosystem (e.g., A2A agent cards, MCP servers, nested catalogs). Using the name `mediaType` implies support for any valid IANA media type and dynamic content negotiation, which is not the intent and can be confusing for implementers.

Furthermore, we need to support combined types that specify both the artifact type and the payload format (e.g., `application/ai-skills+tgz`).

## Decision
We will rename the `mediaType` field to `type` in the `CatalogEntry` schema.
The `type` field is an open text format, so any string value is accepted. The following are recognized "known types" in the ecosystem:
- `application/agent-card+json`
- `application/mcp-server+json`
- `application/ai-catalog+json`
- `application/agent-registry`
- `application/ai-skills+tgz`
- `application/ai-skills+zip`
- `application/ai-skills+md`

For any new or custom types not listed here, it is up to the specific client implementation to handle them correctly.

## Consequences
- **Breaking Change**: This is a breaking change for any implementation relying on the `mediaType` field name.
- **Interoperability**: It ensures all implementers use a consistent, predictable set of identifiers for artifact types.
- **Simplicity**: It simplifies validation and parsing by removing the need to handle arbitrary IANA media types.
