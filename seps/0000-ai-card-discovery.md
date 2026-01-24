---
SEP: 0000
Title: AI Card Discovery via Well-Known URI
Author: [Simon Heimler] <simon.heimler@sap.com>
Status: draft
Type: Standards Track
Created: 2026-01-24
---

## Abstract

This SEP proposes a standardized discovery mechanism for AI native protocols and their metadata through a [.well-known URI](https://www.rfc-editor.org/rfc/rfc8615) endpoint (`/.well-known/ai-cards.json`). This solves the discovery problem that both [MCP](https://modelcontextprotocol.io) (Model Context Protocol) and [A2A](https://a2a-protocol.org) (Agent-to-Agent) protocols face, eliminating the need for each protocol to define its own discovery mechanism independently.

The proposal recognizes that:
- **A2A** has defined [`/.well-known/agent.json`](https://github.com/protocol-registries/well-known-uris/issues/66) for discovery, but has a **single-service assumption** (one agent per host)
- **MCP Server Cards** need to evolve from the existing MCP Registry `server.json` format to include tools, prompts, and resources, proposed as [MCP Server Cards (SEP-2127)](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127), with discovery at `/.well-known/mcp/server-card.json` also having a **single-service assumption** (one server per host)
- Both protocols face the **same limitation**: the single-service assumption doesn't fit real-world multi-service deployments
- **Discovery** is a shared concern that benefits from a unified, multi-service approach
- **Future-proofing**: The discovery mechanism is designed to support future AI protocols, versions and their metadata formats

By providing a protocol-agnostic discovery layer, this SEP enables a single host to advertise multiple MCP servers and/or multiple A2A agents, while allowing each protocol to maintain full ownership of their card formats, keeping their own autonomy and lifecycle.

## Motivation

### The Problem: Single-Service Assumption

Both **A2A** and **MCP** are defining protocol-specific discovery mechanisms:
- **A2A**: [`/.well-known/agent.json`](https://github.com/protocol-registries/well-known-uris/issues/66) 
- **MCP**: `/.well-known/mcp/server-card.json` ([SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127))

Both share a critical **single-service assumption**: one agent or server per host.

**This breaks down in real-world scenarios:**
- A host needs to expose multiple specialized services (e.g., petstore + inventory MCP servers, or sales + support A2A agents)
- A platform provides both MCP servers and A2A agents
- Registries must discover all available services, not just a "primary" one

### The Problem: Discovery Fragmentation

Having separate protocol-specific endpoints creates additional friction:
- **Multiple probes required**: Clients must try `/.well-known/agent.json`, then `/.well-known/mcp/server-card.json`, then future protocols
- **N+1 HTTP requests**: One per protocol, with many failures for unsupported protocols
- **No capability indication**: No standard way to discover what AI protocols a domain supports

### This Proposal

This SEP provides a **single, protocol-agnostic discovery endpoint** (`/.well-known/ai-cards.json`) that:
1. Enables **multi-service discovery** (multiple MCP servers and/or A2A agents per host)
2. Enables **multi-protocol discovery** (single request reveals all AI capabilities)
3. Allows each protocol to **maintain full ownership** of their metadata formats

## Specification

### Well-Known URI

Services supporting AI Card discovery MUST provide a JSON document at `/.well-known/ai-cards.json`.

By appending `.json` it is easier to host this and the linked metadata files on a static file server.

### Discovery Document Format

The discovery document MUST be a JSON object following the [ai-card-v0.schema.json](./0000-ai-card-discovery.schema.json) schema.

```jsonc
{
  "$schema": "https://ai-card.org/schemas/ai-card-v0.schema.json",
  "protocols": [
    // A2A agent example
    {
      "type": "a2a",
      "endpoints": [{"url": "https://example.com/a2a-endpoint"}],
      "metadata": {
        "type": "agent-card",
        "url": "https://example.com/.well-known/PetAgent.json"
      }
    },
    // First MCP server - petstore
    {
      "type": "mcp",
      "endpoints": [{"url": "https://example.com/mcp-endpoint"}],
      "metadata": {
        "type": "mcp-server-card",
        "url": "https://example.com/.well-known/petstore.mcp.json"
      }
    },
    // Second MCP server - inventory (demonstrates multi-service capability)
    {
      "type": "mcp",
      "endpoints": [{"url": "https://example.com/mcp-endpoint-inventory"}],
      "metadata": {
        "type": "mcp-server-card",
        "url": "https://example.com/.well-known/inventory.mcp.json"
      }
    }
  ]
}
```

**Note**: A single host can expose multiple MCP servers or multiple A2A agents. Each should be listed as a separate entry in the `protocols` array, as shown in the example above where two different MCP servers (petstore and inventory) are hosted on the same domain.

### URL Resolution

URLs in the discovery document (both `endpoints[].url` and `metadata.url`) **MAY be relative or absolute**.

#### Absolute URLs
Absolute URLs include the full protocol and authority:
- `https://example.com/mcp-endpoint`
- `https://api.example.com/.well-known/petstore.mcp.json`

#### Relative URLs
Relative URLs are resolved **relative to the location of the discovery document** (`/.well-known/ai-cards.json`), following [RFC 3986](https://www.rfc-editor.org/rfc/rfc3986) URL resolution rules:

**Path-relative URLs** (start with `./` or `../`):
- `./petstore.mcp.json` → resolves to `/.well-known/petstore.mcp.json`
- `./mcp-endpoint` → resolves to `/.well-known/mcp-endpoint`
- `../metadata/server.json` → resolves to `/metadata/server.json`

**Absolute-path URLs** (start with `/`):
- `/api/mcp` → resolves to `/api/mcp` (relative to host root)
- `/metadata/petstore.mcp.json` → resolves to `/metadata/petstore.mcp.json`

#### URL Resolution Examples

For a discovery document served at `https://example.com/.well-known/ai-cards.json`:

| URL Type | Example in Document | Resolves To |
|----------|---------------------|-------------|
| Absolute | `https://api.example.com/mcp` | `https://api.example.com/mcp` |
| Path-relative | `./petstore.mcp.json` | `https://example.com/.well-known/petstore.mcp.json` |
| Path-relative | `../metadata/server.json` | `https://example.com/metadata/server.json` |
| Absolute-path | `/api/mcp` | `https://example.com/api/mcp` |

**Recommendation**: Use relative URLs when metadata and endpoints are co-located with the discovery document. Use absolute URLs when pointing to external services or different domains.

### Metadata Files

Each protocol community maintains **full ownership** of their metadata format. This SEP only defines the discovery mechanism that points to these files.

#### Protocol-Specific Metadata Formats

- **MCP Server Cards** (Defined by MCP community):
  - Should evolve from the existing [MCP Registry `server.json` format](https://github.com/modelcontextprotocol/registry) ([JSON Schema](https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/schemas/2025-12-11.json))
  - Enhanced with tools, prompts, and resources as proposed in [SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127)
  - Full schema control remains with the MCP community

- **A2A Agent Cards** (Defined by A2A specification):
  - Already well-defined by the A2A specification
  - Full schema control remains with the A2A community

#### Scope of This SEP

This SEP **intentionally does not mandate** any particular structure for metadata files. It only standardizes:
1. How to **discover** multiple services on a single host
2. How to **identify** protocol types (`type` field)
3. How to **locate** metadata files (`metadata.url` field)

The scope could be expanded in the future to indicate version(s) of protocols and metadata formats (see Open Questions).

## Rationale

### Why Not a Shared Metadata Model?

Rather than creating a unified card format for MCP and A2A, this SEP keeps card definitions protocol-specific to avoid:
- Ongoing coordination overhead between protocol groups
- Potential compromises that don't serve either protocol well
- Slower evolution requiring multi-party consensus

### Design Principles

**Minimal Coordination Surface**: This SEP minimizes cross-protocol coordination to just three pieces of information:
1. Protocol type identifier (the `type` field)
2. Connection endpoints (the `endpoints` array)  
3. Metadata location (the `metadata` object with `type` and `url`)

Each protocol maintains **full ownership** of their card formats and can evolve independently.

**Standard Discovery Pattern**: Uses the well-established `.well-known` URI scheme ([RFC 8615](https://www.rfc-editor.org/rfc/rfc8615)) for decentralized, client-initiated discovery without requiring centralized registries.

### Integration with Existing Mechanisms

This SEP **coexists** with protocol-specific discovery endpoints:
- A2A's `/.well-known/agent.json`
- MCP's proposed `/.well-known/mcp/server-card.json` (SEP-2127)

**How it works:**
- The `protocols` array enables multi-service discovery
- `metadata.url` can point to protocol-specific card files
- Single-protocol deployments can use protocol-specific endpoints
- Multi-protocol deployments and registries benefit from unified discovery at `/.well-known/ai-cards.json`

## Backward Compatibility

This is a new feature and does not introduce backward compatibility concerns. Services that do not implement the well-known URI simply won't be discoverable through this mechanism.

## Reference Implementation

[To be provided]

## Security Implications

1. **HTTPS Required**: SHOULD require HTTPS for all URLs to prevent man-in-the-middle attacks
2. **URL Validation**: Clients MUST validate `metadata.url` and endpoint URLs are properly formatted
3. **Size Limits**: SHOULD enforce reasonable limits on discovery documents (e.g., 2MB) to prevent DoS attacks
4. **Access Control**: Discovery documents SHOULD be unprotected; MAY protect linked metadata files

## Open Questions

### 1. Protocol Versioning Strategy

**Question**: Should the protocol `type` field include version information (e.g., `"mcp/v1"`, `"a2a/v2"`)?

**Options**:
- **A)** Include in `type`: `"mcp/v1"`, `"a2a/v2"`
- **B)** Separate `version` field: `{"type": "mcp", "version": "1.0"}`
- **C)** Only in metadata files: Extract from `$schema` or dedicated version field

**Trade-offs**:
- Option A enables protocol version filtering without fetching metadata
- Option C keeps discovery simpler but requires metadata fetch to determine version
- Option B provides structured versioning but adds a required field

**Recommendation needed**: How important is version-based filtering at the discovery layer?

### 2. Metadata Format Versioning

**Question**: How should clients determine which version of a metadata format (e.g., MCP Server Card schema) is being used?

**Options**:
- **A)** Add `metadata.schemaVersion` field in discovery document
- **B)** Rely on `$schema` field within the metadata file itself
- **C)** Include version in `metadata.type`: `"mcp-server-card-v1"`

**Impact**: Affects whether clients can validate compatibility before fetching metadata files.

### 3. Supporting Multiple Protocol Versions

**Question**: If a service supports multiple versions of a protocol (e.g., MCP v1 and v2), how should this be represented?

**Options**:
- **A)** Separate entries in `protocols` array (one per version)
- **B)** Single entry with version negotiation at connection time
- **C)** List supported versions within the metadata file

**Example scenario**: A server supports both legacy clients (MCP v1) and new clients (MCP v2).

### 4. Governance and Coordination

**Question**: Should this SEP be:
- **A)** Proposed to MCP community (as MCP SEP) with A2A adoption?
- **B)** Maintained as separate cross-protocol specification?
- **C)** Submitted to IETF/W3C as a broader standard?

**Adoption strategy**: How do we ensure both MCP and A2A ecosystems adopt this approach?

### 5. Registry Discovery Requirements

**Question**: Should registries that index multiple protocols:
- **A)** **Require** `/.well-known/ai-cards.json` as primary discovery
- **B)** **Support** both AI Cards and protocol-specific endpoints (e.g., `/.well-known/agent.json`)
- **C)** **Also support** advanced protocols like ORD for enterprise environments

**Recommendation**: Option B provides maximum compatibility during transition period.

### 6. Registry Data Model Separation

**Question**: How should registry-specific metadata (ratings, download counts, verification status) be handled?

**Proposal**: Clarify that:
- **Service metadata** (MCP Server Cards, A2A Agent Cards) describes the service itself
- **Registry metadata** (ratings, stats) is a registry concern, potentially a superset model
- Registries are **optional** and can define their own API/data models

### 7. Access Control for Metadata

**Question**: Should the discovery document indicate when metadata requires authentication?

**Options**:
- **A)** Add `metadata.accessStrategy` field (e.g., `"public"`, `"oauth2"`, `"api-key"`)
- **B)** Clients discover through HTTP 401/403 responses
- **C)** No indication - assume public discovery, protected metadata requires docs

### 8. Dynamic and Tenant-Specific Metadata

**Question**: How should dynamic or tenant-specific metadata be handled?

**Use case**: Multi-tenant SaaS where each tenant has different available tools/capabilities.

**Options**:
- **A)** Allow dynamic generation of discovery document and metadata files
- **B)** Use query parameters: `/.well-known/ai-cards.json?tenant=acme`
- **C)** Document that discovery is static; dynamic capabilities in metadata files

**Security consideration**: Tenant isolation and information disclosure.

## Alternatives Considered

### Unified Card Model

Creating a single card format that both MCP and A2A adopt. Proposal is to reject this due to the coordination overhead and risk of creating yet another standard.

### Protocol-Specific Discovery (Status Quo)
Having each protocol define its own discovery mechanism:
- MCP: `/.well-known/mcp/server-card.json` ([SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127))
- A2A: `/.well-known/a2a/agent-card.json` (proposed)

**Advantages:**
- Each protocol has full control
- No cross-protocol coordination needed
- Simpler for single-protocol deployments

**Disadvantages:**
- Clients must probe multiple endpoints to discover all capabilities
- Registries must crawl multiple endpoints per domain
- No standard way to discover what protocols a domain supports
- N+1 HTTP requests where N is the number of protocols

**Integration Path:**
This SEP could be implemented **alongside** protocol-specific endpoints:
1. `/.well-known/ai-cards.json` serves as a directory
2. `metadata.url` points to protocol-specific endpoints like `/.well-known/mcp/server-card.json`
3. Single-protocol deployments can skip the directory and only implement their protocol-specific endpoint
4. Multi-protocol deployments and registries benefit from the unified discovery

This allows gradual adoption without breaking existing protocol-specific discovery mechanisms.

### DNS-Based Discovery

Using DNS TXT records for discovery (similar to DKIM or SPF). 
- Only works at domain level, not for path-based or port-based deployments
- Requires DNS infrastructure control
- More complex to implement and query
- Less accessible for web-based clients

This approach could be rejected or be allowed as an alternative to the .well-known URI approach in the future.

## Prior Art

### Summary of Related Standards

| Standard | Endpoint | Scope | Single/Multi-Service | Relationship to This SEP |
|----------|----------|-------|----------------------|-------------------------|
| **[A2A Agent Discovery](#a2a-well-knownagentjson)** | `/.well-known/agent.json` | A2A agents only | Single-service | This SEP enables multi-agent discovery |
| **[MCP SEP-2127](#mcp-sep-2127-mcp-server-cards---http-server-discovery)** | `/.well-known/mcp/server-card.json` | MCP servers only | Single-service | This SEP enables multi-server discovery |
| **[RFC 9727](#rfc-9727-well-knownapi-catalog)** | `/.well-known/api-catalog` | All API types | Multi-service | Generic, not AI-protocol-aware |
| **[ORD](#open-resource-discovery-well-knownopen-resource-discovery)** | `/.well-known/open-resource-discovery` | APIs, Events, Data Products | Multi-service | Enterprise-grade, broader scope than AI |

### MCP SEP-2127: MCP Server Cards - HTTP Server Discovery

[SEP-2127](https://github.com/modelcontextprotocol/modelcontextprotocol/pull/2127) proposes a comprehensive MCP Server Card format including:
- Server identification and versioning
- Transport configuration (streamable-http, stdio, SSE)
- Capabilities (tools, prompts, resources)
- Authentication requirements

Proposed at `/.well-known/mcp/server-card.json` with a **single-server assumption**.

**Relationship to this SEP:**
- SEP-2127 defines **what metadata to include** in server cards
- This SEP addresses **how to discover** multiple servers on a single host
- Discovery uses `/.well-known/ai-cards.json` pointing to individual server card files

### MCP Registry server.json Format

The [MCP Registry `server.json` format](https://github.com/modelcontextprotocol/registry/blob/main/internal/validators/schemas/2025-12-11.json) provides a foundation for MCP Server Cards but lacks tools, prompts, and resources. It should be enhanced (per SEP-2127) and made discoverable via `metadata.url`.

### A2A: `/.well-known/agent.json`

A2A has defined [`/.well-known/agent.json`](https://a2a-protocol.org/latest/specification/) ([IANA registration](https://github.com/protocol-registries/well-known-uris/issues/66)) for agent discovery.

**A2A Agent Cards include:**
- Agent identification and metadata
- Capabilities and supported operations
- Authentication and authorization requirements
- Endpoint information

**Relationship to this SEP:**
- A2A's card format remains **A2A-owned** and unchanged
- The single-agent assumption is addressed by this SEP
- `metadata.url` in the discovery document points to individual Agent Card files
- Enables discovery of **multiple agents** on a single host

### RFC 9727: `/.well-known/api-catalog`

[RFC 9727](https://datatracker.ietf.org/doc/rfc9727/) (IETF Standards Track, June 2025) defines generic API discovery using Linkset format for **any API type** (REST, GraphQL, SOAP).

**Key differences from this SEP:**

| Aspect | RFC 9727 | This SEP |
|--------|----------|----------|
| **Scope** | Generic APIs (REST, GraphQL, SOAP, etc.) | AI-native protocols (MCP, A2A) |
| **Protocol Awareness** | Protocol-agnostic | Protocol-specific (`type: mcp` vs `type: a2a`) |
| **Metadata** | Links to OpenAPI specs, generic docs | Links to AI-specific card formats (MCP Server Cards, A2A Agent Cards) |

**Relationship**: RFC 9727 is too generic for AI protocol discovery; this SEP provides AI-specific protocol identification and metadata.

### Open Resource Discovery: `.well-known/open-resource-discovery`

[ORD](https://open-resource-discovery.org/spec-v1) (Linux Foundation) is an enterprise-grade discovery protocol for APIs, events, data products, domain objects, and taxonomy.

**ORD capabilities include:**
- Comprehensive resource types (APIs, events, data products, domain objects)
- Static vs dynamic perspectives (system-type vs tenant-specific)
- Aggregation across multi-system landscapes
- Access strategies and governance

**Relationship to this SEP:**

ORD **can** handle AI protocol discovery today, but targets a different audience:

| Aspect | ORD | This SEP |
|--------|-----|----------|
| **Target Audience** | Enterprise IT, governance teams | AI developers |
| **Scope** | APIs, events, data products, taxonomy | AI protocols only (MCP, A2A) |
| **Complexity** | Comprehensive, extensive specification | Simple (5 required fields) |
| **Adoption Barrier** | High (complex data models) | Low (small JSON schema) |

**Coexistence options:**
- **Enterprise environments**: Use ORD for comprehensive discovery
- **AI-focused environments**: Use lightweight `/.well-known/ai-cards.json`
- **Hybrid deployments**: Implement both as needed

## Related Work

- [RFC 8615: Well-Known Uniform Resource Identifiers (URIs)](https://www.rfc-editor.org/rfc/rfc8615.html) - Foundation for .well-known URIs
- [RFC 9727: api-catalog](https://datatracker.ietf.org/doc/rfc9727/) - Generic API discovery (see Prior Art for detailed comparison)
- [Open Resource Discovery (ORD)](https://open-resource-discovery.org/spec-v1) - Enterprise-grade resource discovery (see Prior Art for detailed comparison)
- [RFC 9264: Linkset](https://www.rfc-editor.org/rfc/rfc9264.html) - Link set format used by api-catalog
- [OAuth 2.0 Authorization Server Metadata (RFC 8414)](https://www.rfc-editor.org/rfc/rfc8414.html) - Similar discovery pattern for OAuth servers
- [OpenID Connect Discovery](https://openid.net/specs/openid-connect-discovery-1_0.html) - Well-known endpoint for identity providers
