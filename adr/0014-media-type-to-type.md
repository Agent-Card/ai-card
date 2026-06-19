# ADR 0014: Move from `mediaType` to `type` in Catalog Entries and Remove `mediaType` in Attestations

## Status
Accepted

## Date
2026-04-30 (Initial), 2026-05-14 (Revised), 2026-05-28 (Updated)

**Participants:** Pamela Dingle (Microsoft), Sam Betts (Cisco), Junjie Bu (Google), Darrel Miller (Microsoft), Alan Blount (Google), Srinivas Krishnan (Google), Krishna Thota (Google)

## Context
The `ai-catalog` specification originally used `mediaType` to identify the type of AI artifact in a catalog entry, intending to leverage standard IANA media types. However, in practice, we are using a closed, fixed set of types specific to the AI Catalog ecosystem (e.g., A2A agent cards, MCP servers, nested catalogs). Using the name `mediaType` implies support for any valid IANA media type and dynamic content negotiation, which is not the intent and can be confusing for implementers.

Furthermore, we need to support combined types that specify both the artifact type and the payload format. However, to ensure that these types are registerable as standard IANA media types if desired, they must use registered structured syntax suffixes (e.g., `+json`, `+zip`, `+gzip`) rather than unregistered suffixes like `+tgz` or `+md`.

Additionally, the `Attestation` object in the `trustManifest` schema had both a `type` field (identifying the attestation type, e.g., `SOC2-Type2`) and a `mediaType` field (indicating the format of the attestation document, e.g., `application/pdf`). This created terminology inconsistency and confusion for implementers who had to negotiate two separate typing fields within the same attestation metadata.

## Decision
We will make the following schema simplifications:

### 1. Rename `mediaType` to `type` in `CatalogEntry`
We will rename the `mediaType` field to `type` in the `CatalogEntry` schema.
The `type` field is an open text format, so any string value is accepted. To ensure clarity of ownership and governance, the recognized "known types" are partitioned into core protocol types and integrated third-party/ecosystem types:

#### Core Protocol Types (Governed by the AI Catalog WG)
- `application/ai-catalog+json` — nested AI Catalog
- `application/agent-card+json` — reserved for a generic Agent Card format

#### Integrated Ecosystem & Third-Party Types (Governed externally)
- `application/a2a-agent-card+json` — A2A Agent Card
- `application/mcp-server-card+json` — MCP Server Card
- `application/agent-skills+zip` — Agent Skill bundle in a ZIP archive
- `application/agent-skills+gzip` — Agent Skill bundle in a gzipped tarball
- `text/markdown; profile=urn:ai-catalog:agent-skills` — Agent Skill defined in a standard Markdown file

*Notes*:
  -  **hyphens formats**: We decided to use `agent-skills` instead of `agentskills` . Standard IANA media types and URL schemas heavily favor hyphens for readability when combining words (similar to standard formats like x-www-form-urlencoded or octet-stream)
  - **profile parameter for markdown**: (Darrel Miller) For the profile to be strictly standard-compliant, the profile parameter must be a valid URI. Since the team agreed in PR #36 to use the urn:air: (AI Resource) namespace for identifiers, the profile should utilize that exact URN structure. [Note this ADR will need to be updated when the URN structure for AI resources is officially registered.]

So, the fully compliant and correct format the team should use is:

text/markdown; profile="urn:air:agent-skill"

For any new or custom types not listed here, it is up to the specific client implementation to handle them correctly.

### 2. Remove `mediaType` from Attestations
We will completely remove the `mediaType` field from the `Attestation` object schema under `trustManifest`. Instead of requiring an explicit `mediaType` inside the attestation entry, consumers can resolve or infer the format directly from the HTTP response headers when fetching the attestation `uri`, or from the file extension in the URL path.

## Rationale

### Suffixes and Parameters in `CatalogEntry`
To ensure that our recommended types are fully registerable as official IANA media types, we adhere strictly to the IANA Structured Syntax Suffix registry rules (RFC 6838/6839):
- **Custom Ecosystem Formats**: Types like A2A Agent Cards (`application/a2a-agent-card+json`), MCP Servers (`application/mcp-server+json`), and Nested Catalogs (`application/ai-catalog+json`) use custom domain prefixes combined with the standard, registered `+json` suffix.
- **Agent Skill Bundles**: Packages are represented using custom prefixes combined with standard, registered syntax suffixes for archives/compression: `+zip` (registered under RFC 9559) and `+gzip` (registered under RFC 6839). Unregistered suffixes like `+tgz` are avoided to prevent registration failure.
- **Generic Formats (Markdown)**: Standard Markdown is represented by the generic, globally registered `text/markdown` media type. Because using `text/markdown` in isolation does not indicate the document is an Agent Skill (unlike custom prefixes), we use the standard IANA `profile` parameter (`profile=agent-skill`) to cleanly declare the semantic profile of the document while remaining 100% standard-compliant.

### Simplifying Attestations
During the workgroup meeting on May 28, 2026, the team discussed the inconsistency of having both a `type` and `mediaType` in attestations. Darrel Miller decided to simplify the structure by removing the `mediaType` field entirely, noting that the content type of the attestation can easily be determined from the URL or via content negotiation during retrieval. The group agreed to proceed with this removal to simplify the schema and gather implementation feedback.

## Consequences
- **Breaking Change**: This is a breaking change for any implementation relying on the `mediaType` field name in either `CatalogEntry` or `Attestation` objects.
- **Interoperability**: It ensures all implementers use a consistent, predictable set of identifiers for artifact types.
- **Simplicity**: It simplifies validation and parsing by removing the need to handle arbitrary IANA media types in the core catalog entry, and entirely eliminates the redundant `mediaType` in the attestation schema.
