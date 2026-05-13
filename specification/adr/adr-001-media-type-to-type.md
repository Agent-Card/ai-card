# ADR 001: Move from `mediaType` to `type` with Fixed Set of Values

## Status
Accepted

## Context
The `ai-catalog` specification originally used `mediaType` to identify the type of AI artifact in a catalog entry, intending to leverage standard IANA media types. However, in practice, we are using a closed, fixed set of types specific to the AI Catalog ecosystem (e.g., A2A agent cards, MCP servers, nested catalogs). Using the name `mediaType` implies support for any valid IANA media type and dynamic content negotiation, which is not the intent and can be confusing for implementers.

Furthermore, we need to support combined types that specify both the artifact type and the payload format (e.g., `application/ai-skills+tgz`).

## Decision
We will rename the `mediaType` field to `type` in the `CatalogEntry` schema.
We will restrict the allowed values for the `type` field to a fixed set of recognized strings:
- `application/a2a-agent-card+json`
- `application/mcp-server+json`
- `application/ai-catalog+json`
- `application/agent-registry`
- `application/ai-skills+tgz`
- `application/ai-skills+zip`
- `application/ai-skills+md`

## Consequences
- **Breaking Change**: This is a breaking change for any implementation relying on the `mediaType` field name.
- **Interoperability**: It ensures all implementers use a consistent, predictable set of identifiers for artifact types.
- **Simplicity**: It simplifies validation and parsing by removing the need to handle arbitrary IANA media types.
