# ADR 0014: Move from `mediaType` to `type` with Fixed Set of Values

## Status
Accepted

## Date
2026-04-30 2026-05-14

**Participants:** Pamela Dingle (Microsoft), Sam Betts (Cisco), Junjie Bu (Google), Darrel Miller (Microsoft), Alan Blount (Google), Srinivas Krishnan (Google), Krishna Thota (Google)

## Context
The `ai-catalog` specification originally used `mediaType` to identify the type of AI artifact in a catalog entry, intending to leverage standard IANA media types. However, in practice, we are using a closed, fixed set of types specific to the AI Catalog ecosystem (e.g., A2A agent cards, MCP servers, nested catalogs). Using the name `mediaType` implies support for any valid IANA media type and dynamic content negotiation, which is not the intent and can be confusing for implementers.

Furthermore, we need to support combined types that specify both the artifact type and the payload format. However, to ensure that these types are registerable as standard IANA media types if desired, they must use registered structured syntax suffixes (e.g., `+json`, `+zip`, `+gzip`) rather than unregistered suffixes like `+tgz` or `+md`.

## Decision
We will rename the `mediaType` field to `type` in the `CatalogEntry` schema.
The `type` field is an open text format, so any string value is accepted. To ensure clarity of ownership and governance, the recognized "known types" are partitioned into core protocol types and integrated third-party/ecosystem types:

### Core Protocol Types (Governed by the AI Catalog WG)
- `application/ai-catalog+json` — nested AI Catalog
- `application/agent-card+json` — reserved for a generic Agent Card format

### Integrated Ecosystem & Third-Party Types (Governed externally)
- `application/a2a-agent-card+json` — A2A Agent Card
- `application/mcp-server+json` — MCP Server Card
- `application/ai-skills+zip` — AI Skill bundle in a ZIP archive
- `application/ai-skills+gzip` — AI Skill bundle in a gzipped tarball
- `text/markdown; profile=ai-skill` — AI Skill defined in a standard Markdown file

For any new or custom types not listed here, it is up to the specific client implementation to handle them correctly.

### Rationale for Suffixes and Parameters
To ensure that our recommended types are fully registerable as official IANA media types, we adhere strictly to the IANA Structured Syntax Suffix registry rules (RFC 6838/6839):
- **Custom Ecosystem Formats**: Types like A2A Agent Cards (`application/a2a-agent-card+json`), MCP Servers (`application/mcp-server+json`), and Nested Catalogs (`application/ai-catalog+json`) use custom domain prefixes combined with the standard, registered `+json` suffix.
- **AI Skill Bundles**: Packages are represented using custom prefixes combined with standard, registered syntax suffixes for archives/compression: `+zip` (registered under RFC 9559) and `+gzip` (registered under RFC 6839). Unregistered suffixes like `+tgz` are avoided to prevent registration failure.
- **Generic Formats (Markdown)**: Standard Markdown is represented by the generic, globally registered `text/markdown` media type. Because using `text/markdown` in isolation does not indicate the document is an AI Skill (unlike custom prefixes), we use the standard IANA `profile` parameter (`profile=ai-skill`) to cleanly declare the semantic profile of the document while remaining 100% standard-compliant.

## Consequences
- **Breaking Change**: This is a breaking change for any implementation relying on the `mediaType` field name.
- **Interoperability**: It ensures all implementers use a consistent, predictable set of identifiers for artifact types.
- **Simplicity**: It simplifies validation and parsing by removing the need to handle arbitrary IANA media types.
