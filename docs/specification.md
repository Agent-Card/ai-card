---
icon: material/file-document
---

# Full Specification

The AI Catalog specification is published as a W3C-style normative document.

**[View the full specification :material-arrow-right:](https://agent-card.github.io/ai-catalog/spec/){ .md-button .md-button--primary }**

## What's in the specification

The specification covers:

- **Core schema** — formal definitions for AI Catalog, Catalog Entry, Host Info, Publisher, and all fields
- **Trust Manifest** — identity binding, attestations, provenance links, signing, and verification procedures
- **Discovery** — well-known URI, link relation headers, and agent-driven discovery
- **Conformance levels** — normative requirements for Minimal, Discoverable, and Trusted catalogs
- **Version handling** — compatibility rules for producers and consumers
- **Security considerations** — trust layers, catalog poisoning, typosquatting, embedded content safety
- **CDDL schema** — formal machine-readable schema
- **Mappings** — how AI Catalog maps to OCI Distribution, MCP servers (via MCP Server Cards), and Claude Code Plugins

## Relationship to these docs

The developer documentation you're reading now is a practical guide aimed at getting you productive quickly. It draws from the specification but is not normative.

When building a production implementation, refer to the specification for precise requirements — especially for Trust Manifest verification, signature algorithms, and conformance obligations.
